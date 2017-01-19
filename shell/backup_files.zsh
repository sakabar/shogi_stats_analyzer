#!/bin/zsh

set -u

if [ $# -ne 0 ]; then
    "$0 : Argument Error">&2
    exit 1
fi

#kifディレクトリとshogi_log.csvをバックアップする
backup_dir=backup/backup_$(date "+%Y%m%d_%H%M%S")
mkdir -p $backup_dir

sym_kif_dir=kif_dir #シンボリックリンクかもしれない棋譜ディレクトリ
#Dropboxに実体を置き、リポジトリにはシンボリックリンクを置いておく
#バックアップ時にはreadlinkで実体を参照して保存する
readlink $sym_kif_dir >/dev/null 2>&1
if [ $? -eq 0 ]; then
    kif_dir=$(readlink kif)
else
    kif_dir=$sym_kif_dir
fi

sym_shogi_log_file=shogi_log.csv
readlink $sym_shogi_log_file >/dev/null 2>&1
if [ $? -eq 0 ]; then
    log_file=$(readlink $sym_shogi_log_file)
else
    log_file=$sym_shogi_log_file
fi

set -e

cp -a $kif_dir $log_file $backup_dir
tar zcf ${backup_dir}.tar.gz -C $backup_dir:h $backup_dir:t

rm -rf $backup_dir
