from collections import OrderedDict
import pygame

from config import FRAME_DIR, REFERENCE_FRAME_PATH, WIDTH, HEIGHT, VIDEO_FRAME_FPS


class AnimatedVideoBackground:
 

    def __init__(self):
        self.frames = sorted(FRAME_DIR.glob("frame_*.jpg"))
        self.frame_index = 0
        self.timer = 0.0
        self.cache = OrderedDict()
        self.max_cache = 20

        self.fallback = None
        if REFERENCE_FRAME_PATH.exists():
            self.fallback = pygame.image.load(str(REFERENCE_FRAME_PATH)).convert()
            self.fallback = pygame.transform.smoothscale(self.fallback, (WIDTH, HEIGHT))

    def _load_frame(self, index: int):
        if not self.frames:
            return self.fallback

        index %= len(self.frames)
        if index in self.cache:
            surf = self.cache.pop(index)
            self.cache[index] = surf
            return surf

        surf = pygame.image.load(str(self.frames[index])).convert()
        if surf.get_size() != (WIDTH, HEIGHT):
            surf = pygame.transform.smoothscale(surf, (WIDTH, HEIGHT))

        self.cache[index] = surf
        while len(self.cache) > self.max_cache:
            self.cache.popitem(last=False)
        return surf

    def update(self, dt: float):
        if not self.frames:
            return
        self.timer += dt
        frame_duration = 1.0 / VIDEO_FRAME_FPS
        while self.timer >= frame_duration:
            self.timer -= frame_duration
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def draw(self, surface):
        frame = self._load_frame(self.frame_index)
        if frame is not None:
            surface.blit(frame, (0, 0))
        else:
            surface.fill((25, 35, 60))
