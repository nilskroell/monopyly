import numpy as np

def throw_dice(n_dicefaces: int = 6):
    return np.random.choice(np.arange(1,n_dicefaces+1, dtype=int))

def throw_n_dice(n_dice: int = 2, n_dicefaces: int = 6):
    return [throw_dice(n_dicefaces) for i in range(n_dice)]
