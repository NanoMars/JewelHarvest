import sys
import pygame
from pygame.locals import *
 
pygame.init()
 
fpsClock = pygame.time.Clock()
sprites = pygame.sprite.Group()
fps = 60
width, height = 1280, 720
screen = pygame.display.set_mode((width, height))

class GreenGem(pygame.sprite.Sprite): 
  #define the sprite for the greenGem
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.original_image = pygame.image.load("GreenGem.png").convert_alpha() 
    self.image = self.original_image
    self.rect = self.image.get_rect()
    self.rect.center = (width / 2, height / 2)
    self.angle = 0
    
  def update(self):
    self.angle += 1
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect(center=self.rect.center)
greenGem = GreenGem()
sprites.add(greenGem)

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
