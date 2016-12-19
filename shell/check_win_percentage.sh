#!/bin/zsh

set -u

if [ $# -ne 2 ]; then
    echo "$0 : Argument Error:<batch> <topn>">&2
    exit 1
fi


readonly batch=$1 #50
readonly topn=$2

cat shogi_log.csv | gawk -F',' 'NF == 11 {print $0}' | gawk -F',' '$6 != "\"接続\"" {print}' | gawk -F',' '$2 != "\"ぴよ将棋\"" {print}' | grep -v "^\"1棋譜ファイル名" | gawk -F, '$7 == "\"勝\"" || $7 == "\"負\"" { print }' | gawk -F, '$9 != "\"\"" && $9 != "" && $10 != "\"\"" && $10 != "" { print }' | /Users/sak/local/src/anaconda3/envs/py35con/bin/python3.5 src/check_win_percentage.py $batch $topn | column -t > win_percentage.txt
