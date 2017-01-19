#!/bin/zsh

set -u

if [ $# -ne 0 ]; then
    echo "$0 : Argument Error">&2
    exit 1
fi

readonly win_percentage_dir=win_percentage_dir
mkdir -p $win_percentage_dir
csv_file_all=$win_percentage_dir/win_percentage_kifs_all.csv
cat shogi_log.csv | grep -v "^#" | gawk -F',' 'NF == 11 {print $0}' | gawk -F',' '$6 != "\"接続\"" {print}' | gawk -F',' '$2 != "\"ぴよ将棋\"" {print}' | grep -v "^\"1棋譜ファイル名" | gawk -F, '$7 == "\"勝\"" || $7 == "\"負\"" { print }' | gawk -F, '$9 != "\"\"" && $9 != "" && $10 != "\"\"" && $10 != "" { print }' > $csv_file_all

log_size=$(cat $csv_file_all | wc -l)
readonly py_cmd=/Users/sak/local/src/anaconda3/envs/py35con/bin/python3.5 #何故かanacondaでactivateしたコマンドが実行されないので直接指定
cat $csv_file_all | $py_cmd src/check_win_percentage.py $win_percentage_dir 50 5  | column -t > $win_percentage_dir/win_percentage_b050.txt &
cat $csv_file_all | $py_cmd src/check_win_percentage.py $win_percentage_dir 100 5  | column -t > $win_percentage_dir/win_percentage_b100.txt &
cat $csv_file_all | $py_cmd src/check_win_percentage.py $win_percentage_dir $log_size 5  | column -t > $win_percentage_dir/win_percentage_all.txt &
wait

readonly win_percentage_dir_abs=$(cd $win_percentage_dir && pwd)
if [ ! -e $win_percentage_dir_abs/win_percentage.txt ]; then
    ln -s $win_percentage_dir_abs/win_percentage_b100.txt $win_percentage_dir_abs/win_percentage.txt
fi

#まだ反省していない棋譜をリストアップ
shell/listup_not_reviewed_kifs.sh

#現在のkifディレクトリのバックアップ
shell/backup_files.zsh
