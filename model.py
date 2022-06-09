from keras.layers import Input
from keras.engine.training import Model
from keras.layers.convolutional import Conv2D
from keras.layers.core import Dense, Flatten
from keras.regularizers import l2
import keras.backend as K

import numpy as np

import pickle

class PolicyValueNet:
    def __init__(self):
        self.l2_const = 1e-4  # coef of l2 penalty
        # 创建policy value网络
        # policy是针对当前局面所有棋子的概率,越大越值得下(先验概率)
        # value是针对当前局面的评估值,[-1,1]
        # 4*8*8网络
        # 第一层 当前选手的二值网络
        # 第二层 对方选手的二值网络
        # 第三层 来到当前状态的一步
        # 第四层 当前该谁下子
        in_x = network = Input((4, 8, 8))

        # conv layers
        network = Conv2D(filters=32, kernel_size=(3, 3), padding="same", data_format="channels_first",
                         activation="relu", kernel_regularizer=l2(self.l2_const))(network)
        network = Conv2D(filters=64, kernel_size=(3, 3), padding="same", data_format="channels_first",
                         activation="relu", kernel_regularizer=l2(self.l2_const))(network)
        network = Conv2D(filters=128, kernel_size=(3, 3), padding="same", data_format="channels_first",
                         activation="relu", kernel_regularizer=l2(self.l2_const))(network)
        # action policy layers
        policy_net = Conv2D(filters=4, kernel_size=(1, 1), data_format="channels_first",
                            activation="relu", kernel_regularizer=l2(self.l2_const))(network)
        policy_net = Flatten()(policy_net)
        self.policy_net = Dense(8*8,
                                activation="softmax", kernel_regularizer=l2(self.l2_const))(policy_net)

        # state value layers
        value_net = Conv2D(filters=2, kernel_size=(1, 1), data_format="channels_first",
                           activation="relu", kernel_regularizer=l2(self.l2_const))(network)
        value_net = Flatten()(value_net)
        value_net = Dense(64, kernel_regularizer=l2(self.l2_const))(value_net)
        self.value_net = Dense(1, activation="tanh",
                               kernel_regularizer=l2(self.l2_const))(value_net)
        # 创建模型
        self.model = Model(in_x, [self.policy_net, self.value_net])

    # 得到熵
    def get_entropy(self, probs):
        return -np.mean(np.sum(probs * np.log(probs + 1e-10), axis=1))

    def policy_value_fn(self, board, color):
        """
        输入当前棋盘的现状,然后输出当前可行动作和当前局面评价
        """
        vaild_locs = board.get_vaild_loc(color)
        current_state = np.array(board.current_state(color))

        state_union = np.array(current_state.reshape(-1, 4, 8, 8))
        # 输出预测值
        act_probs, value = self.model.predict_on_batch(state_union)

        valid_act_probs = []
        for i in range(8):
            for j in range(8):
                if([i, j] in vaild_locs):
                    valid_act_probs.append(
                        ([i, j], act_probs.flatten()[i*8+j]))


        return valid_act_probs, value[0][0]

    def train(self, state_input, mcts_probs, winner, learning_rate):
        self.model.compile(optimizer='adam', loss=[
                           'categorical_crossentropy', 'mean_squared_error'])

        state_input_union = np.array(state_input).reshape(-1, 4, 8, 8)
        mcts_probs_union = np.array(mcts_probs)
        winner_union = np.array(winner)
        # 获得loss
        loss = self.model.evaluate(state_input_union, [
                                   mcts_probs_union, winner_union], batch_size=len(state_input), verbose=0)

        action_probs, _ = self.model.predict_on_batch(state_input_union)
        entropy = self.get_entropy(action_probs)
        K.set_value(self.model.optimizer.lr, learning_rate)
        self.model.fit(state_input_union, [
                       mcts_probs_union, winner_union], batch_size=len(state_input), verbose=0)
        # 最终返回loss,entropy作为训练结果
        return loss[0], entropy

    def get_policy_param(self):
        net_params = self.model.get_weights()        
        return net_params


    def save_model(self, model_file):
        """
        保存模型参数到文件 
        keras自带的save_weights方法有问题改用pickle
        """
        net_params = self.get_policy_param()
        pickle.dump(net_params, open(model_file, 'wb'), protocol=2)

    def load_model(self, model_file):
        net_params = pickle.load(open(model_file, 'rb'))
        self.model.set_weights(net_params)

