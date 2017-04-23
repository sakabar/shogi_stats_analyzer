"""Check Win Percentage

Usage: check_win_percentage.py <win_percentage_dir> <batch> <topn>
       check_win_percentage.py -h | --help

Options:
    -h, --help  show this help message and exit
"""

from collections import defaultdict
import count_mate
from docopt import docopt
import matplotlib.pyplot as plt
import math
import re
import sys
import os.path #あまり使いたくない

def read_batch_csv(batch_csv):
    win_num_dic  = {} #戦型 -> 勝数の辞書
    lose_num_dic = {} #戦型 -> 敗数の辞書

    for log_tpl in batch_csv:
        win_lose = log_tpl[6]
        turn = log_tpl[7]
        tactics = log_tpl[8]

        key = (turn, tactics)
        #win_num_dicのキーとlose_num_dicのキーが同じになるようにする
        #(例えば、ある戦型Aが0勝4敗の時にもwin_num_dicはAのキーを持つようにする)
        if win_lose == "勝":
            if key in win_num_dic:
                win_num_dic[key] += 1
            else:
                win_num_dic[key]  = 1
                lose_num_dic[key] = 0
        elif win_lose == "負":
            if key in win_num_dic:
                lose_num_dic[key] += 1
            else:
                win_num_dic[key]  = 0
                lose_num_dic[key] = 1
        else:
            raise Exception("Unexpected turn")

    return (win_num_dic, lose_num_dic)

def output_win_lose_num_dic(batch, win_num_dic, lose_num_dic):
    wfi_dic = get_win_p_freq_importance_dic(batch, win_num_dic, lose_num_dic)

    unsorted_lst = []
    for key in wfi_dic:
        turn = key[0]
        tac = key[1]
        win_num = win_num_dic[key]
        lose_num = lose_num_dic[key]
        sum_num = win_num + lose_num

        win_p = wfi_dic[key][0]
        tac_freq = wfi_dic[key][1]
        importance = wfi_dic[key][2]

        tpl = (turn, tac, win_num, lose_num, sum_num, win_p, tac_freq, importance)
        unsorted_lst.append(tpl)

    output_arr = ["勝 負 計 勝率 遭遇率 重要度 手番 戦型"]
    sorted_lst = sorted(unsorted_lst, key=lambda x:(x[7], 1.0 - x[5], (turn, tac)), reverse=True)
    output_arr.extend(["{2:d} {3:d} {4:d} {5:.3f} {6:.2f} {7:.3f} {0} {1}".format(*tpl) for tpl in sorted_lst])

    print("\n".join(output_arr))
    return

#(手番, 戦型)をキーとして(勝率, 遭遇率, 重要度)を値とする辞書を返す
def get_win_p_freq_importance_dic(batch, win_num_dic, lose_num_dic):
    ans_dic = {}

    for key in win_num_dic:
        turn = key[0]
        tac = key[1]
        win_num = win_num_dic[key]
        lose_num = lose_num_dic[key]
        sum_num = win_num + lose_num
        win_p = 1.0 * win_num / sum_num
        tac_freq = 1.0 * sum_num / batch
        importance = 1.0 * lose_num / batch #重要度(= ある戦型になる確認 * その戦型で負ける確率) #(1.0 - win_p) * tac_freq

        tpl = (win_p, tac_freq, importance)
        ans_dic[key] = tpl

    return ans_dic

def draw_importrance(batch, transition_dic, transition_size, input_keys):
    plt.clf()
    for key in input_keys:
        x = list(range(batch, batch + len(transition_dic[key])))
        y_importance = [tpl[2] for tpl in transition_dic[key]]
        plt.plot(x, y_importance, label=key)

    plt.title("重要度推移 (直近{0:d}局ごと)".format(batch))
    plt.ylabel("重要度")
    plt.xlabel("対局ID")

    #X,Y軸の範囲
    plt.xlim(batch, batch + transition_size - 1)
    step = batch
    # plt.xticks(list(range(batch, batch + transition_size, step)) + [batch + transition_size - 1])
    #400局前、300局前、200局前、100局前、今
    plt.xticks(list(range(batch + transition_size - 1, batch + transition_size - 1 - step * 4 - 1, -step)))

    #loc='lower right'で、右下に凡例を表示
    plt.legend(prop={'size' : 10}, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)

    # 右側の余白を調整
    plt.subplots_adjust(right=0.5, top=0.5)
    plt.savefig("result_dir/graph/b{0:03d}_importance.png".format(batch))
    plt.clf()

    return


def draw_tactics_win_p(batch, transition_dic, transition_size, input_keys):
    plt.clf()
    for key in input_keys:
        x = list(range(batch, batch + len(transition_dic[key])))
        y_win_p = [tpl[0] for tpl in transition_dic[key]]
        plt.plot(x, y_win_p, label=key)

    plt.title("勝率推移 (直近{0:d}局ごと)".format(batch))
    plt.ylabel("勝率")
    plt.xlabel("対局ID")

    #X,Y軸の範囲
    plt.xlim(batch, batch + transition_size - 1)
    step = batch
    plt.xticks(list(range(batch + transition_size - 1, batch + transition_size - 1 - step * 4 - 1, -step)))
    # plt.xticks(list(range(batch, batch + transition_size, 20)) + [batch + transition_size - 1])

    #loc='lower right'で、右下に凡例を表示
    plt.legend(prop={'size' : 10}, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)

    # 右側の余白を調整
    plt.subplots_adjust(right=0.5, top=0.5)
    plt.savefig("result_dir/graph/b{0:03d}_tactics_win_p.png".format(batch))
    plt.clf()

    return

def draw_sengo_win_p(batch, transition_size, all_win_p_transition_list, sente_win_p_transition_list, gote_win_p_transition_list, sente_ratio_transition_list):

    #先手後手の対局数が同じ場合の全体勝率
    weighed_all_win_p_transition_list = [0.5 * tpl[0] + 0.5 * tpl[1] for tpl in zip(sente_win_p_transition_list, gote_win_p_transition_list)]

    plt.clf()

    x = list(range(batch, batch + transition_size))

    # 全体勝率は表示しないことにした
    # plt.plot(x, all_win_p_transition_list, label="all")

    #重み付き全体勝率
    plt.plot(x, weighed_all_win_p_transition_list, label="weighed_all")

    #先手勝率
    plt.plot(x, sente_win_p_transition_list, label="先手")

    #後手勝率
    plt.plot(x, gote_win_p_transition_list, label="後手")

    #先手の割合
    plt.plot(x, sente_ratio_transition_list, label="先手割合")

    plt.title("勝率推移 (直近{0:d}局ごと)".format(batch))
    plt.ylabel("勝率")
    plt.xlabel("対局ID")

    #点線の補助線を描画
    for i in range(30, 70+1, 5):
        p = i / 100.0
        plt.plot([batch, batch+transition_size-1], [p, p], ':')


    #X,Y軸の範囲
    plt.xlim(batch, batch + transition_size - 1)
    step = batch
    plt.xticks(list(range(batch + transition_size - 1, batch + transition_size - 1 - step * 4 - 1, -step)))
    # plt.xticks(list(range(batch, batch + transition_size, 20)) + [batch + transition_size - 1])
    # plt.ylim(0.3, 0.6)
    plt.ylim(0.2, 1.0)
    plt.yticks([ y / 100.0 for y in range(20, 100, 5)])


    #loc='lower right'で、右下に凡例を表示
    plt.legend()

    # 右側の余白を調整
    # plt.subplots_adjust(right=0.5, top=0.5)

    plt.savefig("result_dir/graph/b{0:03d}_sengo_win_p.png".format(batch))
    plt.clf()

    return

#レーティング推移をグラフ化し、保存
def draw_avg_rating_transition(batch, transition_size, app_set, avg_rating_transition_list, opponent_avg_rating_transition_list, ignore_app_list=[]):
    plt.clf()
    x = list(range(batch, batch + transition_size))

    for app in app_set:
        if app in ignore_app_list:
            continue
        #複数のサイトでのレーティングをおよそ0-999の範囲に入るようにスライドする
        y = [avg_dic[app] for avg_dic in avg_rating_transition_list]
        y_small = [(rating - 1000.0) if rating >= 1000 else rating for rating in y]
        plt.plot(x, y_small, label=app)

        y = [avg_dic[app] for avg_dic in opponent_avg_rating_transition_list]
        y_small = [(rating - 1000.0) if rating >= 1000 else rating for rating in y]
        #グラフが見にくくなるので、対局相手の平均レートは表示しない。必要なときだけアンコメント
        # plt.plot(x, y_small, label=("%s_rival" % app))


    plt.title("平均レーティング推移 (直近{0:d}局ごと)".format(batch))
    plt.ylabel("レーティング")
    plt.xlabel("対局ID")

    #点線の補助線を描画
    for i in range(0, 400+1, 50):
        plt.plot([batch, batch+transition_size-1], [i, i], ':')


    #X,Y軸の範囲
    plt.xlim(batch, batch + transition_size - 1)
    step = batch
    plt.xticks(list(range(batch + transition_size - 1, batch + transition_size - 1 - step * 4 - 1, -step)))

    # plt.xticks(list(range(batch, batch + transition_size, 20)) + [batch + transition_size - 1])
    x_max = 450
    plt.ylim(50, x_max)
    plt.yticks(list(range(0, x_max + 1, 50)))


    #loc='lower right'で、右下に凡例を表示
    # 凡例は表示しない。対局相手の平均レートを表示するときにはアンコメントしたほうがいいかもしれない。
    plt.legend(loc='upper left', prop={'size' : 10})

    # 右側の余白を調整
    # plt.subplots_adjust(right=0.5, top=0.5)

    plt.savefig("result_dir/graph/b{0:03d}_avg_rating.png".format(batch))
    plt.clf()

#「手数(int)をキーとして回数を値とする辞書」のリストを与え、それをキーごとにグラフ化する
def draw_opp_tsumero_overlook(batch, transition_size, hand_to_cnt_transition_list, suffix_name, ylabel_str="自玉への詰めろ見逃し数"):
    plt.clf()

    x = list(range(batch, batch + transition_size))

    cand = [1,3,5,7,9]
    for n in cand:
        y = [t_dic[n] for t_dic in hand_to_cnt_transition_list]
        plt.plot(x, y, label="%d手詰" % n)

    plt.title("{1}の推移 (直近{0:d}局ごと)".format(batch, ylabel_str))
    plt.ylabel(ylabel_str)
    plt.xlabel("対局ID")

    #点線の補助線を描画
    # plt.plot([batch, batch+transition_size-1], [5, 5], ':')
    # plt.plot([batch, batch+transition_size-1], [10, 10], ':')


    #X,Y軸の範囲
    plt.xlim(batch, batch + transition_size - 1)
    step = batch
    plt.xticks(list(range(batch + transition_size - 1, batch + transition_size - 1 - step * 4 - 1, -step)))
    # plt.xticks(list(range(batch, batch + transition_size, 20)) + [batch + transition_size - 1])

    [xmin, xmax, ymin, ymax] = plt.axis() #今の境界を返す
    plt.axis([xmin,xmax,ymin-1,ymax+1]) #新しい境界を設定
    # plt.ylim(0.0, 1.4)
    # plt.yticks([ y / 100.0 for y in range(10, 100+1, 10)])


    #loc='lower right'で、右下に凡例を表示
    plt.legend(prop={'size' : 7})

    # 右側の余白を調整
    # plt.subplots_adjust(right=0.5, top=0.5)

    save_path = "result_dir/graph/b{0:03d}_{1}.png".format(batch, suffix_name)
    plt.savefig(save_path)
    plt.clf()

    return

def draw_discover_overlook_mate(batch, transition_size, discover_transition_list, overlook_transition_list):
    plt.clf()

    x = list(range(batch, batch + transition_size))

    cand = [1,3,5,7,9]
    for n in cand:
        y = []
        y_d = [d_dic[n] for d_dic in discover_transition_list]
        y_o = [o_dic[n] for o_dic in overlook_transition_list]

        for d, o in zip(y_d, y_o):
            if (d + o) == 0:
                if len(y) == 0:
                    y = [0.0]
                else:
                    y.append(y[-1]) #バッチ中に詰み手順がなかったら前のバッチの値を引き継ぐ
            else:
                r = 1.0 * d / (d + o)
                y.append(r)

        plt.plot(x, y, label="%d手詰" % n)

    plt.title("即詰み発見率推移 (直近{0:d}局ごと)".format(batch))
    plt.ylabel("即詰み発見率")
    plt.xlabel("対局ID")

    #点線の補助線を描画
    plt.plot([batch, batch+transition_size-1], [1.0, 1.0], ':')
    plt.plot([batch, batch+transition_size-1], [0.7, 0.7], ':')


    #X,Y軸の範囲
    plt.xlim(batch, batch + transition_size - 1)
    step = batch
    plt.xticks(list(range(batch + transition_size - 1, batch + transition_size - 1 - step * 4 - 1, -step)))
    # plt.xticks(list(range(batch, batch + transition_size, 20)) + [batch + transition_size - 1])
    plt.ylim(0.0, 1.4)
    plt.yticks([ y / 100.0 for y in range(10, 100+1, 10)])


    #loc='lower right'で、右下に凡例を表示
    plt.legend(prop={'size' : 7})

    # 右側の余白を調整
    # plt.subplots_adjust(right=0.5, top=0.5)

    plt.savefig("result_dir/graph/b{0:03d}_mate.png".format(batch))
    plt.clf()

    return

def draw_transition(batch, transition_dic, transition_size, input_keys):
    draw_importrance(batch, transition_dic, transition_size, input_keys)
    draw_tactics_win_p(batch, transition_dic, transition_size, input_keys)

    return

#切れ負けルールの対局の割合をグラフ化
def draw_byouyomi_rate(batch, kiremake_rate_transition_list, transition_size):
    plt.clf()

    plt.title("秒読みルール割合推移 (直近{0:d}局ごと)".format(batch))
    plt.ylabel("割合")
    plt.xlabel("対局ID")

    #X,Y軸の範囲
    plt.xlim(batch, batch + transition_size - 1)
    step = batch
    plt.xticks(list(range(batch + transition_size - 1, batch + transition_size - 1 - step * 4 - 1, -step)))
    # plt.xticks(list(range(batch, batch + transition_size, 20)) + [batch + transition_size - 1])

    plt.ylim(0.0, 1.0)
    plt.yticks([ i/10.0 for i in range(0, 11)])

    x = list(range(batch, batch + transition_size))
    y = [ 1.0 - r for r in kiremake_rate_transition_list ]
    plt.plot(x, y)

    plt.plot([batch, batch+transition_size-1], [0.5, 0.5], ':')


    # #loc='lower right'で、右下に凡例を表示
    # plt.legend(prop={'size' : 10}, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)

    # 右側の余白を調整
    # plt.subplots_adjust(right=0.5, top=0.5)
    plt.savefig("result_dir/graph/b{0:03d}_byouyomi_rule.png".format(batch))
    plt.clf()

    return


#n棋譜ぶんのCSV情報を引数として、その棋譜内での各アプリでの平均レーティングを求める
def get_avg_rating_dict(batch_csv, ignore_app_list=[]):
    avg_rating_dict = defaultdict(float) #アプリ名をキー、平均レーティングを値とする辞書
    app_sum_dict = defaultdict(float)
    app_cnt_dict = defaultdict(int) #アプリ名をキー、出現回数を値とする辞書

    opponent_avg_rating_dict = defaultdict(float) #アプリ名をキー、平均レーティングを値とする辞書。相手の平均Rを同様に保存
    opponent_app_sum_dict = defaultdict(float)
    # opponent_app_cnt_dict = defaultdict(int) #これはapp_cnt_dictと同じ値になるので不要

    for kif_data in batch_csv:
        #相手もしくは自分のレーティングが不明である対局はスキップ (例: 対面対局など)
        if (kif_data[3] in ignore_app_list) or (kif_data[4] in ignore_app_list):
            continue

        app = kif_data[1]
        rating = float(kif_data[3])
        opponent_rating = float(kif_data[4])

        app_cnt_dict[app] += 1
        app_sum_dict[app] += rating
        opponent_app_sum_dict[app] += opponent_rating

    for app,cnt in app_cnt_dict.items():
        avg_rating_dict[app] = app_sum_dict[app] / app_cnt_dict[app]
        opponent_avg_rating_dict[app] = opponent_app_sum_dict[app] / app_cnt_dict[app]

    return avg_rating_dict, opponent_avg_rating_dict

def get_kiremake_rate(csv_tuples):
    size = len(csv_tuples)

    kiremake_pattern = re.compile(r'[0-9][0-9]:[0-9][0-9]\+00')
    lst = [ tpl[2] for tpl in csv_tuples if kiremake_pattern.search(tpl[2]) ]

    return 1.0 * len(lst) / size


def main(win_percentage_dir, batch, topn):
    apery_dir = 'kif_dir/analyzed/shogiGUI/apery/utf8'
    csv_tuples = [line.rstrip().replace('"', '').split(',') for line in sys.stdin]
    log_size = len(csv_tuples)
    if log_size < batch:
        batch = log_size
    elif batch == 0 or log_size == 0:
        raise Exception("batch_size or log_size == 0")

    all_win_p_transition_list = [] #全体での勝率の推移を記録するためのリスト
    sente_win_p_transition_list = [] #先手での勝率の推移を記録するためのリスト
    gote_win_p_transition_list = [] #後手での勝率の推移を記録するためのリスト
    sente_ratio_transition_list = [] #batch中の先手番の割合

    transition_dic = defaultdict(list) #(手番, 戦型)をキーとして、[(勝率, 遭遇率, 重要度)]を値とする辞書

    avg_rating_transition_list = [] #レーティングの推移を記録するためのリスト
    opponent_avg_rating_transition_list = [] #レーティングの推移を記録するためのリスト

    #レーティング推移を記録しないアプリ一覧
    ignore_app_list = ["不明", "対面", "激指R", "将棋ウォーズp", "将棋ウォーズ(3切れ)", "将棋ウォーズ(10秒)", "将棋クエスト(2分)"]

    app_set = set([tpl[1] for tpl in csv_tuples])

    #ここから詰み関連
    discover_dic_dic = {}
    overlook_dic_dic = {}
    opponent_tsumero_overlook_dic_dic = {}
    opponent_tsumero_overlook_lose_dic_dic = {}
    overlook_lose_dic_dic = {} #相手玉の詰みがあったのに見逃して負け

    for log_line in csv_tuples:
        kif_name = log_line[0]
        analyzed_kif_path = apery_dir + '/' + kif_name

        if (not os.path.exists(analyzed_kif_path)):
            discover_dic_dic[kif_name] = defaultdict(int)
            overlook_dic_dic[kif_name] = defaultdict(int)
            opponent_tsumero_overlook_dic_dic[kif_name] = defaultdict(int)
            opponent_tsumero_overlook_lose_dic_dic[kif_name] = defaultdict(int)
            overlook_lose_dic_dic[kif_name] = defaultdict(int)
            continue


        tagged_kif_lines = count_mate.get_tagged_kif(analyzed_kif_path)
        score_list = count_mate.get_score_list(tagged_kif_lines)
        is_winner = (log_line[6] == "勝")
        is_sente = (log_line[7] == "先手")

        with open('result_dir/score_list/%s' % kif_name, 'w') as move_f:
            s = count_mate.get_score_list_str_lst(score_list)
            move_f.write("\n".join(s))
            move_f.write("\n")


        discover_dic = count_mate.get_discover_dic(is_winner, is_sente, score_list)
        overlook_dic = count_mate.get_overlook_dic(is_sente, score_list)
        opponent_tsumero_overlook_dic = count_mate.get_opponent_tsumero_overlook_dic(is_sente, score_list)

        discover_dic_dic[kif_name] = discover_dic
        overlook_dic_dic[kif_name] = overlook_dic
        opponent_tsumero_overlook_dic_dic[kif_name] = opponent_tsumero_overlook_dic

        if is_winner:
            overlook_lose_dic_dic[kif_name] = defaultdict(int)
            opponent_tsumero_overlook_lose_dic_dic[kif_name] = defaultdict(int)
        else:
            overlook_lose_dic_dic[kif_name] = overlook_dic
            opponent_tsumero_overlook_lose_dic_dic[kif_name] = opponent_tsumero_overlook_dic

    discover_transition_list = [] #詰みの発見数と見逃し数のペアの推移
    overlook_transition_list = [] #詰みの発見数と見逃し数のペアの推移
    opponent_tsumero_overlook_transition_list = [] #詰めろを見逃した数
    opponent_tsumero_overlook_lose_transition_list = [] #負けた対局のみで、詰めろを見逃した数を集計
    overlook_lose_transition_list = [] #詰みを発見できなくて負け
    kiremake_rate_transition_list = [] #切れ負けルールの対局数


    #バッチが100の時のみ、discover_dic_dicとoverlook_dic_dicの中身をファイルに出力
    #バッチ数がいくらであっても出力結果が変わらないため、複数のバッチ数で出力するのは無駄
    #しかも、並列実行するとするとお互いが書き換え合って困ったことになるかもしれない
    if batch == 100:
        count_mate.output_discover_overlook_dic_dic(discover_dic_dic, overlook_dic_dic)
        count_mate.output_tsumero_overlook_dic_dic(opponent_tsumero_overlook_dic_dic)


    for start_kif_ind in range(0, log_size - batch + 1):
        end_kif_ind = start_kif_ind + batch - 1
        batch_csv = csv_tuples[start_kif_ind:end_kif_ind + 1]
        win_num_dic, lose_num_dic = read_batch_csv(batch_csv)
        wfi_dic = get_win_p_freq_importance_dic(batch, win_num_dic, lose_num_dic)

        all_win_p_in_batch = 1.0 * sum([v for k,v in win_num_dic.items()]) / batch
        sente_win = sum([v for k,v in win_num_dic.items()  if k[0] == "先手"])
        sente_lose = sum([v for k,v in lose_num_dic.items() if k[0] == "先手"])
        sente_win_p_in_batch = 1.0 * sente_win / (sente_win + sente_lose)

        gote_win = sum([v for k,v in win_num_dic.items() if k[0] == "後手"])
        gote_lose = sum([v for k,v in lose_num_dic.items() if k[0] == "後手"])
        gote_win_p_in_batch = 1.0 * gote_win / (gote_win + gote_lose)

        sente_ratio_transition_list.append(1.0 * (sente_win + sente_lose) / batch)
        all_win_p_transition_list.append(all_win_p_in_batch)
        sente_win_p_transition_list.append(sente_win_p_in_batch)
        gote_win_p_transition_list.append(gote_win_p_in_batch)

        kiremake_rate_transition_list.append(get_kiremake_rate(batch_csv))

        avg_rating_dict, opponent_avg_rating_dict = get_avg_rating_dict(batch_csv, ignore_app_list)
        avg_rating_transition_list.append(avg_rating_dict)
        opponent_avg_rating_transition_list.append(opponent_avg_rating_dict)

        for key, val in wfi_dic.items():
            transition_dic[key].append(val)


        #ここから詰み関連
        batch_discover_dic = defaultdict(int)
        batch_overlook_dic = defaultdict(int)
        batch_opp_tsumero_overlook_dic = defaultdict(int)
        batch_opp_tsumero_overlook_lose_dic = defaultdict(int)
        batch_overlook_lose_dic = defaultdict(int)
        for log_line in batch_csv:
            kif_name = log_line[0]
            for k, v in discover_dic_dic[kif_name].items():
                batch_discover_dic[k] += v

            for k, v in overlook_dic_dic[kif_name].items():
                batch_overlook_dic[k] += v

            for k, v in opponent_tsumero_overlook_dic_dic[kif_name].items():
                batch_opp_tsumero_overlook_dic[k] += v

            for k, v in opponent_tsumero_overlook_lose_dic_dic[kif_name].items():
                batch_opp_tsumero_overlook_lose_dic[k] += v

            for k, v in overlook_lose_dic_dic[kif_name].items():
                batch_overlook_lose_dic[k] += v

        discover_transition_list.append(batch_discover_dic)
        overlook_transition_list.append(batch_overlook_dic)
        opponent_tsumero_overlook_transition_list.append(batch_opp_tsumero_overlook_dic)
        opponent_tsumero_overlook_lose_transition_list.append(batch_opp_tsumero_overlook_lose_dic)
        overlook_lose_transition_list.append(batch_overlook_lose_dic)


    end_kif_ind = log_size - 1
    start_kif_ind = end_kif_ind - batch + 1
    last_batch_csv = csv_tuples[start_kif_ind:end_kif_ind + 1]
    win_num_dic, lose_num_dic = read_batch_csv(last_batch_csv)
    output_win_lose_num_dic(batch, win_num_dic, lose_num_dic)

    if batch < log_size:
        input_keys = [t[2] for t in sorted([(v[2], (1.0 - v[0]), k) for k, v in wfi_dic.items()], reverse=True)][0:topn]
        transition_size = log_size - batch + 1
        draw_byouyomi_rate(batch, kiremake_rate_transition_list, transition_size)

        draw_discover_overlook_mate(batch, transition_size, discover_transition_list, overlook_transition_list)
        draw_opp_tsumero_overlook(batch, transition_size, opponent_tsumero_overlook_transition_list, "tsumero_all")
        draw_opp_tsumero_overlook(batch, transition_size, opponent_tsumero_overlook_lose_transition_list, "tsumero_lose")
        draw_opp_tsumero_overlook(batch, transition_size, overlook_lose_transition_list, "overlook_lose", "相手玉の即詰みを見逃して負けた数")

        draw_avg_rating_transition(batch, transition_size, app_set, avg_rating_transition_list, opponent_avg_rating_transition_list, ignore_app_list)
        draw_sengo_win_p(batch, transition_size, all_win_p_transition_list, sente_win_p_transition_list, gote_win_p_transition_list, sente_ratio_transition_list)
        draw_transition(batch, transition_dic, transition_size, input_keys)


        with open("{0}/win_percentage_kifs_b{1:03d}.csv".format(win_percentage_dir, batch), 'w') as f:
            f.write("\n".join([",".join(list(tpl)) for tpl in last_batch_csv]))
            f.write("\n")


    return

if __name__ == '__main__':
    args = docopt(__doc__)
    win_percentage_dir = args["<win_percentage_dir>"]
    batch = int(args["<batch>"])
    topn = int(args["<topn>"])
    main(win_percentage_dir, batch, topn)
