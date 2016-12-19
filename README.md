# Shogi Stats Analyzer (SSA)

## 機能
- 最新100局の対局情報から、戦型ごとの勝率を計算
- 重要度top5の戦型の勝率・重要度の推移をグラフで表示

## 使い方
`shogi_log_sample.csv` : これを`shogi_log_sample.csv`にファイル名を変更してください。

このファイルが置いてあるディレクトリを便宜上`SSA_HOME`と表記します。(`shogi_stat_analyzer`のはず)

基本的にはぴよ将棋で出力したkifファイル(piyo_*.kif)を`SSA_HOME`に保存し、`shell/piyo_read_kif`を実行してkifディレクトリ以下に譜棋を移動し、`shogi_log.csv`の情報を編集してください。

`shell/check_win_percentage.sh`を実行すると、最新100局の対局情報を集計した戦型ごとの情報が`win_percentage.txt`に出力されると同時に、重要度top5の戦型の勝率・重要度の推移を`graph`ディレクトリ以下に出力します。


## 追加予定
- 月別の対局情報から、戦型ごとの勝率を計算

## 補足
### ウォーズのレートについて
csvファイルに将棋ウォーズでの棋力を記録する際、ELOレーティングではないが、便宜上以下のように記述する。

二段 500-599 [550]  
初段 400-499 [450]  
1級  300-399 [350]  
2級  200-299 [250]  
3級  100-199 [150]  
4級まで 0-99 [50]

対局相手のレートはその級段位の中心のレートとする。例えば、初段との対局ならばレート450として扱う。自分の棋力がもし3級達成率52.3%なら152.3。

## 設定等
最新n局ぶんのデータを利用 (デフォルト:100)
重要度top nの戦型をグラフで出力 (デフォルト:5)