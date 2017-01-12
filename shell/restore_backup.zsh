#!/bin/zsh

set -u

#バックアップファイルを復元する

if [ $# -ne 1 ]; then
    echo "$0 : Argument Error:<backup_tgz_file>">&2
    exit 1
fi

tgz_file=$1

[ ! -e $tgz_file ] && echo "${tgz_file} doesn't exitsts!">&2 && exit 1

#まずは、現状をバックアップ
shell/backup_files.zsh

rm -rf kif shogi_log.csv
tar xf $tgz_file
mv ${tgz_file:t:r:r}/kif .
mv ${tgz_file:t:r:r}/shogi_log.csv .
rm -rf ${tgz_file:t:r:r}
echo "backup of ${tgz_file} is restored."

exit 0
