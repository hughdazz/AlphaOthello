# AlphaOthello

同济大学人工智能期末大作业
模仿AlphaZero架构实现的卷积神经网络玩黑白棋
*AI final big assignment at Tongji University*
*Mimicking the AlphaZero architecture implemented by convolutional neural network to play Othello*

## 依赖/Dependencies

本项目使用keras深度学习工具包,采用theano作为keras后端(只针对theano做了测试,tensorflow应该也行,采用theano的原因是因为它够轻量)
*This project uses the keras deep learning toolkit, using theano as the keras backend (only for theano did the test, tensorflow should also work, the reason for using theano is because it is light enough)*

用以下命令安装keras及theano
*Install keras and theano with the following command*

`pip install keras==2.0.8`
`pip install theano`

同时本项目实现了前端界面,需要用到flask框架
用以下命令安装flask
*The project also implements the front-end interface, which requires the use of the flask framework*
*Install flask with the following command*

`pip install flask`

## 文件说明/Document descriptions

|文件名|说明|
|---|---|
|board.py|游戏棋盘的实现/Implementation of the game board|
|mcts_pure.py|纯粹蒙特卡洛树搜索的实现/Implementation of pure MCTS|
|model.py|策略价值网络的实现/Realization of policy value network|
|mcts_alpha.py|应用策略价值网络的蒙特卡洛树搜索的实现/Implementation of MCTS with application of policy value network|
|self_play.py|自我对弈进行训练的实现/Implementation of self-training for the game|
|gennerate.py|产生纯粹蒙特卡洛树搜索对弈棋谱的实现/Implementation for generating pure MCTS games|
|train_from_pure.py|从棋谱进行训练的实现/Implementation of training from a chess game|
|server.py|flask服务器的实现/Implementation of flask server|
|templates/index.html|前端的实现/Front-end implementation|

## 实现思路/Realization ideas

模型架构/Model Architecture:

按照AlphaZero的方法,采用卷积神经网络作为预测模型,该模型的输入为四层8*8的数组,第一层为黑子的落子情况,第二层为白子的落子情况,第三层为上一步落子位置,第四层为现在为谁的回合.然后模型有三层的卷积层,分别使用32,64,128个filter.最后卷积层分别连接长度为64的全连接层和长度为1的全连接层作为策略和价值的输出.无池化层.
*According to AlphaZero's method, a convolutional neural network is used as the prediction model.*
*The input of the model is a four-layer 8x8 array, the first layer is the black disc drop, the second layer is the white disc drop the third layer is the previous drop position, and the fourth layer is whose turn it is now.*
*the model has three convolutional layers, using 32, 64 and 128 filters respectively. The final convolutional layer is connected to a fully connected layer of length 64 and a fully connected layer of length 1 as the output of strategy and value respectively. No pooling layer.*

训练方法/Training methods:

让模型自我对弈,使用每个局面作为x,使用pure MCTS的预测值作为policy的y,使用最终赢家作为value的y,在一局结束后立马训练,更新模型.
*Let the model play itself, using each situation as x, using the predicted value of pure MCTS as y of policy, and using the final winner as y of value, and train and update the model immediately after a game.*

## 最终效果/Final result

not too bad.