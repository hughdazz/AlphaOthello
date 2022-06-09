from flask import Flask, request, render_template

from board import Board
import mcts_pure
import json


# 棋盘
board = Board()
pure = mcts_pure.MonteCarlo()

app = Flask(__name__)


@app.route('/vaild_loc', methods=['GET'])
def get_vaild_loc():
    color = request.args.get('color')

    vaild_loc = {}
    vaild_loc['list'] = board.get_vaild_loc(color)
    list_json = json.dumps(vaild_loc, ensure_ascii=False)
    return list_json


@app.route('/set_piece', methods=['GET'])
def set_piece():
    x = request.args.get('x')
    y = request.args.get('y')
    color = request.args.get('color')

    print('\nset x:'+x+' y:'+y+' color:'+color+'\n')

    board.set_piece([int(x), int(y)], color)
    return "null"


@app.route('/board', methods=['GET'])
def get_board():
    board_list = {}
    board_list['list'] = board.board
    return board_list


@app.route('/restart', methods=['GET'])
def restart():
    global board
    board = Board()
    return "null"


@app.route('/pure_search', methods=['GET'])
def pure_search():
    color = request.args.get('color')
    loc = pure.search(board, color, 2)
    return {"loc": loc}


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
