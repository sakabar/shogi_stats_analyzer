import count_mate
from collections import defaultdict
import unittest


class TestMain(unittest.TestCase):
    def test_get_discover_dic0(self):
        is_winner = True
        is_sente = True
        move_list = [(0, [0]), (29998, [-100]), (29998, [29998]), (29999, [29999]), (30000, [30000])]

        expected = defaultdict(int)
        expected[1] = 1
        expected[3] = 1

        actual = count_mate.get_discover_dic(is_winner, is_sente, move_list)
        self.assertEqual(actual, expected)


    #迂回してしまった場合は、実際に指した手順をもとに決定
    #1手詰を見逃しているが、代わりに3手詰を発見したパターン
    def test_get_discover_dic1(self):
        is_winner = True
        is_sente = True
        move_list = [(0, [0]), (-82, [29996]), (29999, [-82]), (29998, [30000]), (29999, [29999]), (30000, [30000])]

        expected = defaultdict(int)
        expected[1] = 1
        expected[3] = 1

        actual = count_mate.get_discover_dic(is_winner, is_sente, move_list)
        self.assertEqual(actual, expected)

    #後手番パターン
    def test_get_discover_dic2(self):
        is_winner = True
        is_sente = False
        move_list = [(0, [0]), (-29999, [0]), (-30000, [-30000])]

        expected = defaultdict(int)
        expected[1] = 1

        actual = count_mate.get_discover_dic(is_winner, is_sente, move_list)
        self.assertEqual(actual, expected)

    #途中で詰み逃しをはさんでいるパターン
    #以前は、詰み逃しの部分も加算していてバグっていた
    def test_get_discover_dic3(self):
        is_winner = True
        is_sente = True
        move_list = [(0, [0]), (-82, [29996]), (29996, [-82]), (29997, [-82]), (0, [0]), (29998, [30000]), (29999, [29999]), (30000, [30000])]

        expected = defaultdict(int)
        expected[1] = 1
        expected[3] = 1

        actual = count_mate.get_discover_dic(is_winner, is_sente, move_list)
        self.assertEqual(actual, expected)

    #即詰み手順の途中で後手が投了したパターン
    #この例だと、3手詰の途中で投了
    def test_get_discover_dic4(self):
        is_winner = True
        is_sente = True
        move_list = [(0, [0]), (-82, [29996]), (29996, [-82]), (29997, [-82]), (0, [0]), (29998, [30000])]

        expected = defaultdict(int)
        expected[1] = 1
        expected[3] = 1

        actual = count_mate.get_discover_dic(is_winner, is_sente, move_list)
        self.assertEqual(actual, expected)

    def test_get_overlook_dic0(self):
        is_sente = True
        move_list = [(0, [0]), (10, [29998]), (0, [0]), (10, [30000])]

        expected = defaultdict(int)
        expected[1] = 1
        expected[3] = 1
        actual = count_mate.get_overlook_dic(is_sente, move_list)

        self.assertEqual(actual, expected)

    def test_get_opp_tsumero_overlook_dic0(self):
        is_sente = False
        move_list = [(0, [0]), (0, [0]), (29999, [0]), (10, [30000])]

        expected = defaultdict(int)
        expected[1] = 1
        actual = count_mate.get_opponent_tsumero_overlook_dic(is_sente, move_list)

        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()


