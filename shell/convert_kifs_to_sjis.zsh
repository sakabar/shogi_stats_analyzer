#!/bin/zsh

source_dir=kif
target_dir=kif_sjis

for kif_file in $source_dir/*.*; do
    if [ -e $target_dir/$kif_file:t ]; then
        if [ $target_dir/$kif_file:t -ot $source_dir/$kif_file:t ]; then
            cat $kif_file | nkf -s -Lm > $target_dir/$kif_file:t
        else
            :
        fi
    else
        cat $kif_file | nkf -s -Lm > $target_dir/$kif_file:t
    fi
done

exit 0
