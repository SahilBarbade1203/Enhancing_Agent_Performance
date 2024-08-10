# -*- coding: utf-8 -*-
"""train.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18w1d0l06RSz46cTdXZTg8hS4RzQUfsWY
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline

import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset,DataLoader
import torch.optim as optim

import yfinance as yf
from collections import deque
import random
import math
from tqdm import tqdm

dataset_dir = "/content/drive/MyDrive/Deep_RL_for_Stock_Trading"

# Define the ticker symbol for NIFTY50
nifty50_ticker = "^NSEI"

# Download the historical data for NIFTY50
nifty50_data = yf.download(nifty50_ticker, start="2010-01-01", end="2019-08-08")

plt.plot(nifty50_data['Close'])
plt.show()

file_name = f"{dataset_dir}/data.csv"

# Save the DataFrame to a CSV file
nifty50_data.to_csv(file_name, index=False)

print(f"File Saved at {file_name}")

#Data Cleaning and EDA
null_values = nifty50_data.isna().values.any()
print(f"Presence of Null value : {int(null_values)}")

if null_values:
  nifty50_data = nifty50_data.fillna(method = "ffill")

#data splitting in 80-20% fashion for training and testing
X=list(nifty50_data["Close"])
data=[float(x) for x in X]
test_size = 0.2

train_data = data[:int(len(data)*(1-test_size))]
test_data = data[int(len(data)*(1-test_size)):]

print(f"Training Data shape : {len(train_data)} and Testing Data Shape : {len(test_data)}")

#training agents (note : replace DQN with required agent names)
#hyperparameters and agent,state intialization
window_size = 10
agent = DQN_Agent(window_size)
data = train_data  # Assuming train_data is defined somewhere
episode_count = 10
l = len(data) - 1
batch_size = 32

losses = []
profits = []

for e in range(episode_count):
    print(f"Running episode {e + 1}/{episode_count}")
    state = getState(data, 0, window_size + 1)
    total_profit = 0
    agent_inventory = []
    states_sell = []
    states_buy = []

    for t in range(l):
        action = agent.act(state)
        next_state = getState(data, t + 1, window_size + 1)
        reward = 0

        if action == 1:  # buy
            agent_inventory.append(data[t])
            states_buy.append(t)

        elif action == 2 and len(agent_inventory) > 0:  # sell
            bought_price = agent_inventory.pop(0)
            reward = max(data[t] - bought_price, 0)
            total_profit += data[t] - bought_price
            states_sell.append(t)

        done = t == l - 1
        agent.remember(state, action, reward, next_state, done)
        state = next_state

        if done:
            print("--------------------------------")
            print(f"Total Profit: {total_profit:.2f}")
            profits.append(total_profit)
            print("--------------------------------")

            plot_behavior(data, states_buy, states_sell, total_profit)

        if len(agent.memory) > batch_size:
            loss = agent.experience_replay(batch_size)
            losses.append(loss)

    if e % 2 == 0:
        torch.save(agent.model.state_dict(), f"{dataset_dir}/model_ep{e}.pth")