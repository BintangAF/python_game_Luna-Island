import os
import pygame
from .settings import *
from .support import get_path, import_folder, crop_alpha_surface


class Animation:
    def __init__(self, frames, start_status='down_idle', speed=7):
        self.frames = frames
        self.status = start_status
        self.speed = speed
        self.frame = 0.0

    def set_status(self, status):
        if status != self.status and status in self.frames:
            self.status = status
            self.frame = 0.0

    def play(self, dt):
        frames_list = self.frames[self.status]
        self.frame += self.speed * dt
        if self.frame >= len(frames_list):
            self.frame = 0.0
        return frames_list[int(self.frame)]


class Player:
    CHAR_W = 38
    CHAR_H = 50

    def __init__(self, pos):
        self.frames = self._load_frames()
        self.animation = Animation(self.frames, 'down_idle', speed=7)
        self.image = self.animation.play(0)
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-14, -18)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2()
        self.facing = 'down'
        self.speed = PLAYER_SPEED
        self.energy_max = 100
        self.energy = 100
        self.running = False

    def _scale_frame(self, surf):
        return pygame.transform.scale(crop_alpha_surface(surf), (self.CHAR_W, self.CHAR_H))

    def _load_idle_pose(self, direction, fallback):
        idle_path = get_path('graphics', 'character', f'{direction}_idle')
        idle_frames = import_folder(idle_path)
        if idle_frames:
            return [self._scale_frame(idle_frames[0])]
        frame04 = get_path('graphics', 'character', direction, '04.png')
        if os.path.exists(frame04):
            try:
                return [self._scale_frame(pygame.image.load(frame04).convert_alpha())]
            except Exception:
                pass
        return [fallback[-1].copy()]

    def _load_frames(self):
        out = {}
        first = None
        for direction in ['down', 'up', 'left', 'right']:
            frames = import_folder(get_path('graphics', 'character', direction))
            if frames:
                scaled = [self._scale_frame(f) for f in frames]
                out[direction] = scaled
                if first is None:
                    first = scaled
        if first is None:
            raise RuntimeError('Aset karakter goa tidak ditemukan.')
        for direction in ['down', 'up', 'left', 'right']:
            if direction not in out:
                out[direction] = [f.copy() for f in first]
            out[f'{direction}_idle'] = self._load_idle_pose(direction, out[direction])
        return out

    def update(self, dt, colliders):
        keys = pygame.key.get_pressed()
        self.direction.update(0, 0)

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1
            self.facing = 'up'
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
            self.facing = 'down'

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.facing = 'right'
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            self.facing = 'left'

        moving = self.direction.length() > 0
        shift_down = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        self.running = bool(shift_down and moving and self.energy > 2)

        self.animation.set_status(self.facing if moving else f'{self.facing}_idle')
        if moving:
            self.direction = self.direction.normalize()

        current_speed = self.speed * (RUN_MULTIPLIER if self.running else 1)
        if self.running:
            self.energy = max(0, self.energy - 18 * dt)
        else:
            self.energy = min(self.energy_max, self.energy + 22 * dt)

        self.pos.x += self.direction.x * current_speed * dt
        self.hitbox.centerx = round(self.pos.x)
        for rect in colliders:
            if self.hitbox.colliderect(rect):
                if self.direction.x > 0:
                    self.hitbox.right = rect.left
                elif self.direction.x < 0:
                    self.hitbox.left = rect.right
                self.pos.x = self.hitbox.centerx

        self.pos.y += self.direction.y * current_speed * dt
        self.hitbox.centery = round(self.pos.y)
        for rect in colliders:
            if self.hitbox.colliderect(rect):
                if self.direction.y > 0:
                    self.hitbox.bottom = rect.top
                elif self.direction.y < 0:
                    self.hitbox.top = rect.bottom
                self.pos.y = self.hitbox.centery

        left = OFFSET_X + 22
        right = OFFSET_X + ROOM_WIDTH - 22
        top = OFFSET_Y + 24
        bottom = OFFSET_Y + ROOM_HEIGHT - 22
        self.hitbox.centerx = max(left, min(self.hitbox.centerx, right))
        self.hitbox.centery = max(top, min(self.hitbox.centery, bottom))
        self.rect.center = self.hitbox.center
        self.pos.update(self.hitbox.center)
        anim_dt = dt * (1.35 if self.running else 1.0)
        self.image = self.animation.play(anim_dt * (0.6 if 'idle' in self.animation.status else 1.0))

    def draw(self, surface):
        self.rect.midbottom = self.hitbox.midbottom
        surface.blit(self.image, self.rect)
