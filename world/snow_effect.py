import random
import pygame
from base import BaseWeatherEffect
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from support import get_path, load_folder_scaled


class SnowEffect(BaseWeatherEffect):
    
    def __init__(self):
        super().__init__()
        self.rng = random.Random(1225)
        self.flakes = []
        self.snow_frames = load_folder_scaled(get_path('graphics', 'salju', 'animation'), min_size=10)
        
        for _ in range(135):
            self.flakes.append([
                self.rng.randrange(-80, SCREEN_WIDTH + 80),
                self.rng.randrange(-120, SCREEN_HEIGHT),
                self.rng.uniform(35, 115),
                self.rng.uniform(-18, 22),
                self.rng.choice([2, 3, 4, 5])
            ])
    
    def draw(self, dt: float) -> None:
        if not self.active:
            return
        
        # Tint dingin
        tint = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        tint.fill((210, 235, 255, 28))
        self.display_surface.blit(tint, (0, 0))
        
        # Draw snow flakes
        for flake in self.flakes:
            flake[0] += flake[3] * dt
            flake[1] += flake[2] * dt
            if flake[1] > SCREEN_HEIGHT + 20 or flake[0] < -120 or flake[0] > SCREEN_WIDTH + 120:
                flake[0] = self.rng.randrange(-80, SCREEN_WIDTH + 80)
                flake[1] = self.rng.randrange(-120, -10)
                flake[2] = self.rng.uniform(35, 115)
                flake[3] = self.rng.uniform(-18, 22)
            
            x, y, size = int(flake[0]), int(flake[1]), int(flake[4])
            if self.snow_frames:
                surf = self.rng.choice(self.snow_frames)
                self.display_surface.blit(surf, (x, y))
            else:
                pygame.draw.circle(self.display_surface, (245, 250, 255), (x, y), size)