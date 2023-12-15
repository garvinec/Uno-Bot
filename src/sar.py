import pandas as pd
import numpy as np
import itertools


def states():
    colors = ['Red', 'Green', 'Yellow', 'Blue']
    types = ['Number', 'Special', 'Wild']
    playable_normal = [0, 1]
    playable_special = [0, 1]
    total = list(range(8))

    # all possible states
    all_states = list(itertools.product(
        colors, types, playable_normal, playable_normal, playable_normal, playable_normal, playable_special, playable_special, playable_special, playable_special, total))

    return all_states


def actions():
    all_actions = [
        "Red", "Green", "Blue", "Yellow", "Skip",
        "Reverse", "Draw2", "Draw4", "Cc"
    ]
    return all_actions


def rewards(states, actions):
    R = np.zeros((len(states), len(actions)))

    for i in range(len(states)):
        if states[i][-1] == 0:
            R[i] = 1

    R = pd.DataFrame(
        data=R,
        columns=actions,
        index=states)

    return R


states = states()
actions = actions()
reward_table = rewards(states, actions)
