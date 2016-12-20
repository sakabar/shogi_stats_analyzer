#!/bin/zsh

set -u

if [ $# -ne 0 ]; then
    echo "$0 : Argument Error">&2
    exit 1
fi

# if [ $# -ne 2 ]; then
#     echo "$0 : Argument Error:<batch> <topn>">&2
#     exit 1
# fi

# readonly batch=$1 #50
# readonly topn=$2

tmp_file=`mktemp -t tmp_file`
cat shogi_log.csv | gawk -F',' 'NF == 11 {print $0}' | gawk -F',' '$6 != "\"接続\"" {print}' | gawk -F',' '$2 != "\"ぴよ将棋\"" {print}' | grep -v "^\"1棋譜ファイル名" | gawk -F, '$7 == "\"勝\"" || $7 == "\"負\"" { print }' | gawk -F, '$9 != "\"\"" && $9 != "" && $10 != "\"\"" && $10 != "" { print }' > $tmp_file

log_size=$(cat $tmp_file | wc -l)
readonly py_cmd=/Users/sak/local/src/anaconda3/envs/py35con/bin/python3.5 #何故かanacondaでactivateしたコマンドが実行されないので直接指定
cat $tmp_file | $py_cmd src/check_win_percentage.py  50 5  | column -t > win_percentage_b050.txt &
cat $tmp_file | $py_cmd src/check_win_percentage.py 100 5  | column -t > win_percentage_b100.txt &
cat $tmp_file | $py_cmd src/check_win_percentage.py $log_size 5  | column -t > win_percentage_all.txt &
wait

rm -rf $tmp_file
