#!/bin/zsh

set -u

cat - | tr '△' '∀' | tr '▲' '△' | tr '∀' '▲'

