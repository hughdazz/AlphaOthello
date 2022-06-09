from model import PolicyValueNet
from board import Board
import mcts_alpha
import mcts_pure
import json

import pandas as pd


def gameover(board):
    l1 = board.get_vaild_loc('X')
    l2 = board.get_vaild_loc('O')
    return len(l1) == 0 and len(l2) == 0


while True:
    states = []
    probs_s = []
    winners = []

    now_board = Board()
    now_model = PolicyValueNet()

    # 获取最新模型
    f = open('id.json', 'r')
    data = json.loads(f.read())
    f.close()

    now_id = data['id']

    if now_id != 0:
        now_model.load_model('model/'+str(now_id)+'.model')
    now_alpha = mcts_alpha.MonteCarlo(now_model)
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
        # 20s
        now_pure.search(now_board, now_player, 15)
        acts_probs = now_pure.get_probs()

        print('当前player: '+now_player)
        now_board.print()

        # 根据mcts_pure给出的概率作为probs
        for act, prob in acts_probs:
            probs[act[0]*8+act[1]] = prob
        states.append(state)
        probs_s.append(probs)
        # 实际根据mcts_alpha的指示下
        loc = now_alpha.search(now_board, now_player, 5)
        print('set ['+str(loc[0])+','+str(loc[1])+']')
        print()
        now_board.set_piece(loc, now_player)
        now_player = 'X' if now_player == 'O' else 'O'

    winner = now_board.get_winner()
    total_size = len(states)
    for _ in range(total_size):
        winners.append(winner)

    # 获取最新id
    f = open('id.json', 'r')
    data = json.loads(f.read())
    f.close()
    now_id = data['id']

    loss, entropy = now_model.train(states, probs_s, winners, 0.005)
    data = [[now_id, loss, entropy]]
    df = pd.DataFrame(data, columns=['id', 'loss', 'entropy'], dtype=float)
    df.to_csv('statics.csv', mode='a', header=False)
    now_model.save_model('model/'+str(now_id+1)+'.model')
    
    f = open('id.json', 'w')
    f.write(json.dumps({"id": now_id+1}))
    f.close()


'''
建立Board
建立PolicyValueNet
load_model(M/00000002.model)

写游戏逻辑
states
probs_s
针对当前的局面,保存state,加入states
调用mcts_pure获得probs,加入probs_s
游戏结束,建立winners数组 1 黑 -1 白 0 平局
用数据训练

save_model(M/00000003.model)
'''
