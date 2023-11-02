import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from constants.paths import *
from conf.general import *
from conf.track import *

# Function to save GIFs
def save_gif(ep_frames_tuple, min_width=512, dpi=80):
    ep, ep_frames = ep_frames_tuple
    # Assume all frames have the same shape as the first frame
    frame_height, frame_width, _ = ep_frames[0].shape
    # Calculate figure size to maintain aspect ratio of the frames
    fig_width = min_width
    fig_height = fig_width * (frame_height / frame_width)
    fig_size = (fig_width / dpi, fig_height / dpi)  # Convert pixel to inches for figure size
    
    fig, ax = plt.subplots(figsize=fig_size)
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
    ax.axis('off')  # This will remove the axes.
    ax.set_position([0, 0, 1, 1])  # This sets the axes to cover the whole figure area.
    ax.patch.set_alpha(0.0)  # Make axes background transparent
    
    im = ax.imshow(ep_frames[0])

    def update(frame):
        im.set_array(frame)
        return [im]

    ani = animation.FuncAnimation(fig, update, frames=ep_frames, blit=True)
    
    # Save the GIF without any additional arguments that may affect size consistency
    ani.save(f"{ATTEMPTS_PATH}/{ep}.gif", writer="pillow", dpi=dpi)
    plt.close(fig)

# Function to save video with improved resolution and composite track
def save_video(frames, video_path, master_track, width=512, video_speed=10):
    original_width = master_track.shape[1]
    scale_factor = width / original_width
    master_track_scaled = cv2.resize(master_track, (width, width), interpolation=cv2.INTER_NEAREST)
    height, width = master_track_scaled.shape[:2]
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), video_speed, (width, height))

    for frame in frames:
        car_position = np.argwhere(np.all(frame == CAR_COLOR, axis=-1))
        if len(car_position) > 0:
            y, x = car_position[0]
            master_track_scaled[y*scale_factor:(y+1)*scale_factor, x*scale_factor:(x+1)*scale_factor] = CAR_COLOR

        frame_bgr = cv2.cvtColor(master_track_scaled, cv2.COLOR_RGB2BGR)
        out.write(frame_bgr)

    out.release()

def combine_all_episodes(frames, video_path, master_track, max_reward_idx, min_width=512, opacity=0.1, trail=True, fade_factor=0.9, video_speed=10, highlight_max=True):
    original_width = master_track.shape[1]
    scale_factor = min_width // original_width
    master_track_scaled = cv2.resize(master_track, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_NEAREST)
    height, width = master_track_scaled.shape[:2]
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), video_speed, (width, height))

    start_color = np.array([0, 255, 0], dtype=float)
    end_color = np.array([0, 0, 255], dtype=float)

    max_timesteps = max(len(episode_frames) for episode_frames in frames.values())
    num_episodes = len(frames)

    episode_histories = {}
    active_episodes = len(frames)
    max_reward_frames = []  # Store trail for the max reward episode
    
    finalized_histories = set()  # Episodes whose trails are finalized

    for t in range(max_timesteps):
        combined_track = np.copy(master_track_scaled).astype(float)
        active_episodes = 0

        for ep_idx, (ep_key, episode_frames) in enumerate(frames.items()):
            if t < len(episode_frames):
                active_episodes += 1
                
                frame = episode_frames[t]
                car_position = np.argwhere(np.all(frame == CAR_COLOR, axis=-1))
                
                if len(car_position) > 0:
                    y, x = car_position[0]
                    
                    if ep_key not in finalized_histories:
                        if trail:
                            if ep_key not in episode_histories:
                                episode_histories[ep_key] = []
                            episode_histories[ep_key].append((y, x))

                        if ep_key == max_reward_idx and highlight_max:
                            max_reward_frames.append((y, x))
                        else:
                            color = start_color + (end_color - start_color) * (ep_idx / num_episodes)
                            special_opacity = opacity
                            
                            if trail and ep_key in episode_histories:
                                for idx, (hist_y, hist_x) in enumerate(reversed(episode_histories[ep_key])):
                                    fading_opacity = special_opacity * (fade_factor ** idx)
                                    combined_track[hist_y*scale_factor:(hist_y+1)*scale_factor, hist_x*scale_factor:(hist_x+1)*scale_factor] = fading_opacity * color + (1 - fading_opacity) * combined_track[hist_y*scale_factor:(hist_y+1)*scale_factor, hist_x*scale_factor:(hist_x+1)*scale_factor]
                            else:
                                combined_track[y*scale_factor:(y+1)*scale_factor, x*scale_factor:(x+1)*scale_factor] = special_opacity * color + (1 - special_opacity) * combined_track[y*scale_factor:(y+1)*scale_factor, x*scale_factor:(x+1)*scale_factor]
            else:
                finalized_histories.add(ep_key)

        # Draw the max reward episode last, including its trail
        if len(max_reward_frames) > 0 and max_reward_idx not in finalized_histories:
            for idx, (y, x) in enumerate(reversed(max_reward_frames)):
                color = np.array([252, 144, 0], dtype=float)
                special_opacity = 1 if not fade_factor else (fade_factor ** idx)
                combined_track[y*scale_factor:(y+1)*scale_factor, x*scale_factor:(x+1)*scale_factor] = special_opacity * color + (1 - special_opacity) * combined_track[y*scale_factor:(y+1)*scale_factor, x*scale_factor:(x+1)*scale_factor]

        frame_bgr = cv2.cvtColor(combined_track.astype(np.uint8), cv2.COLOR_RGB2BGR)
        out.write(frame_bgr)

        if active_episodes == 0:
            break

    out.release()