import sys
import pygame
import math
import io
import random
from PIL import Image, ImageEnhance, ImageOps
import colorsys
from pygame.locals import *

#Define game variables
width, height = 1280, 720
fps = 60
ticks = 0
timePassed = 0

money = 0
valueMultiplier = 1
gemsSpawned = 0
spawnTime = 1

def shift_hue(img_path, degree_shift):
    # Load the image and adjust hue
    img = Image.open(img_path).convert('RGBA')
    ld = img.load()
    
    width, height = img.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = ld[x, y]
            h, s, v = colorsys.rgb_to_hsv(r/255., g/255., b/255.)
            h = (h + degree_shift/360.0) % 1.0
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            ld[x, y] = (int(r * 255), int(g * 255), int(b * 255), a)
    
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

screen = pygame.display.set_mode((width, height))



class Gem(pygame.sprite.Sprite): 
  #define the sprite for the gem
  def __init__(self, value, xPos, yPos):
    self.ticks = 0
    self.value = value
    
    pygame.sprite.Sprite.__init__(self)
    self.original_image = shift_hue("Gem.png", value * 10)
    self.original_image = pygame.transform.scale(self.original_image, (64, 64))
    self.image = self.original_image
    self.rect = self.image.get_rect()
    self.rect.center = (xPos, yPos)
    self.angle = 0
    
    
  def update(self):
    self.ticks += 1
    self.angle = math.sin(self.ticks / fps * 2) * 10
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect(center=self.rect.center)

x, y = 0, 0
# Game loop.
while True:
  fpsClock.tick(fps)
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      sys.exit()
    elif event.type == MOUSEBUTTONDOWN: 
      if event.button == 1:
        x,y = event.pos
        for gem in sprites:
          if gem.rect.collidepoint(x,y): 
            money += gem.value
            sprites.remove(gem)
            print(money)
  # Update.
  sprites.update()
  ticks += 1
  timePassed = ticks/fps
  if timePassed / spawnTime > gemsSpawned:
      spawn_gem(100)
      gemsSpawned += 1
  # Draw.
  screen.fill((255, 255, 255))
  sprites.draw(screen)
  pygame.display.flip()
