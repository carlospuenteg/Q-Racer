from conf.track import *
from conf.general import *
from conf.agent import *

# Directions the car can move
ACTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

# conf.track.
PIXEL_SIZE = 768 // CANVAS_SIZE
SCREEN_SIZE = CANVAS_SIZE * PIXEL_SIZE

# conf.general
GRID_RGB = OBSTACLE_COLOR
GRID_RGBA = [OBSTACLE_COLOR[0], OBSTACLE_COLOR[1], OBSTACLE_COLOR[2], 50]

# conf.ai
print_idx = N_EPISODES // N_PRINTS
if EXTRA_ATTEMPTS:
    EXTRA_FRAMES_MOD = N_EPISODES // EXTRA_ATTEMPTS
else:
    EXTRA_FRAMES_MOD = N_EPISODES+1