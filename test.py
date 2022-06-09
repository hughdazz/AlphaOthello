from mcts_alpha import MonteCarlo
import mcts_pure
from model import PolicyValueNet

from board import Board

b=Board()
m=PolicyValueNet()
m.load_model('model/438.model')
mc=MonteCarlo(m)
pure=mcts_pure.MonteCarlo()
now_player='X'

def gameover(board):
    l1 = board.get_vaild_loc('X')
    l2 = board.get_vaild_loc('O')
    return len(l1) == 0 and len(l2) == 0

while(not gameover(b)):
    if len(b.get_vaild_loc(now_player)) == 0:
        print('pass')
        print()
        now_player = 'X' if now_player == 'O' else 'O'
        continue

    print('当前player: '+now_player)
    b.print()

    # 20s搜索时间
    if(now_player=='X'):
        loc = mc.search(b, now_player, 5)
    else:
        loc = pure.search(b, now_player, 29)
    b.set_piece(loc, now_player)
    print('set ['+str(loc[0])+','+str(loc[1])+']')
    print()
    now_player = 'X' if now_player == 'O' else 'O'

if (b.get_winner()==-1):
    print('Alpha lose')
else:
    print('win')