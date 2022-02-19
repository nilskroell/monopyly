import logging

#from strategy import Strategy
from tradeoffer import TradeOffer
from player import Player
from gamelogic import GameLogic

class TradingPlatform():
    def __init__(self, gamelogic: GameLogic, strategies: list) -> None:
        self.gamelogic = gamelogic
        self.strategies = strategies

    def invite_player_to_trade(self, player: Player) -> None:
        strategy = self.strategies[player.id]
        offer, targeted_players = strategy.initiate_trade(self.gamelogic.gamestate)

        if offer is None or targeted_players is None:
            logging.debug(f"Player {player.id} places no trade initialization.")
            return
        if len(targeted_players) == 0:
            logging.debug(f"Player {player.id} places no valid initialization.")
            return

        self.process_tradeoffer(player, offer, targeted_players)


    def process_tradeoffer(self, proposing_player: Player, offer: TradeOffer, targeted_trading_players: list) -> bool:
        logging.info(f"Processing trade offer from Player {proposing_player.id}")
        proposing_strategy = self.strategies[proposing_player.id]

        # check if trade offer is valid
        if not self.check_if_valid_tradeoffer(proposing_player, offer, targeted_trading_players):
            logging.debug(f"Trade offer from Player {proposing_player.id} is not valid.")
            return False

        logging.debug(f"Trade offer from Player {proposing_player.id} is valid.")

        # send offer to trading partners
        for targeted_trading_player in targeted_trading_players:
            if targeted_trading_player is proposing_player:
                print(f"SKIP player {targeted_trading_player.id}.")
                continue
            targeted_trading_strategy = self.strategies[targeted_trading_player.id]
            counteroffer = self.send_offer_to_trading_partner(targeted_trading_strategy,
                                                              offer,
                                                              proposing_player)
            if counteroffer:
                decision = proposing_strategy.decide_on_counteroffer(targeted_trading_strategy,
                                                                     offer,
                                                                     counteroffer)
                if decision is True:
                    self.carryout_trade(proposing_player,
                                        targeted_trading_player,
                                        offer,
                                        counteroffer)
                    return True
                else:
                    continue
        return False

    def send_offer_to_trading_partner(self,
                                      targeted_trading_strategy,
                                      offer: TradeOffer,
                                      proposing_player: Player) -> TradeOffer:
        logging.debug(f"Sending trade offer from Player {proposing_player.id} to Player {targeted_trading_strategy.id}.")
        counteroffer = targeted_trading_strategy.evaluate_tradeoffer(offer,
                                                                     proposing_player,
                                                                     self.gamelogic.gamestate)

        # preprocess counteroffers (no gifts)
        if counteroffer:
            if counteroffer.money == 0 and len(counteroffer.properties) == 0:
                counteroffer = None

        return counteroffer

    def carryout_trade(self,
                       proposing_player: Player,
                       tradepartner: Player,
                       offer: TradeOffer,
                       counteroffer: TradeOffer) -> None:

        # transfer properties
        for property in offer.properties:
            self.gamelogic.change_property_owner(property, tradepartner)

        for property in counteroffer.properties:
            self.gamelogic.change_property_owner(property, proposing_player)

        # transfer money
        money_to_send = offer.money - counteroffer.money
        self.gamelogic.transfer_money_from_a_to_b(proposing_player,
                                                  tradepartner,
                                                  money_to_send)

    def check_if_valid_tradeoffer(self, proposing_player, offer: TradeOffer, targeted_trading_players: list) -> bool:
        if not isinstance(offer, TradeOffer):
            logging.warn(f"Trade offer from Strategy {proposing_player.id} invalid: " +
                         f"Offer is no TradeOffer.")
            return False

        if not (targeted_trading_players, list):
            logging.warn(f"Trade offer from Strategy {proposing_player.id} invalid: " +
                         f"Players is not a list.")
            return False

        if not self.is_list_of_valid_players(targeted_trading_players):
            logging.warn(f"Trade offer from Strategy {proposing_player.id} invalid: " +
                         f"List of targeted trading partners contains invalid or dead players.")
            return False

        return True

    @staticmethod
    def is_list_of_valid_players(players: list) -> bool:
        for player in players:
            if isinstance(player, Player):
                if not player.alive:
                    return False
            else:
                return False
        return True
