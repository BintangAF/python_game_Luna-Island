import pygame
from settings import *
from abc import ABC, abstractmethod

class Character(pygame.sprite.Sprite, ABC):

    def __init__(self, x, y, name, hp, image_path, size):
        super().__init__()
        self.image = pygame.image.load(image_path)        
        self.image = pygame.transform.scale(self.image, (size[0], size[1]))
        self.rect = self.image.get_rect(topleft=(x, y))                
        self.name = name
        self.hp = hp

    @abstractmethod
    def move(self):
        pass

    # @abstractmethod
    # def interact(self):
    #     pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self, screen):
        pass