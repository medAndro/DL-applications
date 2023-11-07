import pandas as pd
import matplotlib.pyplot as plt


def get_plot(loss, score):
    f, ax = plt.subplots(1, 2, figsize=(20, 8))
    ax[0].grid(True)
    ax[1].grid(True)

    
    ax[0].plot(loss, color='red', linestyle='-',  markersize=8, label='Loss Curve')
    ax[1].plot(score, color='blue', linestyle='-',  markersize=8, label='Reward Curve')

    ax[0].set_title('Training Loss Over Epoch')
    ax[0].set_xlabel('Epoch', fontsize=14)
    ax[0].set_ylabel('Loss', fontsize=14)

    ax[1].set_title('Training Reward Over Epoch')
    ax[1].set_xlabel('Epoch', fontsize=14)
    ax[1].set_ylabel('Reward', fontsize=14)

    ## 플로팅
    plt.show()


def f(col, df):
    result = []
    for data in df[col]:
        idx = data.find(':')
        res = float(data[idx+1:])
        result.append(res)
    return result


df = pd.read_csv('log.txt', sep=",")


df.columns = ['Epoch', 'Action_x', 'Action_y', 'Score', 'Tetrominoes', 'Cleared lines', 'Loss']
df = df[['Score', 'Loss']]

Score_list = f('Score', df)
Loss_list = f('Loss', df)

get_plot(Loss_list, Score_list)
