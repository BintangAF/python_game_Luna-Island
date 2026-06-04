import os
import random
import pygame
from .settings import *
from .objects import Rock
from .support import get_path

try:
    from pytmx.util_pygame import load_pygame
except Exception:
    load_pygame = None


class CaveRoom:
    def __init__(self, floor_number, room_seed, assets):
        self.floor_number = floor_number
        self.room_seed = room_seed
        self.assets = assets
        self.rng = random.Random(room_seed)
        self.floor_tiles = []
        self.rocks = []
        self.tmx_data = self._load_tmx_map()
        self.tmx_colliders = []
        self.key_drop_rect = None
        self.key_obtained = False
        self.door_animating = False
        self.door_anim_timer = 0.0
        self.door_anim_index = 0
        ui_floor_count = max(0, self.floor_number - 1)
        self.finish_ladder_visible = (ui_floor_count > 0 and ui_floor_count % 5 == 0)
        self.finish_ladder_rect = None
        self.finish_ladder_image = self.assets.get('finish_ladder')
        self.generate()
        self.tmx_colliders = self._load_tmx_colliders()
        self._place_finish_ladder()

    def _load_tmx_map(self):
       
        if load_pygame is None:
            print('[PyTMX] Library pytmx belum terinstal. Jalankan: pip install pytmx')
            return None

        candidates = [
            get_path('maps', f'level_{self.floor_number:02d}.tmx'),
            get_path('maps', 'goa_level_01.tmx'),
        ]
        for map_path in candidates:
            if os.path.exists(map_path):
                try:
                    print(f'[PyTMX] Memuat map Tiled: {map_path}')
                    return load_pygame(map_path)
                except Exception as exc:
                    print(f'[PyTMX] Gagal memuat {map_path}: {exc}')
        return None

    def _load_tmx_colliders(self):
        """Ambil collider dari object layer Tiled jika ada."""
        rects = []
        if not self.tmx_data:
            return rects

        for obj in getattr(self.tmx_data, 'objects', []):
            obj_name = str(getattr(obj, 'name', '') or '').lower()
            obj_type = str(getattr(obj, 'type', '') or '').lower()
            is_collider = obj_name.startswith('collider') or obj_type in ('collision', 'collider')
            if is_collider:
                rects.append(pygame.Rect(
                    OFFSET_X + int(obj.x),
                    OFFSET_Y + int(obj.y),
                    int(obj.width),
                    int(obj.height)
                ))

            
            if obj_name == 'door' or obj_type == 'door':
                self.door_rect = pygame.Rect(
                    OFFSET_X + int(obj.x),
                    OFFSET_Y + int(obj.y),
                    int(obj.width),
                    int(obj.height)
                )

        return rects

    def _draw_tmx_map(self, surface):
        """Gambar semua tile layer visible dari Tiled."""
        if not self.tmx_data:
            return False

        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'tiles'):
                for x, y, image in layer.tiles():
                    if image:
                        surface.blit(
                            image,
                            (OFFSET_X + x * self.tmx_data.tilewidth, OFFSET_Y + y * self.tmx_data.tileheight)
                        )
        return True

    def _place_finish_ladder(self):
        if not self.finish_ladder_visible or not self.finish_ladder_image:
            self.finish_ladder_rect = None
            return


        ladder_x = OFFSET_X + ROOM_WIDTH - 170
        ladder_y = OFFSET_Y + 112
        self.finish_ladder_rect = self.finish_ladder_image.get_rect(topleft=(ladder_x, ladder_y))

    def near_finish_ladder(self, player_rect):
        if not self.finish_ladder_rect:
            return False
        return player_rect.colliderect(self.finish_ladder_rect.inflate(48, 42))

    def generate(self):
        for y in range(ROOM_ROWS):
            row = []
            for x in range(ROOM_COLS):
                row.append(self.rng.randrange(len(self.assets['floors'])))
            self.floor_tiles.append(row)

        self.door_rect = pygame.Rect(OFFSET_X + ROOM_WIDTH // 2 - TILE_SIZE, OFFSET_Y + 6, TILE_SIZE * 2, TILE_SIZE * 2)
        self._place_finish_ladder()

        candidates = []
        for gy in range(4, ROOM_ROWS - 4):
            for gx in range(3, ROOM_COLS - 3):
                world_x = OFFSET_X + gx * TILE_SIZE
                world_y = OFFSET_Y + gy * TILE_SIZE
                rect = pygame.Rect(world_x + 2, world_y + 2, 28, 28)
                if rect.colliderect(self.door_rect.inflate(96, 48)):
                    continue
                if self.finish_ladder_rect and rect.colliderect(self.finish_ladder_rect.inflate(80, 70)):
                    continue
                spawn_zone = pygame.Rect(OFFSET_X + ROOM_WIDTH // 2 - 80, OFFSET_Y + ROOM_HEIGHT - 96, 160, 88)
                if rect.colliderect(spawn_zone):
                    continue
                candidates.append(rect)

        self.rng.shuffle(candidates)
        count = self.rng.randint(14, 22)
        selected = []
        for rect in candidates:
            if len(selected) >= count:
                break
            if any(abs(rect.centerx - other.centerx) < 30 and abs(rect.centery - other.centery) < 30 for other in selected):
                continue
            selected.append(rect)

        hidden_index = self.rng.randrange(len(selected)) if selected else -1
        for i, rect in enumerate(selected):
            rock_image = self.assets['rocks'][i % len(self.assets['rocks'])]
            self.rocks.append(Rock(rect, rock_image, self.assets['rock_break'], has_key=(i == hidden_index)))

    def colliders(self):
        rects = [
            pygame.Rect(OFFSET_X, OFFSET_Y, ROOM_WIDTH, 20),
            pygame.Rect(OFFSET_X, OFFSET_Y + ROOM_HEIGHT - 20, ROOM_WIDTH, 20),
            pygame.Rect(OFFSET_X, OFFSET_Y, 20, ROOM_HEIGHT),
            pygame.Rect(OFFSET_X + ROOM_WIDTH - 20, OFFSET_Y, 20, ROOM_HEIGHT),
        ]

     
        rects.extend(self.tmx_colliders)

  
        if not self.door_animating:
            rects.append(pygame.Rect(self.door_rect.x + 10, self.door_rect.y + 12, self.door_rect.width - 20, self.door_rect.height - 8))

       
        if self.finish_ladder_rect:
            rects.append(pygame.Rect(
                self.finish_ladder_rect.x + 5,
                self.finish_ladder_rect.y + 12,
                self.finish_ladder_rect.width - 10,
                self.finish_ladder_rect.height - 10
            ))

        for rock in self.rocks:
            if rock.collidable():
                rects.append(rock.rect)
        return rects

    def nearby_rock(self, player_rect):
        near = None
        nearest_dist = 99999
        for rock in self.rocks:
            if rock.broken:
                continue
            dist = pygame.math.Vector2(rock.rect.center).distance_to(player_rect.center)
            if dist < 58 and dist < nearest_dist:
                nearest_dist = dist
                near = rock
        return near

    def update(self, dt):
        for rock in self.rocks:
            finished = rock.update(dt)
            if finished and rock.has_key:
                self.key_drop_rect = pygame.Rect(rock.rect.centerx - 12, rock.rect.centery - 12, 24, 24)

    def collect_key(self, player_rect):
        if self.key_drop_rect and player_rect.colliderect(self.key_drop_rect.inflate(10, 10)):
            self.key_obtained = True
            self.key_drop_rect = None
            return True
        return False

    def start_door_animation(self):
        if not self.door_animating:
            self.door_animating = True
            self.door_anim_timer = 0.0
            self.door_anim_index = 0

    def update_door_animation(self, dt):
        if not self.door_animating:
            return False
        self.door_anim_timer += dt
        frame_time = 0.14
        self.door_anim_index = min(3, int(self.door_anim_timer / frame_time))
        return self.door_anim_timer >= frame_time * 4

    def draw(self, surface, door_open=False):
        if not self._draw_tmx_map(surface):
            for y in range(ROOM_ROWS):
                for x in range(ROOM_COLS):
                    pos = (OFFSET_X + x * TILE_SIZE, OFFSET_Y + y * TILE_SIZE)
                    if x == 0 or y == 0 or x == ROOM_COLS - 1 or y == ROOM_ROWS - 1:
                        surface.blit(self.assets['walls'][(x + y) % len(self.assets['walls'])], pos)
                    else:
                        surface.blit(self.assets['floors'][self.floor_tiles[y][x]], pos)

        tunnel = pygame.Rect(self.door_rect.x - 10, OFFSET_Y, self.door_rect.width + 20, TILE_SIZE * 2 + 10)
        pygame.draw.rect(surface, (45, 34, 27), tunnel, border_radius=10)

        for rock in self.rocks:
            rock.draw(surface)

        if self.finish_ladder_rect and self.finish_ladder_image:
            surface.blit(self.finish_ladder_image, self.finish_ladder_rect)

        if self.key_drop_rect:
            surface.blit(self.assets['gold_key'], self.key_drop_rect)

        if self.door_animating and self.assets.get('door_frames'):
            door_surf = self.assets['door_frames'][min(self.door_anim_index, len(self.assets['door_frames']) - 1)]
        else:
            door_surf = self.assets['door_closed']
        surface.blit(door_surf, self.door_rect)

        shade = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(shade, (0, 0, 0, 90), shade.get_rect(), 10)
        surface.blit(shade, (OFFSET_X, OFFSET_Y))
