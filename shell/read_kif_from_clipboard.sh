#!/bin/zsh

set -u

#クリップボードに保存された文字列の中から棋譜ファイル名と思われる部分を抜き出して読み込み、
#棋譜の中身をクリップボードに読み込む
which "pbcopy" > /dev/null
isMac=$?

if [ $isMac -eq 0 ];then
    :
else
    echo "$0 : use this command in Mac">&2
    exit 1
fi

clipboard_text=$(mktemp -t tmp_file)
echo -n "clipboard:[">&2
pbpaste | tee $clipboard_text >&2
echo "]">&2

kif_dir=kif_dir/raw/utf8

kif_file=$(cat $clipboard_text | grep -o -m 1 "[0-9]\{8\}_[0-9]\{4\}")".kif"

if [[ $kif_file = ".kif" ]]; then
    echo "Can't read kif_file name from:"$clipboard_text
else
    echo $kif_file >&2
    cat $kif_dir/$kif_file | pbcopy
fi

rm -rf $clipboard_text
