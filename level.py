
import os
import random
import pygame
from settings import *
from sprites import Generic, CameraGroup, CollideTile
from player import Player
from support import get_path

T_GRASS = 0
T_FIELD = 1
T_PATH  = 2
T_YARD  = 3
T_WATER = 4
T_SAND  = 5


def _fill_rect(grid, x, y, w, h, tile_id):
    for ty in range(y, y + h):
        if 0 <= ty < len(grid):
            for tx in range(x, x + w):
                if 0 <= tx < len(grid[0]):
                    grid[ty][tx] = tile_id


def _paint_points(grid, points, tile_id):
    for x, y in points:
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
            grid[y][x] = tile_id


def _ellipse_points(cx, cy, rx, ry):
    points = []
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if ((x - cx) ** 2) / float(rx * rx + 0.01) + ((y - cy) ** 2) / float(ry * ry + 0.01) <= 1.0:
                points.append((x, y))
    return points


def _draw_h_path(grid, x1, x2, y, width=2, tile_id=T_PATH):
    if x1 > x2:
        x1, x2 = x2, x1
    _fill_rect(grid, x1, y, x2 - x1 + 1, width, tile_id)


def _draw_v_path(grid, x, y1, y2, width=2, tile_id=T_PATH):
    if y1 > y2:
        y1, y2 = y2, y1
    _fill_rect(grid, x, y1, width, y2 - y1 + 1, tile_id)


def _distance_to_water(grid, tx, ty, max_dist=3):
    for dist in range(1, max_dist + 1):
        for ny in range(max(0, ty - dist), min(len(grid), ty + dist + 1)):
            for nx in range(max(0, tx - dist), min(len(grid[0]), tx + dist + 1)):
                if max(abs(nx - tx), abs(ny - ty)) != dist:
                    continue
                if grid[ny][nx] == T_WATER:
                    return dist
    return None


def _build_map():
    """Map pulau tanpa sungai/kolam di dalam pulau.
    Semua daratan hijau. Warna coklat hanya untuk area di dalam pagar kayu.
    """
    grid = [[T_WATER] * MAP_W for _ in range(MAP_H)]


    land_rects = [
        (8, 5, 68, 33),
        (6, 3, 18, 12),   
        (27, 3, 18, 10),  
        (55, 4, 15, 10),  
        (7, 14, 13, 10), 
        (44, 14, 27, 10), 
        (9, 24, 27, 13),  
        (52, 25, 18, 11), 
        (34, 20, 15, 10), 
        (37, 37, 3, 4),  
    ]
    for rect in land_rects:
        _fill_rect(grid, *rect, T_GRASS)

    
    coast_cuts = [
        (8, 3, 2, 3), (8, 36, 2, 2), (18, 3, 2, 2),
        (27, 3, 2, 2), (43, 3, 2, 2), (57, 4, 2, 2), (67, 4, 2, 2),
        (74, 5, 2, 5), (74, 31, 2, 4),
        (10, 37, 5, 1), (30, 37, 4, 1), (53, 36, 3, 2), (68, 36, 2, 2),
        (7, 18, 1, 4), (7, 30, 1, 3),
    ]
    for cut in coast_cuts:
        _fill_rect(grid, *cut, T_WATER)

    
    for ty in range(MAP_H):
        for tx in range(MAP_W):
            if grid[ty][tx] != T_GRASS:
                continue
            dist = _distance_to_water(grid, tx, ty, max_dist=3)
            if dist is not None and dist <= 3:
                grid[ty][tx] = T_SAND

    _fill_rect(grid, 6, 5, 18, 10, T_GRASS)
    _fill_rect(grid, 55, 5, 14, 8, T_GRASS)

    _fill_rect(grid, 11, 27, 22, 7, T_FIELD)
    _fill_rect(grid, 37, 22, 10, 6, T_FIELD)
    _fill_rect(grid, 55, 29, 12, 5, T_FIELD)
    
    _fill_rect(grid, 7, 6, 16, 8, T_FIELD)
    _fill_rect(grid, 30, 6, 7, 4, T_FIELD)
    _fill_rect(grid, 56, 6, 12, 6, T_FIELD)

    return grid


def _load_single(path, scale_to=None):
    if not os.path.exists(path):
        return None
    try:
        surf = pygame.image.load(path).convert_alpha()
    except Exception:
        return None
    if scale_to:
        surf = pygame.transform.scale(surf, scale_to)
    return surf


def _load_tile_variants(tile_dir, prefix, ids, scale_to=None):
    surfs = []
    for i in ids:
        surf = _load_single(os.path.join(tile_dir, f'{prefix}_{i:02d}.png'), scale_to)
        if surf:
            surfs.append(surf)
    return surfs


def _load_folder_scaled(path, fixed_size=None, min_size=24):
    surfs = []
    if not os.path.isdir(path):
        return surfs
    for fname in sorted(os.listdir(path)):
        if not fname.lower().endswith('.png'):
            continue
        surf = _load_single(os.path.join(path, fname))
        if not surf:
            continue
        if fixed_size:
            surf = pygame.transform.scale(surf, fixed_size)
        else:
            w, h = surf.get_size()
            scale = max(1, min_size // max(1, max(w, h)))
            surf = pygame.transform.scale(surf, (max(min_size, w * scale), max(min_size, h * scale)))
        surfs.append(surf)
    return surfs


def _choice(surfs):
    return random.choice(surfs).copy() if surfs else None


class AnimatedWater(pygame.sprite.Sprite):
    _shared_index = 0.0
    _last_ticks = 0

    @classmethod
    def step_global(cls):
        now = pygame.time.get_ticks()
        if cls._last_ticks == 0:
            cls._last_ticks = now
            return
        dt = (now - cls._last_ticks) / 1000.0
        cls._last_ticks = now
        cls._shared_index = (cls._shared_index + 2.2 * dt) % 4.0

    def __init__(self, pos, frames, groups, z=None):
        super().__init__(groups)
        self.frames = [f.copy() for f in frames]
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy()
        self.z = z if z is not None else LAYERS['ground']

    def update(self, dt):
        idx = int(AnimatedWater._shared_index) % len(self.frames)
        self.image = self.frames[idx]




class DoorSprite(pygame.sprite.Sprite):
    """Simple door sprite with changeable frames for exit animation."""

    def __init__(self, pos, frames, groups, z=None):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy()
        self.z = z if z is not None else LAYERS['objects']

    def set_frame(self, index):
        self.frame_index = max(0, min(index, len(self.frames) - 1))
        topleft = self.rect.topleft
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=topleft)
        self.hitbox = self.rect.copy()

    def reset(self):
        self.set_frame(0)

class WeatherOverlay:
    """Night and rain overlay with automatic weather."""
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.raining = False
        self.rng = random.Random(2026)
        self.drops = []
        self.splashes = []
        self.rain_sound = None
        self.rain_drops = _load_folder_scaled(get_path('graphics', 'rain', 'drops'), min_size=12)
        self.rain_floor = _load_folder_scaled(get_path('graphics', 'rain', 'floor'), min_size=16)
        for _ in range(100):
            self.drops.append([self.rng.randrange(-100, SCREEN_WIDTH + 100), self.rng.randrange(-100, SCREEN_HEIGHT), self.rng.uniform(360, 620)])
        for _ in range(36):
            self.splashes.append([self.rng.randrange(0, SCREEN_WIDTH), self.rng.randrange(0, SCREEN_HEIGHT), self.rng.uniform(0.2, 1.4)])
        try:
            rain_path = get_path('audio', 'rain.wav')
            if os.path.exists(rain_path):
                self.rain_sound = pygame.mixer.Sound(rain_path)
                self.rain_sound.set_volume(0.22)
        except Exception:
            self.rain_sound = None

    def set_rain(self, value):
        value = bool(value)
        if self.raining == value:
            return
        self.raining = value
        if self.rain_sound:
            if self.raining:
                self.rain_sound.play(loops=-1)
            else:
                self.rain_sound.stop()

    def draw_rain(self, dt):
        if not self.raining:
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
                pygame.draw.line(self.display_surface, (170, 210, 255), (int(d[0]), int(d[1])), (int(d[0] - 4), int(d[1] + 12)), 1)
        for s in self.splashes:
            s[2] -= dt
            if s[2] <= 0:
                s[0] = self.rng.randrange(0, SCREEN_WIDTH)
                s[1] = self.rng.randrange(0, SCREEN_HEIGHT)
                s[2] = self.rng.uniform(0.2, 1.4)
            if self.rain_floor:
                self.display_surface.blit(self.rng.choice(self.rain_floor), (int(s[0]), int(s[1])))

    def draw_darkness(self, alpha):
        if alpha <= 0:
            return
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 18, 48, int(alpha)))
        self.display_surface.blit(overlay, (0, 0))


class GameClock:
    """Stardew-like day widget and automatic day phase."""
    def __init__(self):
        self.day = 1
        self.hour = 6
        self.minute = 0
        self._accum = 0.0
        self.minute_seconds_normal = 1.8
        self.minute_seconds_fast = 0.18
        self.time_speed_fast = False
        self.minute_seconds = self.minute_seconds_normal
        self.rng = random.Random()
        self.weather_roll = random.Random(5077)
        self.is_rainy_day = self.weather_roll.random() < 0.35
        self.font_big = pygame.font.Font(get_path('font', 'LycheeSoda.ttf'), 26) if os.path.exists(get_path('font', 'LycheeSoda.ttf')) else pygame.font.Font(None, 30)
        self.font_small = pygame.font.Font(get_path('font', 'LycheeSoda.ttf'), 20) if os.path.exists(get_path('font', 'LycheeSoda.ttf')) else pygame.font.Font(None, 22)

    def toggle_speed(self):
        self.time_speed_fast = not self.time_speed_fast
        self.minute_seconds = self.minute_seconds_fast if self.time_speed_fast else self.minute_seconds_normal

    def update(self, dt):
        self._accum += dt
        while self._accum >= self.minute_seconds:
            self._accum -= self.minute_seconds
            self.minute += 5
            if self.minute >= 60:
                self.minute = 0
                self.hour += 1
            if self.hour >= 24:
                self.hour = 6
                self.minute = 0
                self.day += 1
                self.is_rainy_day = self.weather_roll.random() < 0.35

    def phase(self):
        h = self.hour
        if 6 <= h < 11:
            return 'Pagi'
        if 11 <= h < 15:
            return 'Siang'
        if 15 <= h < 18:
            return 'Sore'
        return 'Malam'

    def darkness_alpha(self):
        h = self.hour + self.minute / 60
        if 6 <= h < 16:
            return 0
        if 16 <= h < 18:
            return int((h - 16) / 2 * 58)
        if 18 <= h < 20:
            return int(58 + (h - 18) / 2 * 78)
        return 138

    def time_text(self):
        return f'{self.hour:02d}:{self.minute:02d}'

    def _draw_phase_icon(self, surface, icon_x, icon_y):
        phase = self.phase().lower()
        sky = pygame.Rect(icon_x - 4, icon_y - 2, 56, 48)
        pygame.draw.rect(surface, (248, 222, 134), sky, border_radius=8)
        mountain_dark = (94, 117, 76)
        mountain_light = (128, 153, 92)
        sun = (255, 191, 59)
        moon = (238, 232, 177)

        if phase == 'malam':
            pygame.draw.rect(surface, (56, 72, 118), sky, border_radius=8)
            pygame.draw.circle(surface, moon, (icon_x + 27, icon_y + 16), 13)
            pygame.draw.circle(surface, (56, 72, 118), (icon_x + 33, icon_y + 12), 13)
            pygame.draw.circle(surface, (238, 232, 177), (icon_x + 13, icon_y + 10), 1)
            pygame.draw.circle(surface, (238, 232, 177), (icon_x + 44, icon_y + 8), 1)
        elif phase == 'pagi':
            pygame.draw.circle(surface, sun, (icon_x + 24, icon_y + 34), 14)
        elif phase == 'sore':
            pygame.draw.circle(surface, (244, 139, 45), (icon_x + 26, icon_y + 34), 14)
        else:
            pygame.draw.circle(surface, sun, (icon_x + 24, icon_y + 18), 15)

        pygame.draw.polygon(surface, mountain_light, [(icon_x - 2, icon_y + 44), (icon_x + 15, icon_y + 23), (icon_x + 34, icon_y + 44)])
        pygame.draw.polygon(surface, mountain_dark, [(icon_x + 18, icon_y + 44), (icon_x + 39, icon_y + 19), (icon_x + 58, icon_y + 44)])
        pygame.draw.rect(surface, (102, 70, 43), (icon_x - 4, icon_y + 41, 56, 6), border_radius=3)

        if self.is_rainy_day:
            pygame.draw.ellipse(surface, (116, 145, 170), (icon_x + 7, icon_y + 4, 35, 18))
            pygame.draw.ellipse(surface, (137, 161, 184), (icon_x + 19, icon_y, 25, 19))
            for dx in (12, 25, 38):
                pygame.draw.line(surface, (45, 91, 158), (icon_x + dx, icon_y + 26), (icon_x + dx - 4, icon_y + 38), 2)

    def draw(self, surface):
        w, h = 190, 104
        x, y = SCREEN_WIDTH - w - 16, 14
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((244, 214, 143, 235))
        pygame.draw.rect(panel, (119, 74, 34), panel.get_rect(), 4, border_radius=12)
        pygame.draw.rect(panel, (255, 239, 177), pygame.Rect(8, 8, w - 16, h - 16), 2, border_radius=10)
        surface.blit(panel, (x, y))

        day_txt = self.font_small.render(f'Hari {self.day}', True, (78, 43, 20))
        time_txt = self.font_big.render(self.time_text(), True, (54, 31, 18))
        phase_txt = self.font_small.render(self.phase(), True, (78, 43, 20))
        speed_label = ' x10' if self.time_speed_fast else ''
        weather_txt = self.font_small.render(('Hujan' if self.is_rainy_day else 'Cerah') + speed_label, True, (43, 64, 85))
        surface.blit(day_txt, (x + 18, y + 14))
        surface.blit(time_txt, (x + 18, y + 39))
        surface.blit(phase_txt, (x + 18, y + 75))
        surface.blit(weather_txt, (x + 105, y + 75))

        self._draw_phase_icon(surface, x + 126, y + 15)


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.random = random.Random(33)
        self._start_music()

        tiles_dir = get_path('graphics', 'tiles')
        obj_dir = get_path('graphics', 'objects')

        self._water_surfs = _load_folder_scaled(os.path.join(tiles_dir, 'water_anim'), fixed_size=(TILE_SIZE, TILE_SIZE))
        if not self._water_surfs:
            fallback = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            fallback.fill((120, 200, 220))
            self._water_surfs = [fallback]
        self._sand_surfs = _load_folder_scaled(os.path.join(tiles_dir, 'beach'), fixed_size=(TILE_SIZE, TILE_SIZE))
        if not self._sand_surfs:
            self._sand_surfs = self._make_beach_tiles()
        self._grass_surfs = _load_tile_variants(tiles_dir, 'FieldsTile', [38], (TILE_SIZE, TILE_SIZE))
        self._field_surfs = _load_tile_variants(tiles_dir, 'FieldsTile', range(1, 38), (TILE_SIZE, TILE_SIZE))
        self._path_surfs = _load_tile_variants(tiles_dir, 'FieldsTile', [46,47,48,49,50,51,52,53,54,55,56], (TILE_SIZE, TILE_SIZE))
        self._yard_surfs = _load_tile_variants(tiles_dir, 'FieldsTile', [57,58,59,60,61,62,63,64], (TILE_SIZE, TILE_SIZE))

        self._fence_h = _load_single(os.path.join(tiles_dir, 'Tile2_05.png'), (TILE_SIZE, TILE_SIZE))
        self._fence_v = _load_single(os.path.join(tiles_dir, 'Tile2_06.png'), (TILE_SIZE, TILE_SIZE))
        self._fence_post = _load_single(os.path.join(tiles_dir, 'Tile2_01.png'), (TILE_SIZE, TILE_SIZE))

        self._houses = _load_folder_scaled(os.path.join(obj_dir, '7_House'), fixed_size=(TILE_SIZE * 5, TILE_SIZE * 5))
        self._tents = _load_folder_scaled(os.path.join(obj_dir, '6_Tent'), fixed_size=(TILE_SIZE * 3, TILE_SIZE * 3))
        self._stones = _load_folder_scaled(os.path.join(obj_dir, '2_Stone'), fixed_size=(TILE_SIZE, TILE_SIZE))
        self._decor = _load_folder_scaled(os.path.join(obj_dir, '3_Decor'), min_size=28)
        self._grass_objs = _load_folder_scaled(os.path.join(obj_dir, '5_Grass'), min_size=18)
        self._boxes = _load_folder_scaled(os.path.join(obj_dir, '4_Box'), fixed_size=(TILE_SIZE, TILE_SIZE))
       
        self._tree_small = _load_single(os.path.join(obj_dir, 'pydew_trees', 'tree_small_dark.png'), (54, 98)) or _load_single(os.path.join(obj_dir, 'pydew_trees', 'tree_small.png'), (54, 98))
        self._tree_medium = _load_single(os.path.join(obj_dir, 'pydew_trees', 'tree_medium_dark.png'), (72, 108)) or _load_single(os.path.join(obj_dir, 'pydew_trees', 'tree_medium.png'), (72, 108))
        self._dungeon_well = _load_single(os.path.join(obj_dir, 'dungeon_well.png'), (TILE_SIZE * 2, TILE_SIZE * 2))

        self.weather = WeatherOverlay()
        self.clock_ui = GameClock()
        self._ui_face = _load_single(get_path('graphics', 'ui', 'character_face.png'), (54, 48))
        self.door_sound = None
        try:
            door_sound_path = get_path('audio', 'door_open.wav')
            if os.path.exists(door_sound_path):
                self.door_sound = pygame.mixer.Sound(door_sound_path)
                self.door_sound.set_volume(0.35)
        except Exception:
            self.door_sound = None
        self.weather.set_rain(self.clock_ui.is_rainy_day)
        self.mode = 'outside'
        self._setup()
        self._setup_interior()

    def _land_at(self, tx, ty):
        if not (0 <= ty < len(self.grid) and 0 <= tx < len(self.grid[0])):
            return False
        return self.grid[ty][tx] != T_WATER

    def _area_land(self, tx, ty, w=1, h=1):
        for yy in range(ty, ty + h):
            for xx in range(tx, tx + w):
                if not self._land_at(xx, yy):
                    return False
        return True

    def _choose_tile(self, tile_id):
        pools = {
            T_GRASS: self._grass_surfs,
            T_FIELD: self._field_surfs,
            T_PATH: self._path_surfs,
            T_YARD: self._yard_surfs,
            T_SAND: self._sand_surfs,
        }
        lst = pools.get(tile_id) or self._grass_surfs or self._sand_surfs or self._path_surfs or self._yard_surfs or self._field_surfs
        if not lst:
            raise RuntimeError('Tile asset tidak ditemukan. Cek folder graphics/tiles.')
        return self.random.choice(lst).copy()

    def _make_beach_tiles(self):
        tiles = []
        palettes = [
            ((230, 203, 142), (214, 182, 120), (242, 221, 170)),
            ((224, 196, 136), (207, 176, 116), (236, 214, 162)),
            ((235, 208, 148), (218, 186, 126), (246, 224, 174)),
        ]
        for base, dot, shell in palettes:
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            surf.fill(base)
            for y in range(0, TILE_SIZE, 4):
                for x in range(0, TILE_SIZE, 4):
                    if (x + y) % 8 == 0:
                        surf.set_at((x, y), dot)
                    elif (x * 3 + y) % 11 == 0:
                        surf.set_at((x, y), shell)
            tiles.append(surf)
        return tiles

    def _place_object(self, pos, surf, collision=True, collision_size=None, z=LAYERS['objects']):
        if not surf:
            return
        Generic(pos, surf, self.all_sprites, z=z)
        if collision:
            if collision_size is None:
                collision_size = (surf.get_width(), max(12, surf.get_height() - 12))
            CollideTile(pos, collision_size, self.collision_sprites)

    def _setup(self):
        self.grid = _build_map()
        for ty, row in enumerate(self.grid):
            for tx, tile_id in enumerate(row):
                pos = (tx * TILE_SIZE, ty * TILE_SIZE)
                if tile_id == T_WATER:
                    AnimatedWater(pos, self._water_surfs, self.all_sprites, z=LAYERS['ground'])
                    CollideTile(pos, (TILE_SIZE, TILE_SIZE), self.collision_sprites)
                else:
                    Generic(pos, self._choose_tile(tile_id), self.all_sprites, z=LAYERS['ground'])

        self._place_houses()
        self._place_market()
        self._place_fences_and_fields()
        self._place_trees()
        self._place_details()
        self._place_land_stones()
        self.player = Player((SPAWN_X, SPAWN_Y), self.all_sprites, self.collision_sprites)
        self.house_door_rect = pygame.Rect(11 * TILE_SIZE, 9 * TILE_SIZE, TILE_SIZE * 2, TILE_SIZE + 20)

    def _house(self, idx):
        return self._houses[idx % len(self._houses)].copy() if self._houses else None

    def _tent(self, idx):
        return self._tents[idx % len(self._tents)].copy() if self._tents else None

    def _place_houses(self):
        
        houses = [
            (9, 4, 3, True),   
            (28, 5, 1, False),  
            (8, 15, 2, False),  
            (59, 6, 0, False),  
        ]
        for tx, ty, idx, is_main in houses:
            surf = self._house(idx)
            if not surf:
                continue
            if is_main:
                surf = pygame.transform.scale(surf, (TILE_SIZE * 6, TILE_SIZE * 6))
                collision_size = (TILE_SIZE * 5, TILE_SIZE * 5)
                land_check = (5, 5)
            else:
                collision_size = (TILE_SIZE * 4, TILE_SIZE * 4)
                land_check = (4, 3)
            if self._area_land(tx, ty + 2, land_check[0], land_check[1]):
                self._place_object((tx * TILE_SIZE, ty * TILE_SIZE), surf, collision=True, collision_size=collision_size)

    def _place_market(self):
        for i, (tx, ty) in enumerate([(49, 15), (55, 15), (60, 15), (65, 15)]):
            if self._area_land(tx, ty + 1, 3, 2):
                self._place_object((tx * TILE_SIZE, ty * TILE_SIZE), self._tent(i), collision=True, collision_size=(TILE_SIZE * 3, TILE_SIZE * 2))

    def _fence_piece(self, tx, ty, surf):
        if not surf or not self._land_at(tx, ty):
            return
        pos = (tx * TILE_SIZE, ty * TILE_SIZE)
        Generic(pos, surf.copy(), self.all_sprites, z=LAYERS['objects'])
        CollideTile(pos, (TILE_SIZE, TILE_SIZE), self.collision_sprites)

    def _fence_rect(self, x, y, w, h, gate_tiles=None):
        gate_tiles = set(gate_tiles or [])
        for tx in range(x, x + w):
            if (tx, y - 1) not in gate_tiles:
                self._fence_piece(tx, y - 1, self._fence_h)
            if (tx, y + h) not in gate_tiles:
                self._fence_piece(tx, y + h, self._fence_h)
        for ty in range(y, y + h):
            if (x - 1, ty) not in gate_tiles:
                self._fence_piece(x - 1, ty, self._fence_v)
            if (x + w, ty) not in gate_tiles:
                self._fence_piece(x + w, ty, self._fence_v)
        for p in [(x - 1, y - 1), (x + w, y - 1), (x - 1, y + h), (x + w, y + h)]:
            self._fence_piece(p[0], p[1], self._fence_post)

    def _place_crop(self, tx, ty):
        if not self._land_at(tx, ty):
            return
        surf = _choice(self._grass_objs)
        if surf:
            Generic((tx * TILE_SIZE + 8, ty * TILE_SIZE + 10), surf, self.all_sprites, z=LAYERS['objects'])

    def _rect_intersects(self, a, b):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by

    def _tree_area_blocked(self, tx, ty):
        
        tree_footprint = (tx - 1, ty - 1, 4, 5)
        blocked_rects = [
            (6, 5, 18, 10),   
            (28, 5, 10, 6),   
            (55, 5, 14, 8),    
            (44, 12, 33, 14), 
            (7, 14, 15, 9),    
            (11, 13, 8, 5),    
        ]
        return any(self._rect_intersects(tree_footprint, rect) for rect in blocked_rects)

    def _place_fences_and_fields(self):
        self._fence_rect(10, 26, 24, 8, gate_tiles=[(20, 34), (21, 34), (34, 29), (34, 30)])
        self._fence_rect(36, 22, 11, 6, gate_tiles=[(41, 21), (42, 21), (47, 25)])
        self._fence_rect(55, 28, 12, 6, gate_tiles=[(61, 27), (62, 27), (67, 30), (67, 31)])
  
        self._fence_rect(7, 6, 16, 8, gate_tiles=[(12, 14), (13, 14), (14, 14)])
        self._fence_rect(29, 6, 8, 4, gate_tiles=[(33, 10), (34, 10)])
        self._fence_rect(56, 6, 12, 6, gate_tiles=[(61, 12), (62, 12), (63, 12)])

        for y in range(27, 33):
            for x in range(11, 33):
                if x % 2 == 0:
                    self._place_crop(x, y)
        for y in range(29, 33):
            for x in range(56, 66):
                if x % 2 == 0:
                    self._place_crop(x, y)

    def _place_tree(self, tx, ty, medium=False, occupied_rects=None):
        if not (0 <= tx < MAP_W and 0 <= ty < MAP_H):
            return False
        if self.grid[ty][tx] in (T_WATER, T_FIELD):
            return False
        if self._tree_area_blocked(tx, ty):
            return False

        if not self._area_land(max(0, tx), max(0, ty + 1), 2, 2):
            return False

        tree_footprint = (tx - 1, ty - 1, 2, 3)
        if occupied_rects is not None:
            if any(self._rect_intersects(tree_footprint, rect) for rect in occupied_rects):
                return False

        surf = self._tree_medium if medium else self._tree_small
        if not surf:
            return False
        pos = (tx * TILE_SIZE, ty * TILE_SIZE)
        Generic(pos, surf.copy(), self.all_sprites, z=LAYERS['objects'])
        hit_w = 26 if medium else 20
        hit_h = 18
        offset_x = (surf.get_width() - hit_w) // 2
        offset_y = surf.get_height() - hit_h - 5
        CollideTile((pos[0] + offset_x, pos[1] + offset_y), (hit_w, hit_h), self.collision_sprites)
        if occupied_rects is not None:
            occupied_rects.append(tree_footprint)
        return True

    def _place_trees(self):

        occupied_rects = []
        medium = [
            (27, 14), (33, 14), (40, 14),
            (16, 20), (24, 20), (31, 20),
            (18, 36), (26, 36), (34, 36), (50, 36), (58, 36), (66, 35),
            (24, 12), (72, 14), (72, 20), (14, 23), (40, 29), (72, 29), (44, 34)
        ]
        small = [
            (12, 15), (15, 15), (18, 15), (30, 15), (36, 15),
            (13, 18), (19, 18), (27, 18), (35, 18),
            (12, 22), (20, 22), (28, 22),
            (15, 25), (20, 25), (25, 25), (30, 25), (47, 25), (50, 25),
            (14, 34), (22, 34), (30, 34), (54, 34), (60, 34), (65, 33),
            (39, 17), (40, 20), (37, 24), (72, 24), (70, 28), (68, 30),
            (42, 32), (46, 33), (72, 33), (32, 22), (24, 24), (10, 24)
        ]
        for tx, ty in medium:
            self._place_tree(tx, ty, True, occupied_rects)
        for tx, ty in small:
            self._place_tree(tx, ty, False, occupied_rects)

     
        tree_random = random.Random(91)
        extra_candidates = []
        for ty in range(4, 39, 2):
            xs = list(range(7, 76, 3))
            tree_random.shuffle(xs)
            for tx in xs:
                extra_candidates.append((tx + tree_random.choice([-1, 0, 1]), ty + tree_random.choice([-1, 0, 1])))

        extra_total = 0
        for idx, (tx, ty) in enumerate(extra_candidates):
            if extra_total >= 65:
                break
            use_medium = idx % 4 == 0
            if self._place_tree(tx, ty, use_medium, occupied_rects):
                extra_total += 1

    def _stone_area_blocked(self, tx, ty):
        blocked_rects = [
            (6, 5, 18, 10),   
            (55, 5, 14, 8),   
        ]
        point_rect = (tx, ty, 1, 1)
        return any(self._rect_intersects(point_rect, rect) for rect in blocked_rects)

    def _place_details(self):
        box_spots = [(20, 9), (24, 10), (31, 9), (36, 9), (50, 18), (56, 18), (61, 18), (66, 18), (39, 23), (44, 23), (18, 28), (58, 30)]
        for tx, ty in box_spots:
            if self._land_at(tx, ty):
                surf = _choice(self._boxes)
                self._place_object((tx * TILE_SIZE, ty * TILE_SIZE), surf, collision=True, collision_size=(TILE_SIZE, TILE_SIZE))

        decor_spots = [(17, 10), (19, 11), (30, 9), (34, 9), (37, 10), (43, 18), (48, 18), (52, 18), (58, 18), (64, 18), (40, 24), (42, 24), (60, 20)]
        for tx, ty in decor_spots:
            if self._land_at(tx, ty):
                surf = _choice(self._decor)
                if surf:
                    Generic((tx * TILE_SIZE + 4, ty * TILE_SIZE + 6), surf, self.all_sprites, z=LAYERS['objects'])

        
        sea_stone_spots = [
            (4, 8), (5, 9), (3, 11), (5, 13), (4, 16), (5, 18), (3, 21),
            (4, 24), (5, 27), (4, 31), (6, 35),
            (14, 2), (19, 2), (25, 2), (32, 2), (39, 2), (46, 2), (53, 2), (60, 2), (67, 2),
            (72, 5), (73, 8), (72, 12), (73, 16), (72, 20), (73, 24), (72, 28), (73, 32), (72, 35),
            (77, 9), (78, 14), (79, 20), (78, 27), (77, 33),
            (12, 39), (18, 39), (24, 39), (30, 39), (45, 39), (51, 39), (58, 39), (65, 39),
            (7, 37), (9, 38), (70, 37), (68, 38), (55, 37), (41, 38)
        ]
        coast_stone_spots = [(43, 11), (12, 20), (28, 20), (40, 35)]
        for tx, ty in sea_stone_spots + coast_stone_spots:
          
            if self._stone_area_blocked(tx, ty):
                continue
            if (tx, ty) in sea_stone_spots and self._land_at(tx, ty):
                continue
            surf = _choice(self._stones)
            if surf:
                Generic((tx * TILE_SIZE + self.random.randint(0, 8), ty * TILE_SIZE + self.random.randint(0, 8)), surf, self.all_sprites, z=LAYERS['objects'])

        grass_spots = [(9, 12), (13, 13), (17, 14), (26, 13), (32, 13), (41, 12), (49, 12), (56, 12), (64, 13), (18, 23), (24, 23), (33, 23), (48, 24), (65, 24)]
        for tx, ty in grass_spots:
            if self._land_at(tx, ty):
                surf = _choice(self._grass_objs)
                if surf:
                    Generic((tx * TILE_SIZE + self.random.randint(4, 10), ty * TILE_SIZE + self.random.randint(4, 10)), surf, self.all_sprites, z=LAYERS['objects'])

    def _place_land_stones(self):
        stone_spots = [
            (18, 12), (22, 12), (41, 12), (46, 13), (51, 12),
            (14, 18), (20, 18), (25, 19), (32, 18), (38, 18), (58, 18),
            (14, 23), (20, 23), (27, 23), (33, 23), (44, 23), (49, 23), (63, 23),
            (15, 35), (21, 35), (27, 35), (35, 35), (42, 35), (48, 35), (56, 35), (63, 35),
            (60, 26), (66, 27)
        ]
        for tx, ty in stone_spots:
            if self._land_at(tx, ty) and self.grid[ty][tx] != T_FIELD:
                surf = _choice(self._stones)
                if surf:
                    self._place_object((tx * TILE_SIZE + 3, ty * TILE_SIZE + 4), surf, collision=True, collision_size=(max(18, surf.get_width() - 6), max(14, surf.get_height() - 8)))

    def _place_dungeon_well(self):
        if not self._dungeon_well:
            return
        tx, ty = 35, 23
        pos = (tx * TILE_SIZE, ty * TILE_SIZE)
        self._place_object(pos, self._dungeon_well.copy(), collision=True, collision_size=(TILE_SIZE * 2 - 10, TILE_SIZE + 18))

    def _crop_decoration(self, rect, scale=1):
        sheet = _load_single(get_path('graphics', 'objects', 'House Decoration.png'))
        if not sheet:
            return None
        surf = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        surf.blit(sheet, (0, 0), rect)
        if scale != 1:
            surf = pygame.transform.scale(surf, (int(rect[2] * scale), int(rect[3] * scale)))
        return surf

    def _make_interior_tile(self, color, border=None):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill(color)
        if border:
            pygame.draw.rect(surf, border, surf.get_rect(), 1)
        return surf

    def _make_interior_door_zone(self):
        surf = pygame.Surface((TILE_SIZE * 2, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, (148, 95, 58), (0, 8, TILE_SIZE * 2, TILE_SIZE - 8), border_radius=6)
        pygame.draw.rect(surf, (198, 144, 97), (4, 12, TILE_SIZE * 2 - 8, TILE_SIZE - 16), 2, border_radius=4)
        return surf

    def _load_interior_asset(self, filename, size=None, fallback=None):
        surf = _load_single(get_path('graphics', 'interior', filename), size)
        if surf:
            return surf
        return fallback

    def _place_interior_object(self, pos, surf, collision=True, collision_size=None):
        if not surf:
            return
        Generic(pos, surf, self.interior_sprites, z=LAYERS['objects'])
        if collision:
            if collision_size is None:
                collision_size = (surf.get_width(), max(12, surf.get_height() - 6))
            CollideTile(pos, collision_size, self.interior_collision_sprites)

    def _make_light_wall_tile(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill((205, 173, 121))
        for y in range(0, TILE_SIZE, 8):
            pygame.draw.line(surf, (194, 159, 110), (0, y), (TILE_SIZE, y), 1)
        pygame.draw.rect(surf, (159, 126, 81), surf.get_rect(), 1)
        return surf

    def _make_exit_door_frames(self):
        base = pygame.Surface((TILE_SIZE * 2, TILE_SIZE * 2), pygame.SRCALPHA)

        def draw_frame(kind):
            surf = base.copy()
            pygame.draw.rect(surf, (102, 67, 33), (10, 4, 44, 58), border_radius=4)
            pygame.draw.rect(surf, (184, 136, 84), (14, 8, 36, 50), border_radius=3)
            pygame.draw.rect(surf, (120, 79, 42), (18, 12, 28, 40), border_radius=2)
            pygame.draw.rect(surf, (199, 151, 101), (18, 34, 28, 14), 2, border_radius=2)
            pygame.draw.rect(surf, (199, 151, 101), (18, 16, 28, 12), 2, border_radius=2)
            if kind == 'closed':
                pygame.draw.rect(surf, (132, 88, 47), (18, 12, 28, 40), border_radius=2)
                pygame.draw.rect(surf, (184, 136, 84), (21, 16, 22, 12), 2, border_radius=2)
                pygame.draw.rect(surf, (184, 136, 84), (21, 34, 22, 12), 2, border_radius=2)
                pygame.draw.circle(surf, (227, 191, 93), (40, 32), 2)
            elif kind == 'mid':
                points = [(21, 12), (40, 17), (40, 51), (21, 46)]
                pygame.draw.polygon(surf, (132, 88, 47), points)
                pygame.draw.lines(surf, (184, 136, 84), True, points, 2)
                pygame.draw.circle(surf, (227, 191, 93), (36, 32), 2)
                pygame.draw.polygon(surf, (60, 38, 15), [(20, 14), (26, 16), (26, 44), (20, 46)])
            else:
                points = [(18, 12), (28, 18), (28, 48), (18, 52)]
                pygame.draw.polygon(surf, (132, 88, 47), points)
                pygame.draw.lines(surf, (184, 136, 84), True, points, 2)
                pygame.draw.circle(surf, (227, 191, 93), (25, 33), 2)
                pygame.draw.rect(surf, (42, 24, 9), (31, 14, 17, 36), border_radius=2)
            return surf

        return [draw_frame('closed'), draw_frame('mid'), draw_frame('open')]

    def _setup_interior(self):
        self.interior_w = 24
        self.interior_h = 18
        self.interior_sprites = CameraGroup(
            world_width=self.interior_w * TILE_SIZE,
            world_height=self.interior_h * TILE_SIZE,
            background_color=(0, 0, 0),
            center_small_world=True,
        )
        self.interior_collision_sprites = pygame.sprite.Group()

        floor = self._load_interior_asset('wood_floor_tile.png', (TILE_SIZE, TILE_SIZE), self._make_interior_tile((176, 122, 72), (140, 95, 52)))
        light_wall = self._make_light_wall_tile()
        trim = self._make_interior_tile((166, 112, 67), (128, 84, 45))

        for ty in range(self.interior_h):
            for tx in range(self.interior_w):
                if ty < 3:
                    surf = light_wall
                elif ty == 3:
                    surf = trim
                else:
                    surf = floor
                Generic((tx * TILE_SIZE, ty * TILE_SIZE), surf.copy(), self.interior_sprites, z=LAYERS['ground'])

        for tx in range(self.interior_w):
            CollideTile((tx * TILE_SIZE, 0), (TILE_SIZE, TILE_SIZE), self.interior_collision_sprites)
            CollideTile((tx * TILE_SIZE, (self.interior_h - 1) * TILE_SIZE), (TILE_SIZE, TILE_SIZE), self.interior_collision_sprites)
        for ty in range(self.interior_h):
            CollideTile((0, ty * TILE_SIZE), (TILE_SIZE, TILE_SIZE), self.interior_collision_sprites)
            CollideTile(((self.interior_w - 1) * TILE_SIZE, ty * TILE_SIZE), (TILE_SIZE, TILE_SIZE), self.interior_collision_sprites)

        self._place_interior_object((3 * TILE_SIZE, 5 * TILE_SIZE), self._crop_decoration((0, 96, 64, 96), 1.2), True, (62, 78))
        self._place_interior_object((7 * TILE_SIZE, 5 * TILE_SIZE), self._crop_decoration((64, 96, 64, 96), 1.2), True, (62, 78))
        self._place_interior_object((13 * TILE_SIZE, 5 * TILE_SIZE), self._crop_decoration((192, 128, 64, 64), 1.15), True, (70, 60))
        self._place_interior_object((16 * TILE_SIZE, 6 * TILE_SIZE), self._crop_decoration((320, 128, 32, 64), 1.1), True, (35, 55))
        self._place_interior_object((18 * TILE_SIZE, 6 * TILE_SIZE), self._crop_decoration((384, 128, 64, 64), 1.05), True, (62, 52))
        self._place_interior_object((5 * TILE_SIZE, 12 * TILE_SIZE), self._crop_decoration((0, 320, 96, 64), 1.1), False)
        self._place_interior_object((12 * TILE_SIZE, 12 * TILE_SIZE), self._crop_decoration((304, 320, 128, 64), 1.0), False)
        self._place_interior_object((18 * TILE_SIZE, 12 * TILE_SIZE), self._crop_decoration((464, 320, 112, 64), 0.95), False)

        self.exit_center_x = 11 * TILE_SIZE
        self.exit_center_y = 15 * TILE_SIZE
        self.exit_interact_rect = pygame.Rect(self.exit_center_x - 2, 14 * TILE_SIZE + 8, TILE_SIZE * 2 + 4, TILE_SIZE + 12)

        self.interior_door_frames = self._make_exit_door_frames()
        self.interior_door_sprite = DoorSprite((self.exit_center_x, self.exit_center_y), self.interior_door_frames, self.interior_sprites, z=LAYERS['objects'])
        self._interior_door_block = CollideTile((self.exit_center_x + 10, self.exit_center_y + 10), (TILE_SIZE * 2 - 20, TILE_SIZE * 2 - 12), self.interior_collision_sprites)

        self.interior_player = Player((12 * TILE_SIZE, 14 * TILE_SIZE), self.interior_sprites, self.interior_collision_sprites)
        self.exit_animating = False
        self.exit_anim_elapsed = 0.0

    def _fade_transition(self):
        fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade.fill((0, 0, 0))
        for alpha in range(0, 230, 28):
            fade.set_alpha(alpha)
            self.display_surface.blit(fade, (0, 0))
            pygame.display.update()
            pygame.time.delay(14)

    def _enter_house(self):
        self._fade_transition()
        self.mode = 'inside'
        self.exit_animating = False
        self.exit_anim_elapsed = 0.0
        if hasattr(self, 'interior_door_sprite'):
            self.interior_door_sprite.reset()
        self.interior_player.rect.center = (12 * TILE_SIZE, 14 * TILE_SIZE)
        self.interior_player.hitbox.center = self.interior_player.rect.center
        self.interior_player.pos.update(self.interior_player.rect.center)

    def _exit_house(self):
        self._fade_transition()
        self.mode = 'outside'
        self.exit_animating = False
        self.exit_anim_elapsed = 0.0
        if hasattr(self, 'interior_door_sprite'):
            self.interior_door_sprite.reset()
        self.player.rect.center = (12 * TILE_SIZE, 10 * TILE_SIZE)
        self.player.hitbox.center = self.player.rect.center
        self.player.pos.update(self.player.rect.center)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k:
                self.clock_ui.toggle_speed()
            if event.key == pygame.K_e:
                if self.mode == 'outside' and self.house_door_rect.colliderect(self.player.hitbox):
                    self._enter_house()
                elif self.mode == 'inside' and self.exit_interact_rect.colliderect(self.interior_player.hitbox) and not self.exit_animating:
                    self.exit_animating = True
                    self.exit_anim_elapsed = 0.0
                    if self.door_sound:
                        self.door_sound.play()

        ctrl_pressed = pygame.key.get_mods() & pygame.KMOD_CTRL
        if not ctrl_pressed:
            return
        active_group = self.interior_sprites if self.mode == 'inside' else self.all_sprites
        if event.type == pygame.MOUSEWHEEL:
            active_group.change_zoom(event.y)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                active_group.change_zoom(1)
            elif event.button == 5:
                active_group.change_zoom(-1)
            elif event.button == 2:
                active_group.reset_zoom()

    def _draw_player_status(self):
        player = self.interior_player if self.mode == 'inside' else self.player
        panel = pygame.Surface((292, 58), pygame.SRCALPHA)
        panel.fill((255, 221, 128, 232))
        pygame.draw.rect(panel, (125, 75, 28), panel.get_rect(), 4, border_radius=10)
        pygame.draw.rect(panel, (255, 243, 177), pygame.Rect(6, 6, 280, 46), 2, border_radius=8)
        self.display_surface.blit(panel, (14, 14))

        pygame.draw.rect(self.display_surface, (95, 58, 31), (21, 20, 58, 50), border_radius=8)
        pygame.draw.rect(self.display_surface, (255, 238, 173), (24, 23, 52, 44), 2, border_radius=7)
        if self._ui_face:
            self.display_surface.blit(self._ui_face, (23, 23))
        else:
            face = pygame.Surface((42, 42), pygame.SRCALPHA)
            pygame.draw.rect(face, (247, 208, 154), (9, 12, 24, 24), border_radius=8)
            pygame.draw.polygon(face, (230, 233, 234), [(7, 14), (16, 4), (28, 5), (35, 13), (30, 12), (21, 10), (13, 15)])
            pygame.draw.circle(face, (28, 30, 38), (17, 23), 2)
            pygame.draw.circle(face, (28, 30, 38), (27, 23), 2)
            self.display_surface.blit(face, (28, 25))

        for i in range(7):
            x = 76 + i * 30
            y = 29
            pygame.draw.circle(self.display_surface, (216, 42, 55), (x + 7, y + 7), 7)
            pygame.draw.circle(self.display_surface, (216, 42, 55), (x + 17, y + 7), 7)
            pygame.draw.polygon(self.display_surface, (216, 42, 55), [(x + 1, y + 10), (x + 23, y + 10), (x + 12, y + 25)])
            pygame.draw.circle(self.display_surface, (255, 124, 132), (x + 8, y + 5), 2)

        bar_w, bar_h = 34, 172
        x = SCREEN_WIDTH - 58
        y = SCREEN_HEIGHT - bar_h - 28
        pygame.draw.rect(self.display_surface, (185, 94, 19), (x, y, bar_w, bar_h), border_radius=8)
        pygame.draw.rect(self.display_surface, (255, 197, 43), (x + 4, y + 4, bar_w - 8, bar_h - 8), border_radius=6)
        inner = pygame.Rect(x + 9, y + 23, bar_w - 18, bar_h - 34)
        pygame.draw.rect(self.display_surface, (55, 110, 49), inner, border_radius=4)
        fill_h = int(inner.height * (player.energy / max(1, player.energy_max)))
        fill_rect = pygame.Rect(inner.x + 2, inner.bottom - fill_h + 2, inner.width - 4, max(0, fill_h - 4))
        pygame.draw.rect(self.display_surface, (88, 231, 70), fill_rect, border_radius=3)
        pygame.draw.rect(self.display_surface, (113, 70, 24), (x + 8, y - 17, 18, 24), border_radius=4)
        font = self.clock_ui.font_small
        txt = font.render('E', True, (69, 38, 16))
        self.display_surface.blit(txt, (x + 12, y - 14))

    def _draw_inventory_bar(self):
        slots = 10
        slot_size = 42
        gap = 6
        pad = 8
        frame_w = slots * slot_size + (slots - 1) * gap + pad * 2
        frame_h = slot_size + pad * 2
        x = (SCREEN_WIDTH - frame_w) // 2
        y = 14 if self.mode == 'inside' else SCREEN_HEIGHT - frame_h - 14

        panel = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        panel.fill((239, 195, 118, 240))
        pygame.draw.rect(panel, (122, 72, 27), panel.get_rect(), 4, border_radius=10)
        pygame.draw.rect(panel, (255, 233, 173), pygame.Rect(5, 5, frame_w - 10, frame_h - 10), 2, border_radius=8)

        for i in range(slots):
            sx = pad + i * (slot_size + gap)
            sy = pad
            slot_rect = pygame.Rect(sx, sy, slot_size, slot_size)
            inner_rect = pygame.Rect(sx + 3, sy + 3, slot_size - 6, slot_size - 6)
            pygame.draw.rect(panel, (170, 115, 58), slot_rect, border_radius=6)
            pygame.draw.rect(panel, (113, 70, 24), slot_rect, 2, border_radius=6)
            pygame.draw.rect(panel, (241, 205, 139), inner_rect, border_radius=5)
            pygame.draw.rect(panel, (199, 151, 86), inner_rect, 1, border_radius=5)

        self.display_surface.blit(panel, (x, y))

    def _draw_ui(self):
        self._draw_player_status()
        self.clock_ui.draw(self.display_surface)
        self._draw_inventory_bar()


    def _draw_world_labels(self):
        return

    def _start_music(self):
        try:
            music_path = get_path('audio', 'bg_music.mp3')
            if not os.path.exists(music_path):
                music_path = get_path('audio', 'bg.mp3')
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.35)
                pygame.mixer.music.play(loops=-1)
        except Exception as e:
            print(f'[Music] Could not load music: {e}')

    def run(self, dt):
        self.display_surface.fill(COL_BG)
        self.clock_ui.update(dt)
        self.weather.set_rain(self.clock_ui.is_rainy_day)
        AnimatedWater.step_global()
        if self.mode == 'inside':
            if self.exit_animating:
                self.exit_anim_elapsed += dt
                if self.exit_anim_elapsed < 0.08:
                    self.interior_door_sprite.set_frame(0)
                elif self.exit_anim_elapsed < 0.16:
                    self.interior_door_sprite.set_frame(1)
                else:
                    self.interior_door_sprite.set_frame(2)
                if self.exit_anim_elapsed >= 0.24:
                    self._exit_house()
            else:
                self.interior_sprites.update(dt)
                self.interior_door_sprite.set_frame(0)
            self.interior_sprites.custom_draw(self.interior_player)
        else:
            self.all_sprites.custom_draw(self.player)
            self.weather.draw_rain(dt)
            self.all_sprites.update(dt)
        self.weather.draw_darkness(max(self.clock_ui.darkness_alpha(), 62 if self.weather.raining else 0))
        self._draw_world_labels()
        self._draw_ui()
