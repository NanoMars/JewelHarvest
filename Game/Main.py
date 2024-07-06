import sys
import os
import random
import math
import io
import pickle
from PIL import Image
import colorsys
import pygame
from pygame.locals import *

# Set the working directory to the script's location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Initialize Pygame and its components
pygame.init()
pygame.font.init()

# Constants for the game
WIDTH, HEIGHT = 1280, 720
FPS = 60
SCALE_FACTOR = 5

# Constants for button spacing
button_start_x = WIDTH - 10 
button_start_y = 180
button_spacing_y = 10  # Adjusted for better spacing

# Game variables
ticks = 0
gem_time_passed = 0
money = 1000
value_multiplier = 1
gems_spawned = 0
spawn_time = 5
screen_proportion_numerator, screen_proportion_denominator = 14, 19
time_passed = 0
reset_thing = False
max_gems = 10
gems_on_screen = 0
gems_were_on_screen = 0

# Setup display and font
pygame.display.set_caption('Jewelharvest')
game_icon = pygame.image.load('Assets/Other/icon.png')
pygame.display.set_icon(game_icon)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.Font('Assets/Other/Bitfantasy.ttf', 34)  # Increased font size
fps_clock = pygame.time.Clock()

# Load resources
background = pygame.image.load('Assets/Textures/Rock.png').convert()
shop_background = pygame.image.load('Assets/Textures/shopBackground.png').convert()
signboard = pygame.image.load('Assets/Textures/SignBoard.png').convert_alpha()
progress_bar = pygame.image.load('Assets/Textures/Bar.png').convert_alpha()
displayboard = pygame.image.load('Assets/Textures/DisplayBoard.png').convert_alpha()


# Sprite groups
sprites = pygame.sprite.Group()

def save_game(filename='savefile.pkl'):
        game_state = {
            'money': money,
            'value_multiplier': value_multiplier,
            'spawn_time': spawn_time,
            'max_gems': max_gems,
            'gems_on_screen': gems_on_screen,
            'shop_buttons': [(btn.owned, btn.cost) for btn in shop_buttons]
        }
        with open(filename, 'wb') as f:
            pickle.dump(game_state, f)
        print("Game saved!")

def load_game(filename='Saves/savefile.pkl'):
    global ticks, gem_time_passed, money, value_multiplier, gems_spawned, spawn_time, time_passed, reset_thing, max_gems, gems_were_on_screen
    try:
        with open(filename, 'rb') as f:
            game_state = pickle.load(f)
            money = game_state['money']
            value_multiplier = game_state['value_multiplier']
            spawn_time = game_state['spawn_time']
            max_gems = game_state['max_gems']
            gems_were_on_screen = game_state['gems_on_screen']
            for btn, state in zip(shop_buttons, game_state['shop_buttons']):
                btn.owned, btn.cost = state
                btn.update_text_surface()
            print("Game loaded!")
            
    except FileNotFoundError:
        print("No saved game found.")
        
        

def shift_hue(img_path, degree_shift):
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

class ShopButton:
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
        self.text_surface = None
        self.update_text_surface()

    def update_text_surface(self):
        # Include the special character for wrapping in the description text
        self.text_surface = render_text_wrapped(f'{self.owned} {self.description} \n ${self.cost}', font, (0, 0, 0), self.rect.width)

    def display_info(self):
        # Rotate the text surface
        rotated_text = pygame.transform.rotate(self.text_surface, self.angle)
        
        # Calculate the center position of the text surface relative to the button
        text_rect = rotated_text.get_rect()
        text_rect.center = self.rect.center
        
        # Blit the rotated text surface at the calculated position
        screen.blit(rotated_text, text_rect.topleft)

    def handle_click(self, time_passed):
        global money
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
                    self.cost = int(self.base_cost * (1.5 ** self.owned))  # Exponential cost increase
                    self.update_text_surface()  # Update the text surface
                    save_game()
            elif pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
        
    def draw(self):
        global time_passed
        self.update_rotation(time_passed)
        screen.blit(self.image, self.rect.topleft)
        self.display_info()
        self.handle_click(time_passed)

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
    def __init__(self, value, x_pos, y_pos):
        super().__init__()
        global time_passed
        self.value = value
        self.original_image = shift_hue("Assets/Textures/Gem.png", value * 10)
        self.original_image = pygame.transform.scale(self.original_image, (int(self.original_image.get_width() * SCALE_FACTOR), int(self.original_image.get_height() * SCALE_FACTOR)))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self.angle = 0
        self.angle_modifier = random.randrange(-100, 100)

    def update(self):
        self.angle = math.sin(time_passed / 350) * 10
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

def render_text_wrapped(text, font, color, max_width):
    buffer = 45
    adjusted_max_width = max_width - 2 * buffer  # Adjust the max width to include the buffer
    lines = []
    
    # Split the text into segments based on the newline character
    segments = text.split('\n')
    for segment in segments:
        words = segment.split()
        while words:
            line = ''
            while words and font.size(line + words[0])[0] <= adjusted_max_width:
                line += (words.pop(0) + ' ')
            lines.append(line.strip())

    line_surfaces = [font.render(line, True, color) for line in lines]
    text_height = sum(line.get_height() for line in line_surfaces)
    text_surface = pygame.Surface((max_width, text_height), pygame.SRCALPHA)
    y = 0
    for line_surface in line_surfaces:
        x = (max_width - line_surface.get_width()) // 2
        text_surface.blit(line_surface, (x, y))
        y += line_surface.get_height()
    return text_surface

def spawn_gem(value):
    global gems_on_screen, gems_spawned
    gem = Gem(int(value * value_multiplier), random.randrange(0, int(screen_proportion_numerator * WIDTH / screen_proportion_denominator)), random.randrange(0, HEIGHT))
    sprites.add(gem)
    gems_on_screen += 1
    gems_spawned += 1

def increase_value_multiplier():
    global value_multiplier
    value_multiplier = (value_multiplier + 1) + (0.01 * value_multiplier)
    print(value_multiplier)

def spawn_extra_gems():
    global spawn_time, gem_time_passed, gems_spawned, ticks, reset_thing
    reset_thing = True
    current_progress_ratio = gem_time_passed / spawn_time if spawn_time else 0
    spawn_time = (spawn_time * 4) / 5
    
def increase_max_gems():
    global max_gems
    max_gems = max_gems * 1.25

def draw_tiling_background(background, x1=0, y1=0, x2=WIDTH, y2=HEIGHT):
    background = pygame.transform.scale(background, (int(background.get_width() * SCALE_FACTOR), int(background.get_height() * SCALE_FACTOR)))
    bg_width, bg_height = background.get_size()
    for x in range(x1, x2, bg_width):
        for y in range(y1, y2, bg_height):
            screen.blit(background, (x, y))

def draw_progress_bar(bar_image, x, y, progress):
    bar_image = pygame.transform.scale(bar_image, (int(bar_image.get_width() * SCALE_FACTOR), int(bar_image.get_height() * SCALE_FACTOR)))
    bar_width = bar_image.get_width()
    max_reveal_width = int((screen_proportion_numerator / screen_proportion_denominator) * WIDTH)
    reveal_width = int(max_reveal_width * progress)
    screen.blit(bar_image, (x + reveal_width - bar_width, y), (0, 0, bar_width, bar_image.get_height()))

button1 = ShopButton(button_start_x, button_start_y, signboard, increase_value_multiplier, 10, 'Increase Multiplier')
button2 = ShopButton(button_start_x, button_start_y + button1.rect.height + button_spacing_y, signboard, spawn_extra_gems, 30, 'Spawn Accelerator')
button3 = ShopButton(button_start_x, button2.rect.y + button2.rect.height + button_spacing_y, signboard, increase_max_gems, 100, 'Increase Max Gems')

shop_buttons = [button1, button2, button3]


def display_display_board():
    display_board_width = displayboard.get_width() * SCALE_FACTOR
    display_board_height = displayboard.get_height() * SCALE_FACTOR
    x = button_start_x - display_board_width
    y = 10

    display_board_image = pygame.transform.scale(displayboard, (int(displayboard.get_width() * SCALE_FACTOR), int(displayboard.get_height() * SCALE_FACTOR)))
    screen.blit(display_board_image, (x, y))
    money_text = render_text_wrapped(f'{money}$', font, (0, 0, 0), display_board_width)
    money_text_rect = money_text.get_rect(center=(x + display_board_image.get_width() / 2, y + display_board_image.get_height() / 2))
    screen.blit(money_text, money_text_rect.topleft)


#loading game before other stuff
load_game()
gems_spawned -= gems_were_on_screen - 1



# Main game loop
while True:
    pygame.display.set_caption(f'Jewelharvest - ${money}')
    fps_clock.tick(FPS)
    if pygame.time.get_ticks() != 0:
        time_passed = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == QUIT:
            save_game()
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                for gem in sprites:
                    if gem.rect.collidepoint(mouse_x, mouse_y):
                        money += gem.value
                        sprites.remove(gem)
                        gems_on_screen -= 1
                        break

    sprites.update()
    ticks += 1
    
    #print(gem_time_passed)
    #print((gem_time_passed / spawn_time) - gems_spawned)
    #print(gems_on_screen)
    while gem_time_passed / spawn_time > gems_spawned and max_gems > gems_on_screen:
        if reset_thing:
            gems_spawned = int(gem_time_passed / spawn_time)
            reset_thing = False
        spawn_gem(random.randrange(1, 3))
        
    

    draw_tiling_background(background)
    sprites.draw(screen)
    draw_tiling_background(shop_background, screen_proportion_numerator * WIDTH // screen_proportion_denominator, 0, WIDTH, HEIGHT)
    if max_gems > gems_on_screen:
      gem_time_passed += fps_clock.get_time() / 1000
      progress = (gem_time_passed / spawn_time) % 1
      draw_progress_bar(progress_bar, 0, 0, progress)
      
    display_display_board()

    for button in shop_buttons:
        button.draw()

    pygame.display.flip()