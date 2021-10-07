class Player():

    def __init__(self, id: int, start_balance: int = 1500, position: int = 0) -> None:
        self.id = id
        self.balance = start_balance
        self.position = position
        self.alive = True
        