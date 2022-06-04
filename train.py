from model import PolicyValueNet
from board import Board
import mcts_alpha
import mcts_pure

b = Board()
m = PolicyValueNet()
policy,value=m.policy_value_fn(b,'X')

state = b.current_state('X')
probs = []
for i in range(64):
    probs.append(0.5)
winner = 1

state = [state]
probs = [probs]
winner = [winner]

m.train(state, probs, winner, 0.01)

mc=mcts_alpha.MonteCarlo(m)

mc.search(b,'X')

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

