import numpy as np
import random
random.seed(0)
np.random.seed(0)

class QLearningAgent:
    def __init__(self, 
            state_space,        # Tuple specifying the dimensions of the state space, e.g., (10, 10) for a 10x10 grid.
            action_space,       # List of possible actions the agent can take, e.g., ['up', 'down', 'left', 'right'].
            alpha=0.3,          # Learning rate: Value between 0 and 1 to control the weight of new updates to Q-values.
            gamma=0.95,         # Discount factor: Value between 0 and 1 to discount future rewards, affecting the agent's long-term focus.
            epsilon=1.0,        # Exploration rate: Initial probability (0 to 1) of taking a random action instead of the best-known action.
            epsilon_min=0.01,   # Minimum exploration rate: The lowest value epsilon can reach, ensuring some exploration.
            epsilon_decay=0.995 # Decay factor for exploration rate: Multiplier (0 to 1) for epsilon after each episode, reducing the likelihood of exploration over time.
        ):
        self.state_space = state_space
        self.action_space = action_space
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.q_table = np.zeros(state_space + (len(action_space),))
    
    def choose_action(self, state):
        if np.random.rand() < self.epsilon:
            return random.choice(self.action_space)
        else:
            return self.action_space[np.argmax(self.q_table[state])]
        
    def update_q_table(self, state, action, reward, next_state):
        action_idx = self.action_space.index(action)
        next_max = np.max(self.q_table[next_state])
        self.q_table[state][action_idx] = (1 - self.alpha) * self.q_table[state][action_idx] + \
                                           self.alpha * (reward + self.gamma * next_max)
        
    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay