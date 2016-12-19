#!/bin/zsh

#レートカラムのダブルクォートを除く
cat shogi_log.csv | while read line; do
    nf=$(echo $line | awk -F, '{print NF}')
    if [[ $nf -eq 11 ]] && [[ $(echo $line | grep -c '^"1棋譜ファイル名"') -eq 0 ]]; then
        echo $line | cut -d ',' -f1-3 | tr -d '\n'; echo -n ","
        echo $line | cut -d ',' -f4,5 | tr -d '"' | tr -d '\n'; echo -n ","
        echo $line | cut -d ',' -f6-
    else
        echo $line
    fi
done
