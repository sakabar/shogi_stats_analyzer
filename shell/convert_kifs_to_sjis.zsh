#!/bin/zsh

source_dir=kif
target_dir=kif_sjis
[ ! -e kif_sjis ] && mkdir -p $target_dir

for kif_file in $source_dir/*.*; do
    if [ -e $target_dir/$kif_file:t ]; then
        if [ $target_dir/$kif_file:t -ot $source_dir/$kif_file:t ]; then
            echo "converted ${kif_file}"
            cat $kif_file | nkf -s -Lm > $target_dir/$kif_file:t
        else
            :
        fi
    else
        echo "converted ${kif_file}"
        cat $kif_file | nkf -s -Lm > $target_dir/$kif_file:t
    fi
done

exit 0
