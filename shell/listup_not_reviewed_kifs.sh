#!/bin/zsh

#戦型を記入していない棋譜やTODOと書かれた棋譜をリストアップする。

{
    cat shogi_log.csv | awk -F, 'NF == 11 { print }'| grep -v "ぴよ将棋" | gawk -F, '$9 == "" || $9 == "\"\"" { print }'
    cat shogi_log.csv | grep "TODO"
} | sort -k1,1 | uniq

exit 0
