import os
import numpy as np
from multiprocessing import Pool
import time

from classes.TrackEnv import TrackEnv
from classes.QLearningAgent import QLearningAgent
from constants.general import *
from conf.agent import *
from constants.paths import *
from conf.general import *
from utils.plot import *
from utils.vis import *

if __name__ == "__main__":
    t1 = time.time()
    if SAVE_GIFS:
        os.makedirs(ATTEMPTS_PATH, exist_ok=True)
    else:
        os.makedirs(OUTPUT_FOLDER_PATH, exist_ok=True)

    frames = {}
    best_frames = {}
    episode_frames = []
    total_rewards = []

    track = np.load(TRACK_PATH)
    env = TrackEnv(track)
    agent = QLearningAgent(env.track.shape[:2], ACTIONS)

    max_steps = np.count_nonzero(track == ROAD_COLOR)
    max_reward = -np.inf
    max_reward_idx = None

    if DISPLAY_TRACK: 
        show_track(track)

    for episode in range(1, N_EPISODES + 1):
        state = env.reset()
        total_reward = 0
        episode_frames.clear()
        step_counter = 0

        for step in range(max_steps):
            action = agent.choose_action(tuple(state))
            next_state, reward, done = env.step(action)
            true_reward = reward - step_counter*0.5

            step_counter += 1
            if max_steps and step_counter >= max_steps:
                done = True

            agent.update_q_table(tuple(state), action, true_reward, tuple(next_state))
            state = next_state
            total_reward += true_reward

            if env.prev_position is not None:
                env.track[tuple(env.prev_position[::-1])] = env.original_track[tuple(env.prev_position[::-1])]

            episode_frames.append(env.track.copy())

            if env.prev_position is not None:
                env.track[tuple(env.prev_position[::-1])] = CAR_COLOR

            if done:
                break

        agent.decay_epsilon()
        total_rewards.append(total_reward)

        if episode % print_idx == 0:
            print(f"{episode}: Reward({total_reward}), ε({agent.epsilon}), Steps({step_counter})")

        if total_reward > max_reward or episode % EXTRA_FRAMES_MOD == 0:
            frames[episode] = episode_frames.copy()
    
        if total_reward > max_reward:
            best_frames[episode] = episode_frames.copy()
            max_reward = total_reward
            max_reward_idx = episode
            print(f"\t> Found better solution. Episode {episode}, reward {total_reward}, steps {step_counter}")

    plot_rewards(total_rewards, SAVE_REWARDS_PLOT, SHOW_REWARDS_PLOT)
    if SAVE_REWARDS_PLOT:
        print(f"Learning curve saved in {LEARNING_CURVE_PATH}")

    if SAVE_BEST_VIDEO:
        save_video(frames[max_reward_idx], BEST_ATTEMPT_PATH, env.original_track)
        print(f"Best attempt video ({max_reward_idx}) saved in {BEST_ATTEMPT_PATH}")
    
    # Parallelize GIF creation
    if SAVE_GIFS:
        with Pool() as p:
            p.map(save_gif, best_frames.items())

    if SAVE_COMBINED_VIDEO:
        combine_all_episodes(frames, COMBINED_ATTEMPTS_PATH, env.original_track, max_reward_idx)
        print(f"Combined attempts video saved in {COMBINED_ATTEMPTS_PATH}")

    print(f"Total time: {time.time() - t1} seconds")