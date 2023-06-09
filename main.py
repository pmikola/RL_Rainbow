# SARSA(on-policy TD-LAMBDA) FOR AUTOMATIC LASER PARAMETERS SETTING
import random
import time

import numpy as np
import torch
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
from torch import optim

from agent import Agent
from dataset import DataSet
from game import Game
from valueFunction import ValueFunction
from neuralNetwork import Q_Network, Policy_Network

# device = 'cuda' if torch.cuda.is_available() else 'cpu'
# x = dataSet.decode_input(dataSet.create_input_set())
# y = dataSet.create_target(15)


no_of_actions = 256
num_e_bits = 5
num_m_bits = 10

no_of_states = 14 + 9  # + num_e_bits + num_m_bits
alpha = 0.0001
epsilon = 0.012
gamma = 0.99
tau = 0.01
no_of_games = 50
no_of_rounds = 9
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("DEVICE: ", device)
time.sleep(1)
dataset = DataSet(device)
torch.manual_seed(2023)
random.seed(2023)
np.random.seed(2023)
net = Q_Network(no_of_actions, no_of_states, device)
net2 = Policy_Network(no_of_actions, no_of_states, device)
net.to(device).requires_grad_(True)
net2.to(device).requires_grad_(True)
valueFunc = ValueFunction(alpha, epsilon, gamma, tau, device, no_of_actions, v_min=-no_of_games * no_of_rounds,
                          v_max=no_of_games * no_of_rounds)
agent = Agent(net, net2, valueFunc, no_of_states, num_e_bits, num_m_bits, device)
agent.BATCH_SIZE = 100

game = Game(valueFunc, agent, device, no_of_rounds)
game.game_cycles = 72
game.games = no_of_games
game.agent.exp_over = int((game.game_cycles - 12) / 2)
cmap = plt.cm.get_cmap('hsv', game.game_cycles + 5)
r_data = []
a_data = []
l_data = []
loss = []
p_pain = []
c_map_data = []
total_time = 0.
ax = plt.figure().gca()
game.task_id = 1.
for i in range(1, game.game_cycles + 1):
    game.cycle = i
    start = time.time()
    print("GAME CYCLE : ", i)
    rewards, a_val, losses,pains = game.playntrain(game, dataset, games=no_of_games)
    print("  REWARDS TOTAL : ", sum(rewards), " ||  RANDOM GUESSES: ",
          game.agent.no_of_guesses)
    end = time.time()
    t = end - start
    total_time += t
    print("  Elapsed time : ", t, " [s]")
    print("----------------------------------")
    if game.cycle >= int(game.agent.exp_over / 3):
        game.task_id = 0.
    if game.cycle >= int(game.agent.exp_over / 3) * 2:
        game.task_id = 2.
    if game.cycle >= game.agent.exp_over:
        game.task_id = 0.
    if game.cycle >= game.agent.exp_over + int(game.agent.exp_over / 3):
        game.task_id = 1.
    if game.cycle >= game.agent.exp_over + int(game.agent.exp_over / 3) * 2:
        game.task_id = 2.
    if game.cycle >= game.game_cycles - 12:
        game.task_id = 0.
        game.valueFunction.epsilon = 1.
    if game.cycle >= game.game_cycles - 8:
        game.task_id = 1.
        game.valueFunction.epsilon = 1.
    if game.cycle >= game.game_cycles - 4:
        game.task_id = 2.
        game.valueFunction.epsilon = 1.

    if game.cycle % 10 == 0:
        game.agent.counter_coef = 0
    game.agent.counter_coef += 1

    # game.net = net

    r_data.append(rewards)
    a_data.append(a_val)
    p_pain.append(pains)
    l_data.append("Epoch: " + str(i))
    c_map_data.append(cmap(i))
    loss.append(losses)

print("Total time : ", total_time / 60, "[min]")

ax.hist(r_data, alpha=0.65, stacked=False, histtype='bar', label=l_data, color=c_map_data)
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
ax.legend(prop={'size': 6}, loc='upper center', bbox_to_anchor=(0.5, 1.14),
          ncol=9, fancybox=True, shadow=True)

plt.xlabel("Reward value per game")
plt.ylabel("No. of games")
plt.grid()
plt.show()

ay = plt.figure().gca()

ay.hist(a_data, density=True, bins=40, alpha=0.65, stacked=True, histtype='stepfilled', label=l_data, color=c_map_data)
ay.legend(prop={'size': 6}, loc='upper center', bbox_to_anchor=(0.5, 1.14),
          ncol=9, fancybox=True, shadow=True)

plt.xlabel("Values per game")
plt.ylabel("No. of games")
plt.grid()
plt.show()

az = plt.figure().gca()
rewars_total = np.array(sum(r_data, [])) / no_of_rounds
az.plot(rewars_total)

plt.xlabel("No. Games")
plt.ylabel("Rewards")
plt.grid()
plt.show()

ba = plt.figure().gca()
loss_total = np.array(sum(loss, [])) / no_of_rounds
ba.plot(loss_total)

plt.xlabel("No. Games")
plt.ylabel("loss")
plt.grid()
plt.show()

bb = plt.figure().gca()
pain_total = np.array(sum(p_pain, [])) / no_of_rounds
bb.plot(pain_total)

plt.xlabel("No. Games")
plt.ylabel("Pain Level")
plt.grid()
plt.show()