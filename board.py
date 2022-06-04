import numpy as np

class Board(object):
    def __init__(self):
        # 黑 1 白 -1 空 0
        self.board = []
        for _ in range(8):
            tmp = []
            for _ in range(8):
                tmp.append('.')
            self.board.append(tmp)
        # 初始四个子
        self.board[4][3] = 'X'
        self.board[3][4] = 'X'
        self.board[3][3] = 'O'
        self.board[4][4] = 'O'
        # 该数组中存放着合法位置以及相应的被翻转的棋子
        # 首先,黑方或白方调用get_vaild_loc函数会返回该list
        # 然后,存储相应的被翻转的棋子的目的是减少重复计算
        # 因为计算合法落子位置时会落子再撤销,落子步骤返回一个被翻转的列表,这里将其存储
        # 等到真正落子时不用重复计算,直接查表即可
        self.vaild_loc = {}

        self.prev_action = None
        return

    def get_vaild_loc(self, color):
        """
        得到合法落子位置
        """
        # self.vaild_loc={}
        locs = []
        for i in range(8):
            for j in range(8):
                flipped_pos = self.get_flipped_loc(i, j, color)
                if(len(flipped_pos) == 0):
                    continue
                self.vaild_loc[(i, j)] = flipped_pos
                locs.append([i, j])
        return locs

    def get_flipped_loc(self, xstart, ystart, color):
        """
        传入欲下的棋子坐标和棋子颜色
        返回被翻转的棋子坐标   
        """

        # 如果该位置已经有棋子或者出界，返回空列表
        if not self.is_on_board(xstart, ystart) or self.board[xstart][ystart] != '.':
            return []

        # 将color对应的子放到指定位置
        self.board[xstart][ystart] = color
        # 对方棋手
        peer_color = 'X' if color == 'O' else 'O'

        # 要被翻转的棋子
        flipped_pos = []

        for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0],
                                       [-1, 1]]:
            x, y = xstart, ystart
            x += xdirection
            y += ydirection
            # 如果(x,y)在棋盘上，而且为对方棋子,则在这个方向上继续前进，否则循环下一个角度。
            if self.is_on_board(x, y) and self.board[x][y] == peer_color:
                x += xdirection
                y += ydirection
                # 进一步判断点(x,y)是否在棋盘上，如果不在棋盘上，继续循环下一个角度,如果在棋盘上，则进行while循环。
                if not self.is_on_board(x, y):
                    continue
                # 一直走到出界或不是对方棋子的位置
                while self.board[x][y] == peer_color:
                    # 如果一直是对方的棋子，则点（x,y）一直循环，直至点（x,y)出界或者不是对方的棋子。
                    x += xdirection
                    y += ydirection
                    # 点(x,y)出界了和不是对方棋子
                    if not self.is_on_board(x, y):
                        break
                # 出界了，则没有棋子要翻转OXXXXX
                if not self.is_on_board(x, y):
                    continue

                # 是自己的棋子OXXXXXXO
                if self.board[x][y] == color:
                    while True:
                        x -= xdirection
                        y -= ydirection
                        # 回到了起点则结束
                        if x == xstart and y == ystart:
                            break
                        # 需要翻转的棋子
                        flipped_pos.append([x, y])

        # 将前面临时放上的棋子去掉，即还原棋盘
        self.board[xstart][ystart] = '.'

        # 返回翻转的棋子数组,若该数组长度为0则证明该位置不合法
        return flipped_pos

    def set_piece(self, action, color):
        """
        传入欲下的棋子坐标及翻转坐标列表及当前棋手
        落子并翻转
        """
        [x, y] = action
        self.board[x][y] = color
        for [xi, yi] in self.vaild_loc[(x, y)]:
            self.board[xi][yi] = color
        self.prev_action = action

    def is_on_board(self, x, y):
        """
        判断棋子是否未出界
        """
        return x >= 0 and x <= 7 and y >= 0 and y <= 7

    def print(self):
        """
        打印棋盘,方便调试
        """
        for i in range(8):
            for j in range(8):
                print(self.board[i][j], end=' ')
            print()

    def get_winner(self):
        """
        判断黑棋和白旗的输赢，通过棋子的个数进行判断
        :return: 1 黑棋赢,-1 白旗赢,0 表示平局，黑棋个数和白旗个数相等
        """
        # 定义黑白棋子初始的个数
        black_count, white_count = 0, 0
        for i in range(8):
            for j in range(8):
                # 统计黑棋棋子的个数
                if self.board[i][j] == 'X':
                    black_count += 1
                # 统计白旗棋子的个数
                if self.board[i][j] == 'O':
                    white_count += 1
        if black_count > white_count:
            # 黑棋胜
            return 1
        elif black_count < white_count:
            # 白棋胜
            return -1
        elif black_count == white_count:
            # 表示平局，黑棋个数和白旗个数相等
            return 0

    def current_state(self, color):
        now_state = []
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == 'X':
                    now_state.append(1)
                else:
                    now_state.append(0)
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == 'O':
                    now_state.append(1)
                else:
                    now_state.append(0)
        for i in range(8):
            for j in range(8):
                if color == 'X':
                    now_state.append(1)
                else:
                    now_state.append(-1)
        for i in range(8):
            for j in range(8):
                if self.prev_action != None and self.prev_action[0] == i and self.prev_action[1] == j:
                    now_state.append(1)
                else:
                    now_state.append(0)
        return now_state
