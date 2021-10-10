from gamestate import GameState
from player_controller import PlayerController
from player import Player
from tradeoffer import TradeOffer

class Strategy():

    def __init__(self, player: Player, player_controller: PlayerController) -> None:
        self.player = player
        self.player_controller = player_controller
        self.id = self.player.id

    def act(self, gamestate: GameState):
        self.player_controller.buy_property()
        self.player_controller.buy_n_houses(gamestate.fields[self.player.position], 1)
        self.player_controller.mortagage_property(gamestate.fields[self.player.position])

    def evaluate_tradeoffer(self, offer: TradeOffer, proposing_player: Player, gamestate: GameState) -> TradeOffer:
        # None to reject, TradeOffer to deal
        return None

    def decide_on_counteroffer(targeted_trading_partner, offer, counteroffer) -> bool:
        # True: accept, False: reject
        return True