import numpy as np

from playfields import StreetField

def throw_dice(n_dicefaces: int = 6):
    return np.random.choice(np.arange(1,n_dicefaces+1, dtype=int))

def throw_n_dice(n_dice: int = 2, n_dicefaces: int = 6):
    return [throw_dice(n_dicefaces) for i in range(n_dice)]


def get_propertycolor_position_map(fields):
    colors = []
    for f in fields:
        if isinstance(f, StreetField):
            colors.append(f.color)
        else:
            colors.append(-1)

    unique_colors = np.unique(colors)

    # drop -1
    unique_colors = unique_colors[np.where(unique_colors != -1)]
    
    streetcolor_position_map = dict()
    for c in unique_colors:
        idx = np.where(colors == c)[0]
        streetcolor_position_map[c] = list(idx)
    
    return streetcolor_position_map
