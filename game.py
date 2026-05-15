import pygame, sys
from settings import *

class Game():
    def __init__(self, width, height):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))        