#!/bin/zsh
cat shogi_log.csv | awk -F, 'NF == 11 { print }'| grep -v "ぴよ将棋" | gawk -F, '$9 == "" || $9 == "\"\"" { print }'
cat shogi_log.csv | grep "TODO"
exit 0
