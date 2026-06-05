import pygame
from support import *
from config import *
from settings import *

class AnimatedWater(pygame.sprite.Sprite):
    _shared_index = 0.0
    _last_ticks = 0

    @classmethod
    def step_global(cls):
        now = pygame.time.get_ticks()
        if cls._last_ticks == 0:
            cls._last_ticks = now
            return
        dt = (now - cls._last_ticks) / 1000.0
        cls._last_ticks = now
        cls._shared_index = (cls._shared_index + 2.2 * dt) % 4.0

    def __init__(self, pos, frames, groups, z=None):
        super().__init__(groups)
        self.frames = [f.copy() for f in frames]
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy()
        self.z = z if z is not None else LAYERS['ground']

    def update(self, dt):
        idx = int(AnimatedWater._shared_index) % len(self.frames)
        self.image = self.frames[idx]
