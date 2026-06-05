
import os
import random
import pygame

from .settings import *
from .support import get_path, import_folder, load_single, crop_alpha_surface
from .player import Player
from .room import CaveRoom
from .ui import CaveUI


class CaveAdventure:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            pass
        self.fonts = {
            'big': pygame.font.Font(get_path('font', 'LycheeSoda.ttf'), 26) if os.path.exists(get_path('font', 'LycheeSoda.ttf')) else pygame.font.Font(None, 28),
            'small': pygame.font.Font(get_path('font', 'LycheeSoda.ttf'), 20) if os.path.exists(get_path('font', 'LycheeSoda.ttf')) else pygame.font.Font(None, 22),
        }
        self.assets = self.load_assets()
        self.face = load_single(get_path('graphics', 'ui', 'character_face.png'), (54, 48))
        self.ui = CaveUI(self.screen, self.fonts, self.assets, self.face)
        self.player = Player((OFFSET_X + ROOM_WIDTH // 2, OFFSET_Y + ROOM_HEIGHT - 60))
        self.session_seed = random.randint(1000, 999999)
        self.floor_number = 1
        self.hearts = 7
        self.key_count = 0
        self.room = None
        self.tool_swing_timer = 0.0
        self.tool_swing_duration = 0.18
        self.notice_text = ''
        self.notice_timer = 0.0
        self.pending_room_transition = False
        self.game_finished = False
        self.soundtrack = None
        self.run_sound = None
        self.run_sound_playing = False
        self.door_sound = None
        self.pickaxe_sound = None
        self.key_sound = None
        self.intro_played = False
        self.request_exit = False
        self._load_sfx()
        self.generate_room(first_room=True)

    def reset_adventure(self):
        self.session_seed = random.randint(1000, 999999)
        self.floor_number = 1
        self.hearts = 7
        self.key_count = 0
        self.pending_room_transition = False
        self.game_finished = False
        self.request_exit = False
        self.generate_room(first_room=True)

    def enter(self):
        self.request_exit = False
        # Prolog selalu diputar setiap pemain masuk sumur/goa.
        self.intro_played = True
        self.play_cutscene('prolog')
        self._start_soundtrack()

    def leave(self, reset=False):
        self._stop_all_sfx()
        self.request_exit = False
        if reset:
            self.reset_adventure()

    def _load_sfx(self):
        try:
            run_path = get_path('audio', 'run_loop.wav')
            if os.path.exists(run_path):
                self.run_sound = pygame.mixer.Sound(run_path)
                self.run_sound.set_volume(0.22)
        except Exception:
            self.run_sound = None
        try:
            door_path = get_path('audio', 'door_open.wav')
            if os.path.exists(door_path):
                self.door_sound = pygame.mixer.Sound(door_path)
                self.door_sound.set_volume(0.35)
        except Exception:
            self.door_sound = None
        try:
            pickaxe_path = get_path('audio', 'pickaxe_hit.wav')
            if os.path.exists(pickaxe_path):
                self.pickaxe_sound = pygame.mixer.Sound(pickaxe_path)
                self.pickaxe_sound.set_volume(0.65)
        except Exception:
            self.pickaxe_sound = None
        try:
            key_path = get_path('audio', 'key_pickup.wav')
            if os.path.exists(key_path):
                self.key_sound = pygame.mixer.Sound(key_path)
                self.key_sound.set_volume(0.36)
        except Exception:
            self.key_sound = None

    def _update_run_sound(self):
        should_play = bool(getattr(self.player, 'running', False) and self.player.direction.length() > 0)
        if not self.run_sound:
            return
        if should_play and not self.run_sound_playing:
            self.run_sound.play(loops=-1)
            self.run_sound_playing = True
        elif not should_play and self.run_sound_playing:
            self.run_sound.stop()
            self.run_sound_playing = False

    def _stop_all_sfx(self):
        if self.run_sound and self.run_sound_playing:
            self.run_sound.stop()
        self.run_sound_playing = False
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except Exception:
            pass

    def _start_soundtrack(self):
        if not pygame.mixer.get_init():
            return
        for filename in ('music.mp3', 'music.ogg', 'music.wav'):
            music_path = get_path('audio', filename)
            if os.path.exists(music_path):
                try:
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.set_volume(0.35)
                    pygame.mixer.music.play(loops=-1)
                    self.soundtrack = music_path
                    return
                except Exception:
                    continue
        self.soundtrack = None

    def _cutscene_config(self, name):
        return {
            'prolog': {'frames_dir': get_path('graphics', 'cutscenes', 'prolog'), 'audio': get_path('graphics', 'cutscenes', 'prolog_audio.wav'), 'fps': 25},
            'epilog': {'frames_dir': get_path('graphics', 'cutscenes', 'epilog'), 'audio': get_path('graphics', 'cutscenes', 'epilog_audio.wav'), 'fps': 25},
        }.get(name)

    def _draw_cutscene_frame(self, image):
        self.screen.fill((0, 0, 0))
        if image.get_size() != (SCREEN_WIDTH, SCREEN_HEIGHT):
            iw, ih = image.get_size()
            scale = min(SCREEN_WIDTH / max(1, iw), SCREEN_HEIGHT / max(1, ih))
            new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
            image = pygame.transform.smoothscale(image, new_size)
        rect = image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(image, rect)
        pygame.display.update()

    def play_cutscene(self, name):
        config = self._cutscene_config(name)
        if not config:
            return
        frames_dir = config['frames_dir']
        if not os.path.isdir(frames_dir):
            return
        frame_files = sorted(os.path.join(frames_dir, fname) for fname in os.listdir(frames_dir) if fname.lower().endswith(('.jpg', '.jpeg', '.png')))
        if not frame_files:
            return
        self._stop_all_sfx()
        audio_channel = None
        audio_path = config.get('audio')
        if audio_path and os.path.exists(audio_path) and pygame.mixer.get_init():
            try:
                audio_channel = pygame.mixer.Sound(audio_path).play()
            except Exception:
                audio_channel = None
        fps = max(1, int(config.get('fps', 24)))
        clock = pygame.time.Clock()
        skip = False
        for frame_path in frame_files:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    skip = True
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                    skip = True
            if skip:
                break
            try:
                image = pygame.image.load(frame_path).convert()
            except Exception:
                continue
            self._draw_cutscene_frame(image)
            clock.tick(fps)
        if audio_channel:
            audio_channel.stop()

    def show_notice(self, text, duration=2.0):
        self.notice_text = ''
        self.notice_timer = 0.0

    def load_assets(self):
        floor_surfs = [load_single(get_path('graphics', 'tiles', f'cave_floor_{i:02d}.png')) for i in range(1, 5)]
        wall_surfs = [load_single(get_path('graphics', 'tiles', f'cave_wall_{i:02d}.png')) for i in range(1, 4)]
        rock_surfs = import_folder(get_path('graphics', 'objects', 'monster_island_stone'))
        rock_surfs = [pygame.transform.scale(crop_alpha_surface(s), (32, 32)) for s in rock_surfs]
        if not rock_surfs:
            rock_surfs = [load_single(get_path('graphics', 'objects', f'rock_{i:02d}.png')) for i in range(1, 5)]
        rock_break = [load_single(get_path('graphics', 'effects', f'rock_break_{i:02d}.png')) for i in range(1, 5)]
        door_frames = [load_single(get_path('graphics', 'objects', f'front_door_dark_{i:02d}.png')) for i in range(1, 5)]
        door_frames = [s for s in door_frames if s]
        ladder_surf = load_single(get_path('graphics', 'objects', 'tangga.png'))
        if ladder_surf:
            ladder_surf = pygame.transform.scale(crop_alpha_surface(ladder_surf), (42, 120))
        return {
            'floors': [s for s in floor_surfs if s],
            'walls': [s for s in wall_surfs if s],
            'rocks': [s for s in rock_surfs if s],
            'rock_break': [s for s in rock_break if s],
            'door_frames': door_frames,
            'door_closed': door_frames[0] if door_frames else load_single(get_path('graphics', 'objects', 'front_door_dark_01.png')),
            'gold_key': load_single(get_path('graphics', 'objects', 'gold_key.png')),
            'pickaxe': load_single(get_path('graphics', 'objects', 'pickaxe.png')),
            'finish_ladder': ladder_surf,
            'cave_icon': load_single(get_path('graphics', 'ui', 'cave_icon.png')),
        }

    def generate_room(self, first_room=False):
        seed = self.session_seed + self.floor_number * 7919 + random.randint(1, 999)
        self.room = CaveRoom(self.floor_number, seed, self.assets)
        self.player.hitbox.center = (OFFSET_X + ROOM_WIDTH // 2, OFFSET_Y + ROOM_HEIGHT - 56)
        self.player.pos.update(self.player.hitbox.center)
        self.player.rect.center = self.player.hitbox.center
        if not first_room:
            self.show_notice('MASUK GOA BERIKUTNYA', 1.4)

    def use_tool(self):
        if self.pending_room_transition or self.game_finished:
            return
        self.tool_swing_timer = self.tool_swing_duration
        rock = self.room.nearby_rock(self.player.hitbox)
        if rock and rock.hit() and self.pickaxe_sound:
            self.pickaxe_sound.play()

    def try_use_ladder(self):
        if self.pending_room_transition or self.game_finished:
            return False
        if not self.room or not self.room.near_finish_ladder(self.player.hitbox):
            return False
        self._stop_all_sfx()
        self.play_cutscene('epilog')
        # Keluar dari goa hanya melalui interaksi tangga.
        # Level utama akan mengembalikan player ke posisi saat masuk sumur.
        self.request_exit = True
        return True

    def try_use_door(self):
        if self.pending_room_transition or self.game_finished:
            return
        if not self.player.hitbox.colliderect(self.room.door_rect.inflate(10, 10)):
            return
        if self.key_count <= 0:
            self.show_notice('KUNCI EMAS BELUM ADA', 1.4)
            return
        self.key_count -= 1
        self.pending_room_transition = True
        if self.door_sound:
            self.door_sound.play()
        self.room.start_door_animation()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # ESC tidak dipakai untuk kembali ke map utama dari goa.
            # Keluar goa hanya lewat interaksi E pada tangga keluar.
            if event.key == pygame.K_e:
                if not self.try_use_ladder():
                    self.try_use_door()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.use_tool()

    def update(self, dt):
        if self.game_finished:
            self._stop_all_sfx()
            return
        if self.notice_timer > 0:
            self.notice_timer = max(0, self.notice_timer - dt)
        if self.tool_swing_timer > 0:
            self.tool_swing_timer = max(0, self.tool_swing_timer - dt)
        self.player.update(dt, self.room.colliders())
        self._update_run_sound()
        self.room.update(dt)
        if self.pending_room_transition and self.room.update_door_animation(dt):
            self.pending_room_transition = False
            self.floor_number += 1
            self.generate_room()
            return
        if self.room.collect_key(self.player.hitbox):
            self.key_count += 1
            if self.key_sound:
                self.key_sound.play()
            self.show_notice('KUNCI EMAS DIDAPAT!', 2.0)

    def draw_tool_swing(self):
        if self.tool_swing_timer <= 0 or not self.assets.get('pickaxe'):
            return
        t = 1 - (self.tool_swing_timer / self.tool_swing_duration)
        surf = self.assets['pickaxe']
        if self.player.facing == 'left':
            surf = pygame.transform.rotate(surf, 35 - 95 * t)
            pos = (self.player.hitbox.left - 20, self.player.hitbox.centery - 20)
        elif self.player.facing == 'right':
            surf = pygame.transform.rotate(surf, -35 + 95 * t)
            pos = (self.player.hitbox.right - 4, self.player.hitbox.centery - 20)
        elif self.player.facing == 'up':
            surf = pygame.transform.rotate(surf, 50 - 100 * t)
            pos = (self.player.hitbox.centerx - 14, self.player.hitbox.top - 26)
        else:
            surf = pygame.transform.rotate(surf, -50 + 100 * t)
            pos = (self.player.hitbox.centerx - 14, self.player.hitbox.bottom - 8)
        self.screen.blit(surf, pos)

    def draw(self):
        self.screen.fill(COL_DARK_BG)
        pygame.draw.rect(self.screen, (16, 13, 11), (OFFSET_X - 10, OFFSET_Y - 10, ROOM_WIDTH + 20, ROOM_HEIGHT + 20), border_radius=16)
        self.room.draw(self.screen)
        self.player.draw(self.screen)
        self.draw_tool_swing()
        self.ui.draw_all(
            hearts=self.hearts,
            rooms_passed=max(0, self.floor_number - 1),
            key_count=self.key_count,
            energy=self.player.energy,
            energy_max=self.player.energy_max,
            notice_text=self.notice_text,
            notice_timer=self.notice_timer,
        )
