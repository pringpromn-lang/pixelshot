"""
PIXEL SHOT — Main entry point
Run: python main.py
"""
import pygame
from settings import *
from game import Game

def main():
    pygame.init()
    pygame.display.set_caption("PIXEL SHOT")
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock  = pygame.time.Clock()

    game = Game(screen)
    game.run(clock)

    pygame.quit()

if __name__ == "__main__":
    main()
