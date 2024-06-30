import sys
import pygame
import math
import io
import random
from PIL import Image, ImageEnhance, ImageOps
import colorsys
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Initialize font
pygame.font.init()

# Define game variables
width, height = 1280, 720
screen = pygame.display.set_mode((width, height))  # Initialize display before loading images

# Loading fonts and images
font = pygame.font.SysFont('Arial', 24)
signboard = pygame.image.load('SignBoard.png').convert_alpha()  # Now this should work without error

fps = 60
ticks = 0
timePassed = 0
money = 0
valueMultiplier = 1
gemsSpawned = 0
spawnTime = 5
scale_factor = 5

# Rest of your game setup and logic...

def shift_hue(img_path, degree_shift):
    # Load the image and adjust hue
    img = Image.open(img_path).convert('RGBA')
    ld = img.load()
    
    width, height = img.size
    for mouse_y in range(height):
        for mouse_x in range(width):
            r, g, b, a = ld[mouse_x, mouse_y]
            h, s, v = colorsys.rgb_to_hsv(r/255., g/255., b/255.)
            h = (h + degree_shift/360.0) % 1.0
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            ld[mouse_x, mouse_y] = (int(r * 255), int(g * 255), int(b * 255), a)
    
    # Convert the PIL Image to a Pygame Surface
    byte_io = io.BytesIO()
    img.save(byte_io, format='PNG')
    byte_io.seek(0)
    return pygame.image.load(byte_io)
def spawn_gem(value):
    gem = Gem(value * valueMultiplier, random.randrange(0, int(2 * width / 5)), random.randrange(0, int(height)))
    sprites.add(gem)
pygame.init()

fpsClock = pygame.time.Clock()
sprites = pygame.sprite.Group()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        original_width, original_height = self.image.get_size()
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        self.image = pygame.transform.scale(self.image, (new_width, new_height))
        self.rect = self.image.get_rect(topright=(x, y))  # Position the rectangle
        self.clicked = False
    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))  # Use the correct attributes
        
        pos = pygame.mouse.get_pos()
        
        if self.rect.collidepoint(pos):
          if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
            print("clicked")
            self.clicked = True
          elif pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        
class Gem(pygame.sprite.Sprite): 
  #define the sprite for the gem
  def __init__(self, value, xPos, yPos):
    self.ticks = 0
    self.value = value
    
    pygame.sprite.Sprite.__init__(self)
    self.original_image = shift_hue("Gem.png", value * 10)
    original_width, original_height = self.original_image.get_size()
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)
    self.original_image = pygame.transform.scale(self.original_image, (new_width, new_height))
    self.image = self.original_image
    self.rect = self.image.get_rect()
    self.rect.center = (xPos, yPos)
    self.angle = 0
  def update(self):
    self.ticks += 1
    self.angle = math.sin(self.ticks / fps * 2) * 10
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect(center=self.rect.center)


sign_post = Button(width, 0, signboard)



mouse_x, mouse_y = 0, 0


# Game loop.
while True:
  fpsClock.tick(fps)
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      sys.exit()
    elif event.type == MOUSEBUTTONDOWN: 
      if event.button == 1:
        mouse_x,mouse_y = event.pos
        for gem in sprites:
          if gem.rect.collidepoint(mouse_x,mouse_y): 
            money += gem.value
            sprites.remove(gem)
  # Update.
  progress_ratio = 1 - (-1 * (timePassed / spawnTime) + gemsSpawned)
  progressBarWidth = int((2 * width / 5) * progress_ratio)
  
  sprites.update()
  ticks += 1
  timePassed = ticks/fps
  if timePassed / spawnTime > gemsSpawned:
      spawn_gem(random.randrange(1,15))
      gemsSpawned += 1
  # Draw.
  screen.fill((255, 255, 255))
  pygame.draw.rect(screen, (155, 155, 155), (2 * width / 5, 0, width, height))
  pygame.draw.rect(screen, (127, 127, 127), (0, 0, progressBarWidth, int(height / 16)))
  sprites.draw(screen)
  text_surface = font.render(f'Money: ${money}', True, (0, 0, 0))
  screen.blit(text_surface, (10, 10))
  sign_post.draw()
  pygame.display.flip()
