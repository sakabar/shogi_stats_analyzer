#!/bin/zsh

set -u

if [ $# -ne 0 ]; then
    "$0 : Argument Error">&2
    exit 1
fi

#kifディレクトリとshogi_log.csvをバックアップする
backup_dir=backup/backup_$(date "+%Y%m%d_%H%M%S")
mkdir -p $backup_dir

#Dropboxに実体を置き、リポジトリにはシンボリックリンクを置いておく
#バックアップ時にはreadlinkで実体を参照して保存する
readlink kif >/dev/null 2>&1
if [ $? -eq 0 ]; then
    kif_dir=$(readlink kif)
else
    kif_dir=kif
fi

readlink shogi_log.csv >/dev/null 2>&1
if [ $? -eq 0 ]; then
    log_file=$(readlink shogi_log.csv)
else
    log_file=shogi_log.csv
fi

cp -a $kif_dir $log_file $backup_dir
tar zcf ${backup_dir}.tar.gz -C $backup_dir:h $backup_dir:t

rm -rf $backup_dir
