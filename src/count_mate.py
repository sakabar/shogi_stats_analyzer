from collections import defaultdict
import sys
import re

#kifファイルの中身を格納したリストを返す。ただし、後で使いやすいように要所要所で棋譜コメントでタグを挿入している。
def get_tagged_kif(kif_path):
    tagged_kif_lines = []

    with open(kif_path, 'r') as f:
        for line in f:
            line = line.rstrip()
            if line == "手数----指手---------消費時間--":
                tagged_kif_lines.append(line)
                tagged_kif_lines.append("**<SSA_tag><init>")
            elif re.search(r'^ *[0-9]+', line):
                tagged_kif_lines.append("**<SSA_tag><move_end>")
                tagged_kif_lines.append(line)
            else:
                tagged_kif_lines.append(line)

    return tagged_kif_lines


def get_move_list(tagged_kif_lines):
    ans = []

    is_initialization = False #初期状態を表すmoveか
    is_normal_move = False

    #(n, [n,n,n])
    tmp_val = 0
    tmp_cand_list = []
    win_point = 30000
    for line in tagged_kif_lines:
        if line == "**<SSA_tag><init>":
            tpl = (0, [0])
            ans.append(tpl)
            is_initialization = True
            move_ind = 1
        elif line == "**<SSA_tag><move_end>":
            if is_initialization:
                is_initialization = False
                is_normal_move = True
            elif is_normal_move:
                tpl = (tmp_val, tmp_cand_list)
                ans.append(tpl)
                tmp_cand_list = []
                move_ind += 1
            else:
                pass

        else:
            if is_normal_move:
                mate_pat = re.compile(r'評価値 ([+-])詰 ([0-9]+)')
                normal_pat = re.compile(r'評価値 ([+-]?[0-9]+)')
                mate_match = mate_pat.search(line)
                normal_match = normal_pat.search(line)
                if line.startswith('**解析'):
                    if mate_match:
                        mate_sign = mate_match.group(1)
                        #「詰n」は「相手がどんなことをしてきてもこちらが最善手を指せばn手で詰む」ということを表すので、n手詰を意味しているわけではない。
                        #そこで、読み筋に書かれている手の数を数えて、何手詰を読んでいるかを計算する必要がある。
                        think_hands_match = re.search(r'読み筋 (.*)$', line)
                        think_hands = think_hands_match.group(1).rstrip()
                        mate_num = len(think_hands.split(' '))
                        # mate_num = int(mate_match.group(2))
                        if mate_sign == '+':
                            tmp_val = win_point - mate_num
                        elif mate_sign == '-':
                            tmp_val = - (win_point - mate_num)
                        else:
                            #パターンにマッチしたので、こうなることはない
                            raise Exception("Wrong line: [%s]" % line)

                    elif normal_match:
                        tmp_val = int(normal_match.group(1))
                    else:
                        raise Exception("Wrong line: [%s]" % line)
                elif line.startswith('**候補手'):
                    if mate_match:
                        mate_sign = mate_match.group(1)
                        think_hands_match = re.search(r'読み筋 (.*)$', line)
                        think_hands = think_hands_match.group(1).rstrip()
                        mate_num = len(think_hands.split(' ')) - 1 #候補手のほうは、指す手そのものも読み筋に入っている。
                        # mate_num = int(mate_match.group(2))
                        if mate_sign == '+':
                            p = win_point - mate_num
                        elif mate_sign == '-':
                            p = - (win_point - mate_num)
                        else:
                            #パターンにマッチしたので、こうなることはない
                            raise Exception("Wrong line: [%s]" % line)

                        if len(tmp_cand_list) == 0:
                           tmp_cand_list.append(p)
                        elif (move_ind % 2 == 1) and tmp_cand_list[-1] >= p:
                            tmp_cand_list.append(p)
                        elif (move_ind % 2 == 0) and tmp_cand_list[-1] <= p:
                            tmp_cand_list.append(p)
                    elif normal_match:
                        p = int(normal_match.group(1))
                        if len(tmp_cand_list) == 0:
                           tmp_cand_list.append(p)
                        elif (move_ind % 2 == 1) and tmp_cand_list[-1] >= p:
                            tmp_cand_list.append(p)
                        elif (move_ind % 2 == 0) and tmp_cand_list[-1] <= p:
                            tmp_cand_list.append(p)
                    else:
                        raise Exception("Wrong line: [%s]" % line)
                else:
                    pass
            else:
                pass

    return ans

def output_move_list(move_list):
    output_arr = []

    for ind, (v1, v_lst) in enumerate(move_list):
        if ind == 0:
            output_arr.append("S 0 %d %d" % (v1, v_lst[0]))
        elif ind % 2 == 1:
            output_arr.append("+ %d %d %d" % (ind, v1, v_lst[0]))
        else:
            output_arr.append("- %d %d %d" % (ind, v1, v_lst[0]))

    print("\n".join(output_arr))
    return

#即詰みの評価値から、即詰みの手数を算出
def checkmate_score_to_hand_num(is_sente, score):
    checkmate_score = 30000
    ans = 0
    if is_sente:
        ans = checkmate_score - score + 1
    else:
        ans = checkmate_score + score + 1
    return ans

def hand_num_to_checkmate_score(is_sente, n):
    checkmate_score = 30000
    ans = 0
    if is_sente:
        ans = checkmate_score - (n-1)
    else:
        ans = - (checkmate_score - (n-1))

    return ans


def get_discover_dic(is_winner, is_sente, move_list):
    checkmate_score = 30000
    discover_dic = defaultdict(int)
    final_score = move_list[-1][0] #終局時の評価値
    cnt = 0

    if (not is_winner):
        #勝者でない場合は、必ず詰みに失敗している
        return discover_dic

    if is_sente:
        if final_score >= checkmate_score - 100:
            cnt = checkmate_score_to_hand_num(is_sente, final_score) - 1
        else:
            cnt = 0
    else:
        if final_score <= -(checkmate_score - 100):
            cnt = checkmate_score_to_hand_num(is_sente, final_score) - 1
        else:
            cnt = 0

    for ind, (v1, v_lst) in list(enumerate(move_list))[::-1]:
        if is_sente:
            if v1 >= checkmate_score - 100:
                cnt += 1
            else:
                break
        else:
            if v1 <= -(checkmate_score - 100):
                cnt += 1
            else:
                break

    if cnt == 0:
        #評価値が詰み状態にならずに勝利 → 時間か勝勢による投了
        return discover_dic

    #1,3,5,...,cnt手詰に成功
    for i in range(1, cnt+1, 2):
        discover_dic[i] = 1

    return discover_dic

def get_overlook_dic(is_sente, move_list):
    checkmate_score = 30000
    overlook_dic = defaultdict(int)

    if is_sente:
        sente_moves = [move_tpl for ind, move_tpl in enumerate(move_list) if ind % 2  == 1]
        lst = [v_lst[0] for v1, v_lst in sente_moves if v_lst[0] >= (checkmate_score - 100) and v1 < v_lst[0]]

        for overlooked in lst:
            hand_num = checkmate_score - overlooked + 1
            overlook_dic[hand_num] += 1
    else:
        gote_moves = [move_tpl for ind, move_tpl in enumerate(move_list) if ind % 2  == 0]
        lst = [v_lst[0] for v1, v_lst in gote_moves if v_lst[0] <= -(checkmate_score - 100) and v1 > v_lst[0]]

        for overlooked in lst:
            hand_num = checkmate_score + overlooked + 1
            overlook_dic[hand_num] += 1

    return overlook_dic

# def main():
#     # kif_name = "sample_apery2.kif"
#     tagged_kif_lines = get_tagged_kif(kif_name)
#     # for line in tagged_kif_lines:
#     #     print(line)

#     move_list = get_move_list(tagged_kif_lines)

#     is_winner = False
#     is_sente = True
#     discover_dic = get_discover_dic(is_winner, is_sente, move_list)
#     overlook_dic = get_overlook_dic(is_sente, move_list)

#     return

# if __name__ == '__main__':
#     main()
