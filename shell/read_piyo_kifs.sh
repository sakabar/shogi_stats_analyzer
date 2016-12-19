#!/bin/zsh

set -u

trash_dir=trash$(date "+%y%m%d_%H%M")
mkdir $trash_dir

for f in piyo_*.kif; do
    shell/read_kif.sh $f

    #正しく読み込めたら棋譜は削除
    if [ $? -eq 0 ]; then
        mv $f $trash_dir
    fi
done | sort >> shogi_log.csv

