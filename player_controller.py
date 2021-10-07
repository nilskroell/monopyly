from player import Player
from gamelogic import GameLogic
from playfields import Property, StreetField

import logging

class PlayerController():
    def __init__(self, player: Player, gamelogic: GameLogic) -> None:
        self.player = player
        self.gamelogic = gamelogic
    
    def buy_property(self) -> None:
        property = self.gamelogic.fields[self.player.position]

        if self.player is not self.gamelogic.active_player:
            logging.warn(f"Player {self.player.id} cannot buy property {property.position}: " +
                         f"Player {self.player.id} is not the active player. " +
                         f"(Player {self.gamelogic.active_player.id} is.)")
            return False

        if not isinstance(property, Property):
            logging.warn(f"Player {self.player.id} cannot buy property {property.position}: " +
                         f"Field {property.position} is not a property.")
            return False

        if property.owner:
            logging.warn(f"Player {self.player.id} cannot buy property {property.position}: " +
                         f"Already owned by {property.owner.id}.")
            return False
        
        if property.buying_price > self.player.balance:
            logging.warn(f"Player {self.player.id} cannot buy property {property.position}: " +
                         f"Player {self.player.id} has {self.player.balance} € cash, " +
                         f"but property {property.position} costs {property.buying_price} €")
            return False

        self.gamelogic.buy_property_from_bank(self.player, property)
        return True

    def mortagage_property(self, property: Property) -> bool:

        if not isinstance(property, Property):
            logging.warn(f"Player {self.player.id} cannot mortagage field {property.position}: " +
                       + f"field {property.position} is not a property.")
            return False

        if self.player is not property.owner:
            logging.warn(f"Player {self.player.id} cannot mortagage property {property.position}: " +
                         f"Player {self.player.id} is not the owner of {property.position}. " +
                         f"(Player {property.owner.id} is.)")
            return False

        if property.mortgaged:
            logging.warn(f"Player {self.player.id} cannot mortagage property {property.position}: " +
                         f"Property {property.position} is already mortagaged.")
            return False

        if isinstance(property, StreetField) and property.n_houses > 0:
            logging.warn(f"Player {self.player.id} cannot mortagage property {property.position}: " +
                            f"{property.n_houses} houses are still standing on property {property.position}.")
            return False

        self.gamelogic.mortgage_property(property)
        return True

    def demortagage_property(self, property: Property) -> bool:

        if not isinstance(property, Property):
            logging.warn(f"Player {self.player.id} cannot demortagage field {property.position}: " +
                       + f"field {property.position} is not a property.")
            return False

        if self.player is not property.owner:
            logging.warn(f"Player {self.player.id} cannot demortagage property {property.position}: " +
                         f"Player {self.player.id} is not the owner of {property.position}. " +
                         f"(Player {property.owner.id} is.)")
            return False

        if not property.mortgaged:
            logging.warn(f"Player {self.player.id} cannot demortagage property {property.position}: "
                         f"Property {property.position} is not mortagaged.")
            return False

        self.gamelogic.mortgage_property(property)
        return True

    def buy_n_houses_on_property(self, street: StreetField, n_houses_to_buy: int) -> bool:
        if not isinstance(street, StreetField):
            logging.warn(f"Player {self.player.id} cannot buy house/s on field {street.position}: " +
                         f"Field {street.position} is not a street.")
            return False

        if self.player is not street.owner:
            logging.warn(f"Player {self.player.id} cannot buy house/s on street {street.position}: " +
                         f"Player {self.player.id} is not the owner of {street.position}. " +
                         f"(Player {street.owner.id} is.)")
            return False

        if street.mortgaged:
            logging.warn(f"Player {self.player.id} cannot buy house/s on street {street.position}: " +
                         f"Street {street.position} is mortagaged.")
            return False

        if not isinstance(n_houses_to_buy, int):
            logging.warn(f"Player {self.player.id} cannot buy house/s on street {street.position}: " +
                         f"{n_houses_to_buy} is not an integer ().")
            return False
        
        if n_houses_to_buy <= 0:
            logging.warn(f"Player {self.player.id} cannot buy house/s on street {street.position}: " +
                         f"{n_houses_to_buy} is negative or zero.")
            return False

        n_houses_after_transaction = street.n_houses + n_houses_to_buy
        if n_houses_after_transaction > street.max_n_houses_per_street:
            logging.warn(f"Player {self.player.id} cannot buy {n_houses_to_buy} house/s on street {street.position}: " +
                         f"Maximum number of houses ({street.max_n_houses_per_street}) would be exceeded " +
                         f"after transaction ({n_houses_after_transaction})")
            return False

        n_total_houses_after_transaction = self.gamelogic.n_total_houses - n_houses_to_buy
        if n_total_houses_after_transaction <= 0:
            logging.warn(f"Player {self.player.id} cannot buy {n_houses_to_buy} house/s on street {street.position}: " +
                         f"Not enough houses in the bank (currently {self.gamelogic.n_total_houses}).")
            return False

        self.gamelogic.buy_n_houses_on_streetfield(self.player, street, n_houses_to_buy)
        return True

        
            

    # buy house(s)

    # sell house(s)

    # propose_trade?

    # accept_trade?

    # refuse_trade?