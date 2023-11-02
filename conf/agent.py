N_EPISODES = 5000           # Episodes to run in training
N_PRINTS = 1000             # Print every N_PRINTS times throughout training

DISPLAY_TRACK = False       # Display the track at the start

SAVE_GIFS = False           # Save a folder with the best attempts as GIFs (each time the max reward is surpassed)
SAVE_BEST_VIDEO = True      # Save a video with the best attempt
SAVE_COMBINED_VIDEO = True  # Save a video with the best attempts and extra attempts combined
EXTRA_ATTEMPTS = 100        # Number of extra attempts to use in the combined video

SHOW_REWARDS_PLOT = False   # Show a plot of the rewards at the end of the training
SAVE_REWARDS_PLOT = True    # Save a plot of the rewards