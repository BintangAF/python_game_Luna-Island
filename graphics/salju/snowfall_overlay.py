
import os
import pygame

class SnowfallOverlay:
    def __init__(self, screen_size, folder_path, frame_duration=90):
        self.screen_width, self.screen_height = screen_size
        self.frames = []
        for name in sorted(os.listdir(folder_path)):
            if name.endswith('.png'):
                image = pygame.image.load(os.path.join(folder_path, name)).convert_alpha()
                self.frames.append(image)
        self.frame_index = 0
        self.timer = 0
        self.frame_duration = frame_duration

    def update(self, dt):
        self.timer += dt
        if self.frames and self.timer >= self.frame_duration:
            self.timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def draw(self, surface):
        if not self.frames:
            return
        frame = self.frames[self.frame_index]
        fw, fh = frame.get_size()
        for x in range(0, self.screen_width + fw, fw):
            for y in range(0, self.screen_height + fh, fh):
                surface.blit(frame, (x, y))
