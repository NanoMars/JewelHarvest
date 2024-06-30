import sys
import pygame
from pygame.locals import *
 
pygame.init()
 
fpsClock = pygame.time.Clock()
sprites = pygame.sprite.Group()
fps = 60
width, height = 1280, 720
screen = pygame.display.set_mode((width, height))

class Player(pygame.sprite.Sprite): 
  #define the sprite for the player
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.Surface((50,50))
    self.image.fill((0,0,0))
    self.rect = self.image.get_rect()
    self.rect.center = (width / 2, height / 2)
  def update(self):
    self.rect.x += 5
    self.rect.y += 5
    
player = Player()
sprites.add(player)

# Game loop.
while True:
  fpsClock.tick(fps)
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      sys.exit()
  
  # Update.
  sprites.update()
  
  # Draw.
  screen.fill((255, 255, 255))
  sprites.draw(screen)
  pygame.display.flip()
