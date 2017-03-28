#!/bin/zsh

set -u

#得られるレートの期待値を計算する

if [ $# -ne 0 ]; then
    echo "Argument Error">&2
    exit 1
fi

cat - | tail -n +2 | awk '
{
  if ($2 == 0){
    #勝率100%の場合は悲観的に考えて、1回ぶん負けたものとして勝率を計算
    p = 1.0 * $1 / ($1 + $2 + 1)
  }
  else{
    p = 1.0 * $1 / ($1 + $2)
  }

  w  = $5
  r  = 800.0 * p - 400.0
  e  = r / 25.0
  wr = w * e
  print($0" "p" "w" "r" "e" "wr)
}'
