from collections import OrderedDict
import pygame

from config import WIDTH, HEIGHT, START_VIDEO_FRAME_DIR, START_VIDEO_FPS


class StartVideoPlayer:


    def __init__(self):
        self.frames = sorted(START_VIDEO_FRAME_DIR.glob("frame_*.jpg"))
        self.index = 0
        self.timer = 0.0
        self.finished = False
        self.cache = OrderedDict()
        self.max_cache = 30

    def reset(self):
        self.index = 0
        self.timer = 0.0
        self.finished = False
        self.cache.clear()

    def _load_frame(self, index):
        if not self.frames:
            return None

        if index in self.cache:
            surface = self.cache.pop(index)
            self.cache[index] = surface
            return surface

        surface = pygame.image.load(str(self.frames[index])).convert()
        if surface.get_size() != (WIDTH, HEIGHT):
            surface = pygame.transform.smoothscale(surface, (WIDTH, HEIGHT))

        self.cache[index] = surface
        while len(self.cache) > self.max_cache:
            self.cache.popitem(last=False)

        return surface

    def update(self, dt):
        if self.finished or not self.frames:
            self.finished = True
            return

        self.timer += dt
        frame_duration = 1.0 / START_VIDEO_FPS

        while self.timer >= frame_duration:
            self.timer -= frame_duration
            self.index += 1

            if self.index >= len(self.frames):
                self.index = len(self.frames) - 1
                self.finished = True
                break

    def draw(self, surface):
        frame = self._load_frame(self.index)
        if frame is None:
            surface.fill((0, 0, 0))
            return

        surface.blit(frame, (0, 0))
