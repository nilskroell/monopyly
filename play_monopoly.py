from actioncard import ActionCard
from gamestate import GameState
from playfields import ActionField, Property, StreetField, StartField, TaxField
from gamelogic import GameLogic
from player import Player
from player_controller import PlayerController
from trading_platform import TradingPlatform
import io_utils

import random
import logging
from pathlib import Path
import importlib.util
from pathlib import Path

import numpy as np



logging.basicConfig(level=logging.INFO, format='%(message)s')

def read_strategy_classes(foldername, shuffle=False):
    filenames = io_utils.get_list_of_all_files(foldername, ".py")
    if shuffle:
        random.shuffle(filenames)
    strategy_classes = []
    for filename in filenames:
        s = read_class_from_file(filename)
        strategy_classes.append(s)

    return strategy_classes

def print_player_update(players):
    print(f"n = {len(players)} in the game.")
    for player in players:
        print(f"Player {player.id}: {player.alive} ({player.balance} €)")

def read_class_from_file(fullfilename: Path):
    spec = importlib.util.spec_from_file_location(fullfilename.stem, fullfilename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Strategy

# USER DEFINED GAME PARAMETERS

START_BALANCE = 1500
PASS_GO_INCOME = 20

PRINT_END_RESULTS = False

# INITIALIZE GAME
# read strategies
strategy_classes = read_strategy_classes(Path("./strategies"))
n_strategies = len(strategy_classes)
# Initialize players
players = [Player(start_balance=START_BALANCE, position=0)
           for i in range(n_strategies)]

strategies = []

# Initialize fields
colors = np.arange(10)
n_fields = np.tile([2, 3], 5)
buying_prices = np.arange(60, 160, 10)
house_prices = (0.5 * buying_prices).astype(int)
base_rents = (0.3 * buying_prices).astype(int)
n_dice = 2
n_dicefaces = 6

MAX_ROUNDS = 1000

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

# Initialize player controllers
player_controllers = [PlayerController(
    player=p, gamestate=gamestate, gamelogic=gamelogic) for p in players]

strategies = [s(player=player, player_controller=player_controller) for s, player, player_controller in zip(strategy_classes, players, player_controllers)]

# initialize trading platform
trading_platform = TradingPlatform(gamelogic=gamelogic, strategies=strategies)

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

        # trading
        trading_platform.invite_player_to_trade(player)

        print(n_living_players(players))

        print("")
        
    print_player_update(players)
    n_rounds_played += 1
    if n_rounds_played > MAX_ROUNDS:
        break

print(f"END: Game ends after {n_rounds_played} rounds.")

if PRINT_END_RESULTS:
    print_player_update(players)

    for field in gamestate.fields:
        s = f"Field {field.position}: "
        if isinstance(field, Property):
            s += f"Owner: {('P' + str(field.owner.id)) if field.owner else 'none'}, Color: {field.color}, Monopoly: {field.monopoly}, Mortaged: {field.mortgaged}, "
        if isinstance(field, StreetField):
            s += f"Houses: {field.n_houses}"

        print(s)