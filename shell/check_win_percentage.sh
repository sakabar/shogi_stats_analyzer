#!/bin/zsh

set -u

if [ $# -ne 0 ]; then
    echo "$0 : Argument Error">&2
    exit 1
fi

tmp_csv_file=`mktemp -t tmp_csv_file`
cat shogi_log.csv | grep -v "^#" | gawk -F',' 'NF == 11 {print $0}' | gawk -F',' '$6 != "\"接続\"" {print}' | gawk -F',' '$2 != "\"ぴよ将棋\"" {print}' | grep -v "^\"1棋譜ファイル名" | gawk -F, '$7 == "\"勝\"" || $7 == "\"負\"" { print }' | gawk -F, '$9 != "\"\"" && $9 != "" && $10 != "\"\"" && $10 != "" { print }' > $tmp_csv_file

log_size=$(cat $tmp_csv_file | wc -l)
readonly py_cmd=/Users/sak/local/src/anaconda3/envs/py35con/bin/python3.5 #何故かanacondaでactivateしたコマンドが実行されないので直接指定
cat $tmp_csv_file | $py_cmd src/check_win_percentage.py  50 5  | column -t > win_percentage_b050.txt &
cat $tmp_csv_file | $py_cmd src/check_win_percentage.py 100 5  | column -t > win_percentage_b100.txt &
cat $tmp_csv_file | $py_cmd src/check_win_percentage.py $log_size 5  | column -t > win_percentage_all.txt &
wait

#まだ反省していない棋譜をリストアップ
shell/listup_not_reviewed_kifs.sh

#現在のkifディレクトリのバックアップ
shell/backup_files.zsh

rm -rf $tmp_csv_file
