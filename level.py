from __future__ import annotations
import os
import random

import pygame

from settings import *
from sprites import *
from entities.player import Player
from support import *

from maps.build_map import T_GRASS, T_FIELD, T_PATH, T_YARD, T_WATER, T_SAND, build_map
from musim import MonthSeasonManager
from MonthNameUI import MonthNameUI
from cave_link.adventure import CaveAdventure
from crafting.crafting_manager import CraftingManager

from world.game_clock import GameClock
from world.animated_water import AnimatedWater
from world.weather_manager import WeatherManager
from inventories.inventory import Inventory
from items.seed_item import SeedItem
from items.food_item import FoodItem
from items.material_item import MaterialItem
from asset_registry import AssetRegistry
from world_builders import (
    TileBuilder,
    HouseBuilder,
    FenceBuilder,
    TreeBuilder,
    DetailBuilder,
    MarketBuilder,
)
from ui_panels import (
    ShopPanel,
    CraftingPanel,
    InventoryBar,
    PlayerStatusPanel,
    ProximityPrompt,
)

from camera_group import CameraGroup
class Level:

    def __init__(self, app) -> None:
        self.app = app
        self.display_surface = pygame.display.get_surface()

        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.random = random.Random(33)

        self._start_music()
        self.month_system = MonthSeasonManager()
        self.season_mode = self.month_system.visual_season
        self.month_ui = MonthNameUI()

        self.weather_manager = WeatherManager()
        self.clock_ui = GameClock()
        self.clock_ui.day = self.month_system.day

        self.assets = AssetRegistry()
        self.assets.load()

        self._door_sound = self._load_door_sound()

        self.money = 120
        self.inventory = Inventory(max_slots=20)
        self.inventory.money = 120
        
        wood_item = MaterialItem("Kayu", 8, 4, "assets/images/items/wood.png")
        self.inventory.add_item(wood_item, 5)
        
        stone_item = MaterialItem("Batu", 6, 3, "assets/images/items/stone.png")
        self.inventory.add_item(stone_item, 3) 
        
        self.shop_npcs = []
        self.well_gateway = None
        self.cave_game = CaveAdventure()
        self.cave_return_pos = None
        self.mode = "outside"
        self.pvz_active = False

        self.crafting = CraftingManager()

        self.shop_panel = ShopPanel(self)
        self.crafting_panel = CraftingPanel(self)
        self.inventory_bar = InventoryBar(self)
        self.status_panel = PlayerStatusPanel(self)
        self.proximity_prompt = ProximityPrompt(self)
        self.inventory_bar.open()

        self._ui_panels = [
            self.shop_panel,
            self.crafting_panel,
            self.inventory_bar,
            self.status_panel,
            self.proximity_prompt,
        ]

        self.clock_ui.season_mode = self.season_mode

        if self.month_system.is_rainy_day:
            self.weather_manager.set_weather("rain")
        else:
            self.weather_manager.set_weather(None)

        self._setup()
        self._setup_interior()

    def _setup(self) -> None:
        self.random.seed(33)
        self.grid = build_map()

        builders = [
            TileBuilder(self),
            HouseBuilder(self),
            FenceBuilder(self),
            TreeBuilder(self),
            DetailBuilder(self),
            MarketBuilder(self),
        ]
        for builder in builders:
            builder.build()

        self.player = Player(
            (SPAWN_X, SPAWN_Y),
            self.all_sprites,
            self.collision_sprites,
        )
        self.house_door_rect = pygame.Rect(
            11 * TILE_SIZE,
            9 * TILE_SIZE,
            TILE_SIZE * 2,
            TILE_SIZE + 20,
        )

    def _setup_interior(self) -> None:
        self.interior_w = 24
        self.interior_h = 18
        self.interior_sprites = CameraGroup(
            world_width=self.interior_w * TILE_SIZE,
            world_height=self.interior_h * TILE_SIZE,
            background_color=(0, 0, 0),
            center_small_world=True,
        )
        self.interior_collision_sprites = pygame.sprite.Group()

        theme = self._get_interior_theme()
        floor = self._make_interior_tile(*theme["floor"])
        light_wall = self._make_seasonal_wall_tile()
        trim = self._make_interior_tile(*theme["trim"])

        for ty in range(self.interior_h):
            for tx in range(self.interior_w):
                surf = light_wall if ty < 3 else trim if ty == 3 else floor
                Generic(
                    (tx * TILE_SIZE, ty * TILE_SIZE),
                    surf.copy(),
                    self.interior_sprites,
                    z=LAYERS["ground"],
                )

        for tx in range(self.interior_w):
            CollideTile(
                (tx * TILE_SIZE, 0),
                (TILE_SIZE, TILE_SIZE),
                self.interior_collision_sprites,
            )
            CollideTile(
                (tx * TILE_SIZE, (self.interior_h - 1) * TILE_SIZE),
                (TILE_SIZE, TILE_SIZE),
                self.interior_collision_sprites,
            )
        for ty in range(self.interior_h):
            CollideTile(
                (0, ty * TILE_SIZE),
                (TILE_SIZE, TILE_SIZE),
                self.interior_collision_sprites,
            )
            CollideTile(
                ((self.interior_w - 1) * TILE_SIZE, ty * TILE_SIZE),
                (TILE_SIZE, TILE_SIZE),
                self.interior_collision_sprites,
            )

        self._populate_interior()

        self.exit_center_x = 11 * TILE_SIZE
        self.exit_center_y = 15 * TILE_SIZE
        self.exit_interact_rect = pygame.Rect(
            self.exit_center_x - 2,
            14 * TILE_SIZE + 8,
            TILE_SIZE * 2 + 4,
            TILE_SIZE + 12,
        )
        frames = self._make_exit_door_frames()
        self.interior_door_sprite = DoorSprite(
            (self.exit_center_x, self.exit_center_y),
            frames,
            self.interior_sprites,
            z=LAYERS["objects"],
        )
        self._interior_door_block = CollideTile(
            (self.exit_center_x + 10, self.exit_center_y + 10),
            (TILE_SIZE * 2 - 20, TILE_SIZE * 2 - 12),
            self.interior_collision_sprites,
        )
        self.interior_player = Player(
            (12 * TILE_SIZE, 14 * TILE_SIZE),
            self.interior_sprites,
            self.interior_collision_sprites,
        )
        self.exit_animating = False
        self.exit_anim_elapsed = 0.0

    def _populate_interior(self) -> None:
        placements = [
            ((3 * TILE_SIZE, 5 * TILE_SIZE), (0, 96, 64, 96, 1.2), (62, 78)),
            ((7 * TILE_SIZE, 5 * TILE_SIZE), (64, 96, 64, 96, 1.2), (62, 78)),
            ((16 * TILE_SIZE, 6 * TILE_SIZE), (320, 128, 32, 64, 1.1), (35, 55)),
            ((18 * TILE_SIZE, 6 * TILE_SIZE), (384, 128, 64, 64, 1.05), (62, 52)),
            ((5 * TILE_SIZE, 12 * TILE_SIZE), (0, 320, 96, 64, 1.1), None),
            ((12 * TILE_SIZE, 12 * TILE_SIZE), (304, 320, 128, 64, 1.0), None),
            ((18 * TILE_SIZE, 12 * TILE_SIZE), (464, 320, 112, 64, 0.95), None),
        ]
        for pos, crop_args, col_size in placements:
            *rect, scale = crop_args
            surf = self._crop_decoration(tuple(rect), scale)
            if surf:
                Generic(pos, surf, self.interior_sprites, z=LAYERS["objects"])
                if col_size:
                    CollideTile(pos, col_size, self.interior_collision_sprites)

    def run(self, dt: float) -> None:
        if self._check_midnight_pvz():
            return

        if self.mode == "cave":
            self._run_cave(dt)
            return

        self.display_surface.fill(COL_BG)
        self._update_time(dt)
        AnimatedWater.step_global()
        
        # self.weather_manager.set_weather('rain')

        if self.mode == "inside":
            self._run_interior(dt)
        else:
            self._run_outside(dt)

        self.weather_manager.draw_darkness(self._darkness_level())
        self._draw_ui()

    def _run_cave(self, dt: float) -> None:
        self.cave_game.update(dt)
        self.cave_game.draw()
        if self.cave_game.request_exit:
            self._return_from_cave()

    def _run_interior(self, dt: float) -> None:
        if self.exit_animating:
            self.exit_anim_elapsed += dt
            frame = (
                0
                if self.exit_anim_elapsed < 0.08
                else (1 if self.exit_anim_elapsed < 0.16 else 2)
            )
            self.interior_door_sprite.set_frame(frame)
            if self.exit_anim_elapsed >= 0.24:
                self._exit_house()
        else:
            self.interior_sprites.update(dt)
            self.interior_door_sprite.set_frame(0)
        self.interior_sprites.custom_draw(self.interior_player)

    def _run_outside(self, dt: float) -> None:
        self.all_sprites.custom_draw(self.player)

        self.weather_manager.update(dt)

        if self.season_mode == "snow":
            pass
        elif self.season_mode == "autumn":
            pass

        if not self.shop_panel.is_open:
            self.all_sprites.update(dt)

    def handle_event(self, event: pygame.Event) -> None:
        if self.mode == "cave":
            self.cave_game.handle_event(event)
            if self.cave_game.request_exit:
                self._return_from_cave()
            return

        menu_active = self.shop_panel.is_open or self.crafting_panel.is_open
        if hasattr(self, "player"):
            self.player.menu_active = menu_active

        for panel in self._ui_panels:
            if panel.handle_event(event):

                if not menu_active:
                    self._restore_player_controls()
                return

        if event.type == pygame.KEYDOWN:
            self._handle_global_keys(event)

        ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL
        if ctrl:
            self._handle_zoom(event)

    def _handle_global_keys(self, event: pygame.Event) -> None:
        key = event.key
        if key == pygame.K_k:
            self.clock_ui.toggle_speed()
        elif key == pygame.K_l:
            self.advance_month()
        elif key == pygame.K_e:
            self._interact()

    def _interact(self) -> None:
        if self.mode == "outside":
            npc = self._get_nearby_shop_npc()
            if npc:
                self._open_for_npc(npc)
            elif self._near_well_gateway():
                self._enter_cave()
            elif self.house_door_rect.colliderect(self.player.hitbox):
                self._enter_house()
        elif self.mode == "inside":
            if (
                self.exit_interact_rect.colliderect(self.interior_player.hitbox)
                and not self.exit_animating
            ):
                self.exit_animating = True
                self.exit_anim_elapsed = 0.0
                if self._door_sound:
                    self._door_sound.play()

    def _open_for_npc(self, npc) -> None:
        self._freeze_player()

        npc.interact(self)

    def _handle_zoom(self, event: pygame.Event) -> None:
        group = self.interior_sprites if self.mode == "inside" else self.all_sprites
        if event.type == pygame.MOUSEWHEEL:
            group.change_zoom(event.y)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                group.change_zoom(1)
            elif event.button == 5:
                group.change_zoom(-1)
            elif event.button == 2:
                group.reset_zoom()

    def _enter_house(self) -> None:
        self._stop_player_movement(self.player)
        self._fade_transition()
        self.mode = "inside"
        self.exit_animating = False
        self.exit_anim_elapsed = 0.0
        if hasattr(self, "interior_door_sprite"):
            self.interior_door_sprite.reset()
        self.interior_player.rect.center = (12 * TILE_SIZE, 14 * TILE_SIZE)
        self.interior_player.hitbox.center = self.interior_player.rect.center
        self.interior_player.pos.update(self.interior_player.rect.center)

    def _exit_house(self) -> None:
        self._stop_player_movement(self.interior_player)
        self._fade_transition()
        self.mode = "outside"
        self.exit_animating = False
        self.exit_anim_elapsed = 0.0
        if hasattr(self, "interior_door_sprite"):
            self.interior_door_sprite.reset()
        self.player.rect.center = (12 * TILE_SIZE, 10 * TILE_SIZE)
        self.player.hitbox.center = self.player.rect.center
        self.player.pos.update(self.player.rect.center)

    def _enter_cave(self) -> None:
        if self.mode != "outside" or not self.well_gateway:
            return
        self._stop_player_movement(self.player)
        self.cave_return_pos = self.player.rect.center
        self._fade_transition()
        self.mode = "cave"
        self.cave_game.enter()

    def _return_from_cave(self) -> None:
        self.cave_game.leave(reset=True)
        self._fade_transition()
        self.mode = "outside"
        if self.cave_return_pos is None and self.well_gateway:
            self.cave_return_pos = (
                self.well_gateway.rect.centerx,
                self.well_gateway.rect.bottom + 20,
            )
        if self.cave_return_pos:
            p = self.player
            p.rect.center = self.cave_return_pos
            p.hitbox.center = p.rect.center
            p.pos.update(p.rect.center)
            self.cave_return_pos = None
        self._start_music()

    def _fade_transition(self) -> None:
        fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade.fill((0, 0, 0))
        for alpha in range(0, 230, 28):
            fade.set_alpha(alpha)
            self.display_surface.blit(fade, (0, 0))
            pygame.display.update()
            pygame.time.delay(14)

    def advance_month(self) -> None:
        self.month_system.advance_month()
        self.clock_ui.day = self.month_system.day
        self._sync_season_from_month(force=True)

    def _sync_season_from_month(self, force: bool = False) -> None:
        new_mode = self.month_system.visual_season
        changed = force or new_mode != self.season_mode
        self.season_mode = new_mode
        self.clock_ui.season_mode = self.season_mode

        
        if self.season_mode == "snow":
            self.weather_manager.set_weather("snow")
        elif self.season_mode == "autumn":
            self.weather_manager.set_weather("autumn")
        else:
            if self.month_system.is_rainy_day:
                self.weather_manager.set_weather("rain")
            else:
                self.weather_manager.set_weather(None)

        if changed:
            self._rebuild_interior_for_season()
            if self.mode == "outside":
                self._rebuild_outside_for_season()

    def _rebuild_outside_for_season(self) -> None:
        if not hasattr(self, "player"):
            return
        old_center = self.player.rect.center
        old_zoom = self.all_sprites.zoom
        old_energy = getattr(self.player, "energy", 100)
        old_facing = getattr(self.player, "facing", "down")
        self._stop_player_movement(self.player)

        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.all_sprites.set_zoom(old_zoom)
        self._setup()

        p = self.player
        p.rect.center = old_center
        p.hitbox.center = old_center
        p.pos.update(old_center)
        p.energy = old_energy
        p.facing = old_facing
        p.sprinting = False
        p.direction.update(0, 0)

    def _rebuild_interior_for_season(self) -> None:
        old_zoom = (
            getattr(self.interior_sprites, "zoom", CAMERA_ZOOM)
            if hasattr(self, "interior_sprites")
            else CAMERA_ZOOM
        )
        old_center = (
            getattr(
                self.interior_player,
                "rect",
                type("R", (), {"center": (12 * TILE_SIZE, 14 * TILE_SIZE)})(),
            ).center
            if hasattr(self, "interior_player")
            else (12 * TILE_SIZE, 14 * TILE_SIZE)
        )
        old_energy = getattr(getattr(self, "interior_player", None), "energy", 100)
        old_facing = getattr(getattr(self, "interior_player", None), "facing", "down")
        if hasattr(self, "interior_player"):
            self._stop_player_movement(self.interior_player)

        self._setup_interior()
        self.interior_sprites.set_zoom(old_zoom)

        p = self.interior_player
        p.rect.center = old_center
        p.hitbox.center = old_center
        p.pos.update(old_center)
        p.energy = old_energy
        p.facing = old_facing
        p.sprinting = False
        p.direction.update(0, 0)

    def _check_midnight_pvz(self) -> bool:
        if (
            not self.pvz_active
            and self.clock_ui.hour == 16
            and self.clock_ui.minute == 0
        ):
            self._start_pvz_mode()
            return True
        return False

    def _start_pvz_mode(self) -> None:
        if self.pvz_active:
            return
        self.pvz_active = True
        self.pvz_return_pos = self.player.rect.center
        pygame.mixer.music.stop()
        self.player.controls_enabled = False
        from scenes.pvz_scene import PVZScene

        self.app.change_scene(PVZScene(self.app))

    def _land_at(self, tx: int, ty: int) -> bool:
        if not (0 <= ty < len(self.grid) and 0 <= tx < len(self.grid[0])):
            return False
        return self.grid[ty][tx] != T_WATER

    def _area_land(self, tx: int, ty: int, w: int = 1, h: int = 1) -> bool:
        return all(
            self._land_at(xx, yy)
            for yy in range(ty, ty + h)
            for xx in range(tx, tx + w)
        )

    def _near_well_gateway(self) -> bool:
        return (
            self.mode == "outside"
            and self.well_gateway is not None
            and hasattr(self, "player")
            and self.well_gateway.interact_rect.colliderect(self.player.hitbox)
        )

    def _get_nearby_shop_npc(self):
        """Mendapatkan NPC terdekat (polymorphism sudah otomatis)"""
        if self.mode != "outside" or not hasattr(self, "player"):
            return None
        for npc in self.shop_npcs:
            if npc.interact_rect.colliderect(self.player.hitbox):
                return npc
        return None

    @staticmethod
    def _stop_player_movement(player) -> None:
        if hasattr(player, "stop_run_sound"):
            player.stop_run_sound()
        player.direction.update(0, 0)
        player.sprinting = False
        if hasattr(player, "velocity_x"):
            player.velocity_x = 0
        if hasattr(player, "velocity_y"):
            player.velocity_y = 0

    def _freeze_player(self) -> None:
        """Freeze player dan set menu_active = True."""
        self._stop_player_movement(self.player)
        if hasattr(self, "player"):
            self.player.controls_enabled = False

    def _restore_player_controls(self) -> None:
        if hasattr(self, "player"):
            self.player.controls_enabled = True
            self.player.menu_active = False

    def _update_time(self, dt: float) -> None:
        day_changed = self.clock_ui.update(dt)
        if day_changed:
            self.month_system.advance_day()
            self.clock_ui.day = self.month_system.day
            self._sync_season_from_month()
        self.clock_ui.season_mode = self.season_mode

        
        if self.month_system.is_rainy_day:
            self.weather_manager.set_weather("rain")
        elif self.season_mode == "snow":
            self.weather_manager.set_weather("snow")
        elif self.season_mode == "autumn":
            self.weather_manager.set_weather("autumn")
        else:
            self.weather_manager.set_weather(None)

    def _darkness_level(self) -> int:
        base = {
            "rain": 62,
            "snow": 18,
            "autumn": 8,
        }.get(self.season_mode, 0)
        return max(self.clock_ui.darkness_alpha(), base)

    def _draw_ui(self) -> None:
        for panel in self._ui_panels:
            panel.draw(self.display_surface)
            panel.update(0)
        self.clock_ui.draw(self.display_surface, self.month_system.date_text)
        self.month_ui.draw(self.display_surface, self.month_system.month_name)

    def _start_music(self) -> None:
        try:
            path = get_path("audio", "bg_music.mp3")
            if not os.path.exists(path):
                path = get_path("audio", "bg.mp3")
            if os.path.exists(path):
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(0.35)
                pygame.mixer.music.play(loops=-1)
        except Exception as e:
            print(f"[Music] Could not load music: {e}")

    @staticmethod
    def _load_door_sound():
        try:
            path = get_path("audio", "door_open.wav")
            if os.path.exists(path):
                snd = pygame.mixer.Sound(path)
                snd.set_volume(0.35)
                return snd
        except Exception:
            pass
        return None

    def _get_interior_theme(self) -> dict:
        themes = {
            "snow": {
                "floor": ((214, 219, 229), (175, 180, 194)),
                "wall": ((233, 238, 246), (205, 213, 225)),
                "trim": ((183, 190, 204), (150, 157, 170)),
            },
            "rain": {
                "floor": ((153, 127, 100), (118, 95, 71)),
                "wall": ((198, 188, 177), (170, 160, 150)),
                "trim": ((137, 111, 87), (111, 88, 66)),
            },
            "autumn": {
                "floor": ((182, 126, 74), (148, 98, 52)),
                "wall": ((222, 184, 132), (188, 149, 101)),
                "trim": ((168, 112, 64), (136, 88, 47)),
            },
        }
        return themes.get(
            self.season_mode,
            {
                "floor": ((176, 122, 72), (140, 95, 52)),
                "wall": ((205, 173, 121), (194, 159, 110)),
                "trim": ((166, 112, 67), (128, 84, 45)),
            },
        )

    def _make_interior_tile(self, color: tuple, border=None) -> pygame.Surface:
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill(color)
        if border:
            pygame.draw.rect(surf, border, surf.get_rect(), 1)
        return surf

    def _make_seasonal_wall_tile(self) -> pygame.Surface:
        theme = self._get_interior_theme()["wall"]
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill(theme[0])
        for y in range(0, TILE_SIZE, 8):
            pygame.draw.line(surf, theme[1], (0, y), (TILE_SIZE, y), 1)
        pygame.draw.rect(
            surf, tuple(max(0, c - 30) for c in theme[1]), surf.get_rect(), 1
        )
        return surf

    def _crop_decoration(self, rect: tuple, scale: float = 1) -> pygame.Surface | None:
        sheet = load_single(get_path("graphics", "objects", "House Decoration.png"))
        if not sheet:
            return None
        surf = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        surf.blit(sheet, (0, 0), rect)
        if scale != 1:
            surf = pygame.transform.scale(
                surf, (int(rect[2] * scale), int(rect[3] * scale))
            )
        return surf

    def _make_exit_door_frames(self) -> list[pygame.Surface]:
        base = pygame.Surface((TILE_SIZE * 2, TILE_SIZE * 2), pygame.SRCALPHA)

        def draw_frame(kind: str) -> pygame.Surface:
            surf = base.copy()
            pygame.draw.rect(surf, (102, 67, 33), (10, 4, 44, 58), border_radius=4)
            pygame.draw.rect(surf, (184, 136, 84), (14, 8, 36, 50), border_radius=3)
            pygame.draw.rect(surf, (120, 79, 42), (18, 12, 28, 40), border_radius=2)
            pygame.draw.rect(
                surf, (199, 151, 101), (18, 34, 28, 14), 2, border_radius=2
            )
            pygame.draw.rect(
                surf, (199, 151, 101), (18, 16, 28, 12), 2, border_radius=2
            )
            if kind == "closed":
                pygame.draw.rect(surf, (132, 88, 47), (18, 12, 28, 40), border_radius=2)
                pygame.draw.rect(
                    surf, (184, 136, 84), (21, 16, 22, 12), 2, border_radius=2
                )
                pygame.draw.rect(
                    surf, (184, 136, 84), (21, 34, 22, 12), 2, border_radius=2
                )
                pygame.draw.circle(surf, (227, 191, 93), (40, 32), 2)
            elif kind == "mid":
                pts = [(21, 12), (40, 17), (40, 51), (21, 46)]
                pygame.draw.polygon(surf, (132, 88, 47), pts)
                pygame.draw.lines(surf, (184, 136, 84), True, pts, 2)
                pygame.draw.circle(surf, (227, 191, 93), (36, 32), 2)
                pygame.draw.polygon(
                    surf, (60, 38, 15), [(20, 14), (26, 16), (26, 44), (20, 46)]
                )
            else:
                pts = [(18, 12), (28, 18), (28, 48), (18, 52)]
                pygame.draw.polygon(surf, (132, 88, 47), pts)
                pygame.draw.lines(surf, (184, 136, 84), True, pts, 2)
                pygame.draw.circle(surf, (227, 191, 93), (25, 33), 2)
                pygame.draw.rect(surf, (42, 24, 9), (31, 14, 17, 36), border_radius=2)
            return surf

        return [draw_frame("closed"), draw_frame("mid"), draw_frame("open")]
