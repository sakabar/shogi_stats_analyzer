#!/bin/zsh
set -u

#Aperyで解析するために、sjis化してApery用フォルダに保存

utf8_dir=kif_dir/raw/utf8

for kif_file in $utf8_dir/*.kif; do
    shell/cp_kif_for_apery.zsh $kif_file
done

exit 0
