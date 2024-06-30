import sys
import pygame
import math
from pygame.locals import *
 
pygame.init()

fpsClock = pygame.time.Clock()
sprites = pygame.sprite.Group()
width, height = 1280, 720
screen = pygame.display.set_mode((width, height))

#Define game variables
fps = 60
money = 0

class GreenGem(pygame.sprite.Sprite): 
  #define the sprite for the greenGem
  def __init__(self, value):
    self.ticks = 0
    self.value = value
    
    pygame.sprite.Sprite.__init__(self)
    self.original_image = pygame.image.load("GreenGem.png").convert_alpha() 
    self.original_image = pygame.transform.scale(self.original_image, (64, 64))
    self.image = self.original_image
    self.rect = self.image.get_rect()
    self.rect.center = (width / 2, height / 2)
    self.angle = 0
    
    
  def update(self):
    self.ticks += 1
    self.angle = math.sin(self.ticks / fps * 2) * 15
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect(center=self.rect.center)

greenGem = GreenGem(5)
sprites.add(greenGem)

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
            print(money)
  # Update.
  sprites.update()
  #in event handling:
  
  
  # Draw.
  screen.fill((255, 255, 255))
  sprites.draw(screen)
  pygame.display.flip()
