#!/bin/zsh

set -u

if [ $# -ne 0 ]; then
    "$0 : Argument Error">&2
    exit 1
fi

#kifディレクトリとshogi_log.csvをバックアップする
backup_dir=backup/backup_$(date "+%Y%m%d_%H%M%S")
mkdir -p $backup_dir
cp -a kif shogi_log.csv $backup_dir
tar zcf ${backup_dir}.tar.gz -C $backup_dir:h $backup_dir:t

rm -rf $backup_dir
