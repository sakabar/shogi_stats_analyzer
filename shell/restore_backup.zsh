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

#復元
#shogi_log.csvやkif_dirがシンボリックリンクだった場合でも、
#その場所に実体が復元されてしまうという問題がある。
#復元できたあとにアレコレするのは、複元がそもそもできないよりはマシか。

kif_dir=kif_dir
log_file=shogi_log.csv
rm -rf $kif_dir $log_file
tar xf $tgz_file

echo "backup of ${tgz_file} is restored."

exit 0
