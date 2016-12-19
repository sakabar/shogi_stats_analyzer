#!/bin/zsh

set -u

result_str_file=$(mktemp -t hoge)
cat shogi_log.csv | grep -v "^\"1棋譜ファイル名" | while read line; do
    kif_file=$(echo $line | awk -F, '{print $1}' | tr -d '"')
    if [[ $kif_file:e != "kif" ]]; then
        continue
    fi
    ./shell/read_kif.sh kif/$kif_file > $result_str_file 2>/dev/null

    finish=$(cat $result_str_file | awk -F, '{print $6}')
    win_lose=$(cat $result_str_file | awk -F, '{print $7}')
    sengo=$(cat $result_str_file | awk -F, '{print $8}')

    orig_finish=$(echo $line | awk -F, '{print $6}')
    orig_win_lose=$(echo $line | awk -F, '{print $7}')
    orig_sengo=$(echo $line | awk -F, '{print $8}')

    if [[ $finish != $orig_finish ]] || [[ $win_lose != $orig_win_lose ]] || [[ $sengo != $orig_sengo ]]; then
        if [[ $finish != $orig_finish ]] && [[ $orig_finish = "\"接続\"" ]] && [[ $win_lose = $orig_win_lose ]] && [[ $sengo = $orig_sengo ]]; then
            : #元の記述が「接続」、システムが「投了」を出力した場合は、正解と見なす
        else
            echo $line
            cat $result_str_file
            echo "----------"
            # echo $finish
            # echo $win_lose
        fi
    fi
done

rm -rf $result_str_file
