from gamestate import GameState
from player_controller import PlayerController
from player import Player
from tradeoffer import TradeOffer

import numpy as np

class Strategy():

    def __init__(self, player: Player, player_controller: PlayerController) -> None:
        self.player = player
        self.player_controller = player_controller
        self.id = self.player.id

    def act(self, gamestate: GameState):
        self.player_controller.buy_property()
        self.player_controller.buy_n_houses(gamestate.fields[self.player.position], 1)
        self.player_controller.mortagage_property(gamestate.fields[self.player.position])

    def initiate_trade(self, gamestate: GameState) -> tuple:
        target_partners = gamestate.players
        own_properties = self.player_controller.get_properties_owned_by_player(self.player)
        if len(own_properties) == 0:
            sel_properties = None
        else:
            sel_idx = np.random.randint(len(own_properties), size=1)[0]
            sel_properties = own_properties[sel_idx]
        offer = TradeOffer(properties=[sel_properties], money=0)
        return offer, target_partners

    def evaluate_tradeoffer(self, offer: TradeOffer, proposing_player: Player, gamestate: GameState) -> TradeOffer | None:
        # None to reject, TradeOffer to deal
        return None

    def decide_on_counteroffer(self, targeted_trading_partner, offer, counteroffer) -> bool:
        # True: accept, False: reject
        return True
