import numpy as np
from model import PolicyValueNet
import os
import json
import pandas as pd

files = os.listdir('game')
for file in files:
    dataset = np.load('game/'+file, allow_pickle=True).item()
    print(file)

    # 获取最新模型
    f = open('id.json', 'r')
    data = json.loads(f.read())
    f.close()

    now_model = PolicyValueNet()
    now_id = data['id']
    if now_id != 0:
        now_model.load_model('model/'+str(now_id)+'.model')

    loss, entropy = now_model.train(dataset['states'], dataset['probs_s'],
                                    dataset['winners'], 0.005)
    df = pd.DataFrame([[now_id, loss, entropy]], columns=[
                      'id', 'loss', 'entropy'], dtype=float)
    df.to_csv('statics.csv', mode='a', header=False)
    now_model.save_model('model/'+str(now_id+1)+'.model')
    f = open('id.json', 'w')
    f.write(json.dumps({"id": now_id+1}))
    f.close()
