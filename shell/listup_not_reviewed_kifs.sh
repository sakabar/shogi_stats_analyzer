#!/bin/zsh

set -u

#戦型を記入していない棋譜やTODOと書かれた棋譜をリストアップする。

log_file=shogi_log.csv
output_file=not_reviewed_kifs.csv
utf8_kif_dir=kif_dir/raw/utf8

{
    cat $log_file | awk -F, 'NF == 11 { print }'| grep -v "ぴよ将棋" | gawk -F, '$9 == "" || $9 == "\"\"" { print }'
    cat $log_file | grep -i "TODO"
} | sort -k1,1 | uniq > $output_file

output_dir=~/Dropbox/shogi/ssa_share/todo_kifs
rm -rf $output_dir
mkdir -p $output_dir
cat $output_file | cut -d ',' -f1 | tr -d '"' | while read f; do
    cat $utf8_kif_dir/$f | nkf -Lm -s > $output_dir/$f:t
done

exit 0
