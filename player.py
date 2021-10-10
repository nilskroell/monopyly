class Player():

    def __init__(self, start_balance: int = 1500, position: int = 0) -> None:
        self.id = None
        self.balance = start_balance
        self.position = position
        self.alive = True
        