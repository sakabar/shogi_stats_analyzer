#!/bin/zsh

set -u

#戦型ことの勝率を計算する
result_dir=win_percentage_dir_$(date "+%y%m%d_%H%M")
mkdir $result_dir
rm -rf win_percentage_dir_latest
ln -s $result_dir win_percentage_dir_latest

#"7勝敗","8手番","9戦型"
# cat shogi_log.csv | grep -v "^\"1棋譜ファイル名" | cut -d ',' -f7,8,9 | gawk -F, '$1 != "" && $2 != "" && $3 != "" { print }' | tr -d '"' | awk -F',' '
cat shogi_log.csv | gawk -F',' 'NF == 11 {print $0}' | gawk -F',' '$6 != "\"接続\"" {print}' | gawk -F',' '$2 != "\"ぴよ将棋\"" {print}' | grep -v "^\"1棋譜ファイル名" | gawk -F, '$7 == "\"勝\"" || $7 == "\"負\"" { print }' | gawk -F, '$9 != "\"\"" && $9 != "" && $10 != "\"\"" && $10 != "" { print }' | tail -n 100 | tee $result_dir/win_percentage_kifs.csv | cut -d ',' -f7,8,9,10 | tr -d '"' | gawk -F',' '
{
  k = $2","$3
  if (k in k_arr){
      k_arr[k] += 1
    }
    else{
      k_arr[k] = 1
    }

  if ($1 == "勝"){
    if (k in win_arr){
      win_arr[k] += 1
    }
    else{
      win_arr[k] = 1
    }
  }
  else if ($1 == "負"){
    if (k in lose_arr){
      lose_arr[k] += 1
    }
    else{
      lose_arr[k] = 1
    }
  }
}

END{
  sum = 0
  win_sum = 0
  for(k in k_arr){
    if (! (k in win_arr)){
        win_arr[k] = 0
    }
    if (! (k in lose_arr)){
        lose_arr[k] = 0
    }

    sum += win_arr[k] + lose_arr[k]
    win_sum += win_arr[k]
  }

  sente_sum = 0
  gote_sum = 0
  for(k in k_arr){
    if (k ~ /先手/){
      sente_sum += win_arr[k] + lose_arr[k]
    }
    else if(k ~ /後手/){
      gote_sum += win_arr[k] + lose_arr[k]
    }
  }

  for(k in k_arr){
    p1 = 1.0 * win_arr[k] / (win_arr[k] + lose_arr[k])
    s = win_arr[k] + lose_arr[k]
    if(k ~ /先手/){
      p2 = 0.5 * s / sente_sum
    }
    else if(k ~ /後手/){
      p2 = 0.5 * s / gote_sum
    }
    p3 = p1 * p2
    p4 = (1.0 - p1) * p2
    print p1","win_arr[k]","lose_arr[k]","s,","p2","p3","k","p4
  }
}' | sort -t ',' -k9,9nr | awk -F',' 'BEGIN{print "勝率,勝,負,合計,遭遇率,勝率への寄与,手番,戦型,重要度"}; {printf("%.3f,%d,%d,%d,%.3f,%.3f,%s,%s,%.3f\n", $1, $2, $3, $4, $5, $6, $7, $8, $9)}' | tee $result_dir/win_percentage.csv | tail -n+2 | tr ',' '\t'  | column -t > $result_dir/win_percentage.txt

{
cat $result_dir/win_percentage.txt | awk 'BEGIN{win_sum = 0; lose_sum = 0; win_p = 0}; $7 == "先手" { win_sum += $2; lose_sum += $3; win_p += $6; print $0}; END{printf("%.3f %d %d %d 0.500 %.3f 先手\n", 1.0 * win_sum / (win_sum + lose_sum), win_sum, lose_sum, win_sum + lose_sum, win_p)}' | column -t | tee $result_dir/win_percentage_sente.txt | tail -n 1
cat $result_dir/win_percentage.txt | awk 'BEGIN{win_sum = 0; lose_sum = 0; win_p = 0}; $7 == "後手" { win_sum += $2; lose_sum += $3; win_p += $6; print $0}; END{printf("%.3f %d %d %d 0.500 %.3f 後手\n", 1.0 * win_sum / (win_sum + lose_sum), win_sum, lose_sum, win_sum + lose_sum, win_p)}' | column -t | tee $result_dir/win_percentage_gote.txt | tail -n 1
cat $result_dir/win_percentage.txt | awk 'BEGIN{win_sum = 0; lose_sum = 0; win_p = 0}; { win_sum += $2; lose_sum += $3; win_p += $6; print $0}; END{printf("%.3f %d %d %d 1.000 %.3f 全て\n", 1.0 * win_sum / (win_sum + lose_sum), win_sum, lose_sum, win_sum + lose_sum, win_p)}' | tail -n 1
} | column -t > $result_dir/win_percentage_sengo.txt

