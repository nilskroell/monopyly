class ActionCard():

    def __init__(self,
                 teleport_position=None,
                 n_steps_forward: int = 0,
                 n_steps_backward: int = 0,
                 money_to_pay: int = 0,
                 money_to_get: int = 0,
                 money_to_pay_per_house: int = 0
                 ) -> None:

        for var in (n_steps_forward,
                    n_steps_backward,
                    money_to_pay,
                    money_to_get,
                    money_to_pay_per_house):
            assert isinstance(var, int) and var >= 0

        assert teleport_position is None or (isinstance(teleport_position, int) and teleport_position >= 0)

        self.teleport_position = teleport_position
        self.n_steps_forward = n_steps_forward
        self.n_steps_backward = n_steps_backward
        self.money_to_pay = money_to_pay
        self.money_to_get = money_to_get
        self.money_to_pay_per_house = money_to_pay_per_house
