#!/bin/zsh

set -u

#Usage: shell/read_piyo_kifs.sh
#1. SSAのディレクトリ中にあるpiyo_*.kifの名前を対局開始時間に基づいて変換し、kifディレクトリ以下に保存
#2. 対局情報をshogi_log.csvに追記
#3. cache/trash_[時刻]ディレクトリに、元のkifを保存

trash_dir=cache/trash$(date "+%y%m%d_%H%M")
mkdir -p $trash_dir

#81Dojoの棋譜のファイル名から対局開始時間を読み取って、棋譜ファイル内に記入
# 81Dojo-2016-12-31-14-10.kif
# "開始日時：2016/12/31"の行 -> "開始日時：2016/12/31 14:10:00"に書き換え
cnt=$(ls -U *.kif  | grep -c "^81Dojo-")
if [ $cnt -ge 1 ];then
    for f in 81Dojo-*.kif; do
        nkf --overwrite -w -Lu $f
        nf=$(cat $f | grep -m 1 "^開始日時" | awk '{printf("%d",NF)}')
        if [ $nf -eq 1 ]; then
            start_time=$(echo -n $f:t:r | cut -d '-' -f5,6 | tr '-' ':')":00"
            gsed -i 's|^\(開始日時.*\)$|\1 '$start_time'|' $f
        fi
    done
fi

ls -U | grep -e "^81Dojo-.*\.kif$" -e "^piyo_.*.kif$" | while read f; do
    shell/read_kif.sh $f

    #正しく読み込めた棋譜のみ移動
    if [ $? -eq 0 ]; then
        mv $f $trash_dir
    fi
done | sort >> shogi_log.csv
