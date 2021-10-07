class GameState():
    def __init__(self,
                 players: list,
                 fields: list,
                 pass_go_income: int = 200,
                 n_total_houses: int = 120,
                 buyback_quota: float = 0.5,
                 n_dice: int = 2,
                 n_dicefaces: int = 6) -> None:
                 
        self.active_player = None
        self.players = players
        self.fields = fields
        self.board_length = len(self.fields)

        self.pass_go_income = pass_go_income
        self.n_total_houses = n_total_houses # TODO: outsource to gamestate or bank?
        self.buyback_quota = buyback_quota
        self.n_dice = n_dice
        self.n_dicefaces = n_dicefaces