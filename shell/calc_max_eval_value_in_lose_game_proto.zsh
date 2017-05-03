#!/bin/zsh

set -u

kif_list=kif_list.txt
log_file=shogi_log.csv
score_list_dir=result_dir/score_list

cat $kif_list | while read line; do
    kif_name=$(echo $line | awk -F, '{print $1}')
    log_line=$(cat $log_file | awk -F, -v kif_name=\"$kif_name\" '$1 == kif_name {print $0}' | head -n1)
    touryo=$(echo $log_line | awk -F, '{print $6}' | tr -d '"')
    win_lose=$(echo $log_line | awk -F, '{print $7}' | tr -d '"')
    sengo=$(echo $log_line | awk -F, '{print $8}' | tr -d '"')


    [[ $win_lose != "負" ]] && continue

    if [[ $sengo = "先手" ]]; then
        sengo_sym="+"
    else
        sengo_sym="-"
    fi

    if [[ -e $score_list_dir/$kif_name ]]; then
        echo -n "${kif_name} ${touryo} ${win_lose} ${sengo}"
        echo -n " "
        cat $score_list_dir/$kif_name | grep "^${sengo_sym}" | awk '$1 == "+" {printf("%s %d %d %d\n", $1, $2, $3, $4)}; $1 == "-" {printf("%s %d %d %d\n", $1, $2, -$3, -$4)}' | sort -k3,3nr | head -n1
    fi
done | sort -k7,7nr | cat -n
