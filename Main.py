import sys
import random
import math
import io
from PIL import Image
import colorsys
import pygame
from pygame.locals import *

# Initialize Pygame and its components
pygame.init()
pygame.font.init()

# Constants for the game
WIDTH, HEIGHT = 1280, 720
FPS = 60
SCALE_FACTOR = 5

# Constants for button spacing
button_start_x = WIDTH - 10 
button_start_y = 10
button_spacing_y = 10  # Adjusted for better spacing

# Game variables
ticks = 0
gem_time_passed = 0
money = 0
value_multiplier = 1
gems_spawned = 0
spawn_time = 5
screen_proportion_numerator, screen_proportion_denominator = 14, 19
gem_time_passed_adjustment = 0
time_passed = 0

# Setup display and font
screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.SysFont('Arial', 24)
fps_clock = pygame.time.Clock()

# Load resources
background = pygame.image.load('Rock.png').convert()
shop_background = pygame.image.load('shopBackground.png').convert()
signboard = pygame.image.load('SignBoard.png').convert_alpha()
progress_bar = pygame.image.load('Bar.png').convert_alpha()

# Sprite groups
sprites = pygame.sprite.Group()

def shift_hue(img_path, degree_shift):
    """
    Shift the hue of an image.

    Args:
    img_path (str): Path to the image file.
    degree_shift (float): Amount to shift the hue.

    Returns:
    pygame.Surface: The modified image as a Pygame surface.
    """
    img = Image.open(img_path).convert('RGBA')
    ld = img.load()
    width, height = img.size
    
    for y in range(height):
        for x in range(width):
            r, g, b, a = ld[x, y]
            h, s, v = colorsys.rgb_to_hsv(r / 255., g / 255., b / 255.)
            h = (h + degree_shift / 360.0) % 1.0
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            ld[x, y] = (int(r * 255), int(g * 255), int(b * 255), a)
    
    byte_io = io.BytesIO()
    img.save(byte_io, format='PNG')
    byte_io.seek(0)
    return pygame.image.load(byte_io)

import pygame
import math

import pygame
import math

class ShopButton:
    """
    A class representing a shop button in the game.
    """
    def __init__(self, x, y, image, action, cost, description):
        self.image = pygame.transform.scale(image, (int(image.get_width() * SCALE_FACTOR), int(image.get_height() * SCALE_FACTOR)))
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(topright=(x, y))
        self.action = action
        self.base_cost = cost
        self.cost = cost
        self.description = description
        self.owned = 0
        self.clicked = False
        self.last_click_time = 0
        self.rotating = False
        self.angle = 0
        self.animation_time = 6000  # in milliseconds
        self.direction = 1

    def draw(self):
        global time_passed
        self.update_rotation(time_passed)
        screen.blit(self.image, self.rect.topleft)
        self.display_info()
        self.handle_click(time_passed)

    def display_info(self):
        text_surface = font.render(f'{self.owned} {self.description} - ${self.cost}', True, (0, 0, 0))
        rotated_text = pygame.transform.rotate(text_surface, self.angle)
        text_rect = rotated_text.get_rect(center=self.rect.center)
        screen.blit(rotated_text, text_rect.topleft)

    def handle_click(self, time_passed):
        global money  # Declare global variable at the beginning
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.rotating = True
                self.last_click_time = time_passed  # Reset last click time when clicked
                self.clicked = True
                self.direction = self.direction * -1
                if money >= self.cost:
                    self.action()  # Call the unique action
                    money -= self.cost
                    self.owned += 1
                    self.cost = self.base_cost * (self.owned + 1)  # Increase cost based on the number owned
            elif pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

    def update_rotation(self, time_passed):
        if time_passed - self.last_click_time >= self.animation_time:
            self.rotating = False
            self.angle = 0
        elif self.rotating:
            elapsed_time = time_passed - self.last_click_time
            self.angle = (math.sin(7 * (elapsed_time / 1000) + math.pi) * (10 / ((elapsed_time / 1000 * 20) + math.pi)) * 7) * self.direction
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class Gem(pygame.sprite.Sprite):
    """
    A class to represent a gem with physics and effects.
    """
    def __init__(self, value, x_pos, y_pos):
        super().__init__()
        global time_passed
        self.value = value
        self.original_image = shift_hue("Gem.png", value * 10)
        self.original_image = pygame.transform.scale(self.original_image, (int(self.original_image.get_width() * SCALE_FACTOR), int(self.original_image.get_height() * SCALE_FACTOR)))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self.angle = 0
        self.angle_modifier = random.randrange(-100, 100)

    def update(self):
        self.angle = math.sin(time_passed / 350) * 10
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

def spawn_gem(value):
    """
    Function to spawn a new gem on the screen.

    Args:
    value (int): The value of the gem.
    """
    gem = Gem(value * value_multiplier, random.randrange(0, int(screen_proportion_numerator * WIDTH / screen_proportion_denominator)), random.randrange(0, HEIGHT))
    sprites.add(gem)

def increase_value_multiplier():
    """
    Action to increase the value multiplier.
    """
    global value_multiplier
    value_multiplier += 1

def spawn_extra_gems():
    """
    Action to spawn extra gems.
    """
    global spawn_time, gem_time_passed, gems_spawned, gem_time_passed_adjustment, ticks
    # Calculate the current progress ratio
    current_progress_ratio = gem_time_passed / spawn_time if spawn_time else 0
    
    # Calculate the new spawn time
    spawn_time = (spawn_time * 4) / 5
    
    # Adjust gem_time_passed_adjustment using the formula
    gem_time_passed_adjustment = (5 / 4) * (ticks + gem_time_passed_adjustment) - ticks
    
    # Recalculate gems_spawned based on new spawn_time
    gems_spawned = int(gem_time_passed / spawn_time) + 1
    

def draw_tiling_background(background, x1=0, y1=0, x2=WIDTH, y2=HEIGHT):
    """
    Draw a tiling background on the screen within the given coordinates.

    Args:
    background (pygame.Surface): The background image to tile.
    x1, y1, x2, y2 (int): Coordinates to define the area to fill with the background.
    """
    background = pygame.transform.scale(background, (int(background.get_width() * SCALE_FACTOR), int(background.get_height() * SCALE_FACTOR)))
    bg_width, bg_height = background.get_size()
    for x in range(x1, x2, bg_width):
        for y in range(y1, y2, bg_height):
            screen.blit(background, (x, y))

def draw_progress_bar(bar_image, x, y, progress):
    """
    Draw a progress bar that is gradually revealed from left to right.

    Args:
    bar_image (pygame.Surface): The progress bar image.
    x, y (int): The starting coordinates of the progress bar.
    progress (float): The progress value (0 to 1).
    """
    bar_image = pygame.transform.scale(bar_image, (int(bar_image.get_width() * SCALE_FACTOR), int(bar_image.get_height() * SCALE_FACTOR)))
    bar_width = bar_image.get_width()
    max_reveal_width = int((screen_proportion_numerator / screen_proportion_denominator) * WIDTH)
    reveal_width = int(max_reveal_width * progress)
    screen.blit(bar_image, (x + reveal_width - bar_width, y), (0, 0, bar_width, bar_image.get_height()))

# Create shop buttons
button1 = ShopButton(button_start_x, button_start_y, signboard, increase_value_multiplier, 10, 'Increase Multiplier')
button2 = ShopButton(button_start_x, button_start_y + button1.image.get_height() + button_spacing_y, signboard, spawn_extra_gems, 20, 'Spawn Extra Gems')
shop_buttons = [button1, button2]

# Game loop
while True:
    fps_clock.tick(FPS)
    if pygame.time.get_ticks != 0:
      time_passed = pygame.time.get_ticks()
    print(time_passed)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                for gem in sprites:
                    if gem.rect.collidepoint(mouse_x, mouse_y):
                        money += gem.value
                        sprites.remove(gem)
                        break  # Exit the loop after finding the clicked gem
    
    # Update game state
    sprites.update()
    ticks += 1
    gem_time_passed = (time_passed + gem_time_passed_adjustment) / 1000
    if gem_time_passed / spawn_time > gems_spawned:
        spawn_gem(random.randrange(10000, 10001))
        gems_spawned += 1

    # Render everything
    draw_tiling_background(background)
    sprites.draw(screen)
    draw_tiling_background(shop_background, screen_proportion_numerator * WIDTH // screen_proportion_denominator, 0, WIDTH, HEIGHT)

    progress = (gem_time_passed / spawn_time) % 1  # Calculate the progress value
    draw_progress_bar(progress_bar, 0, 0, progress)  # Draw the progress bar
    #print(1 + ((gem_time_passed / spawn_time) - gems_spawned))

    text_surface = font.render(f'Money: ${money}', True, (0, 0, 0))
    screen.blit(text_surface, (10, 10))

    
    # Draw and update shop buttons
    for button in shop_buttons:
        button.draw()

    pygame.display.flip()