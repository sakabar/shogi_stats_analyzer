#!/bin/zsh

set -u
set -e

#バックアップファイルを復元する

if [ $# -ne 1 ]; then
    echo "$0 : Argument Error:<backup_tgz_file>">&2
    exit 1
fi

tgz_file=$1

[ ! -e $tgz_file ] && echo "${tgz_file} doesn't exitsts!">&2 && exit 1

#まずは、現状をバックアップ
shell/backup_files.zsh

kif_dir=kif_dir
log_file=shogi_log.csv
rm -rf $kif_dir $log_file
tar xf $tgz_file

backuped_dir=${tgz_file:t:r:r}
mv $backuped_dir/$kif_dir  .
mv $backuped_dir/$log_file .
rm -rf $backuped_dir
echo "backup of ${tgz_file} is restored."

exit 0
