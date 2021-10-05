import numpy as np

from player import Player

class Property():
    def __init__(self) -> None:
        self.owner_id = None

class StreetField(Property):
    def __init__(self, color: str, value: int, houseprice: int) -> None:
        super().__init__()
        self.color = color
        self.value = value
        self.houseprice = houseprice

        self.n_houses = 0
        self.n_hotels = 0

        self.mortgaged = False

    def calc_rent(self) -> int:
        # TODO
        raise NotImplementedError()

    def acquire(self, player: Player) -> None:
        self.owner_id = player.owner_id
        

class TrainstationField(Property):
    def __init__(self) -> None:
        super().__init__()

    def calc_rent(self) -> int:
        # TODO
        raise NotImplementedError()


class PowerplantField(Property):
    def __init__(self) -> None:
        super().__init__()

    def calc_rent(self, dices: list, factor: int) -> int:
        # TODO: make dynamic
        return np.sum(dices) * factor


