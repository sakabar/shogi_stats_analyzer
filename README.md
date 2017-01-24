# Shogi Stats Analyzer (SSA)

## 機能
- 最新50・100局の対局情報から、戦型ごとの勝率を計算
- 重要度top5の戦型の勝率・重要度の推移をグラフで表示(50局・100局ごと)
- 総合勝率、先手勝率、後手勝率の推移をグラフで出力(50局・100局ごと)
- 各サイトの50局・100局ごとの平均レーティング推移をグラフで出力
- 即詰みを発見できた割合を計算

## 使い方
`shogi_log_sample.csv` : これを`shogi_log_sample.csv`にファイル名を変更してください。

このファイルが置いてあるディレクトリを便宜上`SSA_HOME`と表記します。(`shogi_stats_analyzer`のはず)

基本的にはぴよ将棋で出力したkifファイル(piyo_*.kif)を`SSA_HOME`に保存し、`shell/piyo_read_kif`を実行してkifディレクトリ以下に譜棋を移動し、`shogi_log.csv`の情報を編集してください。

`shell/check_win_percentage.sh`を実行すると、最新100局の対局情報を集計した戦型ごとの情報が`win_percentage.txt`に出力されると同時に、重要度top5の戦型の勝率・重要度の推移を`graph`ディレクトリ以下に出力します。また、先手・後手・総合の勝率推移のグラフも出力されます。


## 追加検討中機能
- 月別の対局情報から、戦型ごとの勝率を計算
- 成績が悪化/改善した要因を推定
 - アルゴリズムが思い付けば or 調べて見つかれば
- ある戦法の負け棋譜をクラスタリングして原因分析
 - クラスタリングするには自分のぶんだけでは棋譜数が足りない
 - 大まかに、序盤中盤終盤どこに原因があったかとか、相手の特定の動きに弱いとかが分かるだけでも充分?
- Apery等のソフトで解析した棋譜群を読み込んで分析
 - 一致率や平均低下評価値
- 相手の詰めろを見逃した割合をグラフ化 
- 棋譜ごとに、詰みを見逃した回数などを出力して後で確認できるようにする
 - 出力形式はどうするか

## 補足
### ウォーズのレートについて
csvファイルに将棋ウォーズでの棋力を記録する際、ELOレーティングではないが、便宜上以下のように記述する。

二段 500-599 [550]  
初段 400-499 [450]  
1級  300-399 [350]  
2級  200-299 [250]  
3級  100-199 [150]  
4級まで 0-99 [50]

対局相手のレートはその級段位の中心のレートとする。例えば、初段との対局ならばレート450として扱う。自分の棋力がもし3級達成率52.3%なら152.3。相手のレートは、相手の実際の達成率を記録しても構わないが、棋譜読み込み時には以下の基準で自動的にレートが記入されるので注意

## 設定等
最新n局ぶんのデータを利用 (デフォルト:100)  
重要度top nの戦型をグラフで出力 (デフォルト:5)

## 出力するデータとその意味
- `result_dir/win_percentage_dir/win_percentage_bXXX.txt`
 - 最近XXX局の、戦型ごとの勝率が記録されます
 - より上に記録されている戦型ほど、「その戦型でよく負けている(=重要度が高い)」戦型です。つまり、より上に記録されている戦法を強化すると効率が良いと考えられます
- `result_dir/win_percentage_dir/win_percentage_kifs_bXXX.csv`
 - 集計対象の、最近XXX局の対局情報です 
- `result_dir/graph/bXXX_avg_rating.png`
 - XXX局単位での平均レーティング推移を表します。これが高くなっていれば、棋力は向上していると言えるでしょう
- `result_dir/graph/bXXX_importance.png`
 -  最近XXX局で重要度トップnの戦型の、重要度の推移を表します。その戦型が最近急に重要度を増したのかどうかが判断できます
-	`result_dir/graph/bXXX_sengo_win_p.png`
 - XXX局単位での先手勝率や後手勝率を表します。また、先手になる割合と後手になる割合が1:1になるように補正した際の勝率を表します
- `result_dir/graph/bXXX_tactics_win_p.png` 
 - 最近XXX局で重要度トップnの戦型の、勝率の推移を表します。単に負けが多くて重要度が高くなっているのか、それとも勝率は高いがその戦型になる割合非常に多いのかが分かります
- `result_dir/graph/bXXX_mate.png`
 - XXX局単位での詰みの発見率を表します。これが高ければ、終盤力が強いと言えるでしょう
- `result_dir/graph/bXXX_tsumero.png`
 -  XXX局単位で相手の詰めろを見逃した数を表します。これが低いほど、頓死が死ないと言えるでしょう
- `result_dir/checkmate/discover/*.kif`
 - 対局ごとの発見した詰みの数を記録してあります
- `result_dir/checkmate/overlook/*.kif`
	- 対局ごとの見逃した詰み(勝てているはずだった)の数を記録してあります。
- `result_dir/checkmate/tsumero/*.kif`
 - 対局ごとの相手の詰めろを見逃した数を記録してあります。

## 詰みの発見・見逃しに関する仕様
- 王手の連続で相手を詰ませて勝利した場合、自分が王手をかけてから詰ませるまでにかかった手数のぶん、「詰み発見数」が加算されます。
 - 例えば、自分が王手をかけてから7手で相手を詰ませた場合、1手詰,3手詰,5手詰,7手詰の「詰み発見数」がそれぞれ1加算されます
 - 相手が最善手を指さずに早詰になった場合は、早詰の手数で計算されます
- n手の即詰みがある局面でその手順を選択しなかった場合、n手詰の「詰み見逃し数」が1加算されます。n手の即詰みがある局面で(n+2)手の即詰み手順に進んだ場合でも、n手詰の「詰み見逃し数」は1加算されます。
- **要確認事項**: Aperyで100万局面を読ませた結果を読み込んで利用しているが、100万局面の読みで13手,15手…の詰みを読みきることができているか?
 - 言い換えると、本当は即詰みの順が存在したのに、Aperyがそれを見逃しているということはあるか?