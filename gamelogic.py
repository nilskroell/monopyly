from gamestate import GameState
from player import Player
from playfields import NonProperty, Property, StreetField
import utils

import logging
import numpy as np


class GameLogic():
    def __init__(self, gamestate: GameState) -> None:
        self.gamestate = gamestate

    def set_active_player(self, current_player: Player) -> None:
        self.gamestate.active_player = current_player

    # Basic stuff
    def roll_dice(self) -> tuple:
        dice = utils.throw_n_dice(n_dice=self.gamestate.n_dice, n_dicefaces=self.gamestate.n_dicefaces)
        n_dots = np.sum(dice)
        pasch = np.min(dice) == np.max(dice)

        logging.debug(f"Alea iacta est: {dice} {'(pasch)' if pasch else ''}")

        return n_dots, pasch


    def process_player_position(self, player: Player) -> None:
        field = self.gamestate.fields[player.position]
        if isinstance(field, Property):
            if field.mortgaged:
                return
            else:
                if field.owner is None:
                    return
                elif field.owner is player:
                    return
                else:
                    rent = self.calc_rent(field)
                    self.transfer_money_from_a_to_b(player, field.owner, rent)
        elif isinstance(field, NonProperty):
            pass


    def throw_and_go(self, player: Player) -> None: # in main loop
        n_dots, pasch = self.roll_dice()
        self.move_player_forward(player, n_dots)
        # TODO: wait for strategy input
        self.process_player_position(player)

        # TODO: wait for strategy input
        
        if pasch:
            # TODO: throw_and_go again
            pass

    @staticmethod
    def calc_rent(property: Property):
        # TODO
        return property.base_rent
    
    # Player balance
    @staticmethod
    def increase_player_balance(player: Player, amount: int) -> None:
        assert amount >= 0
        player.balance +=  amount

    def decrease_player_balance(self, player: Player, amount: int) -> None:
        assert amount >= 0
        player.balance -= amount
        self.check_player_lifestatus(player)

    @staticmethod
    def check_player_lifestatus(player: Player) -> None:
        if player.balance < 0:
            player.alive = False


    def transfer_money_from_a_to_b(self, player_a: Player, player_b: Player, amount: int) -> None:
        # TODO: What if balance of player_a is not enough?
        logging.info(f"Transfer {amount} € from Player {player_a.id} to Player {player_b.id}.")
        self.decrease_player_balance(player_a, amount)
        self.increase_player_balance(player_b, amount)

    def pass_go(self, player: Player) -> None:
        logging.info(f"Player {player.id} has passed GO.")
        self.increase_player_balance(player, self.gamestate.pass_go_income)

    # Player movement
    def move_player_forward(self, player: Player, n_steps: int) -> None:
        target_position = player.position + n_steps

        while target_position >= self.gamestate.board_length:
            target_position = target_position - self.gamestate.board_length
            self.pass_go(player)
           
        logging.debug(f"Move Player {player.id} from position {player.position} to position {target_position}.")
        player.position = target_position
        
    def move_player_backward(self, player: Player, n_steps: int) -> None:
        target_position = player.position - n_steps
        if target_position < 0:
            target_position = target_position % self.gamestate.board_length

        logging.debug(f"Move Player {player.id} from position {player.position} to position {target_position}.")
        player.position = (player.position - n_steps) % self.gamestate.board_length

    def move_player_forward_to_position(self, player: Player, target_position: int) -> None:
        n_steps = target_position - player.position
        if n_steps < 0:
            n_steps += self.gamestate.board_length
        
        self.move_player_forward(player, n_steps)


    # Property
    @staticmethod
    def change_property_owner(property: Property, new_owner: Player):
        logging.info(f"Change ownership of property {property.position} from " +
                     f"{('Player ' + property.owner.id) if property.owner else 'the bank'}" +
                     " to Player {new_owner.id}.")
        property.owner = new_owner

    def buy_property_from_bank(self, player: Player, property: Property):
        logging.info(f"Player {player.id} buys property {property.position} from bank for {property.buying_price} €.")
        self.change_property_owner(property, player)
        self.decrease_player_balance(player, property.buying_price)

    def buy_n_houses_on_streetfield(self, player: Player, street: StreetField, n_houses_to_buy: int):
        total_price_to_pay = n_houses_to_buy * street.house_price
        logging.info(f"Player {player.id} buys {n_houses_to_buy} on street {street.position}.")
        self.decrease_player_balance(player, total_price_to_pay)
        street.n_houses += n_houses_to_buy
        self.gamestate.n_total_houses -= n_houses_to_buy
        
    def sell_n_houses_on_streetfield(self, player: Player, street: StreetField, n_houses_to_sell: int):
        total_amount_to_get_back = self.gamestate.buyback_quota * n_houses_to_sell * street.house_price
        logging.info(f"Player {player.id} sells {n_houses_to_sell} on street {street.position} back to bank.")
        self.increase_player_balance(player, total_amount_to_get_back)
        street.n_houses -= n_houses_to_sell
        self.gamestate.n_total_houses += n_houses_to_sell

    # Mortagage
    def mortgage_property(self, property: Property):
        logging.info(f"Mortgaged property {property.position} for {property.mortagage_value} €.")
        self.increase_player_balance(property.owner, property.mortagage_value)
        property.mortgaged = True


    def demortgage_property(self, property: Property):
        logging.info(f"Demortgaged property {property.position} for {property.mortagage_value} €.")
        self.decrease_player_balance(property.owner, property.mortagage_value)
        property.mortgaged = False