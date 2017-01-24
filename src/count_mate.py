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


                        mate_num_think = len(think_hands.split(' '))
                        # mate_num = int(mate_match.group(2))
                        if mate_sign == '+':
                            tmp_val = win_point - mate_num_think
                        elif mate_sign == '-':
                            tmp_val = - (win_point - mate_num_think)
                        else:
                            #パターンにマッチしたので、こうなることはない
                            raise Exception("Wrong line: [%s]" % line)

                    elif normal_match:
                        tmp_val = int(normal_match.group(1))

                        #Aperyの解析結果に評価値35314があって驚愕した。(20170110_0058.kif)
                        #勝勢だけど詰みではない場合は、評価値を25000に下げる
                        #この処理だと、評価値の上下で悪手好手を判定しようとするときにバグの原因になるかも FIXME
                        fixed_val = 25000
                        if (tmp_val > win_point):
                            tmp_val = fixed_val
                        elif tmp_val < - win_point:
                            tmp_val = - fixed_val

                    else:
                        raise Exception("Wrong line: [%s]" % line)
                elif line.startswith('**候補手'):
                    if mate_match:
                        mate_sign = mate_match.group(1)
                        think_hands_match = re.search(r'読み筋 (.*)$', line)
                        think_hands = think_hands_match.group(1).rstrip()
                        mate_num_think = len(think_hands.split(' ')) #候補手のほうは、指す手そのものも読み筋に入っている。
                        # mate_num = int(mate_match.group(2))

                        #読み筋の手数が偶数だったら1を足す
                        #なぜか、詰+9の表示が出ているのに読み筋は8手しか表示されないということがあった。最後の1手詰は省略されている?
                        if (mate_num_think % 2) == 0:
                            mate_num_think += 1

                        _is_sente = mate_sign == '+'
                        p = hand_num_to_checkmate_score(_is_sente, mate_num_think)

                        if len(tmp_cand_list) == 0:
                           tmp_cand_list.append(p)
                        elif x_gt_y(_is_sente, tmp_cand_list[-1], p):
                            tmp_cand_list.append(p)

                    elif normal_match:
                        # #Aperyの解析結果に評価値35314があって驚愕した。(20170110_0058.kif)
                        # #勝勢だけど詰みではない場合は、評価値を25000に下げる
                        # #この処理だと、評価値の上下で悪手好手を判定しようとするときにバグの原因になるかも FIXME
                        p = int(normal_match.group(1))
                        fixed_val = 25000
                        _is_sente = (move_ind % 2 == 1)

                        if (p > win_point):
                            p = fixed_val
                        elif p < - win_point:
                            p = - fixed_val

                        if len(tmp_cand_list) == 0:
                           tmp_cand_list.append(p)
                        elif x_gt_y(_is_sente, tmp_cand_list[-1], p):
                            tmp_cand_list.append(p)
                    else:
                        raise Exception("Wrong line: [%s]" % line)
                else:
                    pass
            else:
                pass

    return ans

def get_move_list_str_lst(move_list):
    output_arr = []

    for ind, (v1, v_lst) in enumerate(move_list):
        if ind == 0:
            output_arr.append("S 0 %d %d" % (v1, v_lst[0]))
        elif ind % 2 == 1:
            output_arr.append("+ %d %d %d" % (ind, v1, v_lst[0]))
        else:
            output_arr.append("- %d %d %d" % (ind, v1, v_lst[0]))

    return output_arr

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

    if is_in_checkmate_procedure(is_sente, final_score):
        cnt = checkmate_score_to_hand_num(is_sente, final_score) - 1
    else:
        cnt = 0

    for ind, (v1, v_lst) in list(enumerate(move_list))[::-1]:
        if is_in_checkmate_procedure(is_sente, v1):
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

def get_moves(is_sente, move_list):
    if is_sente:
        return [move_tpl for ind, move_tpl in enumerate(move_list) if ind % 2  == 1]
    else:
        return [move_tpl for ind, move_tpl in enumerate(move_list) if ind % 2  == 0 and ind > 0]

def is_in_checkmate_procedure(is_sente, score):
    checkmate_score = 30000
    if is_sente:
        return score >= (checkmate_score - 100)
    else:
        return score <= -(checkmate_score - 100)

def x_gt_y(is_sente, x, y):
    if is_sente:
        return x > y
    else:
        return x < y

def x_lt_y(is_sente, x, y):
    if is_sente:
        return x < y
    else:
        return x > y

def get_opponent_tsumero_overlook_dic(is_sente, move_list):
    opp_tsumero_overlook_dic = defaultdict(int)

    moves = get_moves(is_sente, move_list)
    lst = [v1 for v1, v_lst in moves if is_in_checkmate_procedure((not is_sente), v1) and x_lt_y(is_sente, v1, v_lst[0])]

    for opp_tsumero in lst:
        hand_num = checkmate_score_to_hand_num((not is_sente), opp_tsumero) - 1
        #15手より多い手数の詰み筋は無視
        #Apery自体そんなに正確に読んでいない場合があるし、少なくとも今は15手詰を読める能力は
        #必要ない
        if (hand_num <= 15):
            opp_tsumero_overlook_dic[hand_num] += 1


    return opp_tsumero_overlook_dic


def get_overlook_dic(is_sente, move_list):
    overlook_dic = defaultdict(int)

    moves = get_moves(is_sente, move_list)
    lst = [v_lst[0] for v1, v_lst in moves if is_in_checkmate_procedure(is_sente, v_lst[0]) and x_lt_y(is_sente, v1, v_lst[0])]

    for overlooked in lst:
        hand_num = checkmate_score_to_hand_num(is_sente, overlooked)
        #15手より多い手数の詰み筋は無視
        #Apery自体そんなに正確に読んでいない場合があるし、少なくとも今は15手詰を読める能力は
        #必要ない
        if (hand_num <= 15):
            overlook_dic[hand_num] += 1

    return overlook_dic

def output_tsumero_overlook_dic_dic(tsumero_dic_dic):
    for _kif_file in tsumero_dic_dic.keys():
        _dicover_dic = tsumero_dic_dic[_kif_file]
        sorted_list = sorted(_dicover_dic.items(), key=lambda tpl:tpl[0])
        tsumero_output_path = "result_dir/checkmate/tsumero/%s" % _kif_file
        ans_str_lst = ["%d %d" % (k, v) for k, v in sorted_list]
        with open(tsumero_output_path, 'w') as f:
            if len(ans_str_lst) == 0:
                f.write("")
            else:
                f.write("\n".join(ans_str_lst))
                f.write("\n")

    return


#discover_dic_dicとoverlook_dic_dicの内容をファイルに保存
def output_discover_overlook_dic_dic(discover_dic_dic, overlook_dic_dic):
    key_set = set(list(discover_dic_dic.keys()) + list(overlook_dic_dic.keys()))
    for _kif_file in key_set:
        _dicover_dic = discover_dic_dic[_kif_file]
        sorted_list = sorted(_dicover_dic.items(), key=lambda tpl:tpl[0])
        discover_output_path = "result_dir/checkmate/discover/%s" % _kif_file
        ans_str_lst = ["%d %d" % (k, v) for k, v in sorted_list]
        with open(discover_output_path, 'w') as f:
            if len(ans_str_lst) == 0:
                f.write("")
            else:
                f.write("\n".join(ans_str_lst))
                f.write("\n")

        _overlook_dic = overlook_dic_dic[_kif_file]
        sorted_list = sorted(_overlook_dic.items(), key=lambda tpl:tpl[0])
        overlook_output_path = "result_dir/checkmate/overlook/%s" % _kif_file
        ans_str_lst = ["%d %d" % (k, v) for k, v in sorted_list]
        with open(overlook_output_path, 'w') as f:
            if len(ans_str_lst) == 0:
                f.write("")
            else:
                f.write("\n".join(ans_str_lst))
                f.write("\n")

    return
