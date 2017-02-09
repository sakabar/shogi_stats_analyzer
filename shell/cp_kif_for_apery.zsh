#!/bin/zsh
set -u

#Aperyで解析するために、sjis化してApery用フォルダに保存

if [ $# -ne 1 ]; then
    echo "Argument Error:<kif_file>">&2
    exit 1
fi

kif_file=$1

utf8_dir=kif_dir/raw/utf8
analyzed_dir=kif_dir/analyzed/shogiGUI/apery/utf8
to_analyze_dir=kif_dir/to_analyze
mkdir -p $analyzed_dir
mkdir -p $to_analyze_dir

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

exit 0
