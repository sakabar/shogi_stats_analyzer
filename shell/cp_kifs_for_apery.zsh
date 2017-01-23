#!/bin/zsh
set -u

#Aperyで解析するために、sjis化してApery用フォルダに保存

utf8_dir=kif_dir/raw/utf8
analyzed_dir=kif_dir/analyzed/shogiGUI/apery/utf8
to_analyze_dir=kif_dir/to_analyze
mkdir -p $analyzed_dir
mkdir -p $to_analyze_dir

for kif_file in $utf8_dir/*.kif; do
    if [ -e $analyzed_dir/$kif_file:t ]; then
        if [ $utf8_dir/$kif_file:t -nt $analyzed_dir/$kif_file:t ]; then
            echo "converted ${kif_file} to ${to_analyze_dir}"
            #ぴよ将棋などの解析によって付与された棋譜コメントは削除
            cat $kif_file | grep -v '^*' | nkf -s -Lm > $to_analyze_dir/$kif_file:t
        else
            :
        fi
    else
        echo "converted ${kif_file} to ${to_analyze_dir}"
        cat $kif_file | grep -v '^*' | nkf -s -Lm > $to_analyze_dir/$kif_file:t
    fi
done

exit 0
