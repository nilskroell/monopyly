from numpy.lib.arraysetops import unique
from gamestate import GameState
from playfields import Property, StreetField, StartField
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
START_BALANCE = 1500
PASS_GO_INCOME = 200

N_ROUNDS = 1000

# INITIALIZE GAME
# Initialize players
players = [Player(id=i, start_balance=START_BALANCE, position=0) for i in range(N_PLAYERS)]


# Initialize fields
colors = np.arange(10)
n_fields = np.tile([2, 3], 5)
buying_prices = np.arange(60, 160, 10)
house_prices = (0.5 * buying_prices).astype(int)
base_rents = (0.1 * buying_prices).astype(int)
n_dice = 2
n_dicefaces = 6

my_fields = [StartField(position=0)]
pos = 1
for (color, buying_price, base_rent, house_price, n) in zip(colors, buying_prices, base_rents, house_prices, n_fields):
    for i in range(n):
        my_fields.append(StreetField(position=pos,
                                     color=color,
                                     buying_price=buying_price,
                                     base_rent=base_rent,
                                     house_price=house_price))
        pos += 1

# Initialize gamelogic
gamestate = GameState(players=players, fields=my_fields, pass_go_income=PASS_GO_INCOME, n_dice=n_dice, n_dicefaces=n_dicefaces)
gamelogic = GameLogic(gamestate=gamestate)

# Shuffle player sequence
random.shuffle(players)

# Initialize player controllers
player_controllers = [PlayerController(player=p, gamestate=gamestate, gamelogic=gamelogic) for p in players]

# initialize strategies
strategies = [Strategy(player=player, player_controller=player_controller) for (player, player_controller) in zip(players, player_controllers)]

# START GAME

for i in range(N_ROUNDS):
    for j, player in enumerate(players):
        print(f"Balance player {player.id}: {player.balance} €")

        player_controller = player_controllers[j]

        logging.debug(f">>> Player {player.id}'s turn:")
        if not player.alive:
            logging.info(f"Player {player.id} is dead: SKIP")
            continue
        gamelogic.set_active_player(player)
        n_dots, pasch = gamelogic.roll_dice()
        gamelogic.move_player_forward(player, n_dots)
        strategies[j].act(gamestate)
        gamelogic.process_player_position(player)

        print(f"Balance player {player.id}: {player.balance} €")
        print("")

print("END")

for player in players:
    print(f"Player {player.id}: {player.alive} ({player.balance} €)")

for field in gamestate.fields:
    if isinstance(field, Property):
        print(f"Field {field.position}: Owner: {('P' + str(field.owner.id)) if field.owner else 'none'}, Monopoly: {field.monopoly}, Mortaged: {field.mortgaged}")

