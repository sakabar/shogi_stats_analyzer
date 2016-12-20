#!/bin/zsh

set -u

#Usage: shell/read_piyo_kifs.sh
#1. SSAのディレクトリ中にあるpiyo_*.kifの名前を対局開始時間に基づいて変換し、kifディレクトリ以下に保存
#2. 対局情報をshogi_log.csvに追記
#3. cache/trash_[時刻]ディレクトリに、元のkifを保存

trash_dir=cache/trash$(date "+%y%m%d_%H%M")
mkdir -p $trash_dir

for f in piyo_*.kif; do
    shell/read_kif.sh $f

    #正しく読み込め棋譜のみ移動
    if [ $? -eq 0 ]; then
        mv $f $trash_dir
    fi
done | sort >> shogi_log.csv

