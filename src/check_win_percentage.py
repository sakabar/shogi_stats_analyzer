"""Check Win Percentage

Usage: check_win_percentage.py <batch> <topn>
       check_win_percentage.py -h | --help

Options:
    -h, --help  show this help message and exit
"""

from collections import defaultdict
from docopt import docopt
import matplotlib.pyplot as plt
import sys

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
    plt.xlim(batch, batch + transition_size)
    plt.xticks(list(range(batch, batch + transition_size, 20)) + [batch + transition_size])

    #loc='lower right'で、右下に凡例を表示
    plt.legend(prop={'size' : 10}, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)

    # 右側の余白を調整
    plt.subplots_adjust(right=0.5, top=0.5)
    plt.savefig("graph/b{0:03d}_importance.png".format(batch))
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
    plt.xlim(batch, batch + transition_size)
    plt.xticks(list(range(batch, batch + transition_size, 20)) + [batch + transition_size])

    #loc='lower right'で、右下に凡例を表示
    plt.legend(prop={'size' : 10}, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)

    # 右側の余白を調整
    plt.subplots_adjust(right=0.5, top=0.5)
    plt.savefig("graph/b{0:03d}_tactics_win_p.png".format(batch))
    plt.clf()

    return

def draw_sengo_win_p(batch, transition_size, all_win_p_transition_list, sente_win_p_transition_list, gote_win_p_transition_list):

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

    plt.title("勝率推移 (直近{0:d}局ごと)".format(batch))
    plt.ylabel("勝率")
    plt.xlabel("対局ID")

    #X,Y軸の範囲
    plt.xlim(batch, batch + transition_size)
    plt.xticks(list(range(batch, batch + transition_size, 20)) + [batch + transition_size])
    plt.ylim(0.35, 0.55)
    plt.yticks([ y / 100.0 for y in range(35, 55, 5)])


    #loc='lower right'で、右下に凡例を表示
    plt.legend()

    # 右側の余白を調整
    # plt.subplots_adjust(right=0.5, top=0.5)

    plt.savefig("graph/b{0:03d}_sengo_win_p.png".format(batch))
    plt.clf()

    return

#レーティング推移をグラフ化し、保存
def draw_avg_rating_transition(batch, transition_size, app_set, avg_rating_transition_list, ignore_app_list=[]):
    plt.clf()
    x = list(range(batch, batch + transition_size))

    for app in app_set:
        if app in ignore_app_list:
            continue
        #複数のサイトでのレーティングを0-999の範囲にたたみこむ
        #この方法だと、81Dojoで1000近辺の人はレーティングが正しく表示されない。
        #また、今後長期間
        y = [avg_dic[app] for avg_dic in avg_rating_transition_list]
        y_small = [(rating - 1000.0) if rating >= 1000 else rating for rating in y]
        plt.plot(x, y_small, label=app)

    plt.title("平均レーティング推移 (直近{0:d}局ごと)".format(batch))
    plt.ylabel("レーティング")
    plt.xlabel("対局ID")

    #X,Y軸の範囲
    plt.xlim(batch, batch + transition_size)
    plt.xticks(list(range(batch, batch + transition_size, 20)) + [batch + transition_size])
    # plt.ylim(0.35, 0.55)
    # plt.yticks([ y / 100.0 for y in range(35, 55, 5)])


    #loc='lower right'で、右下に凡例を表示
    # 凡例は表示しない
    # plt.legend()

    # 右側の余白を調整
    # plt.subplots_adjust(right=0.5, top=0.5)

    plt.savefig("graph/b{0:03d}_avg_rating.png".format(batch))
    plt.clf()

def draw_transition(batch, transition_dic, transition_size, input_keys):
    draw_importrance(batch, transition_dic, transition_size, input_keys)
    draw_tactics_win_p(batch, transition_dic, transition_size, input_keys)

    return

#n棋譜ぶんのCSV情報を引数として、その棋譜内での各アプリでの平均レーティングを求める
def get_avg_rating_dict(batch_csv, ignore_app_list=[]):
    avg_rating_dict = defaultdict(float) #アプリ名をキー、平均レーティングを値とする辞書
    app_sum_dict = defaultdict(float)
    app_cnt_dict = defaultdict(int) #アプリ名をキー、出現回数を値とする辞書
    for kif_data in batch_csv:
        if kif_data[3] in ignore_app_list:
            continue

        app = kif_data[1]
        rating = float(kif_data[3])

        app_cnt_dict[app] += 1
        app_sum_dict[app] += rating

    for app,cnt in app_cnt_dict.items():
        avg_rating_dict[app] = app_sum_dict[app] / app_cnt_dict[app]

    return avg_rating_dict





def main(batch, topn):
    csv_tuples = [line.rstrip().replace('"', '').split(',') for line in sys.stdin]
    log_size = len(csv_tuples)
    if log_size < batch:
        batch = log_size
    elif batch == 0 or log_size == 0:
        raise Exception("batch_size or log_size == 0")

    all_win_p_transition_list = [] #全体での勝率の推移を記録するためのリスト
    sente_win_p_transition_list = [] #先手での勝率の推移を記録するためのリスト
    gote_win_p_transition_list = [] #後手での勝率の推移を記録するためのリスト

    transition_dic = defaultdict(list) #(手番, 戦型)をキーとして、[(勝率, 遭遇率, 重要度)]を値とする辞書

    avg_rating_transition_list = [] #レーティングの推移を記録するためのリスト
    #レーティング推移を記録しないアプリ一覧
    ignore_app_list = ["不明", "対面", "激指R", "将棋ウォーズp", "将棋ウォーズ(3切れ)", "将棋ウォーズ(10秒)"]

    app_set = set([tpl[1] for tpl in csv_tuples])

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

        all_win_p_transition_list.append(all_win_p_in_batch)
        sente_win_p_transition_list.append(sente_win_p_in_batch)
        gote_win_p_transition_list.append(gote_win_p_in_batch)

        avg_rating_dict = get_avg_rating_dict(batch_csv, ignore_app_list)
        avg_rating_transition_list.append(avg_rating_dict)

        for key, val in wfi_dic.items():
            transition_dic[key].append(val)


    end_kif_ind = log_size - 1
    start_kif_ind = end_kif_ind - batch + 1
    last_batch_csv = csv_tuples[start_kif_ind:end_kif_ind + 1]
    win_num_dic, lose_num_dic = read_batch_csv(last_batch_csv)
    output_win_lose_num_dic(batch, win_num_dic, lose_num_dic)

    if batch < log_size:
        input_keys = [t[2] for t in sorted([(v[2], (1.0 - v[0]), k) for k, v in wfi_dic.items()], reverse=True)][0:topn]
        transition_size = log_size - batch + 1
        draw_avg_rating_transition(batch, transition_size, app_set, avg_rating_transition_list, ignore_app_list)
        draw_sengo_win_p(batch, transition_size, all_win_p_transition_list, sente_win_p_transition_list, gote_win_p_transition_list)
        draw_transition(batch, transition_dic, transition_size, input_keys)


        with open("win_percentage_kifs_b{0:03d}.csv".format(batch), 'w') as f:
            f.write("\n".join([",".join(list(tpl)) for tpl in last_batch_csv]))
            f.write("\n")


    return

if __name__ == '__main__':
    args = docopt(__doc__)
    batch = int(args["<batch>"])
    topn = int(args["<topn>"])
    main(batch, topn)
