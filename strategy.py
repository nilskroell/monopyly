from gamestate import GameState
from player_controller import PlayerController
from player import Player

class Strategy():

    def __init__(self, player: Player, player_controller: PlayerController) -> None:
        self.player = player
        self.player_controller = player_controller

    def act(self, gamestate: GameState):
        self.player_controller.buy_property()