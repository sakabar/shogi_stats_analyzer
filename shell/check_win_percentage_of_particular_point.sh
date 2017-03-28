#!/bin/zsh

set -u

#特定の時点(譜棋ID, 1-origin)での成績を出力
if [ $# -ne 1 ]; then
    echo "$0 : Argument Error:<kif_id>">&2
    exit 1
fi

kif_id=$1

readonly win_percentage_dir=result_dir/win_percentage_dir
mkdir -p result_dir/graph
mkdir -p $win_percentage_dir
mkdir -p result_dir/checkmate/discover
mkdir -p result_dir/checkmate/overlook
mkdir -p result_dir/checkmate/tsumero
mkdir -p result_dir/score_list

log_file=shogi_log.csv
csv_file_all=$win_percentage_dir/win_percentage_kifs_all.csv

cat $log_file | grep -v "^#" | gawk -F',' 'NF == 11 {print $0}' | gawk -F',' '$6 != "\"接続\"" {print}' | gawk -F',' '$2 != "\"ぴよ将棋\"" {print}' | grep -v "^\"1棋譜ファイル名" | gawk -F, '$7 == "\"勝\"" || $7 == "\"負\"" { print }' | gawk -F, '$9 != "\"\"" && $9 != "" && $10 != "\"\"" && $10 != "" { print }' | head -n $kif_id > $csv_file_all

log_size=$(cat $csv_file_all | wc -l)
readonly py_cmd=/Users/sak/local/src/anaconda3/envs/py35con/bin/python3.5 #何故かanacondaでactivateしたコマンドが実行されないので直接指定
# cat $csv_file_all | $py_cmd src/check_win_percentage.py $win_percentage_dir 25 5  | column -t > $win_percentage_dir/win_percentage_b025.txt &
cat $csv_file_all | $py_cmd src/check_win_percentage.py $win_percentage_dir 50 5  | column -t > $win_percentage_dir/win_percentage_b050.txt &
cat $csv_file_all | $py_cmd src/check_win_percentage.py $win_percentage_dir 100 5  | column -t > $win_percentage_dir/win_percentage_b100.txt &
# cat $csv_file_all | $py_cmd src/check_win_percentage.py $win_percentage_dir 200 5  | column -t > $win_percentage_dir/win_percentage_b200.txt &
cat $csv_file_all | $py_cmd src/check_win_percentage.py $win_percentage_dir $log_size 5  | column -t > $win_percentage_dir/win_percentage_all.txt &
wait

readonly win_percentage_dir_abs=$(cd $win_percentage_dir && pwd)
if [ ! -e $win_percentage_dir_abs/win_percentage.txt ]; then
    ln -s $win_percentage_dir_abs/win_percentage_b100.txt $win_percentage_dir_abs/win_percentage.txt
fi
