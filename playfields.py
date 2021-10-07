from player import Player

import numpy as np

class Field():
    def __init__(self, position: int) -> None:
        self.position = position

class Property(Field):
    def __init__(self, position: int, buying_price: int, base_rent: int, color: int, mortagage_share: float) -> None:
        super().__init__(position)
        assert mortagage_share <= 1
        assert mortagage_share > 0
        self.color = color
        self.monopoly = False

        self.owner: Player = None
        self.buying_price: int = buying_price

        self.base_rent = base_rent

        self.mortagage_value: int = int(mortagage_share * self.buying_price)
        self.mortgaged = False

class StreetField(Property):
    def __init__(self,
                 position: int,
                 color: int,
                 buying_price: int,
                 base_rent: int,
                 house_price: int,
                 max_n_houses_per_street: int = 5,
                 rent_factors: list = None,
                 mortagage_share : float = 0.5) -> None:
        super().__init__(position, buying_price, base_rent, color, mortagage_share)
        
        self.house_price = house_price
        self.n_houses: int = 0
        self.max_n_houses_per_street = max_n_houses_per_street
        self.rent_factors = rent_factors

        if self.rent_factors is None:
            self.rent_factors = np.arange(2, 2 + self.max_n_houses_per_street , 1)

class TrainstationField(Property):
    def __init__(self) -> None:
        super().__init__()

class UtilityField(Property):
    def __init__(self) -> None:
        super().__init__()


class NonProperty(Field):
    def __init__(self, position: int) -> None:
        super().__init__(position)

class FreeParkingField(NonProperty):
    def __init__(self, position: int) -> None:
        super().__init__(position)

class TaxField(NonProperty):
    def __init__(self, position: int) -> None:
        super().__init__(position)

class StartField(NonProperty):
    def __init__(self, position: int) -> None:
        super().__init__(position)