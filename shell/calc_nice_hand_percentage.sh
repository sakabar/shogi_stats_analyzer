#!/bin/zsh

set -u

#Aperyの出力した「一致率」を出力する。

analyzed_kif_dir=kif_dir/analyzed/shogiGUI/apery/utf8
log_file=shogi_log.csv

for f in $analyzed_kif_dir/*.kif; do
    tmp_var=$(cat $log_file | grep -m 1 -- $f:t | cut -d , -f8)

    if [[ $tmp_var = '"先手"' ]] || [[ $tmp_var = '"下手"' ]]; then
        nice_val=$(cat $f | grep '^*一致率' | gawk '{print $3}' | tr -d '%')
    elif [[ $tmp_var = '"後手"' ]] || [[ $tmp_var = '"上手"' ]]; then
        nice_val=$(cat $f | grep '^*一致率' | gawk '{print $7}' | tr -d '%')
    else
        echo "Error in ${f}: [${tmp_var}]">&2
        exit 1
    fi
    echo "${nice_val} ${f:t}"
done

