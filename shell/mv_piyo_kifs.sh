#!/bin/zsh

set -u

for f in ~/Dropbox/shogi/ssa_share/piyo*.kif; do
    echo $f:t >&2
    mv -i $f .
done
