#!/bin/zsh

set -u
set -e

if [ $# -ne 0 ]; then
    "$0 : Argument Error">&2
    exit 1
fi

#kifディレクトリとshogi_log.csvをバックアップする
backup_dir=backup/backup_$(date "+%Y%m%d_%H%M%S")
# mkdir -p $backup_dir

#以前まではシンボリックリンクの実体をわざわざ辿っていたが、
#tar -hオプションの存在を知って解決

#cp -a でファイルの情報を保って保存したかったが、それだとシンボリックリンクそのものが
#コピーされてしまうので断念。解凍時に工夫することにした

kif_dir=kif_dir
shogi_log_file=shogi_log.csv
# cp -a $kif_dir $log_file $backup_dir
tar zcfh ${backup_dir}.tar.gz $shogi_log_file $kif_dir

# rm -rf $backup_dir
