#!/bin/zsh

set -u
set -e

#初期化時に行う
#kif_dirの実体は別の場所に置いて、そこからシンボリックリンクを貼って運用しているため、
#.gitkeepで予めディレクトリをリポジトリに登録しておくと、それが削除された扱い(changes to be commit)になって困る
#そこで、必要なディレクトリはこのリポジトリのインストール後に作成してもらうことにする

utf8_kif_dir=kif_dir/raw/utf8
sjis_kif_dir=kif_dir/raw/sjis
apery_utf8_kif_dir=kif_dir/analyzed/shogiGUI/apery/utf8
apery_sjis_kif_dir=kif_dir/analyzed/shogiGUI/apery/sjis

mkdir -p $utf8_kif_dir
mkdir -p $sjis_kif_dir
mkdir -p $apery_utf8_kif_dir
mkdir -p $apery_sjis_kif_dir
mkdir -p result_dir

config_file=config/player_name.txt
if [ ! -e $config_file ]; then
    echo "あなた\nプレイヤー" > $config_file
fi
echo "config/player_name.txt には、棋譜内で解析対象にしたい人のアカウント名などを記入します。"
echo "現在、登録されている名前は、"
echo ""
cat config/player_name.txt
echo ""
echo "です。"
