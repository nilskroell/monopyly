import numpy as np

def throw_dice():
    return np.random.sample(np.arange(1,6+1))

def throw_two_dices():
    dice_1 = throw_dice()
    dice_2 = throw_dice()
    return [dice_1, dice_2]