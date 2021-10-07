from playfields import StreetField, StartField
from gamelogic import GameLogic
from player import Player
from player_controller import PlayerController

import random
import logging

import numpy as np
import matplotlib.pyplot as plt

from strategy import Strategy

logging.basicConfig(level=logging.DEBUG, format='%(message)s')


# USER DEFINED GAME PARAMETERS
N_PLAYERS = 10
START_BALANCE = 500
PASS_GO_INCOME = 0

N_ROUNDS = 100

# INITIALIZE GAME
# Initialize players
players = [Player(id=i, start_balance=START_BALANCE, position=0) for i in range(N_PLAYERS)]



# Initialize fields

colors = np.arange(10)
n_fields = np.repeat([2, 3], repeats=5)
buying_prices = np.arange(60, 160, 10)
house_prices = (0.5 * buying_prices).astype(int)

my_fields = [StartField(position=0)]
pos = 1
for (color, buying_price, house_price, n) in zip(colors, buying_prices, house_prices, n_fields):
    for i in range(n):
        my_fields.append(StreetField(position=pos, color=color, buying_price=buying_price, house_price=house_price))
        pos += 1

print(len(my_fields))
# Initialize gamelogic
my_gamelogic = GameLogic(players=players, fields=my_fields, pass_go_income=PASS_GO_INCOME)


# Shuffle player sequence
random.shuffle(players)

# Initialize player controllers
player_controllers = [PlayerController(player=p, gamelogic=my_gamelogic) for p in players]

# initialize strategies
strategies = [Strategy(player=p, player_controller=pc) for (p, pc) in zip(players, player_controllers)]

# START GAME

for i in range(N_ROUNDS):
    for j, player in enumerate(players):
        print(f"Balance player {player.id}: {player.balance} €")

        player_controller = player_controllers[j]

        logging.debug(f">>> Player {player.id}'s turn:")
        if not player.alive:
            logging.info(f"Player {player.id} is dead: SKIP")
        my_gamelogic.set_active_player(player)
        n_dots, pasch = my_gamelogic.roll_dice()
        my_gamelogic.move_player_forward(player, n_dots)
        strategies[j].act()
        my_gamelogic.process_player_position(player)

        print(f"Balance player {player.id}: {player.balance} €")
        print("")

print("END")

for player in players:
    print(f"Player {player.id}: {player.alive}")


