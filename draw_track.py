import pygame
import sys
import numpy as np
import os

from constants.paths import *
from constants.general import *
from conf.general import *

os.makedirs(TRACK_FOLDER_PATH, exist_ok=True)

# Function to draw grid with less opacity
def draw_transparent_grid():
    s = pygame.Surface((SCREEN_SIZE,SCREEN_SIZE), pygame.SRCALPHA)
    for x in range(0, SCREEN_SIZE+1, PIXEL_SIZE):
        pygame.draw.line(s, GRID_RGBA, (x, 0), (x, SCREEN_SIZE))
    for y in range(0, SCREEN_SIZE+1, PIXEL_SIZE):
        pygame.draw.line(s, GRID_RGBA, (0, y), (SCREEN_SIZE, y))
    screen.blit(s, (0,0))

# Function to draw grid
def draw_grid(n_grid=3):
    for x in range(0, SCREEN_SIZE+1, SCREEN_SIZE // n_grid):
        pygame.draw.line(screen, GRID_RGB, (x, 0), (x, SCREEN_SIZE))
    for y in range(0, SCREEN_SIZE+1, SCREEN_SIZE // n_grid):
        pygame.draw.line(screen, GRID_RGB, (0, y), (SCREEN_SIZE, y))

# Initialize Pygame
pygame.init()

# Initialize screen and clock
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption('Pixelated Canvas')
clock = pygame.time.Clock()

# Load saved canvas if exists, otherwise initialize
if os.path.exists(TRACK_PATH):
    canvas = np.load(TRACK_PATH)
else:
    canvas = np.full((CANVAS_SIZE, CANVAS_SIZE, 3), BG_COLOR, dtype=np.uint8)

# Initialize other variables
bucket_fill = False
draw_color = OBSTACLE_COLOR
undo_stack = []

# Function to draw the canvas
def draw_canvas():
    for i in range(CANVAS_SIZE):
        for j in range(CANVAS_SIZE):
            pygame.draw.rect(screen, tuple(canvas[i, j]), (j * PIXEL_SIZE, i * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))

# Function to save the current state of canvas for undo
def save_state():
    undo_stack.append(canvas.copy())

# Function to perform bucket fill
def bucket_fill_func(x, y, fill_color):
    if np.array_equal(canvas[y, x], fill_color): # Check if the clicked color is the same as fill color
        return  # Do nothing if they're the same
    save_state()
    stack = [(x, y)]
    while stack:
        x, y = stack.pop()
        if x < 0 or x >= CANVAS_SIZE or y < 0 or y >= CANVAS_SIZE: # If out of bounds, don't do anything
            continue
        if np.array_equal(canvas[y,x], fill_color) or np.array_equal(canvas[y,x], OBSTACLE_COLOR):  # If not background color or already filled, don't do anything
            continue
        canvas[y, x] = fill_color  # Fill with fill_color
        stack.extend([(x-1, y), (x+1, y), (x, y-1), (x, y+1)])

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL): # Undo
                if undo_stack:
                    canvas = undo_stack.pop()
            elif event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL): # Save
                np.save(TRACK_PATH, canvas)
            elif event.key == pygame.K_s:
                if not (pygame.key.get_mods() & pygame.KMOD_CTRL): # Use start color
                    draw_color = START_COLOR
            elif event.key == pygame.K_f:
                if not (pygame.key.get_mods() & pygame.KMOD_CTRL): # Use finish color
                    draw_color = FINISH_COLOR
            elif event.key == pygame.K_b:
                if not (pygame.key.get_mods() & pygame.KMOD_CTRL): # Use background color
                    draw_color = BG_COLOR
            elif event.key == pygame.K_r:
                if not (pygame.key.get_mods() & pygame.KMOD_CTRL): # Use road color
                    draw_color = ROAD_COLOR
            elif event.key == pygame.K_o:
                if not (pygame.key.get_mods() & pygame.KMOD_CTRL): # Use obstacle color
                    draw_color = OBSTACLE_COLOR
        elif event.type == pygame.KEYUP: # Reset draw color to obstacle color
            draw_color = OBSTACLE_COLOR
            

        elif event.type == pygame.MOUSEBUTTONDOWN:  # Mouse click
            x, y = event.pos
            x = x // PIXEL_SIZE
            y = y // PIXEL_SIZE
            save_state()
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:  # Check if Shift key is pressed
                bucket_fill_func(x, y, draw_color)
            else:
                canvas[y, x] = draw_color

    # Paint with selected color while left mouse button is pressed
    buttons = pygame.mouse.get_pressed()
    if buttons[0] and not bucket_fill:
        x, y = pygame.mouse.get_pos()
        x = x // PIXEL_SIZE
        y = y // PIXEL_SIZE
        canvas[y, x] = draw_color


    # Draw the canvas, grid and update the screen
    draw_canvas()
    draw_grid()
    draw_transparent_grid()  # Fine grid
    pygame.display.update()
    clock.tick(60)