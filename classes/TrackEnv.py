import numpy as np

from conf.general import *

class TrackEnv:
    def __init__(self, track):
        self.original_track = track.copy()
        self.track = None
        try:
            self.start = np.argwhere(np.all(track == START_COLOR, axis=-1))[0][::-1]  # Flip the indices
        except:
            raise Exception("Start position not found")
        try:
            self.finish = np.argwhere(np.all(track == FINISH_COLOR, axis=-1))[0][::-1]  # Flip the indices
        except:
            raise Exception("Finish position not found")
        self.prev_position = None
        self.reset()
        
    def reset(self):
        self.track = self.original_track.copy()
        self.position = self.start.copy()
        self.prev_position = None
        self.done = False
        self.track[tuple(self.position[::-1])] = CAR_COLOR  # Flip the indices
        return self.position
    
    def step(self, action):
        reward = 0
        if self.prev_position is not None:
            self.track[tuple(self.prev_position[::-1])] = self.original_track[tuple(self.prev_position[::-1])]  # Flip the indices
        
        next_position = self.position + np.array(action)
        
        # Out of bounds
        if (next_position < 0).any() or (next_position >= self.track.shape[:2]).any() or \
        np.array_equal(self.track[tuple(next_position[::-1])], OBSTACLE_COLOR):
            self.done = True
            reward += -1000
        
        # If you reach the end
        elif np.array_equal(self.track[tuple(next_position[::-1])], FINISH_COLOR):  # Flip the indices
            self.done = True
            reward += 100 * self.track.shape[0]

        else:
            # Car is moving torwards the finish (y axes)
            if (next_position[1] < self.position[1] and next_position[1] > self.finish[1]) or (next_position[1] > self.position[1] and next_position[1] < self.finish[1]):
                reward += 100
            # Car is moving away from the finish (y axes)
            if (next_position[1] < self.position[1] and next_position[1] < self.finish[1]) or (next_position[1] > self.position[1] and next_position[1] > self.finish[1]):
                reward += -100

            # Car is moving torwards the finish (x axes)
            if (next_position[0] < self.position[0] and next_position[0] > self.finish[0]) or (next_position[0] > self.position[0] and next_position[0] < self.finish[0]):
                reward += 100
            # Car is moving away from the finish (x axes)
            if (next_position[0] < self.position[0] and next_position[0] < self.finish[0]) or (next_position[0] > self.position[0] and next_position[0] > self.finish[0]):
                reward += -100

        # If you return to the previous position
        if np.array_equal(next_position, self.prev_position):
            reward += -500

        self.prev_position = self.position.copy()
        
        if not self.done:
            self.position = next_position
            
        self.track[tuple(self.position[::-1])] = CAR_COLOR  # Flip the indices
        return self.position, reward, self.done