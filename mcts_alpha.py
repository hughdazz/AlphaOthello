from copy import deepcopy
from func_timeout import FunctionTimedOut, func_timeout
import random
import board
import sys
import math
from model import PolicyValueNet

from math import log, sqrt


class Node:
    def __init__(self, board, parent, color, action, prob, model):
        self.parent = parent  # 父节点
        self.children = []  # 子节点列表
        self.visit_times = 0  # 访问次数
        self.board = board  # 游戏选择这个Node的时的棋盘
        self.color = color  # 当前玩家
        self.prob = prob  # 当前节点的先验概率
        self.prevAction = action  # 到达这个节点的落子坐标
        self.isover = self.gameover(board)  # 是否结束了

        self.reward = {'X': 0, 'O': 0}
        self.bestVal = {'X': 0, 'O': 0}
        # 根据神经网络获取policy,value
        self.unvisitActions, self.value = model.policy_value_fn(board, color)
        # 按照先验概率从大到小的顺序来对动作进行排序
        self.unvisitActions.sort(key=lambda x: -x[1])
        if (self.isover == False) and (len(self.unvisitActions) == 0):  # 没得走了但游戏还没结束
            self.unvisitActions.append(("noway", 0))  # ?

    def gameover(self, board):
        l1 = board.get_vaild_loc('X')
        l2 = board.get_vaild_loc('O')
        return len(l1) == 0 and len(l2) == 0

    # 根据UCT公式计算最佳节点
    def calcBestVal(self, color):
        # 这里加入神经网络获取的先验概率p,5是玄学数字
        self.bestVal[color] = self.reward[color] / self.visit_times + 5 * \
            self.prob * sqrt(log(self.parent.visit_times) / self.visit_times)


class MonteCarlo:
    def __init__(self, policy_value_net):
        self.policy_value_net = policy_value_net

    def search(self, board, color, time_limit):
        # board: 当前棋局
        # color: 当前玩家

        # 特殊情况：只有一种选择
        valid_loc = board.get_vaild_loc(color)
        if len(valid_loc) == 1:
            return valid_loc[0]

        # 复制棋盘,在该棋盘上进行后续搜索
        newboard = deepcopy(board)
        # 创建根节点
        # 根节点parent,action都为None
        root = Node(newboard, None, color, None, 0.1, self.policy_value_net)

        # 考虑时间限制,这个函数要改改
        try:
            # 测试程序规定每一步在60s以内
            func_timeout(time_limit, self.whileFunc, args=[root])
        except FunctionTimedOut:
            pass

        # 这里有误,MCTS选择的是走的最多的节点
        # return self.best_child(root, math.sqrt(2), color).prevAction
        # 选择走的最多的节点
        action = None
        visits = 0
        for child in root.children:
            if child.visit_times > visits:
                action = child.prevAction
        return action

    def whileFunc(self, root):
        while True:
            # mcts的步骤
            # selection选择,expantion扩展
            # 这里根据树策略扩展节点,
            expand_node = self.tree_policy(root)
            # 神经网络输出的value代替simulation模拟,返回扩展节点的reward
            reward = expand_node.value
            # backpropagation回溯,更新沿途节点信息
            self.backup(expand_node, reward)

    def expand(self, node):
        """
        输入一个节点,在该节点上拓展一个新的节点,使用random方法执行Action,返回新增的节点 
        """
        # 从开头弹出一个动作
        action, prob = node.unvisitActions.pop()

        # 执行action，得到新的board
        newBoard = deepcopy(node.board)
        if action != "noway":
            newBoard.set_piece(action, node.color)
        else:
            pass

        newColor = 'X' if node.color == 'O' else 'O'
        newNode = Node(newBoard, node, newColor, action,
                       prob, self.policy_value_net)
        node.children.append(newNode)

        return newNode

    def best_child(self, node, color):
        # 对每个子节点调用一次计算bestValue
        for child in node.children:
            child.calcBestVal(color)

        # 对子节点按照bestValue排序，降序
        sortedChildren = sorted(
            node.children, key=lambda x: x.bestVal[color], reverse=True)

        # 返回bestValue最大的元素
        return sortedChildren[0]

    def tree_policy(self, node):
        """
        传入当前需要开始搜索的节点（例如根节点）
        根据exploration/exploitation算法返回最好的需要expend的节点
        注意如果节点是叶子结点直接返回(叶节点即是已经到达某一终局的节点)
        """
        retNode = node
        while not retNode.isover:
            if len(retNode.unvisitActions) > 0:
                # 还有未展开的节点,则进行扩展
                return self.expand(retNode)
            else:
                # 选择val最大的
                retNode = self.best_child(retNode,  retNode.color)

        return retNode

    def backup(self, node, reward):
        """
        回溯时将每个节点的父节点的reward都更新
        """
        newNode = node
        # 节点不为None时
        while newNode is not None:
            newNode.visit_times += 1

            if reward > 0:
                newNode.reward['X'] += 1
                newNode.reward['O'] -= 1
            elif reward < 0:
                newNode.reward['X'] -= 1
                newNode.reward['O'] += 1
            elif reward == 0:
                pass

            newNode = newNode.parent
