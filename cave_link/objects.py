import pygame


class Rock:
    def __init__(self, rect, image, break_frames, has_key=False):
        self.rect = rect
        self.image = image
        self.break_frames = break_frames
        self.has_key = has_key
        self.broken = False
        self.breaking = False
        self.break_index = 0
        self.break_timer = 0.0
        self.break_duration = 0.075
        self.hp = 3
        self.hit_flash = 0.0

    def hit(self):
        if self.broken or self.breaking:
            return False
        self.hp -= 1
        self.hit_flash = 0.13
        if self.hp <= 0:
            self.breaking = True
            self.break_index = 0
            self.break_timer = 0.0
        return True

    def update(self, dt):
        if self.hit_flash > 0:
            self.hit_flash = max(0, self.hit_flash - dt)
        if not self.breaking:
            return False
        self.break_timer += dt
        if self.break_timer >= self.break_duration:
            self.break_timer = 0.0
            self.break_index += 1
            if self.break_index >= len(self.break_frames):
                self.breaking = False
                self.broken = True
                return True
        return False

    def draw(self, surface):
        if self.broken:
            return
        surf = self.break_frames[min(self.break_index, len(self.break_frames) - 1)] if self.breaking else self.image
        if self.hit_flash > 0:
            surf = surf.copy()
            flash = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 80))
            surf.blit(flash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        surface.blit(surf, self.rect)

    def collidable(self):
        return not self.broken
