import pandas as pd
import numpy as np
import random

import sar


class QLearningAgent:
    def __init__(self, alpha=0.2, epsilon=0.4):
        self.states = sar.states()
        self.actions = sar.actions()
        self.R = sar.rewards(self.states, self.actions)
        self.alpha = alpha
        self.epsilon = epsilon
        self.q_table = pd.DataFrame(
            data=np.zeros((len(self.states), len(self.actions))),
            columns=self.actions,
            index=self.states
        )
        self.visit = self.q_table.copy()
        self.prev_state = 0
        self.prev_action = 0

    # greedy
    def choose_action(self, state, actions):
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(actions)  # explore random action

        else:
            random.shuffle(actions)  # exploit
            val_max = 0

            for i in actions:
                val = self.q_table.loc[[state], i][0]
                if val >= val_max:
                    val_max = val
                    action = i

        return action

    # for playing against real player after training
    def choose_move(self, state, actions, q_table):
        random.shuffle(actions)  # exploit
        val_max = 0

        for i in actions:
            val = q_table[q_table['State'] == str(state)][i].values[0]
            if val >= val_max:
                val_max = val
                action = i

        return action

    def update_q_table(self, state, action):
        if self.prev_state != 0:
            prev_q = self.q_table.loc[[self.prev_state], self.prev_action][0]
            this_q = self.q_table.loc[[state], action][0]
            reward = self.R.loc[[state], action][0]

            if reward == 0:
                self.q_table.loc[[self.prev_state], self.prev_action] = prev_q + \
                    self.alpha * (reward + this_q - prev_q)
            else:
                self.q_table.loc[[self.prev_state], self.prev_action] = prev_q + \
                    self.alpha * (reward - prev_q)

            self.visit.loc[[self.prev_state], self.prev_action] += 1

        self.prev_state = state
        self.prev_action = action
