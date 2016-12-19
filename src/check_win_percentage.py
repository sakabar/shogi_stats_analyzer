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

def draw_transition(batch, transition_dic, all_win_p_transition_list, input_keys):
    for key in input_keys:
        x = list(range(batch, batch + len(transition_dic[key])))
        y_importance = [tpl[2] for tpl in transition_dic[key]]
        plt.plot(x, y_importance, label=key)

    plt.title("重要度推移 (batch={0:d})".format(batch))
    plt.ylabel("重要度")
    plt.xlabel("対局ID")

    #X,Y軸の範囲
    plt.xlim(batch, batch + len(all_win_p_transition_list))
    plt.xticks(list(range(batch, batch + len(all_win_p_transition_list), 20)))

    #loc='lower right'で、右下に凡例を表示
    plt.legend(prop={'size' : 10}, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)

    # 右側の余白を調整
    plt.subplots_adjust(right=0.5, top=0.5)
    plt.savefig("graph/importance.png")
    plt.clf()

######################################################

    for key in input_keys:
        x = list(range(batch, batch + len(transition_dic[key])))
        y_win_p = [tpl[0] for tpl in transition_dic[key]]
        plt.plot(x, y_win_p, label=key)

    #総合勝率
    x = list(range(batch, batch + len(all_win_p_transition_list)))
    plt.plot(x, all_win_p_transition_list, label="all")

    plt.title("勝率推移 (batch={0:d})".format(batch))
    plt.ylabel("勝率")
    plt.xlabel("対局ID")


    #X,Y軸の範囲
    plt.xlim(batch, batch + len(all_win_p_transition_list))
    plt.xticks(list(range(batch, batch + len(all_win_p_transition_list), 20)))

    #loc='lower right'で、右下に凡例を表示
    plt.legend(prop={'size' : 10}, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)

    # 右側の余白を調整
    plt.subplots_adjust(right=0.5, top=0.5)
    plt.savefig("graph/win_p.png")
    plt.clf()

    return


def main(batch, topn):
    csv_tuples = [line.rstrip().replace('"', '').split(',') for line in sys.stdin]
    log_size = len(csv_tuples)
    if log_size < batch:
        batch = log_size

    all_win_p_transition_list = [] #全体での勝率の推移を記録するためのリスト
    transition_dic = defaultdict(list) #(手番, 戦型)をキーとして、[(勝率, 遭遇率, 重要度)]を値とする辞書
    for start_kif_ind in range(0, log_size - batch + 1):
        end_kif_ind = start_kif_ind + batch - 1
        batch_csv = csv_tuples[start_kif_ind:end_kif_ind + 1]
        win_num_dic, lose_num_dic = read_batch_csv(batch_csv)
        wfi_dic = get_win_p_freq_importance_dic(batch, win_num_dic, lose_num_dic)

        all_win_p_in_batch = 1.0 * sum([v for k,v in win_num_dic.items()]) / batch
        all_win_p_transition_list.append(all_win_p_in_batch)

        for key, val in wfi_dic.items():
            transition_dic[key].append(val)


    input_keys = [t[2] for t in sorted([(v[2], (1.0 - v[0]), k) for k, v in wfi_dic.items()], reverse=True)][0:topn]
    draw_transition(batch, transition_dic, all_win_p_transition_list,input_keys)

    end_kif_ind = log_size - 1
    start_kif_ind = end_kif_ind - batch
    last_batch_csv = csv_tuples[start_kif_ind:end_kif_ind + 1]
    win_num_dic, lose_num_dic = read_batch_csv(last_batch_csv)
    output_win_lose_num_dic(batch, win_num_dic, lose_num_dic)
    with open("win_percentage_kifs.csv", 'w') as f:
        f.write("\n".join([",".join(list(tpl)) for tpl in last_batch_csv]))
        f.write("\n")


    return

if __name__ == '__main__':
    args = docopt(__doc__)
    batch = int(args["<batch>"])
    topn = int(args["<topn>"])
    main(batch, topn)
