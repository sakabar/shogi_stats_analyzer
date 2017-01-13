#!/bin/zsh

set -u

#戦型を記入していない棋譜やTODOと書かれた棋譜をリストアップする。

{
    cat shogi_log.csv | awk -F, 'NF == 11 { print }'| grep -v "ぴよ将棋" | gawk -F, '$9 == "" || $9 == "\"\"" { print }'
    cat shogi_log.csv | grep -i "TODO"
} | sort -k1,1 | uniq > not_reviewed_kifs.csv

output_dir=~/Dropbox/shogi/ssa_share/todo_kifs
rm -rf $output_dir
mkdir -p $output_dir
cat not_reviewed_kifs.csv | cut -d ',' -f1 | tr -d '"' | while read f; do
    cat kif/$f | nkf -Lm -s > $output_dir/$f:t
done

exit 0
