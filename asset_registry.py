from __future__ import annotations
import os
import pygame
from settings import TILE_SIZE
from support import (
    get_path,
    load_folder_scaled,
    load_tile_variants,
    load_single,
)


class SeasonAssets:
    __slots__ = (
        "grass_surfs",
        "field_surfs",
        "path_surfs",
        "yard_surfs",
        "sand_surfs",
        "houses",
        "tents",
        "stones",
        "decor",
        "grass_objs",
        "boxes",
        "fence_h",
        "fence_v",
        "fence_post",
        "tree_small",
        "tree_medium",
    )

    def __init__(self):
        for slot in self.__slots__:
            setattr(self, slot, None)


class AssetRegistry:
    def __init__(self) -> None:
        self._seasons: dict[str, SeasonAssets] = {
            "normal": SeasonAssets(),
            "snow": SeasonAssets(),
            "autumn": SeasonAssets(),
        }
        self.water_surfs: list[pygame.Surface] = []

    def for_season(self, mode: str) -> SeasonAssets:
        return self._seasons.get(mode, self._seasons["normal"])

    def load(self) -> None:
        """Load semua asset dari disk."""
        self._load_water()
        self._load_season_assets(
            "normal",
            tiles_dir=get_path("graphics", "tiles"),
            obj_dir=get_path("graphics", "objects"),
            tile_prefix="FieldsTile",
            sand_prefix="beach",
        )
        self._load_season_assets(
            "snow",
            tiles_dir=get_path("graphics", "salju", "tiles"),
            obj_dir=get_path("graphics", "salju", "objects"),
            tile_prefix="snow_FieldsTile",
            sand_prefix="snow_sand",
            fence_prefix="snow_",
        )
        self._load_season_assets(
            "autumn",
            tiles_dir=get_path("graphics", "gugur", "tiles"),
            obj_dir=get_path("graphics", "gugur", "objects"),
            tile_prefix="gugur_FieldsTile",
            sand_prefix="gugur_sand",
            fence_prefix="gugur_",
        )

        normal = self._seasons["normal"]
        for season in ("snow", "autumn"):
            s = self._seasons[season]
            for slot in SeasonAssets.__slots__:
                if not getattr(s, slot):
                    setattr(s, slot, getattr(normal, slot))

    def _load_water(self) -> None:
        water_dir = get_path("graphics", "tiles", "water_anim")
        self.water_surfs = load_folder_scaled(
            water_dir, fixed_size=(TILE_SIZE, TILE_SIZE)
        )
        if not self.water_surfs:
            fallback = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            fallback.fill((120, 200, 220))
            self.water_surfs = [fallback]

    def _load_season_assets(
        self,
        season: str,
        tiles_dir: str,
        obj_dir: str,
        tile_prefix: str,
        sand_prefix: str,
        fence_prefix: str = "",
    ) -> None:
        s = self._seasons[season]
        ts = TILE_SIZE

        s.grass_surfs = load_tile_variants(tiles_dir, tile_prefix, [38], (ts, ts))
        s.field_surfs = load_tile_variants(
            tiles_dir, tile_prefix, range(1, 38), (ts, ts)
        )
        s.path_surfs = load_tile_variants(
            tiles_dir,
            tile_prefix,
            [46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56],
            (ts, ts),
        )
        s.yard_surfs = load_tile_variants(
            tiles_dir, tile_prefix, [57, 58, 59, 60, 61, 62, 63, 64], (ts, ts)
        )

        if sand_prefix == "beach":
            s.sand_surfs = load_folder_scaled(
                os.path.join(tiles_dir, "beach"), fixed_size=(ts, ts)
            )
        else:
            s.sand_surfs = load_tile_variants(
                tiles_dir, sand_prefix, range(1, 7), (ts, ts)
            )

        if not s.grass_surfs:
            s.grass_surfs = load_folder_scaled(tiles_dir, fixed_size=(ts, ts))

        s.houses = load_folder_scaled(
            os.path.join(obj_dir, "7_House"), fixed_size=(ts * 5, ts * 5)
        )
        s.tents = load_folder_scaled(
            os.path.join(obj_dir, "6_Tent"), fixed_size=(ts * 3, ts * 3)
        )
        s.stones = load_folder_scaled(
            os.path.join(obj_dir, "2_Stone"), fixed_size=(ts, ts)
        )
        s.decor = load_folder_scaled(os.path.join(obj_dir, "3_Decor"), min_size=28)
        s.grass_objs = load_folder_scaled(os.path.join(obj_dir, "5_Grass"), min_size=18)
        s.boxes = load_folder_scaled(
            os.path.join(obj_dir, "4_Box"), fixed_size=(ts, ts)
        )

        fp = fence_prefix
        s.fence_h = load_single(os.path.join(tiles_dir, f"{fp}Tile2_05.png"), (ts, ts))
        s.fence_v = load_single(os.path.join(tiles_dir, f"{fp}Tile2_06.png"), (ts, ts))
        s.fence_post = load_single(
            os.path.join(tiles_dir, f"{fp}Tile2_01.png"), (ts, ts)
        )

        tree_dir = os.path.join(obj_dir, "pydew_trees")
        s.tree_small = load_single(
            os.path.join(tree_dir, "tree_small_dark.png"), (54, 98)
        ) or load_single(os.path.join(tree_dir, "tree_small.png"), (54, 98))
        s.tree_medium = load_single(
            os.path.join(tree_dir, "tree_medium_dark.png"), (72, 108)
        ) or load_single(os.path.join(tree_dir, "tree_medium.png"), (72, 108))
