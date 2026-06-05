from __future__ import annotations
import random
from typing import TYPE_CHECKING

import pygame

from base import BaseWorldBuilder
from settings import TILE_SIZE, LAYERS, MAP_W, MAP_H
from sprites import Generic, CollideTile
from maps.build_map import T_GRASS, T_FIELD, T_PATH, T_YARD, T_WATER, T_SAND
from plant import Plant
from seed import Seed
from world.animated_water import AnimatedWater
from support import get_path, load_single

if TYPE_CHECKING:
    from level import Level

def _stable_seed(*values: object) -> int:
    seed = 2166136261
    for v in values:
        if isinstance(v, str):
            for ch in v:
                seed ^= ord(ch)
                seed = (seed * 16777619) & 0xFFFFFFFF
        else:
            n = int(v)  
            seed ^= (n + 0x9E3779B9 + ((seed << 6) & 0xFFFFFFFF) + (seed >> 2)) & 0xFFFFFFFF
            seed = (seed * 16777619) & 0xFFFFFFFF
    return seed & 0xFFFFFFFF

def _stable_choice(surfs: list, *key: object):
    if not surfs:
        return None
    return surfs[_stable_seed(*key) % len(surfs)].copy()


def _stable_offset(max_x: int, max_y: int, *key: object) -> tuple[int, int]:
    seed = _stable_seed(*key)
    return seed % (max_x + 1), (seed // 97) % (max_y + 1)


def _rect_intersects(a: tuple, b: tuple) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by

class TileBuilder(BaseWorldBuilder):
    """Menaruh tile ground layer (termasuk air animasi)."""

    def build(self) -> None:
        level = self._level
        assets = level.assets
        season = self._season_mode

        for ty, row in enumerate(self._grid):
            for tx, tile_id in enumerate(row):
                pos = (tx * TILE_SIZE, ty * TILE_SIZE)
                if tile_id == T_WATER:
                    AnimatedWater(pos, assets.water_surfs,
                                  self._all_sprites, z=LAYERS["ground"])
                    CollideTile(pos, (TILE_SIZE, TILE_SIZE),
                                self._collision_sprites)
                else:
                    surf = self._choose_tile(tile_id, tx, ty)
                    Generic(pos, surf, self._all_sprites, z=LAYERS["ground"])

    def _choose_tile(self, tile_id: int, tx: int, ty: int) -> pygame.Surface:
        sa = self._level.assets.for_season(self._season_mode)

        pool_map = {
            T_GRASS: sa.grass_surfs,
            T_FIELD: sa.field_surfs,
            T_PATH:  sa.path_surfs,
            T_YARD:  sa.yard_surfs,
            T_SAND:  sa.sand_surfs,
        }
        lst = pool_map.get(tile_id)
        if not lst:
            lst = (sa.grass_surfs or sa.sand_surfs or sa.path_surfs
                   or sa.yard_surfs or sa.field_surfs)
        if not lst:
            raise RuntimeError("Tile asset tidak ditemukan. Cek folder graphics/tiles.")
        return _stable_choice(lst, "tile", tile_id, tx, ty)


class FarmPlotTile(pygame.sprite.Sprite):
    def __init__(self, pos, state_surfs, groups):
        super().__init__(groups)
        self.state_surfs = state_surfs
        self.state = 0
        self.image = self.state_surfs[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS["ground"]
        self.hitbox = self.rect.copy()

    def set_state(self, state: int) -> None:
        self.state = max(0, min(state, len(self.state_surfs) - 1))
        surf = self.state_surfs[self.state]
        if surf is not None:
            self.image = surf


class FarmPlotManager:
    """Kelola ladang khusus di bawah rumah pemain."""

    PLOT_COORDS = [
        (18, 28), (20, 28), (22, 28), (24, 28),
        (18, 30), (20, 30), (22, 30), (24, 30),
        (18, 32), (20, 32), (22, 32), (24, 32),
    ]
    STATE_UNTILLED = 0
    STATE_HOED = 1
    STATE_PLANTED = 2
    STATE_WATERED = 3
    STATE_GROWN = 4

    def __init__(self, level: "Level") -> None:
        self._level = level
        self._tiles: dict[tuple[int, int], FarmPlotTile] = {}
        self._state_surfs = self._load_state_surfaces()
        self._battle_unlocked_types: set[str] = set()

    def _load_state_surfaces(self) -> list[pygame.Surface]:
        untilled = load_single(get_path("graphics", "tiles", "FieldsTile_38.png"), (TILE_SIZE, TILE_SIZE))
        hoed = load_single(get_path("graphics", "tiles", "FieldsTile_01.png"), (TILE_SIZE, TILE_SIZE))
        seeded = load_single(get_path("graphics", "tiles", "seeded_tile1.png"), (TILE_SIZE, TILE_SIZE))
        watered = load_single(get_path("graphics", "tiles", "seeded_tile2.png"), (TILE_SIZE, TILE_SIZE))

        fallback = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        fallback.fill((160, 134, 99, 255))

        return [
            untilled or fallback.copy(),
            hoed or fallback.copy(),
            seeded or fallback.copy(),
            watered or fallback.copy(),
            None,  # placeholder for grown plant sprite (loaded per-plant)
        ]

    def build(self) -> None:
        for tx, ty in self.PLOT_COORDS:
            if not self._level._land_at(tx, ty):
                continue
            pos = (tx * TILE_SIZE, ty * TILE_SIZE)
            tile = FarmPlotTile(pos, self._state_surfs, (self._level.all_sprites,))
            # per-tile plant metadata
            tile.seed = None
            tile.plant = None
            tile.plant_type = None
            tile.growth_minutes = 0
            tile.watered = False
            self._tiles[(tx, ty)] = tile

    def interact(self) -> bool:
        tile = self._get_target_tile()
        if tile is None:
            return False

        active_item = self._level.inventory_bar.get_active_item()

        if tile.state == self.STATE_GROWN:
            return self._handle_grown_tile(tile)

        if active_item == "Hoe" and tile.state == self.STATE_UNTILLED:
            tile.set_state(self.STATE_HOED)
            return True

        active_seed = None
        if active_item is not None:
            active_seed = self._level.inventory.get_item(active_item)

        if tile.state == self.STATE_HOED:
            if isinstance(active_seed, Seed):
                self._level.inventory.remove_item(active_seed)
                tile.seed = active_seed
                tile.plant_type = self._seed_name_to_type(active_seed.name)
                tile.growth_minutes = 0
                tile.watered = False
                tile.plant = None
                tile.set_state(self.STATE_PLANTED)
                return True
            if active_item and active_item.startswith("Biji ") and self._level.inventory.get(active_item, 0) > 0:
                # plant seed and record type for legacy string seed names
                plant_type = self._seed_name_to_type(active_item)
                self._level.inventory.remove_item(active_item)
                tile.seed = None
                tile.plant_type = plant_type
                tile.growth_minutes = 0
                tile.watered = False
                tile.plant = None
                tile.set_state(self.STATE_PLANTED)
                return True
            return False

        if active_item in ("Air", "Watering Can") and tile.state == self.STATE_PLANTED:
            if active_item == "Air":
                if self._level.inventory.get("Air", 0) <= 0:
                    return False
                self._level.inventory.remove_item("Air")
            tile.watered = True
            tile.growth_minutes = 0
            tile.set_state(self.STATE_WATERED)
            return True

        return False

    def _get_target_tile(self) -> FarmPlotTile | None:
        player = self._level.player
        directions = {
            "left": (-TILE_SIZE, 0),
            "right": (TILE_SIZE, 0),
            "up": (0, -TILE_SIZE),
            "down": (0, TILE_SIZE),
        }
        dx, dy = directions.get(player.facing, (0, 0))
        tx = (player.hitbox.centerx + dx) // TILE_SIZE
        ty = (player.hitbox.centery + dy) // TILE_SIZE
        if (tx, ty) in self._tiles:
            return self._tiles[(tx, ty)]

        tx = player.hitbox.centerx // TILE_SIZE
        ty = player.hitbox.centery // TILE_SIZE
        return self._tiles.get((tx, ty))


    def reset(self) -> None:
        for tile in self._tiles.values():
            tile.set_state(self.STATE_UNTILLED)
            tile.seed = None
            tile.plant = None
            tile.plant_type = None
            tile.growth_minutes = 0
            tile.watered = False

    def get_plot_states(self) -> dict[tuple[int, int], int]:
        return {coord: tile.state for coord, tile in self._tiles.items()}

    def is_plot_tile(self, tx: int, ty: int) -> bool:
        return (tx, ty) in self._tiles

    def get_plot_tile(self, tx: int, ty: int) -> FarmPlotTile | None:
        return self._tiles.get((tx, ty))

    def has_active_plot(self) -> bool:
        return bool(self._tiles)


    def is_ready_to_plant(self, tx: int, ty: int) -> bool:
        tile = self._tiles.get((tx, ty))
        return bool(tile and tile.state == self.STATE_HOED)

    def is_watered(self, tx: int, ty: int) -> bool:
        tile = self._tiles.get((tx, ty))
        return bool(tile and tile.state == self.STATE_WATERED)


    def __contains__(self, key: tuple[int, int]) -> bool:
        return key in self._tiles

    def __getitem__(self, key: tuple[int, int]) -> FarmPlotTile | None:
        return self._tiles.get(key)

    def __iter__(self):
        return iter(self._tiles.items())

    def _seed_name_to_type(self, item_name: str) -> str:
        name = item_name.lower()
        if "kacang" in name or "pea" in name or "polong" in name:
            return "peashooter"
        if "jamur" in name or "mushroom" in name:
            return "mushroom"
        if "matahari" in name or "bunga" in name or "sunflower" in name:
            return "sunflower"
        if "walnut" in name or "kenari" in name or "kentang" in name:
            return "walnut"
        # fallback: take last word and sanitize
        parts = item_name.split()
        return parts[-1].lower()

    def _load_plant_sprite(self, plant_type: str) -> pygame.Surface | None:
        if not plant_type:
            return None
        candidates = [
            f"{plant_type}.png",
            f"{plant_type.lower()}.png",
            f"{plant_type.capitalize()}.png",
            f"{plant_type.upper()}.png",
        ]
        for filename in candidates:
            path = get_path("assets", "images", "plants", filename)
            surf = load_single(path, (TILE_SIZE, TILE_SIZE))
            if surf:
                return surf
        # additional common name fallback
        alternative = {
            "peashooter": "peashooter.png",
            "mushroom": "jamur.png",
            "sunflower": "sunflower.png",
            "walnut": "walnut.png",
        }.get(plant_type)
        if alternative:
            path = get_path("assets", "images", "plants", alternative)
            return load_single(path, (TILE_SIZE, TILE_SIZE))
        return None

    def _make_plant(self, plant_type: str, growth_time: int) -> Plant | None:
        plant_surf = self._load_plant_sprite(plant_type)
        if not plant_surf:
            return None
        return Plant(name=plant_type, image=plant_surf, growth_time=growth_time)

    def update(self, minutes_passed: int) -> None:
        """Call from Level each time the clock advances. minutes_passed is sum of in-game minutes."""
        if minutes_passed <= 0:
            return
        # decay and growth thresholds (in in-game minutes)
        decay_threshold = 100  # if not watered within 100 minutes, planted seed dies
        growth_threshold = 60  # after watering, take 60 minutes to become grown

        for coord, tile in list(self._tiles.items()):
            if tile.state == self.STATE_PLANTED and not tile.watered:
                tile.growth_minutes += minutes_passed
                if tile.growth_minutes >= decay_threshold:
                    # seed dies, reset tile
                    tile.seed = None
                    tile.plant = None
                    tile.plant_type = None
                    tile.growth_minutes = 0
                    tile.watered = False
                    tile.set_state(self.STATE_UNTILLED)
            elif tile.state == self.STATE_WATERED and tile.watered:
                tile.growth_minutes += minutes_passed
                if tile.growth_minutes >= growth_threshold:
                    # become grown
                    tile.set_state(self.STATE_GROWN)
                    plant = self._make_plant(tile.plant_type, growth_threshold)
                    if plant:
                        tile.plant = plant
                        tile.image = plant.image
                    else:
                        plant_surf = self._load_plant_sprite(tile.plant_type)
                        if plant_surf:
                            tile.image = plant_surf
                    tile.growth_minutes = 0
                    tile.watered = False

    def _handle_grown_tile(self, tile: FarmPlotTile) -> bool:
        plant_type = tile.plant_type or "tanaman"
        if plant_type in self._battle_unlocked_types:
            return False
        self._battle_unlocked_types.add(plant_type)
        if hasattr(self._level, "battle_unlock_panel"):
            self._level.battle_unlock_panel.open(plant_type)
            return True
        return False


class FarmBuilder(BaseWorldBuilder):
    """Build the special farm plot under the main house."""

    def build(self) -> None:
        self._level.farm = FarmPlotManager(self._level)
        self._level.farm.build()

    def _place_plot_tile(self, tx: int, ty: int, surf: pygame.Surface) -> None:
        pass

    def _plot_tile_rect(self, tx: int, ty: int) -> tuple[int, int, int, int]:
        return (tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def _is_plot_tile(self, tx: int, ty: int) -> bool:
        return self._level.farm.is_plot_tile(tx, ty)

    def _plot_state(self, tx: int, ty: int) -> int:
        tile = self._level.farm.get_plot_tile(tx, ty)
        return tile.state if tile else self._level.farm.STATE_UNTILLED

    def _tile_state_name(self, state: int) -> str:
        return ["untilled", "hoed", "planted", "watered", "grown"][state]


    def _plot_coords(self) -> list[tuple[int, int]]:
        return FarmPlotManager.PLOT_COORDS


    def _plot_positions(self) -> list[tuple[int, int]]:
        return [(tx * TILE_SIZE, ty * TILE_SIZE) for tx, ty in self._plot_coords()]


    def _plot_surf_for_state(self, state: int) -> pygame.Surface | None:
        return self._level.farm._state_surfs[state] if self._level.farm else None


    def _plot_state_from_item(self, item_name: str) -> int | None:
        if item_name == "Hoe":
            return self._level.farm.STATE_HOED
        if item_name and item_name.startswith("Biji "):
            return self._level.farm.STATE_PLANTED
        if item_name in ("Air", "Watering Can"):
            return self._level.farm.STATE_WATERED
        return None


    def _plot_message(self, text: str) -> None:
        pass


    def _plot_tile_index(self, tx: int, ty: int) -> int:
        return self._plot_coords().index((tx, ty)) if (tx, ty) in self._plot_coords() else -1

    def _draw_plot_grid(self) -> None:
        pass

    def _show_plot_help(self) -> None:
        pass

    def _hide_plot_help(self) -> None:
        pass

    def _clear_plot_tiles(self) -> None:
        pass

    def _reset_plot(self) -> None:
        if self._level.farm:
            self._level.farm.reset()


    def _plot_state_from_active_item(self) -> int | None:
        item = self._level.inventory_bar.get_active_item()
        return self._plot_state_from_item(item) if item else None

    def _ensure_plot_ready(self) -> bool:
        return self._level.farm is not None and self._level.farm.has_active_plot()


    def _plot_tile_action(self, tx: int, ty: int) -> None:
        self._level.farm.interact()

    def _plot_tile_cursor(self, tx: int, ty: int) -> None:
        pass

    def _plot_tile_hover(self, tx: int, ty: int) -> None:
        pass

    def _plot_tile_marker(self, tx: int, ty: int) -> None:
        pass

    def _plot_tile_info(self, tx: int, ty: int) -> None:
        pass

    def _plot_tile_state_description(self, state: int) -> str:
        return [
            "Ladang belum dicangkul.",
            "Ladang siap ditanami.",
            "Benih sudah ditanam.",
            "Tanaman sudah disiram.",
        ][state]

    def _place_plot_helpers(self) -> None:
        pass

    def _plot_tile_overlay(self) -> None:
        pass

    def _update_plot(self) -> None:
        pass

    def _plot_tile_label(self, tx: int, ty: int) -> str:
        return f"Plot {self._plot_tile_index(tx, ty) + 1}" if self._plot_tile_index(tx, ty) >= 0 else ""

    def _plot_target_description(self) -> str:
        return "Gunakan Hoe, biji tanaman, dan Air di area ladang ini."


    def _plot_help_text(self) -> str:
        return "Pilih alat/biji di bar inventaris, lalu tekan E di atas salah satu tile." 

    def _plot_tooltip(self) -> None:
        pass


    def _plot_state_text(self, state: int) -> str:
        return [
            "Belum dicangkul",
            "Sudah dicangkul",
            "Sudah ditanam",
            "Sudah disiram",
            "Tanaman dewasa",
        ][state]


    def _plot_state_color(self, state: int) -> tuple[int, int, int]:
        return [(170, 125, 75), (200, 150, 80), (138, 180, 70), (75, 152, 229), (120, 200, 100)][state]


    def _plot_state_icon(self, state: int) -> pygame.Surface | None:
        return None

    def _plot_state_label(self, state: int) -> str:
        return ["Belum cangkul", "Dicangkul", "Ditanam", "Disiram", "Dewasa"][state]

    def _plot_selectors(self) -> None:
        pass

    def _plot_action_text(self, state: int) -> str:
        return [
            "Tekan E untuk mencangkul.",
            "Tekan E sambil memilih biji untuk menanam.",
            "Tekan E sambil memilih Air untuk menyiram.",
            "Tanaman siap tumbuh.",
        ][state]


    def _plot_tile_state_name(self, state: int) -> str:
        return ["untilled", "hoed", "planted", "watered", "grown"][state]


    def _plot_is_last(self, tx: int, ty: int) -> bool:
        return self._plot_tile_index(tx, ty) == len(self.PLOT_COORDS) - 1


    def _plot_next(self, tx: int, ty: int) -> tuple[int, int] | None:
        idx = self._plot_tile_index(tx, ty)
        if idx < 0 or idx + 1 >= len(self.PLOT_COORDS):
            return None
        return self.PLOT_COORDS[idx + 1]

    def _plot_previous(self, tx: int, ty: int) -> tuple[int, int] | None:
        idx = self._plot_tile_index(tx, ty)
        if idx <= 0:
            return None
        return self.PLOT_COORDS[idx - 1]


    def _plot_help(self) -> None:
        pass


    def _plot_hint(self) -> None:
        pass


    def _plot_description(self) -> None:
        pass


    def _plot_target(self) -> None:
        pass


class HouseBuilder(BaseWorldBuilder):
    """Menaruh rumah & sumur portal ke goa."""

    HOUSE_DATA = [
        (9,  4,  3, True),
        (28, 5,  1, False),
        (8,  15, 2, False),
        (59, 6,  0, False),
    ]

    def build(self) -> None:
        self._place_houses()
        self._place_well_gateway()

    
    def _place_houses(self) -> None:
        sa = self._level.assets.for_season(self._season_mode)
        houses = sa.houses
        if not houses:
            return

        for tx, ty, idx, is_main in self.HOUSE_DATA:
            surf = houses[idx % len(houses)].copy()
            if is_main:
                surf = pygame.transform.scale(surf, (TILE_SIZE * 6, TILE_SIZE * 6))
                col_size = (TILE_SIZE * 5, TILE_SIZE * 5)
                land_check = (5, 5)
            else:
                col_size = (TILE_SIZE * 4, TILE_SIZE * 4)
                land_check = (4, 3)

            if self._level._area_land(tx, ty + 2, *land_check):
                self._place_object(
                    (tx * TILE_SIZE, ty * TILE_SIZE), surf,
                    collision=True, collision_size=col_size,
                )

    def _place_well_gateway(self) -> None:
        from sprites import WellGatewaySprite
        surf = load_single(get_path("graphics", "portal", "well_gateway.png"))
        if not surf:
            return
        tx, ty = 16, 8
        pos = (tx * TILE_SIZE, ty * TILE_SIZE)
        self._level.well_gateway = WellGatewaySprite(
            pos, surf,
            (self._all_sprites, self._collision_sprites),
        )

    
    def _place_object(self, pos, surf, collision=True, collision_size=None,
                      z=LAYERS["objects"]) -> None:
        if not surf:
            return
        Generic(pos, surf, self._all_sprites, z=z)
        if collision:
            if collision_size is None:
                collision_size = (surf.get_width(), max(12, surf.get_height() - 12))
            CollideTile(pos, collision_size, self._collision_sprites)


class FenceBuilder(BaseWorldBuilder):
    """Menaruh pagar dan tanaman/crop di ladang."""

    def build(self) -> None:
        self._place_fences()
        self._place_crops()

    def _fence_rect(self, x: int, y: int, w: int, h: int,
                    gate_tiles: list[tuple] | None = None) -> None:
        gate_tiles = set(gate_tiles or [])
        sa = self._level.assets.for_season(self._season_mode)
        fh, fv, fp = sa.fence_h, sa.fence_v, sa.fence_post

        for tx in range(x, x + w):
            if (tx, y - 1) not in gate_tiles:
                self._fence_piece(tx, y - 1, fh)
            if (tx, y + h) not in gate_tiles:
                self._fence_piece(tx, y + h, fh)
        for ty in range(y, y + h):
            if (x - 1, ty) not in gate_tiles:
                self._fence_piece(x - 1, ty, fv)
            if (x + w, ty) not in gate_tiles:
                self._fence_piece(x + w, ty, fv)
        for px, py in [(x-1,y-1),(x+w,y-1),(x-1,y+h),(x+w,y+h)]:
            self._fence_piece(px, py, fp)

    def _fence_piece(self, tx: int, ty: int, surf) -> None:
        if not surf or not self._level._land_at(tx, ty):
            return
        pos = (tx * TILE_SIZE, ty * TILE_SIZE)
        Generic(pos, surf.copy(), self._all_sprites, z=LAYERS["objects"])
        CollideTile(pos, (TILE_SIZE, TILE_SIZE), self._collision_sprites)

    def _place_fences(self) -> None:
        # self._fence_rect(10, 26, 24, 8, gate_tiles=[(20,34),(21,34),(34,29),(34,30)])
        self._fence_rect(36, 22, 11, 6, gate_tiles=[(41,21),(42,21),(47,25)])
        self._fence_rect(55, 28, 12, 6, gate_tiles=[(61,27),(62,27),(67,30),(67,31)])
        self._fence_rect( 7,  6, 16, 8, gate_tiles=[(12,14),(13,14),(14,14)])
        self._fence_rect(29,  6,  8, 4, gate_tiles=[(33,10),(34,10)])
        self._fence_rect(56,  6, 12, 6, gate_tiles=[(61,12),(62,12),(63,12)])

    def _place_crops(self) -> None:
        sa = self._level.assets.for_season(self._season_mode)
        grass_objs = sa.grass_objs
        if not grass_objs:
            return

        # Penempatan crop di area ladang (bukan di pagar) dengan pola tertentu
        # for y in range(27, 33):
        #     for x in range(11, 33):
        #         if x % 2 == 0:
        #             self._place_crop(x, y, grass_objs)
        for y in range(29, 33):
            for x in range(56, 66):
                if x % 2 == 0:
                    self._place_crop(x, y, grass_objs)

    def _place_crop(self, tx: int, ty: int, grass_objs: list) -> None:
        if not self._level._land_at(tx, ty):
            return
        surf = _stable_choice(grass_objs, "crop", tx, ty)
        if surf:
            Generic(
                (tx * TILE_SIZE + 8, ty * TILE_SIZE + 10),
                surf, self._all_sprites, z=LAYERS["objects"],
            )

class TreeBuilder(BaseWorldBuilder):
    """Menaruh pohon (medium & small) di seluruh peta."""

    
    MEDIUM_POSITIONS = [
        (27,14),(33,14),(40,14),(16,20),(24,20),(31,20),
        (18,36),(26,36),(34,36),(50,36),(58,36),(66,35),
        (24,12),(72,14),(72,20),(14,23),(40,29),(72,29),(44,34),
    ]
    SMALL_POSITIONS = [
        (12,15),(15,15),(18,15),(30,15),(36,15),
        (13,18),(19,18),(27,18),(35,18),
        (12,22),(20,22),(28,22),
        (15,15),(20,15),(19,15),(30,15),(47,15),(50,15),
        (14,34),(22,34),(30,34),(54,34),(60,34),(65,33),
        (39,17),(40,20),(37,24),(72,24),(70,28),(68,30),
        (42,32),(46,33),(72,33),(32,22),(24,24),(10,24),
    ]
    
    BLOCKED_RECTS = [
        (6,5,18,10),(28,5,10,6),(55,5,14,8),(44,12,33,14),(7,14,15,9),(11,13,8,5),
    ]

    def build(self) -> None:
        occupied: list[tuple] = []
        for tx, ty in self.MEDIUM_POSITIONS:
            self._place_tree(tx, ty, medium=True, occupied=occupied)
        for tx, ty in self.SMALL_POSITIONS:
            self._place_tree(tx, ty, medium=False, occupied=occupied)
        # self._place_extra_trees(occupied)

    def _place_tree(self, tx: int, ty: int, medium: bool,
                    occupied: list) -> bool:
        if not (0 <= tx < MAP_W and 0 <= ty < MAP_H):
            return False
        if self._grid[ty][tx] in (T_WATER, T_FIELD):
            return False
        if self._is_blocked(tx, ty):
            return False
        if not self._level._area_land(max(0, tx), max(0, ty + 1), 2, 2):
            return False

        footprint = (tx - 1, ty - 1, 2, 3)
        if any(_rect_intersects(footprint, r) for r in occupied):
            return False

        sa = self._level.assets.for_season(self._season_mode)
        surf = sa.tree_medium if medium else sa.tree_small
        if not surf:
            return False

        pos = (tx * TILE_SIZE, ty * TILE_SIZE)
        Generic(pos, surf.copy(), self._all_sprites, z=LAYERS["objects"])
        hit_w = 26 if medium else 20
        offset_x = (surf.get_width() - hit_w) // 2
        offset_y = surf.get_height() - 18 - 5
        CollideTile(
            (pos[0] + offset_x, pos[1] + offset_y),
            (hit_w, 18),
            self._collision_sprites,
        )
        occupied.append(footprint)
        return True

    def _is_blocked(self, tx: int, ty: int) -> bool:
        fp = (tx - 1, ty - 1, 4, 5)
        return any(_rect_intersects(fp, r) for r in self.BLOCKED_RECTS)

    def _place_extra_trees(self, occupied: list) -> None:
        tree_rand = random.Random(91)
        candidates: list[tuple[int, int]] = []
        for ty in range(4, 39, 2):
            xs = list(range(7, 76, 3))
            tree_rand.shuffle(xs)
            for tx in xs:
                candidates.append((
                    tx + tree_rand.choice([-1, 0, 1]),
                    ty + tree_rand.choice([-1, 0, 1]),
                ))
        total = 0
        for i, (tx, ty) in enumerate(candidates):
            if total >= 65:
                break
            if self._place_tree(tx, ty, medium=(i % 4 == 0), occupied=occupied):
                total += 1

class DetailBuilder(BaseWorldBuilder):
    """Menaruh box, dekor, batu pantai, rumput, dan batu darat."""

    
    BOX_SPOTS   = [(20,9),(24,10),(31,9),(36,9),(50,18),(56,18),(61,18),(66,18),(39,23),(44,23),(18,22),(58,30)]
    DECOR_SPOTS = [(17,10),(19,11),(30,9),(34,9),(37,10),(43,18),(48,18),(52,18),(58,18),(64,18),(40,24),(42,24),(60,20)]
    SEA_STONES  = [
        (4,8),(5,9),(3,11),(5,13),(4,16),(5,18),(3,21),(4,24),(5,27),(4,31),(6,35),
        (14,2),(19,2),(25,2),(32,2),(39,2),(46,2),(53,2),(60,2),(67,2),
        (72,5),(73,8),(72,12),(73,16),(72,20),(73,24),(72,28),(73,32),(72,35),
        (77,9),(78,14),(79,20),(78,27),(77,33),
        (12,39),(18,39),(24,39),(30,39),(45,39),(51,39),(58,39),(65,39),
        (7,37),(9,38),(70,37),(68,38),(55,37),(41,38),
    ]
    COAST_STONES = [(43,11),(12,20),(28,20),(40,35)]
    GRASS_SPOTS  = [(9,12),(13,13),(17,14),(26,13),(32,13),(41,12),(49,12),(56,12),(64,13),(18,23),(24,23),(33,23),(48,24),(65,24)]
    LAND_STONES  = [
        (18,12),(22,12),(41,12),(46,13),(51,12),
        (14,18),(20,18),(25,19),(32,18),(38,18),(58,18),
        (14,23),(20,23),(27,23),(33,23),(44,23),(49,23),(63,23),
        (15,35),(21,35),(27,35),(35,35),(42,35),(48,35),(56,35),(63,35),
        (60,26),(66,27),
    ]
    STONE_BLOCKED = [(6,5,18,10),(55,5,14,8)]

    def build(self) -> None:
        sa = self._level.assets.for_season(self._season_mode)
        self._place_boxes(sa)
        self._place_decor(sa)
        self._place_sea_stones(sa)
        self._place_grass(sa)
        self._place_land_stones(sa)

    def _place_boxes(self, sa) -> None:
        for tx, ty in self.BOX_SPOTS:
            if self._level._land_at(tx, ty):
                surf = _stable_choice(sa.boxes, "box", tx, ty)
                self._place_obj((tx*TILE_SIZE, ty*TILE_SIZE), surf, True, (TILE_SIZE, TILE_SIZE))

    def _place_decor(self, sa) -> None:
        for tx, ty in self.DECOR_SPOTS:
            if self._level._land_at(tx, ty):
                surf = _stable_choice(sa.decor, "decor", tx, ty)
                if surf:
                    Generic((tx*TILE_SIZE+4, ty*TILE_SIZE+6), surf,
                            self._all_sprites, z=LAYERS["objects"])

    def _place_sea_stones(self, sa) -> None:
        for tx, ty in self.SEA_STONES + self.COAST_STONES:
            if self._is_stone_blocked(tx, ty):
                continue
            if (tx, ty) in self.SEA_STONES and self._level._land_at(tx, ty):
                continue
            surf = _stable_choice(sa.stones, "stone", tx, ty)
            if surf:
                ox, oy = _stable_offset(8, 8, "sea_stone_offset", tx, ty)
                Generic((tx*TILE_SIZE+ox, ty*TILE_SIZE+oy), surf,
                        self._all_sprites, z=LAYERS["objects"])

    def _place_grass(self, sa) -> None:
        for tx, ty in self.GRASS_SPOTS:
            if self._level._land_at(tx, ty):
                surf = _stable_choice(sa.grass_objs, "grass", tx, ty)
                if surf:
                    ox, oy = _stable_offset(6, 6, "grass_offset", tx, ty)
                    Generic((tx*TILE_SIZE+4+ox, ty*TILE_SIZE+4+oy), surf,
                            self._all_sprites, z=LAYERS["objects"])

    def _place_land_stones(self, sa) -> None:
        from maps.build_map import T_FIELD
        for tx, ty in self.LAND_STONES:
            if (self._level._land_at(tx, ty)
                    and self._grid[ty][tx] != T_FIELD):
                surf = _stable_choice(sa.stones, "stone", tx, ty)
                if surf:
                    self._place_obj(
                        (tx*TILE_SIZE+3, ty*TILE_SIZE+4), surf, True,
                        (max(18, surf.get_width()-6), max(14, surf.get_height()-8)),
                    )

    def _is_stone_blocked(self, tx: int, ty: int) -> bool:
        return any(_rect_intersects((tx, ty, 1, 1), r) for r in self.STONE_BLOCKED)

    def _place_obj(self, pos, surf, collision: bool, col_size=None,
                   z=LAYERS["objects"]) -> None:
        if not surf:
            return
        Generic(pos, surf, self._all_sprites, z=z)
        if collision:
            CollideTile(pos, col_size or (surf.get_width(), max(12, surf.get_height()-12)),
                        self._collision_sprites)


class MarketBuilder(BaseWorldBuilder):    
    NPC_DATA = [

        {
            "filename": "npc_1_boy_shopkeeper.png",
            "name": "Pedagang Biji Tanaman",
            "center": (51*TILE_SIZE + TILE_SIZE//2, 18*TILE_SIZE + TILE_SIZE//2),
            "fallback": (91, 150, 72),
            "type": "shop",
            "buy_items": [
                {"name": "Biji Bunga Matahari", "buy_price": 15, "image": "assets/items/seeds/sunflower_seed.png"},
                {"name": "Biji Kentang", "buy_price": 12, "image": "assets/items/seeds/potato_seed.png"},
                {"name": "Biji Kacang Polong", "buy_price": 10, "image": "assets/items/seeds/pea_seed.png"},
                {"name": "Rumput", "buy_price": 2, "image": "assets/items/materials/grass.png"},
                {"name": "Kayu", "buy_price": 4, "image": "assets/items/materials/wood.png"},
                {"name": "Batu", "buy_price": 3, "image": "assets/items/materials/stone.png"},
            ],
            "items": [
                {"name":"Biji Bunga Matahari","price":30,"desc":"Biji bunga matahari yang indah.","stock":10, "image": "assets/items/seeds/sunflower_seed.png"},
                {"name":"Biji Kentang","price":25,"desc":"Biji tanaman kentang","stock":8, "image": "assets/items/seeds/potato_seed.png"},
                {"name":"Biji Kacang Polong","price":20,"desc":"Biji tanaman kacang polong","stock":8, "image": "assets/items/seeds/pea_seed.png"},
                {"name":"Rumput","price":5,"desc":"Rumput segar","stock":20, "image": "assets/items/materials/grass.png"},
                {"name":"Kayu","price":8,"desc":"Kayu berkualitas","stock":15, "image": "assets/items/materials/wood.png"},
                {"name":"Batu","price":6,"desc":"Batu alam","stock":15, "image": "assets/items/materials/stone.png"},
            ],
        },
        {
            "filename": "npc_2_girl_shopkeeper.png",
            "name": "Pedagang Ramuan & Bunga",
            "center": (57*TILE_SIZE + TILE_SIZE//2, 18*TILE_SIZE + TILE_SIZE//2),
            "fallback": (116, 78, 150),
            "type": "shop",
            "buy_items": [
                {"name": "Biji Jamur", "buy_price": 20, "image": "assets/items/seeds/mushroom_seed.png"},
                {"name": "Bunga", "buy_price": 6, "image": "assets/items/materials/flower.png"},
                {"name": "Gandum", "buy_price": 5, "image": "assets/items/materials/wheat.png"},
                {"name": "Telur", "buy_price": 8, "image": "assets/items/food/egg.png"},
                {"name": "Air", "buy_price": 1, "image": "assets/items/materials/water.png"},
                {"name": "Besi", "buy_price": 12, "image": "assets/items/materials/iron.png"},
            ],
            "items": [
                {"name":"Biji Jamur","price":40,"desc":"Biji jamur langka untuk kebun.","stock":5, "image": "assets/items/seeds/mushroom_seed.png"},
                {"name":"Bunga","price":12,"desc":"Bunga wangi untuk crafting.","stock":15, "image": "assets/items/materials/flower.png"},
                {"name":"Gandum","price":10,"desc":"Gandum untuk membuat roti.","stock":20, "image": "assets/items/materials/wheat.png"},
                {"name":"Telur","price":15,"desc":"Telur segar untuk memasak.","stock":10, "image": "assets/items/food/egg.png"},
                {"name":"Air","price":3,"desc":"Air bersih untuk ramuan.","stock":30, "image": "assets/items/materials/water.png"},
                {"name":"Besi","price":25,"desc":"Logam besi untuk crafting lanjutan.","stock":8, "image": "assets/items/materials/iron.png"},
            ],
        },
        {
            "filename": "npc_1_boy_shopkeeper.png",
            "name": "Pengrajin",
            "center": (60*TILE_SIZE + TILE_SIZE//2, 18*TILE_SIZE + TILE_SIZE//2),
            "fallback": (141, 100, 180),
            "type": "crafter",
            "buy_items": [],
            "items": [],
        },
    ]
    
    def build(self) -> None:
        """Build market: tenda dan NPC - IMPLEMENTASI ABSTRACT METHOD"""
        self._place_tents()
        self._place_npcs()

    def _place_tents(self) -> None:
        sa = self._level.assets.for_season(self._season_mode)
        tents = sa.tents
        if not tents:
            return
        for i, (tx, ty) in enumerate([(49,15),(55,15),(60,15),(65,15)]):
            if self._level._area_land(tx, ty+1, 3, 2):
                surf = tents[i % len(tents)].copy()
                Generic((tx*TILE_SIZE, ty*TILE_SIZE), surf,
                        self._all_sprites, z=LAYERS["objects"])
                CollideTile((tx*TILE_SIZE, ty*TILE_SIZE),
                            (TILE_SIZE*3, TILE_SIZE*2), self._collision_sprites)

    def _place_npcs(self) -> None:
        from npc.shop_npc import ShopNPC
        from npc.crafter_npc import CrafterNPC
        
        self._level.shop_npcs = []
        
        for data in self.NPC_DATA:
            image = self._load_npc_image(data["filename"], data["fallback"])
            
            if data["type"] == "shop":
                npc = ShopNPC(
                    data["center"], image,
                    (self._all_sprites, self._collision_sprites),
                    data["name"],
                    data.get("items", []),
                    data.get("buy_items", []) 
                )
            elif data["type"] == "crafter":
                npc = CrafterNPC(
                    data["center"], image,
                    (self._all_sprites, self._collision_sprites),
                    data["name"]
                )
            else:
                continue
            
            self._level.shop_npcs.append(npc)
            

    def _load_npc_image(self, filename: str, fallback_color: tuple) -> pygame.Surface:
        import os
        surf = load_single(get_path("graphics", "npc", filename))
        if surf:
            return self._scale_npc(surf)
        fb = pygame.Surface((42, 58), pygame.SRCALPHA)
        pygame.draw.ellipse(fb, fallback_color, (9, 5, 24, 22))
        pygame.draw.rect(fb, fallback_color, (10, 24, 22, 23), border_radius=5)
        pygame.draw.rect(fb, (88, 55, 34), (13, 45, 7, 11))
        pygame.draw.rect(fb, (88, 55, 34), (22, 45, 7, 11))
        return fb

    @staticmethod
    def _scale_npc(surf: pygame.Surface) -> pygame.Surface:
        rect = surf.get_bounding_rect(min_alpha=1)
        if rect.width > 0 and rect.height > 0:
            rect.inflate_ip(6, 6)
            rect.clamp_ip(surf.get_rect())
            cropped = pygame.Surface(rect.size, pygame.SRCALPHA)
            cropped.blit(surf, (0, 0), rect)
            surf = cropped
        return pygame.transform.scale(surf, (42, 58))