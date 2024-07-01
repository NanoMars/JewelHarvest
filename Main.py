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

# Game variables
ticks = 0
time_passed = 0
money = 0
value_multiplier = 1
gems_spawned = 0
spawn_time = 5

# Setup display and font
screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.SysFont('Arial', 24)
fps_clock = pygame.time.Clock()

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

class Button():
    """
    A simple button class for Pygame.
    """
    def __init__(self, x, y, image):
        self.image = pygame.transform.scale(image, (int(image.get_width() * SCALE_FACTOR), int(image.get_height() * SCALE_FACTOR)))
        self.rect = self.image.get_rect(topright=(x, y))
        self.clicked = False

    def draw(self):
        screen.blit(self.image, self.rect.topleft)
        self.handle_click()

    def handle_click(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                print("Button clicked")
                self.clicked = True
            elif pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

class Gem(pygame.sprite.Sprite):
    """
    A class to represent a gem with physics and effects.
    """
    def __init__(self, value, x_pos, y_pos):
        super().__init__()
        self.value = value
        self.original_image = shift_hue("Gem.png", value * 10)
        self.original_image = pygame.transform.scale(self.original_image, (int(self.original_image.get_width() * SCALE_FACTOR), int(self.original_image.get_height() * SCALE_FACTOR)))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self.ticks = 0
        self.angle = 0

    def update(self):
        self.ticks += 1
        self.angle = math.sin(self.ticks / FPS * 2) * 10
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

def spawn_gem(value):
    """
    Function to spawn a new gem on the screen.

    Args:
    value (int): The value of the gem.
    """
    gem = Gem(value * value_multiplier, random.randrange(0, int(2 * WIDTH / 5)), random.randrange(0, HEIGHT))
    sprites.add(gem)

# Load resources
signboard = pygame.image.load('SignBoard.png').convert_alpha()
sign_post = Button(WIDTH, 0, signboard)

# Game loop
while True:
    fps_clock.tick(FPS)
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
    time_passed = ticks / FPS
    if time_passed / spawn_time > gems_spawned:
        spawn_gem(random.randrange(1, 15))
        gems_spawned += 1

    # Render everything
    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, (155, 155, 155), (2 * WIDTH / 5, 0, WIDTH, HEIGHT))
    pygame.draw.rect(screen, (127, 127, 127), (0, 0, int((2 * WIDTH / 5) * (1 - (-1 * (time_passed / spawn_time) + gems_spawned))), int(HEIGHT / 16)))
    sprites.draw(screen)
    text_surface = font.render(f'Money: ${money}', True, (0, 0, 0))
    screen.blit(text_surface, (10, 10))
    sign_post.draw()
    pygame.display.flip()