from board import Board
import mcts_pure

import numpy as np
import random
import string


def gameover(board):
    l1 = board.get_vaild_loc('X')
    l2 = board.get_vaild_loc('O')
    return len(l1) == 0 and len(l2) == 0


# 根据pure方法生成棋谱，加速训练过程
while True:
    states = []
    probs_s = []
    winners = []

    now_board = Board()
    now_pure = mcts_pure.MonteCarlo()

    # 黑子先行
    now_player = 'X'

    while(not gameover(now_board)):
        # 获得state
        state = now_board.current_state(now_player)
        probs = []
        for i in range(64):
            probs.append(0)
        # 如果无子可下则跳过
        if len(now_board.get_vaild_loc(now_player)) == 0:
            print('pass')
            print()
            now_player = 'X' if now_player == 'O' else 'O'
            continue
        # 20s搜索时间
        loc = now_pure.search(now_board, now_player, 20)
        acts_probs = now_pure.get_probs()
        # 根据mcts_pure给出的概率作为probs
        for act, prob in acts_probs:
            probs[act[0]*8+act[1]] = prob

        print('当前player: '+now_player)
        now_board.print()

        states.append(state)
        probs_s.append(probs)
        # 实际选择pure最大估值
        now_board.set_piece(loc, now_player)
        print('set ['+str(loc[0])+','+str(loc[1])+']')
        print()
        now_player = 'X' if now_player == 'O' else 'O'

    winner = now_board.get_winner()
    total_size = len(states)
    for _ in range(total_size):
        winners.append(winner)
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))
    my_dict = {'states': states, 'probs_s': probs_s, 'winners': winners}
    np.save('game/'+ran_str, my_dict)

