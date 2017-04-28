#!/bin/zsh

set -u

#戦型を記入していない棋譜やTODOと書かれた棋譜をリストアップする。

log_file=shogi_log.csv
output_file=not_reviewed_kifs.csv
utf8_kif_dir=kif_dir/raw/utf8
analyzed_kif_dir=kif_dir/analyzed/shogiGUI/apery/utf8


{
    cat $log_file | grep -v '^#' | awk -F, 'NF == 11 { print }'| grep -v "ぴよ将棋" | gawk -F, '$9 == "" || $9 == "\"\"" { print }'
    cat $log_file | grep -v '^#' | grep -i "TODO"
} | sort -k1,1 | uniq > $output_file

output_dir=~/Dropbox/shogi/ssa_share/todo_kifs
rm -rf $output_dir
mkdir -p $output_dir
cat $output_file | cut -d ',' -f1 | tr -d '"' | while read f; do
    if [[ -e $analyzed_kif_dir/$f ]]; then
        cat $analyzed_kif_dir/$f | nkf -Lm -s > $output_dir/$f:t
    else
        cat $utf8_kif_dir/$f | nkf -Lm -s > $output_dir/$f:t
    fi
done

exit 0
