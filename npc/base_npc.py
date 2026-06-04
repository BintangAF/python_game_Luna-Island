from settings import *
from abc import ABC, abstractmethod
import pygame

class BaseNPC(pygame.sprite.Sprite, ABC):
    """Abstract base class untuk semua NPC"""
    
    def __init__(self, center_pos, image, groups, name):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(center=center_pos)
        self.z = LAYERS['player']
        self.name = name
        self.hitbox = self.rect.inflate(-16, -12)
        self.hitbox.height = max(14, self.hitbox.height // 2)
        self.hitbox.bottom = self.rect.bottom
        self.interact_rect = self.rect.inflate(76, 60)
    
    @abstractmethod
    def interact(self, level) -> None:
        """Dipanggil saat player berinteraksi dengan NPC"""
        pass
    
    def update(self, dt):
        """Optional: untuk animasi NPC"""
        pass