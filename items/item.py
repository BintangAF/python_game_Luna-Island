from abc import ABC, abstractmethod
import pygame


class Item(ABC):
    """Base class untuk semua item dalam game"""
    
    def __init__(self, name: str, description: str, icon_path: str = None):
        self.name = name
        self.description = description
        self.icon_path = icon_path
        self._icon = None
    
    @abstractmethod
    def use(self, target) -> bool:
        pass
    
    def get_icon(self, size=(32, 32)):
        """Load icon item"""
        if self._icon is None:
            try:
                import os
                if self.icon_path and os.path.exists(self.icon_path):
                    img = pygame.image.load(self.icon_path).convert_alpha()
                    self._icon = pygame.transform.scale(img, size)
                else:
                    print(f"Icon path not found for {self.name}: {self.icon_path}") 
            except:
                print(f"Error loading icon for {self.name}")
        return self._icon
        
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"