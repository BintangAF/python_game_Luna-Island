import random
import pygame
from base import BaseWeatherEffect
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from support import get_path, load_folder_scaled


class AutumnEffect(BaseWeatherEffect):

    def __init__(self):
        super().__init__()
        self.rng = random.Random(1020)
        self.leaves = []
        self.leaf_frames = load_folder_scaled(
            get_path("graphics", "gugur", "animation"), min_size=14
        )

        for _ in range(90):
            self.leaves.append(
                [
                    self.rng.randrange(-80, SCREEN_WIDTH + 80),
                    self.rng.randrange(-140, SCREEN_HEIGHT),
                    self.rng.uniform(45, 135),
                    self.rng.uniform(-55, 35),
                    self.rng.uniform(0.0, 6.28),
                ]
            )

    def draw(self, dt: float) -> None:
        if not self.active:
            return

        tint = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        tint.fill((255, 190, 85, 22))
        self.display_surface.blit(tint, (0, 0))

        for leaf in self.leaves:
            leaf[4] += dt * 2.4
            leaf[0] += (
                leaf[3] + 22 * pygame.math.Vector2(1, 0).rotate_rad(leaf[4]).x
            ) * dt
            leaf[1] += leaf[2] * dt

            if (
                leaf[1] > SCREEN_HEIGHT + 24
                or leaf[0] < -120
                or leaf[0] > SCREEN_WIDTH + 120
            ):
                leaf[0] = self.rng.randrange(-80, SCREEN_WIDTH + 80)
                leaf[1] = self.rng.randrange(-140, -10)
                leaf[2] = self.rng.uniform(45, 135)
                leaf[3] = self.rng.uniform(-55, 35)

            x, y = int(leaf[0]), int(leaf[1])
            if self.leaf_frames:
                surf = self.rng.choice(self.leaf_frames)
                self.display_surface.blit(surf, (x, y))
            else:
                pygame.draw.ellipse(self.display_surface, (211, 101, 34), (x, y, 8, 4))
