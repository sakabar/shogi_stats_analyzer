#!/bin/zsh

set -u

#特定の時点(譜棋ID, 1-origin)での成績を出力
if [ $# -ne 1 ]; then
    echo "$0 : Argument Error:<kif_id>">&2
    exit 1
fi

kif_id=$1

log_file=shogi_log.csv
csv_file_all=win_percentage_kifs_all.csv
cat $log_file | grep -v "^#" | gawk -F',' 'NF == 11 {print $0}' | gawk -F',' '$6 != "\"接続\"" {print}' | gawk -F',' '$2 != "\"ぴよ将棋\"" {print}' | grep -v "^\"1棋譜ファイル名" | gawk -F, '$7 == "\"勝\"" || $7 == "\"負\"" { print }' | gawk -F, '$9 != "\"\"" && $9 != "" && $10 != "\"\"" && $10 != "" { print }' | head -n $kif_id > $csv_file_all

log_size=$(cat $csv_file_all | wc -l)
readonly py_cmd=/Users/sak/local/src/anaconda3/envs/py35con/bin/python3.5 #何故かanacondaでactivateしたコマンドが実行されないので直接指定
cat $csv_file_all | $py_cmd src/check_win_percentage.py  50 5  | column -t > win_percentage_b050.txt &
cat $csv_file_all | $py_cmd src/check_win_percentage.py 100 5  | column -t > win_percentage_b100.txt &
cat $csv_file_all | $py_cmd src/check_win_percentage.py $log_size 5  | column -t > win_percentage_all.txt &
wait

#現在のkifディレクトリのバックアップ
shell/backup_files.zsh
