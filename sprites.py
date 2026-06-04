import math
import pygame
from settings import *



class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z=None):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z if z is not None else LAYERS['objects']
        self.hitbox = self.rect.inflate(0, 0)


class CollideTile(pygame.sprite.Sprite):
   
    def __init__(self, pos, size, groups):
        super().__init__(groups)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy()
        self.z = LAYERS['ground']

class DoorSprite(pygame.sprite.Sprite):
    """Simple door sprite with changeable frames for exit animation."""

    def __init__(self, pos, frames, groups, z=None):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy()
        self.z = z if z is not None else LAYERS['objects']

    def set_frame(self, index):
        self.frame_index = max(0, min(index, len(self.frames) - 1))
        topleft = self.rect.topleft
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=topleft)
        self.hitbox = self.rect.copy()

    def reset(self):
        self.set_frame(0)

class WellGatewaySprite(pygame.sprite.Sprite):
    """Aset sumur sebagai gerbang menuju mode goa."""

    def __init__(self, pos, image, groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['objects']
        self.hitbox = pygame.Rect(self.rect.x + 16, self.rect.y + 42, max(24, self.rect.width - 32), max(20, self.rect.height - 48))
        self.interact_rect = self.hitbox.inflate(60, 54)
