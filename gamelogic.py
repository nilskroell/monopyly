from actioncard import ActionCard
from gamestate import GameState
from player import Player
from playfields import ActionField, NonProperty, Property, StreetField, TaxField
import utils

import logging
import numpy as np


class GameLogic():
    def __init__(self, gamestate: GameState) -> None:
        self.gamestate = gamestate

    def set_active_player(self, current_player) -> None:
        self.gamestate.active_player = current_player

    # Basic stuff
    def roll_dice(self) -> tuple:
        dice = utils.throw_n_dice(
            n_dice=self.gamestate.n_dice, n_dicefaces=self.gamestate.n_dicefaces)
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
        elif isinstance(field, TaxField):
            self.pay_taxes(player, field)
        elif isinstance(field, ActionField):
            self.process_actionfield(field, player)
        else:
            pass

    def pay_taxes(self, player: Player, taxfield: TaxField) -> None:
        logging.info(f"Player {player.id} pays {taxfield.tax} € taxes on field {taxfield.position}")
        self.decrease_player_balance(player, taxfield.tax, creditor=None)

    def calc_rent(self, property: Property) -> int:
        if property.monopoly:
            if isinstance(property, StreetField):
                if property.n_houses == 0:
                    return int(property.base_rent * self.gamestate.monopoly_factor)
                else:
                    return int(property.base_rent * property.rent_factors[property.n_houses - 1])
            else:
                return int(property.base_rent * self.gamestate.monopoly_factor)
        else:
            return property.base_rent

        # TODO: Trainstation, Utility

    def process_actionfield(self, actionfield: ActionField, player: Player):
        actioncard = self.draw_actioncard(actionfield)

        if actioncard.teleport_position:
            self.move_player_forward_to_position(player, actioncard.teleport_position)

        if actioncard.n_steps_forward > 0:
            self.move_player_forward(player, actioncard.n_steps_forward)

        if actioncard.n_steps_backward > 0:
            self.move_player_backward(player, actioncard.n_steps_backward)

        if actioncard.money_to_pay > 0:
            self.decrease_player_balance(player, actioncard.money_to_pay, creditor=None)

        if actioncard.money_to_get > 0:
            self.increase_player_balance(player, actioncard.money_to_get)    

        if actioncard.money_to_pay_per_house > 0:
            n_houses_player = self.determine_n_house_owned_by_player(player)
            amount_to_pay = actioncard.money_to_pay_per_house * n_houses_player
            self.decrease_player_balance(player, amount_to_pay, creditor=None)

    @staticmethod
    def draw_actioncard(actionfield: ActionField) -> ActionCard:
        actioncard = actionfield.actioncards[0]

        # Logging string        
        s = ""
        if actioncard.teleport_position:
            s += f"teleport to position {actioncard.teleport_position},"
        if actioncard.n_steps_forward > 0:
            s += f"move {actioncard.n_steps_forward} step(s) forward,"
        if actioncard.n_steps_backward > 0:
            s += f"move {actioncard.n_steps_backward} step(s) backward,"
        if actioncard.money_to_pay > 0:
            s += f"pay {actioncard.money_to_pay} €,"
        if actioncard.money_to_get > 0:
            s += f"get {actioncard.money_to_get} €,"
        if actioncard.money_to_pay_per_house > 0:
            s += f"pay {actioncard.money_to_pay_per_house} € per house"
        
        if len(s) == 0:
            s = "-"
        else:
            s = s[0:-1] + "."

        logging.info(f"Draw actioncard: {s}")

        # move actioncard to bottom of pile
        actionfield.actioncards.append(actionfield.actioncards.pop(0))
        return actioncard

    def determine_n_house_owned_by_player(self, player: Player) -> int:
        owned_properties = self.get_properties_owned_by_player(player)
        total_n_house_owned = 0
        for property in owned_properties:
            if isinstance(property, StreetField):
                total_n_house_owned += property.n_houses

        return total_n_house_owned

    def get_properties_owned_by_player(self, player: Player) -> list:
        owned_properties = []
        for field in self.gamestate.fields:
            if isinstance(field, Property):
                if field.owner is player:
                    owned_properties.append(field)

        return owned_properties

    def update_monopoly(self, color: int) -> None:
        property_positions = self.gamestate.streetcolor_position_map[color]

        monopoly_flag = self.check_monopoly(property_positions)

        logging.debug(f"Monopoly check of color {color}: {monopoly_flag}")

        for pos in property_positions:
            self.gamestate.fields[pos].monopoly = monopoly_flag
            logging.debug(f"Monopoly status of field {pos} "
                          + f"changed to {monopoly_flag}")

    def check_monopoly(self, property_positions) -> bool:
        first_owner = self.gamestate.fields[property_positions[0]].owner

        if first_owner is None:
            return False

        for pos in property_positions[1::]:
            if first_owner is not self.gamestate.fields[pos].owner:
                return False

        return True

    def max_diff_n_houses_is_valid(self, street_of_interest: StreetField, delta_n_houses: int) -> bool:
        color = street_of_interest.color
        property_positions = self.gamestate.streetcolor_position_map[color]

        n_houses_street = []
        for pos in property_positions:
            if pos == street_of_interest.position:
                n_houses = street_of_interest.n_houses + delta_n_houses
            else:
                n_houses = self.gamestate.fields[pos].n_houses

            n_houses_street.append(n_houses)

        if (max(n_houses_street) - min(n_houses_street)) <= self.gamestate.max_diff_n_houses:
            return True
        else:
            return False

    # Player balance
    def increase_player_balance(self, player: Player, amount: int) -> None:
        assert amount >= 0
        player.balance += amount

    def decrease_player_balance(self, player: Player, amount: int, creditor) -> None:
        assert amount >= 0
        player.balance -= amount
        self.check_player_lifestatus(player, creditor)

    def check_player_lifestatus(self, player: Player, creditor) -> None:
        if player.balance < 0:
            self.kill_player(player, creditor)

    def kill_player(self, player: Player, creditor) -> None:
        player.alive = False
        for field in self.gamestate.fields:
            if isinstance(field, Property) and field.owner is player:
                field.owner = creditor
                if isinstance(field, StreetField):
                    self.sell_n_houses_on_streetfield(creditor,
                                                      field,
                                                      field.n_houses)

    def transfer_money_from_a_to_b(self, player_a: Player, player_b: Player, amount: int) -> None:
        logging.info(f"Transfer {amount} € from Player {player_a.id} " +
                     f"to Player {player_b.id}.")
        self.decrease_player_balance(player_a, amount, creditor=player_b)
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

        logging.debug(f"Move Player {player.id} from position {player.position} "
                      + f"to position {target_position}.")
        player.position = target_position

    def move_player_backward(self, player: Player, n_steps: int) -> None:
        target_position = player.position - n_steps
        if target_position < 0:
            target_position = target_position % self.gamestate.board_length

        logging.debug(f"Move Player {player.id} from position {player.position} " +
                      f"to position {target_position}.")
        player.position = (player.position -
                           n_steps) % self.gamestate.board_length

    def move_player_forward_to_position(self, player: Player, target_position: int) -> None:
        n_steps = target_position - player.position
        if n_steps < 0:
            n_steps += self.gamestate.board_length

        self.move_player_forward(player, n_steps)

    # Property
    def change_property_owner(self, property: Property, new_owner):
        logging.info(f"Change ownership of property {property.position} from " +
                     f"{('Player ' + str(property.owner.id)) if property.owner else 'the bank'}" +
                     f" to Player {new_owner.id}.")
        property.owner = new_owner
        self.update_monopoly(property.color)

    def buy_property_from_bank(self, player: Player, property: Property):
        logging.info(f"Player {player.id} buys property {property.position} " +
                     f"from bank for {property.buying_price} €.")
        self.change_property_owner(property, player)
        self.decrease_player_balance(
            player, property.buying_price, creditor=None)

    def buy_n_houses_on_streetfield(self, player: Player, street: StreetField, n_houses_to_buy: int):
        total_price_to_pay = n_houses_to_buy * street.house_price
        logging.info(f"Player {player.id} buys {n_houses_to_buy} " +
                     f"on street {street.position}.")
        self.decrease_player_balance(player, total_price_to_pay, creditor=None)
        street.n_houses += n_houses_to_buy
        self.gamestate.n_total_houses -= n_houses_to_buy

    def sell_n_houses_on_streetfield(self, player, street: StreetField, n_houses_to_sell: int):
        if player:
            total_amount_to_get_back = int(self.gamestate.buyback_quota *
                                        n_houses_to_sell * street.house_price)
            logging.info(f"Player {player.id} sells {n_houses_to_sell} on " +
                        f"street {street.position} back to bank.")
            self.increase_player_balance(player, total_amount_to_get_back)
            street.n_houses -= n_houses_to_sell
            self.gamestate.n_total_houses += n_houses_to_sell
        else:
            logging.info(f"{n_houses_to_sell} houses transfered from street to bank due to.")
            street.n_houses -= n_houses_to_sell
            self.gamestate.n_total_houses += n_houses_to_sell


    # Mortagage
    def mortgage_property(self, property: Property):
        if property.owner:
            logging.info(f"Mortgaged property {property.position} " +
                         f"for {property.mortagage_value} €.")
            self.increase_player_balance(property.owner,
                                         property.mortagage_value)
            property.mortgaged = True

    def demortgage_property(self, property: Property):
        if property.owner:
            logging.info(f"Demortgaged property {property.position} " +
                         f"for {property.mortagage_value} €.")
            self.decrease_player_balance(property.owner,
                                         property.mortagage_value,
                                         creditor=None)
            property.mortgaged = False
