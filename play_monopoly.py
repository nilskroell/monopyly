from actioncard import ActionCard
from gamestate import GameState
from playfields import ActionField, Property, StreetField, StartField, TaxField
from gamelogic import GameLogic
from player import Player
from player_controller import PlayerController

import random
import logging

import numpy as np

from strategy import Strategy

logging.basicConfig(level=logging.INFO, format='%(message)s')


# USER DEFINED GAME PARAMETERS
N_PLAYERS = 3
START_BALANCE = 1500
PASS_GO_INCOME = 20

# INITIALIZE GAME
# Initialize players
players = [Player(id=i, start_balance=START_BALANCE, position=0)
           for i in range(N_PLAYERS)]


# Initialize fields
colors = np.arange(10)
n_fields = np.tile([2, 3], 5)
buying_prices = np.arange(60, 160, 10)
house_prices = (0.5 * buying_prices).astype(int)
base_rents = (0.3 * buying_prices).astype(int)
n_dice = 2
n_dicefaces = 6

fields = [StartField()]
fields.append(TaxField(tax=100))

actioncards = [ActionCard(teleport_position=0),
               ActionCard(n_steps_forward=1),
               ActionCard(n_steps_backward=1),
               ActionCard(money_to_pay=25),
               ActionCard(money_to_get=100),
               ActionCard(money_to_pay_per_house=10)]

fields.append(ActionField(actioncards=actioncards))

for (color, buying_price, base_rent, house_price, n) in zip(colors, buying_prices, base_rents, house_prices, n_fields):
    for i in range(n):
        fields.append(StreetField(color=color,
                                  buying_price=buying_price,
                                  base_rent=base_rent,
                                  house_price=house_price))

# Initialize gamelogic
gamestate = GameState(players=players,
                      fields=fields,
                      pass_go_income=PASS_GO_INCOME,
                      n_dice=n_dice,
                      n_dicefaces=n_dicefaces)
gamelogic = GameLogic(gamestate=gamestate)

# Shuffle player sequence
random.shuffle(players)

# Initialize player controllers
player_controllers = [PlayerController(
    player=p, gamestate=gamestate, gamelogic=gamelogic) for p in players]

# initialize strategies
strategies = [Strategy(player=player, player_controller=player_controller) for (
    player, player_controller) in zip(players, player_controllers)]

# START GAME


def n_living_players(players: list) -> int:
    count = 0
    for player in players:
        if player.alive:
            count += 1
    return count


n_rounds_played = 0
while n_living_players(players) > 1:
    for j, player in enumerate(players):
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
        print("")
    n_rounds_played += 1
    if n_rounds_played > 10:
        break

print(f"END after {n_rounds_played}")

for player in players:
    print(f"Player {player.id}: {player.alive} ({player.balance} €)")

for field in gamestate.fields:
    s = f"Field {field.position}: "
    if isinstance(field, Property):
        s += f"Owner: {('P' + str(field.owner.id)) if field.owner else 'none'}, Color: {field.color}, Monopoly: {field.monopoly}, Mortaged: {field.mortgaged}, "
    if isinstance(field, StreetField):
        s += f"Houses: {field.n_houses}"

    print(s)
