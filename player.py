import os
import pygame
from settings import *
from support import import_folder, get_path


def _crop_alpha_surface(surface: pygame.Surface, padding: int = 2) -> pygame.Surface:
    """Crop transparent padding before scaling the player sprite."""
    rect = surface.get_bounding_rect(min_alpha=1)
    if rect.width <= 0 or rect.height <= 0:
        return surface
    rect.inflate_ip(padding * 2, padding * 2)
    rect.clamp_ip(surface.get_rect())
    cropped = pygame.Surface(rect.size, pygame.SRCALPHA)
    cropped.blit(surface, (0, 0), rect)
    return cropped


class Animation:
    """Simple animation player."""

    def __init__(self, frames: dict, start_status: str, speed: float = 6):
        self.frames = frames
        self.status = start_status
        self.speed = speed
        self.frame = 0.0

    def set_status(self, status: str):
        if status != self.status and status in self.frames:
            self.status = status
            self.frame = 0.0

    def play(self, dt: float) -> pygame.Surface:
        frames_list = self.frames[self.status]
        self.frame += self.speed * dt
        if self.frame >= len(frames_list):
            self.frame = 0.0
        return frames_list[int(self.frame)]


class Player(pygame.sprite.Sprite):
   
    CHAR_W = 38
    CHAR_H = 50

    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)

        self.anim_frames = self._load_frames()
        self.animation = Animation(self.anim_frames, 'down_idle', speed=7)

        self.image = self.animation.play(0)
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['player']

        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = PLAYER_SPEED
        self.run_multiplier = 1.75
        self.energy_max = 100
        self.energy = self.energy_max
        self.sprinting = False
        self.facing = 'down'

       
        self.hitbox = self.rect.inflate(-14, -18)
        self.collision_sprites = collision_sprites

        self.run_sound = None
        self.run_sound_playing = False
        try:
            run_sound_path = get_path('audio', 'run_loop.wav')
            if os.path.exists(run_sound_path):
                self.run_sound = pygame.mixer.Sound(run_sound_path)
                self.run_sound.set_volume(0.22)
        except Exception:
            self.run_sound = None

    def _scale_frame(self, surf: pygame.Surface) -> pygame.Surface:
        return pygame.transform.scale(_crop_alpha_surface(surf), (self.CHAR_W, self.CHAR_H))

    def _load_idle_pose_from_frame04(self, base_dir: str, fallback_frames: list) -> list:
        frame04_path = get_path('graphics', 'character', base_dir, '04.png')
        if os.path.exists(frame04_path):
            try:
                surf = pygame.image.load(frame04_path).convert_alpha()
                return [self._scale_frame(surf)]
            except Exception:
                pass
        return [fallback_frames[-1].copy()] if fallback_frames else []

    def _load_frames(self) -> dict:
        char_base = get_path('graphics', 'character')
        move_dirs = ['down', 'up', 'left', 'right']
        frames = {}
        first_available = None

        for d in move_dirs:
            loaded = import_folder(f'{char_base}/{d}')
            if loaded:
                scaled = [self._scale_frame(s) for s in loaded]
                frames[d] = scaled
                if first_available is None:
                    first_available = scaled

        if first_available is None:
            raise RuntimeError('Character asset tidak ditemukan. Cek folder graphics/character.')

        for d in move_dirs:
            if d not in frames:
                frames[d] = [surf.copy() for surf in first_available]

       
        for d in move_dirs:
            frames[f'{d}_idle'] = self._load_idle_pose_from_frame04(d, frames[d])
            if not frames[f'{d}_idle']:
                frames[f'{d}_idle'] = [frames[d][-1].copy()]

        return frames

    def _input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1
            self.facing = 'up'
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
            self.facing = 'down'
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.facing = 'right'
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            self.facing = 'left'
        else:
            self.direction.x = 0

        moving = self.direction.length() > 0
        self.sprinting = bool(keys[pygame.K_SPACE] and moving and self.energy > 1)

        if moving:
            self.animation.set_status(self.facing)
        else:
            self.animation.set_status(f'{self.facing}_idle')

    def _move(self, dt):
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        current_speed = self.speed * (self.run_multiplier if self.sprinting else 1)
        if self.sprinting:
            self.energy = max(0, self.energy - 9 * dt)
        else:
            self.energy = min(self.energy_max, self.energy + 18 * dt)

        self.pos.x += self.direction.x * current_speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self._collide('horizontal')

        self.pos.y += self.direction.y * current_speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self._collide('vertical')

        hw = self.rect.width // 2
        hh = self.rect.height // 2
        wx = MAP_W * TILE_SIZE
        wy = MAP_H * TILE_SIZE
        self.rect.centerx = max(hw, min(self.rect.centerx, wx - hw))
        self.rect.centery = max(hh, min(self.rect.centery, wy - hh))
        self.pos.x = self.rect.centerx
        self.pos.y = self.rect.centery
        self.hitbox.center = self.rect.center

    def _collide(self, axis):
        for sprite in self.collision_sprites.sprites():
            hb = getattr(sprite, 'hitbox', sprite.rect)
            if hb.colliderect(self.hitbox):
                if axis == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox.right = hb.left
                    if self.direction.x < 0:
                        self.hitbox.left = hb.right
                    self.rect.centerx = self.hitbox.centerx
                    self.pos.x = self.hitbox.centerx
                else:
                    if self.direction.y > 0:
                        self.hitbox.bottom = hb.top
                    if self.direction.y < 0:
                        self.hitbox.top = hb.bottom
                    self.rect.centery = self.hitbox.centery
                    self.pos.y = self.hitbox.centery

    def _update_run_sound(self):
        should_play = self.sprinting and self.direction.length() > 0 and self.energy > 0
        if self.run_sound:
            if should_play and not self.run_sound_playing:
                self.run_sound.play(loops=-1)
                self.run_sound_playing = True
            elif not should_play and self.run_sound_playing:
                self.run_sound.stop()
                self.run_sound_playing = False

    def update(self, dt):
        self._input()
        self._move(dt)
        self._update_run_sound()
        anim_dt = dt * (0.6 if 'idle' in self.animation.status else 1.0)
        self.image = self.animation.play(anim_dt)
