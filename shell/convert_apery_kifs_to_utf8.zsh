#!/bin/zsh
set -u

#Aperyで解析した棋譜を、文字コードを変えて移動

source_dir=kif_dir/to_analyze
sjis_dir=kif_dir/analyzed/shogiGUI/apery/sjis
utf8_dir=kif_dir/analyzed/shogiGUI/apery/utf8


[ ! -e $sjis_dir ] && mkdir -p $sjis_dir
[ ! -e $utf8_dir ] && mkdir -p $utf8_dir

for kif_file in $source_dir/*.kif; do
    cnt=$(cat $kif_file | nkf -w -Lu | grep -c '^**解析')
    if [ $cnt -eq 0 ]; then
        echo "${kif_file} is not analyzed!">&2
        continue
    fi

    if [ -e $utf8_dir/$kif_file:t ]; then
        if [ $kif_file -nt $utf8_dir/$kif_file:t ];then
            cat $kif_file | nkf -w -Lu > $utf8_dir/$kif_file:t
            mv -f $kif_file $sjis_dir/$kif_file:t
        fi
    else
        cat $kif_file | nkf -w -Lu > $utf8_dir/$kif_file:t
        mv -f $kif_file $sjis_dir/$kif_file:t
    fi
done

exit 0
