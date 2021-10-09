import utils

class GameState():
    def __init__(self,
                 players: list,
                 fields: list,
                 pass_go_income: int = 200,
                 n_total_houses: int = 120,
                 max_diff_n_houses: int = 1,
                 buyback_quota: float = 0.5,
                 monopoly_factor: float = 2.0,
                 n_dice: int = 2,
                 n_dicefaces: int = 6) -> None:
                 
        self.active_player = None
        self.players = players
        self.fields = fields
        self.board_length = len(self.fields)
        self.monopoly_factor = monopoly_factor
        self.max_diff_n_houses = max_diff_n_houses
        self.pass_go_income = pass_go_income
        self.n_total_houses = n_total_houses
        self.buyback_quota = buyback_quota
        self.n_dice = n_dice
        self.n_dicefaces = n_dicefaces

        self.streetcolor_position_map = utils.get_propertycolor_position_map(self.fields)