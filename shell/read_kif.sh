#!/bin/zsh
#2016/11/17-2016/11/22

set -u

#Usage: shell/read_kif.sh hoge.kif
#1. hoge.kif名前を対局開始時間に基づいて変換し、kifディレクトリ以下に保存
#2. 対局情報をcsv形式で出力 (shogi_log.csvに手動で追記する必要あり)

if [[ $# -ne 1 ]]; then
    echo "$0 : Argument Error: <kif_file>">&2
    exit 1
fi

input_kif_file=$1

tmp_file=`mktemp -t tmpfile_`
cat $input_kif_file | nkf -w -Lu | grep -v "^$" > $tmp_file

kif_dir=kif_dir/raw/utf8
#開始日時：2016年11月16日(水) 12:25:10
new_file_name=$kif_dir"/"$(cat $tmp_file | grep "^開始日時" | head -n 1 | grep -o "[0-9]\+/[0-9]\+/[0-9]\+ [0-9]\+[:：][0-9]\+" | tr ' ' '_' | tr -d '/:：')".kif"
if [[ $new_file_name = $kif_dir"/.kif" ]]; then
    new_file_name=$kif_dir"/"$(cat $tmp_file | grep "^開始日時" | head -n 1 | grep -o "[0-9]\+年[0-9]\+月[0-9]\+日(.) [0-9]\+[:：][0-9]\+" | gsed -e 's/([^)]*)//g' | tr ' ' '_' | tr '年' '/' | tr '月' '/' | tr -d '日' | tr -d '/:：')".kif"
fi
if [[ $new_file_name = $kif_dir"/.kif" ]]; then
    new_file_name=$kif_dir"/"$(cat $tmp_file | grep "^開始日時" | head -n 1 | grep -o "[0-9]\+年[0-9]\+月[0-9]\+日 [0-9]\+:[0-9]\+" | gsed -e 's/([^)]*)//g' | tr ' ' '_' | tr '年' '/' | tr '月' '/' | tr -d '日' | tr -d '/:')".kif"
fi
if [[ $new_file_name = $kif_dir"/.kif" ]]; then
    if [[ $(echo $input_kif_file:t:r | grep -c "^81Dojo") -ge 1 ]]; then
        # 81Dojo-2016-11-22-20-27.kif
        new_file_name=$kif_dir"/"$(echo $input_kif_file:t:r | sed -e 's/^81Dojo-//' | sed -e 's/-//' | sed -e 's/-//' | sed -e 's/-/_/' | sed -e 's/-//')".kif"
    fi
fi


if [[ $new_file_name = $kif_dir"/.kif" ]]; then
    echo "Time read error" >&2
    exit 1
fi


is_touryo=$(cat $tmp_file | grep -E -c "[0-9]+ 投了|[0-9]+ 詰み")
is_jikan=$(cat $tmp_file | grep -c "[0-9]\+ 切れ負け")
is_hansoku=$(cat $tmp_file | grep -c "反則手")
if [[ $is_touryo -eq 0 ]] && [[ $is_jikan -eq 0 ]] && [[ $is_hansoku -eq 0 ]]; then
    last_hand_num=$(cat $tmp_file | tail -n 1 | awk '{print $1}')
    echo " $[$last_hand_num + 1] 投了" >> $tmp_file
fi

if [[ $is_touryo -ge 1 ]] && [[ $is_jikan -ge 1 ]]; then
    echo "Unexpected pattern: both touryo and jikan" >&2
    exit 1
fi

if [[ -e $new_file_name ]]; then
    echo $new_file_name" already exists." >&2

    rm -rf tmp_file
    # mv $new_file_name $new_file_name".old"
    # mv -f $tmp_file $new_file_name
else
    echo "generate "$new_file_name >&2
    mv $tmp_file $new_file_name
fi

field="$(cat $new_file_name | grep "^棋戦" | awk -F'：' '{print $2}')"
if [[ $field = "" ]]; then
    field="$(cat $new_file_name | grep "^場所" | awk -F'：' '{print $2}')"
fi


is_sente=$(cat $new_file_name | grep "^先手：" | grep -E -c "pymeoa|saka_bar|榊原|プレイヤー|あなた")
is_gote=$(cat $new_file_name | grep "^後手：" | grep -E -c "pymeoa|saka_bar|榊原|プレイヤー|あなた")


if [[ $is_sente -eq 1 ]]; then
    teban="先手"
elif [[ $is_gote -eq 1 ]]; then
    teban="後手"
else
    echo "Unexpected pattern. 1">&2
    echo "\"${new_file_name:t}\",\"${field}\",\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\""
    exit 1
fi

is_hansoku=$(cat $new_file_name | grep -c "反則手")
is_touryo=$(cat $new_file_name | grep -c -E "[0-9]+ 投了|[0-9]+ 詰み")
is_jikan=$(cat $new_file_name | grep -c "[0-9]\+ 切れ負け")

if [[ $is_jikan -ge 1 ]]; then
    loser_num=$(cat $new_file_name | grep "[0-9]\+ 切れ負け" | tail -n 1 | awk '{print $1}')
    finish="時間"
    if [[ $[$loser_num % 2] -eq 0 ]]; then
        loser="後手"
    else
        loser="先手"
    fi

    if [[ $loser = $teban ]]; then
        win_lose="負"
    else
        win_lose="勝"
    fi
elif [[ $is_hansoku -ge 1 ]]; then
    #反則手の場合、投了と違って「反則手」の手数番号の偶奇と着手者の偶寄が異なる
    #「33 反則手」という行があったら、32手目が反則手→後手の負け
    #「33 投了」という行があったら、32手目の次の人が投了→後手の勝ち
    loser_num=$(cat $new_file_name | grep "[0-9]\+ 反則手" | tail -n 1 | awk '{print $1}')
    finish="反則"
    if [[ $[$loser_num % 2] -eq 0 ]]; then
        loser="先手"
    else
        loser="後手"
    fi

    if [[ $loser = $teban ]]; then
        win_lose="負"
    else
        win_lose="勝"
    fi
else
    finish="投了"
    loser_num=$(cat $new_file_name | grep "[0-9]\+ 投了" | tail -n 1 | awk '{print $1}')
    if [[ $loser_num = "" ]]; then
        loser_num=$(cat $new_file_name | grep "[0-9]\+ 詰み" | tail -n 1 | awk '{print $1}')
    fi

    if [[ $[$loser_num % 2] -eq 0 ]]; then
        loser="後手"
    else
        loser="先手"
    fi

    if [[ $loser = $teban ]]; then
        win_lose="負"
    else
        win_lose="勝"
    fi
# else
#     echo "Unexpected pattern 2.">&2
#     echo "\"${new_file_name:t}\",\"${field}\",\"\",\"\",\"\",\"\",\"\",\"${teban}\",\"\",\"\",\"\""
#     exit 1
fi

battle_time=""
aite_level=""
if [[ $field = "将棋ウォーズ(10分)" ]];then
    field="将棋ウォーズ"
    battle_time="00:10+00"
    if [[ $teban = "先手" ]]; then
        aite_dankyu=$(cat $new_file_name | grep "^後手" | head -n1 | grep -E -o "[0-9]+級|初段|二段|三段|四段")
    else
        aite_dankyu=$(cat $new_file_name | grep "^先手" | head -n1 | grep -E -o "[0-9]+級|初段|二段|三段|四段")
    fi

    if [[ $aite_dankyu = "四段" ]]; then
        aite_level=750
    elif [[ $aite_dankyu = "三段" ]]; then
        aite_level=650
    elif [[ $aite_dankyu = "二段" ]]; then
        aite_level=550
    elif [[ $aite_dankyu = "初段" ]]; then
        aite_level=450
    else
        kyu=$(echo $aite_dankyu | tr -d '級')
        tmp_level=$[450 - 100 * $kyu]
        if [[ $tmp_level -le 0 ]]; then
            aite_level=0
        else
            aite_level=$tmp_level
        fi
    fi
elif [[ $(echo $field | grep -o "^......" | head -n 1 ) = "81Dojo" ]]; then
    field="81Dojo"
elif [[ $(echo $field | grep -o "^........." | head -n 1 ) = "レーティング対局室" ]]; then
    battle_time=$(echo $field | grep -o "([^)]*)" | tr -d "()")
    field="24"
elif [[ $(echo $field | grep -o "^......" | head -n 1 ) = "将棋クエスト" ]]; then
    battle_time=$(echo $field | grep -o "([^)]*)" | tr -d "()")
    field="将棋クエスト"
fi

echo "\"${new_file_name:t}\",\"${field}\",\"${battle_time}\",,${aite_level},\"${finish}\",\"${win_lose}\",\"${teban}\",\"\",\"\",\"\""
