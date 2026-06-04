import os
import random
import pygame
from base import BaseWeatherEffect
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from support import get_path, load_folder_scaled


class RainEffect(BaseWeatherEffect):
    def __init__(self):
        super().__init__()
        self.rng = random.Random(2026)
        self.drops = []
        self.splashes = []
        self.rain_sound = None
        self.rain_drops = load_folder_scaled(
            get_path("graphics", "rain", "drops"), min_size=12
        )
        self.rain_floor = load_folder_scaled(
            get_path("graphics", "rain", "floor"), min_size=16
        )

        for _ in range(100):
            self.drops.append(
                [
                    self.rng.randrange(-100, SCREEN_WIDTH + 100),
                    self.rng.randrange(-100, SCREEN_HEIGHT),
                    self.rng.uniform(360, 620),
                ]
            )

        for _ in range(36):
            self.splashes.append(
                [
                    self.rng.randrange(0, SCREEN_WIDTH),
                    self.rng.randrange(0, SCREEN_HEIGHT),
                    self.rng.uniform(0.2, 1.4),
                ]
            )

        try:
            rain_path = get_path("audio", "rain.wav")
            if os.path.exists(rain_path):
                self.rain_sound = pygame.mixer.Sound(rain_path)
                self.rain_sound.set_volume(0.22)
        except Exception:
            self.rain_sound = None

    def set_active(self, active: bool) -> None:
        """Override untuk handle suara"""
        if self.active == active:
            return
        self.active = active
        if self.rain_sound:
            if self.active:
                self.rain_sound.play(loops=-1)
            else:
                self.rain_sound.stop()

    def draw(self, dt: float) -> None:
        if not self.active:
            return

        for d in self.drops:
            d[0] += 150 * dt
            d[1] += d[2] * dt
            if d[1] > SCREEN_HEIGHT + 40:
                d[0] = self.rng.randrange(-120, SCREEN_WIDTH)
                d[1] = self.rng.randrange(-100, -10)
            if self.rain_drops:
                surf = self.rng.choice(self.rain_drops)
                self.display_surface.blit(surf, (int(d[0]), int(d[1])))
            else:
                pygame.draw.line(
                    self.display_surface,
                    (170, 210, 255),
                    (int(d[0]), int(d[1])),
                    (int(d[0] - 4), int(d[1] + 12)),
                    1,
                )

        for s in self.splashes:
            s[2] -= dt
            if s[2] <= 0:
                s[0] = self.rng.randrange(0, SCREEN_WIDTH)
                s[1] = self.rng.randrange(0, SCREEN_HEIGHT)
                s[2] = self.rng.uniform(0.2, 1.4)
            if self.rain_floor:
                self.display_surface.blit(
                    self.rng.choice(self.rain_floor), (int(s[0]), int(s[1]))
                )

    def draw_darkness(self, alpha: int) -> None:
        """Draw darkness overlay untuk malam"""
        if alpha <= 0:
            return
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 18, 48, int(alpha)))
        self.display_surface.blit(overlay, (0, 0))
