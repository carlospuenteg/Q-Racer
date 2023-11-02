import matplotlib.pyplot as plt
import numpy as np

from constants.paths import LEARNING_CURVE_PATH
from conf.plot import REWARDS_PLOT_WIDTH

# Function to calculate moving average
def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

# Display the track at the start
def show_track(track):
    plt.imshow(track)
    plt.title("Original Track")
    plt.axis('off')
    plt.show()

def plot_rewards(total_rewards, save=True, show=False, dpi=300, width_pixels=REWARDS_PLOT_WIDTH):
    original_figsize = plt.gcf().get_size_inches()
    aspect_ratio = original_figsize[1] / original_figsize[0]
    
    width_inches = width_pixels / dpi
    height_inches = width_inches * aspect_ratio
    
    plt.figure(figsize=(width_inches, height_inches))
    
    window_size = int(len(total_rewards) * 0.01)
    window_size = max(1, window_size)
    
    smoothed_rewards = moving_average(total_rewards, window_size)

    plt.plot(smoothed_rewards)
    plt.xlabel('Episode')
    plt.ylabel('Total Reward (Moving Avg)')
    plt.title('Learning Progress')

    plt.tight_layout()  # Adjust layout

    if save:
        plt.savefig(LEARNING_CURVE_PATH, dpi=dpi)

    if show:
        plt.show()