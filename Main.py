import sys
 
import pygame
from pygame.locals import *
 
pygame.init()
 
fpsClock = pygame.time.Clock()
sprites = pygame.sprite.Group()

fps = 60
width, height = 1280, 720
screen = pygame.display.set_mode((width, height))
 
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
  sprites.draw(screen)
  screen.fill((15, 15, 25))
  pygame.display.flip()
