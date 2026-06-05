from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING

import pygame
import os
from base import BaseUIPanel
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from items.material_item import MaterialItem

if TYPE_CHECKING:
    from level import Level


class InventoryBar(BaseUIPanel):

    _SLOTS = 10
    _SLOT_SIZE = 42
    _GAP = 6
    _PAD = 8

    def open(self, *args, **kwargs) -> None:
        self._open = True

    def close(self) -> None:
        self._open = False

    def handle_event(self, event: pygame.Event) -> bool:
        return False

    def draw(self, surface: pygame.Surface) -> None:
        ss, gs, pad = self._SLOT_SIZE, self._GAP, self._PAD
        fw = self._SLOTS * ss + (self._SLOTS - 1) * gs + pad * 2
        fh = ss + pad * 2

        x = (SCREEN_WIDTH - fw) // 2
        y = pad + 4 if self._level.mode == "inside" else SCREEN_HEIGHT - fh - 14

        panel = pygame.Surface((fw, fh), pygame.SRCALPHA)
        panel.fill((239, 195, 118, 240))
        pygame.draw.rect(panel, (122, 72, 27), panel.get_rect(), 4, border_radius=10)
        pygame.draw.rect(
            panel,
            (255, 233, 173),
            pygame.Rect(5, 5, fw - 10, fh - 10),
            2,
            border_radius=8,
        )

        grouped_items = self._level.inventory.get_all_items_grouped()
        inv_items = list(grouped_items.items())

        font = self._font_small
        icon_size = 28

        for i in range(self._SLOTS):
            sx = pad + i * (ss + gs)
            sy = pad
            sr = pygame.Rect(sx, sy, ss, ss)
            ir = pygame.Rect(sx + 3, sy + 3, ss - 6, ss - 6)
            pygame.draw.rect(panel, (170, 115, 58), sr, border_radius=6)
            pygame.draw.rect(panel, (113, 70, 24), sr, 2, border_radius=6)
            pygame.draw.rect(panel, (241, 205, 139), ir, border_radius=5)
            pygame.draw.rect(panel, (199, 151, 86), ir, 1, border_radius=5)

            if i < len(inv_items):
                name, count = inv_items[i]

                item = self._level.inventory.get_item(name)
                if item:
                    icon = item.get_icon((icon_size, icon_size))
                    if icon:
                        icon_x = sx + (ss - icon_size) // 2
                        icon_y = sy + (ss - icon_size) // 2 - 4
                        panel.blit(icon, (icon_x, icon_y))

                ct = font.render(str(count), True, (60, 39, 24))
                panel.blit(
                    ct, (sx + ss - ct.get_width() - 4, sy + ss - ct.get_height() - 2)
                )

        surface.blit(panel, (x, y))

        coin_txt = font.render(
            f"Koin: {self._level.inventory.money}", True, (255, 239, 177)
        )
        cbg = pygame.Surface(
            (coin_txt.get_width() + 18, coin_txt.get_height() + 12), pygame.SRCALPHA
        )
        cbg.fill((78, 43, 20, 218))
        pygame.draw.rect(cbg, (225, 188, 104), cbg.get_rect(), 2, border_radius=8)
        cbg.blit(coin_txt, (9, 6))
        surface.blit(cbg, (x + fw + 12, y + 8))

        coin_txt = font.render(f"Koin: {self._level.money}", True, (255, 239, 177))
        cbg = pygame.Surface(
            (coin_txt.get_width() + 18, coin_txt.get_height() + 12), pygame.SRCALPHA
        )
        cbg.fill((78, 43, 20, 218))
        pygame.draw.rect(cbg, (225, 188, 104), cbg.get_rect(), 2, border_radius=8)
        cbg.blit(coin_txt, (9, 6))
        surface.blit(cbg, (x + fw + 12, y + 8))

    def _get_item_image(self, item_name: str) -> str:
        """Dapatkan path gambar berdasarkan nama item"""

        item_images = {
            "Biji Bunga Matahari": "assets/images/items/sunflower_seed.png",
            "Biji Kentang": "assets/images/items/potato_seed.png",
            "Biji Kacang Polong": "assets/images/items/pea_seed.png",
            "Rumput": "assets/images/items/grass.png",
            "Kayu": "assets/images/items/wood.png",
            "Batu": "assets/images/items/stone.png",
            "Biji Jamur": "assets/images/items/mushroom_seed.png",
            "Bunga": "assets/images/items/flower.png",
            "Gandum": "assets/images/items/wheat.png",
            "Telur": "assets/images/items/egg.png",
            "Air": "assets/images/items/water.png",
            "Besi": "assets/images/items/iron.png",
            "Ramuan": "assets/images/items/water.png",
            "Roti": "assets/images/items/bread.png",
            "Pedang Kayu": "assets/images/items/wooden_sword.png",
            "Beliung": "assets/images/items/pickaxe.png",
            "Obat Herbal": "assets/images/items/herbal_medicine.png",
            "Pancing": "assets/images/items/fishing_rod.png",
        }
        return item_images.get(item_name, None)

    def _load_item_image(self, image_path, size):
        import os

        try:
            if os.path.exists(image_path):
                img = pygame.image.load(image_path).convert_alpha()
                return pygame.transform.scale(img, size)
            else:
                return print(f"Image not found: {image_path}")
        except Exception as e:
            return print(f"Error loading image {image_path}: {e}")

    def update(self, dt: float) -> None:
        pass


class PlayerStatusPanel(BaseUIPanel):
    """Panel foto + bar energi karakter."""

    def __init__(self, level: "Level") -> None:
        super().__init__(level)
        self._open = True
        from support import get_path
        from support import load_single

        self._face = load_single(
            get_path("graphics", "ui", "character_face.png"), (54, 48)
        )

    def open(self, *args, **kwargs) -> None:
        self._open = True

    def close(self) -> None:
        pass

    def handle_event(self, event: pygame.Event) -> bool:
        return False

    def draw(self, surface: pygame.Surface) -> None:
        player = (
            self._level.interior_player
            if self._level.mode == "inside"
            else self._level.player
        )

        panel = pygame.Surface((292, 58), pygame.SRCALPHA)
        panel.fill((255, 221, 128, 232))
        pygame.draw.rect(panel, (125, 75, 28), panel.get_rect(), 4, border_radius=10)
        pygame.draw.rect(
            panel, (255, 243, 177), pygame.Rect(6, 6, 280, 46), 2, border_radius=8
        )
        surface.blit(panel, (14, 14))

        pygame.draw.rect(surface, (95, 58, 31), (21, 20, 58, 50), border_radius=8)
        pygame.draw.rect(surface, (255, 238, 173), (24, 23, 52, 44), 2, border_radius=7)
        if self._face:
            surface.blit(self._face, (23, 23))

        for i in range(7):
            hx = 76 + i * 30
            hy = 29
            pygame.draw.circle(surface, (216, 42, 55), (hx + 7, hy + 7), 7)
            pygame.draw.circle(surface, (216, 42, 55), (hx + 17, hy + 7), 7)
            pygame.draw.polygon(
                surface,
                (216, 42, 55),
                [(hx + 1, hy + 10), (hx + 23, hy + 10), (hx + 12, hy + 25)],
            )
            pygame.draw.circle(surface, (255, 124, 132), (hx + 8, hy + 5), 2)

        bw, bh = 34, 172
        bx = SCREEN_WIDTH - 58
        by = SCREEN_HEIGHT - bh - 28
        pygame.draw.rect(surface, (185, 94, 19), (bx, by, bw, bh), border_radius=8)
        pygame.draw.rect(
            surface, (255, 197, 43), (bx + 4, by + 4, bw - 8, bh - 8), border_radius=6
        )
        inner = pygame.Rect(bx + 9, by + 23, bw - 18, bh - 34)
        pygame.draw.rect(surface, (55, 110, 49), inner, border_radius=4)
        fill_h = int(inner.height * (player.energy / max(1, player.energy_max)))
        fill_rect = pygame.Rect(
            inner.x + 2, inner.bottom - fill_h + 2, inner.width - 4, max(0, fill_h - 4)
        )
        pygame.draw.rect(surface, (88, 231, 70), fill_rect, border_radius=3)

        font = self._level.clock_ui.font_small
        pygame.draw.rect(
            surface, (113, 70, 24), (bx + 8, by - 17, 18, 24), border_radius=4
        )
        surface.blit(font.render("E", True, (69, 38, 16)), (bx + 12, by - 14))

    def update(self, dt: float) -> None:
        pass


class ProximityPrompt(BaseUIPanel):
    """Label kecil 'Tekan E untuk ...' saat player dekat interactable."""

    def open(self, *args, **kwargs) -> None:
        self._open = True

    def close(self) -> None:
        self._open = False

    def handle_event(self, event: pygame.Event) -> bool:
        return False

    def draw(self, surface: pygame.Surface) -> None:
        if self._level.mode != "outside":
            return
        if self._level.shop_panel.is_open or self._level.crafting_panel.is_open:
            return

        text = self._get_prompt_text()
        if not text:
            return

        font = self._level.clock_ui.font_small
        label = font.render(text, True, (255, 255, 255))
        px, py = 16, 10
        w = label.get_width() + px * 2
        h = label.get_height() + py * 2
        x = (SCREEN_WIDTH - w) // 2
        y = SCREEN_HEIGHT - 132

        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((34, 27, 20, 220))
        pygame.draw.rect(bg, (225, 188, 104), bg.get_rect(), 3, border_radius=10)
        bg.blit(label, (px, py))
        surface.blit(bg, (x, y))

    def update(self, dt: float) -> None:
        pass

    def _get_prompt_text(self) -> str | None:
        level = self._level
        npc = level._get_nearby_shop_npc()
        if npc:
            if getattr(npc, "type", "") == "crafter":
                return f"Tekan E untuk Crafting — {npc.name}"
            return f"Tekan E untuk belanja — {npc.name}"
        if level._near_well_gateway():
            return "Tekan E untuk masuk Goa lewat sumur"
        if hasattr(level, "house_door_rect") and level.house_door_rect.colliderect(
            level.player.hitbox
        ):
            return "Tekan E untuk masuk rumah"
        return None


class ShopPanel(BaseUIPanel):
    """Panel pembelian DAN penjualan item"""

    def __init__(self, level: "Level") -> None:
        super().__init__(level)
        self.active_npc = None
        self.selected_index = 0
        self.scroll_offset = 0
        self.message = ""
        self.message_timer = 0.0
        self.mode = "buy"
        self._VISIBLE = 5
        self._W, self._H = 620, 620

    def open(self, npc) -> None:
        """Buka shop panel"""
        self._open = True
        self.active_npc = npc
        self.selected_index = 0
        self.scroll_offset = 0
        self.mode = "buy"
        self.message = ""
        self.message_timer = 2.0

    def close(self) -> None:
        """Tutup shop panel"""
        self._open = False
        self.active_npc = None
        self.message = ""
        self.message_timer = 0.0
        self.selected_index = 0
        self.scroll_offset = 0
        self.mode = "buy"

    def handle_event(self, event: pygame.Event) -> bool:
        if not self._open:
            return False
        if event.type != pygame.KEYDOWN:
            return False

        key = event.key

        if key in (pygame.K_e, pygame.K_q, pygame.K_ESCAPE):
            self.close()
            if hasattr(self._level, "_restore_player_controls"):
                self._level._restore_player_controls()
            return True

        if key == pygame.K_TAB:
            self._toggle_mode()
            return True

        items = self._get_current_items()
        if not items:
            return True

        if key == pygame.K_UP:
            self.selected_index = max(0, self.selected_index - 1)
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index
        elif key == pygame.K_DOWN:
            self.selected_index = min(len(items) - 1, self.selected_index + 1)
            if self.selected_index >= self.scroll_offset + self._VISIBLE:
                self.scroll_offset = self.selected_index - self._VISIBLE + 1
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.mode == "buy":
                self._buy(self.selected_index)
            else:
                self._sell(self.selected_index)

        return True

    def _toggle_mode(self) -> None:
        """Ganti antara mode beli dan jual"""
        if self.mode == "buy":

            if self.active_npc and self.active_npc.buy_items:
                self.mode = "sell"
                self.selected_index = 0
                self.scroll_offset = 0
                self._show_msg("")
            else:
                self._show_msg("NPC ini tidak membeli item apapun!")
        else:
            self.mode = "buy"
            self.selected_index = 0
            self.scroll_offset = 0
            self._show_msg("Mode BELI - Pilih item untuk dibeli")

    def _get_current_items(self):
        """Dapatkan daftar item sesuai mode aktif"""
        if self.mode == "buy":
            return self.active_npc.shop_items if self.active_npc else []
        else:

            inventory_items = []
            grouped = self._level.inventory.get_all_items_grouped()

            for item_name, count in grouped.items():
                item = self._level.inventory.get_item(item_name)
                if item and hasattr(item, "sell_price"):
                    inventory_items.append(
                        {
                            "name": item_name,
                            "count": count,
                            "sell_price": item.sell_price,
                            "desc": f"Jual {item_name} seharga {item.sell_price} koin",
                            "image": item.icon_path,
                        }
                    )
            return inventory_items

    def draw(self, surface: pygame.Surface) -> None:
        if not self._open or not self.active_npc:
            return

        npc = self.active_npc
        w, h = self._W, self._H
        x = (SCREEN_WIDTH - w) // 2
        y = (SCREEN_HEIGHT - h) // 2

        self._draw_shadow(surface, x, y, w, h)
        panel = self._make_panel_surface(w, h)

        mode_text = "BELI" if self.mode == "buy" else "JUAL"
        title = self._font_big.render(f"{npc.name} — {mode_text}", True, (68, 39, 19))
        coin = self._font_small.render(f"Koin: {self._level.money}", True, (68, 39, 19))
        panel.blit(title, (24, 20))
        panel.blit(coin, (w - coin.get_width() - 28, 26))

        tab_hint = self._font_small.render("TAB: Ganti Mode", True, (100, 70, 40))
        panel.blit(tab_hint, (24, 55))

        items = self._get_current_items()
        item_y_start = 90
        icon_size = 40

        for i in range(self._VISIBLE):
            idx = self.scroll_offset + i
            if idx >= len(items):
                break

            item = items[idx]
            row_y = item_y_start + i * 75
            row_rect = pygame.Rect(24, row_y, w - 48, 70)

            bg = (255, 233, 173) if idx == self.selected_index else (245, 220, 160)
            pygame.draw.rect(panel, bg, row_rect, border_radius=8)
            pygame.draw.rect(panel, (154, 96, 44), row_rect, 2, border_radius=8)

            image_path = item.get("image")
            if image_path:
                icon = self._load_item_image(image_path, (icon_size, icon_size))
                if icon:
                    panel.blit(icon, (row_rect.x + 8, row_rect.y + 15))
                    text_x = row_rect.x + icon_size + 16
                else:
                    text_x = row_rect.x + 12
            else:
                text_x = row_rect.x + 12

            if self.mode == "buy":
                name_text = item["name"]
                price_text = f"{item['price']} koin"
                desc_text = item["desc"]
                stock = item.get("stock")
                stock_text = f"Stok: {stock}" if stock is not None else "Stok: ∞"
            else:
                name_text = f"{item['name']} (x{item['count']})"
                price_text = f"Jual: {item['sell_price']} koin"
                desc_text = item["desc"]
                stock_text = f"Milik: {item['count']}"

            panel.blit(
                self._font_small.render(name_text, True, (56, 34, 18)),
                (text_x, row_rect.y + 8),
            )
            panel.blit(
                self._font_small.render(desc_text, True, (91, 66, 43)),
                (text_x, row_rect.y + 30),
            )

            price_color = (86, 51, 23) if self.mode == "buy" else (36, 92, 35)
            price_render = self._font_small.render(price_text, True, price_color)
            panel.blit(
                price_render,
                (row_rect.right - price_render.get_width() - 12, row_rect.y + 50),
            )

            stock_render = self._font_small.render(stock_text, True, (100, 70, 40))
            panel.blit(stock_render, (text_x, row_rect.y + 52))

        if items and 0 <= self.selected_index < len(items):
            sel = items[self.selected_index]
            info_y = item_y_start + self._VISIBLE * 75 + 10
            ir = pygame.Rect(24, info_y, w - 48, 70)
            pygame.draw.rect(panel, (255, 233, 173), ir, border_radius=8)
            pygame.draw.rect(panel, (154, 96, 44), ir, 2, border_radius=8)

            if self.mode == "buy":
                action_text = f"Tekan ENTER untuk membeli {sel['name']}"
            else:
                action_text = f"Tekan ENTER untuk menjual {sel['name']} (dapat {sel['sell_price']} koin)"

            panel.blit(
                self._font_small.render(action_text, True, (56, 34, 18)),
                (ir.x + 12, ir.y + 12),
            )

            if self.mode == "buy":
                panel.blit(
                    self._font_small.render(
                        f"Harga: {sel['price']} koin", True, (86, 51, 23)
                    ),
                    (ir.x + 12, ir.y + 36),
                )
            else:
                panel.blit(
                    self._font_small.render(
                        f"Harga jual: {sel['sell_price']} koin / unit",
                        True,
                        (36, 92, 35),
                    ),
                    (ir.x + 12, ir.y + 36),
                )

        panel.blit(
            self._font_small.render(
                "Up/Down : Pilih  |  ENTER : Aksi  |  TAB : Ganti Mode  |  E/Q : Tutup",
                True,
                (78, 48, 23),
            ),
            (24, h - 62),
        )

        if self.message and self.message_timer > 0:
            mc = (
                (36, 92, 35)
                if "berhasil" in self.message or "dijual" in self.message
                else (135, 45, 35)
            )
            panel.blit(self._font_small.render(self.message, True, mc), (24, h - 88))

        surface.blit(panel, (x, y))

    def _load_item_image(self, image_path, size):

        if os.path.exists(image_path):
            img = pygame.image.load(image_path).convert_alpha()
            return pygame.transform.scale(img, size)
        else:
            name = os.path.splitext(os.path.basename(image_path))[0].lower()
            return self._level.item_image_cache.get(name)

    def _create_item_object_from_data(self, item_data: dict):
        """Buat Item object dari data dictionary"""
        from items.seed_item import SeedItem
        from items.food_item import FoodItem
        from items.material_item import MaterialItem
        from items.weapon import Weapon

        name = item_data["name"]
        price = item_data["price"]
        image = item_data.get("image")

        if "Biji" in name:
            plant_type = name.replace("Biji ", "").lower()
            plant_type = plant_type.replace("bunga matahari", "sunflower")
            plant_type = plant_type.replace("kacang polong", "pea")
            return SeedItem(name, plant_type, 10, price, price // 2, image)
        elif name in ["Ramuan", "Roti"]:
            return FoodItem(name, 20, price, price // 2, image)
        elif name == "Pedang Kayu":
            return Weapon(name, damage=15, durability=50, icon_path=image)
        elif name == "Beliung":
            from items.tool import Tool

            return Tool(name, "Alat untuk menambang", 100, icon_path=image)
        else:
            return MaterialItem(name, price, price // 2, image)

    def _buy(self, index: int) -> None:
        """Beli item dari NPC"""
        npc = self.active_npc
        if not npc or not (0 <= index < len(npc.shop_items)):
            return
        item_data = npc.shop_items[index]

        if item_data.get("stock", 1) <= 0:
            self._show_msg(f"{item_data['name']} sedang habis!")
            return

        if self._level.inventory.money < item_data["price"]:
            self._show_msg(f"Koin tidak cukup untuk membeli {item_data['name']}.")
            return

        self._level.inventory.money -= item_data["price"]

        item_obj = self._create_item_object_from_data(item_data)
        if item_obj:
            self._level.inventory.add_item(item_obj)
        else:

            fallback_item = MaterialItem(
                item_data["name"],
                item_data["price"],
                item_data["price"] // 2,
                item_data.get("image"),
            )
            self._level.inventory.add_item(fallback_item)

        if "stock" in item_data:
            item_data["stock"] -= 1

        self._show_msg(f" {item_data['name']} berhasil dibeli!")

    def _create_item_object(self, item_name: str):
        """Buat object Item berdasarkan nama item hasil crafting"""
        from items.weapon import Weapon
        from items.food_item import FoodItem
        from items.material_item import MaterialItem
        from items.tool import Tool

        if item_name == "Pedang Kayu":
            return Weapon(
                "Pedang Kayu",
                damage=15,
                durability=50,
                icon_path="assets/images/items/wooden_sword.png",
            )
        elif item_name == "Beliung":
            return Tool(
                "Beliung",
                "Alat untuk menambang",
                100,
                icon_path="assets/images/items/pickaxe.png",
            )
        elif item_name == "Ramuan":
            return FoodItem(
                "Ramuan",
                energy_restore=30,
                buy_price=20,
                sell_price=10,
                icon_path="assets/images/items/water.png",
            )
        elif item_name == "Roti":
            return FoodItem(
                "Roti",
                energy_restore=20,
                buy_price=15,
                sell_price=8,
                icon_path="assets/images/items/bread.png",
            )
        elif item_name == "Obat Herbal":
            return FoodItem(
                "Obat Herbal",
                energy_restore=50,
                buy_price=30,
                sell_price=15,
                icon_path="assets/images/items/herbal_medicine.png",
            )
        elif item_name == "Pancing":
            return Tool(
                "Pancing",
                "Alat untuk memancing",
                60,
                icon_path="assets/images/items/fishing_rod.png",
            )
        else:
            return MaterialItem(item_name, 0, 0, None)

    def _sell(self, index: int) -> None:
        """Jual item ke NPC"""
        items = self._get_current_items()
        if not items or index >= len(items):
            return

        item = items[index]
        item_name = item["name"]
        sell_price = item["sell_price"]

        if self._level.inventory.remove_item(item_name, 1):
            self._level.inventory.money += sell_price
            self._show_msg(f"{item_name} terjual! +{sell_price} koin")
        else:
            self._show_msg(f"Tidak memiliki {item_name}!")

    def _show_msg(self, text: str) -> None:
        self.message = text
        self.message_timer = 2.0

    def update(self, dt: float) -> None:
        if self.message_timer > 0:
            self.message_timer = max(0.0, self.message_timer - dt)
            if self.message_timer <= 0 and not self._open:
                self.message = ""


class CraftingPanel(BaseUIPanel):
    """Panel crafting item di NPC Pengrajin."""

    def __init__(self, level: "Level") -> None:
        super().__init__(level)
        self.active_npc = None
        self.selected_index = 0
        self.scroll_offset = 0
        self.message = ""
        self.message_timer = 0.0
        self._VISIBLE = 5
        self._W, self._H = 620, 620

    def open(self, npc) -> None:
        """Buka crafting panel"""
        self._open = True
        self.active_npc = npc
        self.selected_index = 0
        self.scroll_offset = 0
        self.message = ""
        self.message_timer = 2.0

    def close(self) -> None:
        """Tutup crafting panel"""
        self._open = False
        self.active_npc = None
        self.message = ""
        self.message_timer = 0.0
        self.selected_index = 0
        self.scroll_offset = 0

    def handle_event(self, event: pygame.Event) -> bool:
        """Handle event untuk crafting panel"""
        if not self._open:
            return False
        if event.type != pygame.KEYDOWN:
            return False

        key = event.key
        if key in (pygame.K_e, pygame.K_q, pygame.K_ESCAPE):
            self.close()
            if hasattr(self._level, "_restore_player_controls"):
                self._level._restore_player_controls()
            return True

        items = list(self._level.crafting.recipes.keys())
        if not items:
            return True

        if key == pygame.K_UP:
            self.selected_index = max(0, self.selected_index - 1)
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index
        elif key == pygame.K_DOWN:
            self.selected_index = min(len(items) - 1, self.selected_index + 1)
            if self.selected_index >= self.scroll_offset + self._VISIBLE:
                self.scroll_offset = self.selected_index - self._VISIBLE + 1
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self._craft(items[self.selected_index])

        return True

    def draw(self, surface: pygame.Surface) -> None:
        if not self._open or not self.active_npc:
            return

        npc = self.active_npc
        w, h = self._W, self._H
        x = (SCREEN_WIDTH - w) // 2
        y = (SCREEN_HEIGHT - h) // 2

        shadow = pygame.Surface((w, h), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 110))
        surface.blit(shadow, (x + 5, y + 7))

        panel = self._make_panel_surface(w, h)

        title = self._font_big.render(f"{npc.name} — Crafting", True, (68, 39, 19))
        coin = self._font_small.render(f"Koin: {self._level.money}", True, (68, 39, 19))
        panel.blit(title, (24, 20))
        panel.blit(coin, (w - coin.get_width() - 28, 26))

        items = list(self._level.crafting.recipes.keys())
        item_y_start = 90
        visible_items = 5
        icon_size = 32

        for i in range(visible_items):
            idx = self.scroll_offset + i
            if idx >= len(items):
                break

            item_name = items[idx]
            recipe = self._level.crafting.recipes[item_name]
            row_y = item_y_start + i * 85
            row_rect = pygame.Rect(24, row_y, w - 48, 75)

            bg_color = (
                (255, 233, 173) if idx == self.selected_index else (245, 220, 160)
            )
            pygame.draw.rect(panel, bg_color, row_rect, border_radius=8)
            pygame.draw.rect(panel, (154, 96, 44), row_rect, 2, border_radius=8)

            image_path = recipe.get("image")
            if image_path:
                icon = self._load_item_image(image_path, (icon_size, icon_size))
                if icon:
                    panel.blit(icon, (row_rect.x + 8, row_rect.y + 14))
                    text_x = row_rect.x + icon_size + 16
                else:
                    text_x = row_rect.x + 12
            else:
                text_x = row_rect.x + 12

            name = self._font_small.render(item_name, True, (56, 34, 18))
            panel.blit(name, (text_x, row_rect.y + 8))

            desc = self._font_small.render(recipe["desc"], True, (91, 66, 43))
            panel.blit(desc, (text_x, row_rect.y + 30))

            bahan_text = ", ".join([f"{b} x{j}" for b, j in recipe["bahan"].items()])
            bahan = self._font_small.render(f"Bahan: {bahan_text}", True, (100, 70, 40))
            panel.blit(bahan, (text_x, row_rect.y + 52))

            can_craft, _ = self._level.crafting.can_craft(
                self._level.inventory, item_name
            )

            status_color = (36, 92, 35) if can_craft else (135, 45, 35)
            status_text = " Bisa dibuat" if can_craft else "Bahan kurang"
            status = self._font_small.render(status_text, True, status_color)
            panel.blit(
                status, (row_rect.right - status.get_width() - 12, row_rect.y + 55)
            )

        if items and 0 <= self.selected_index < len(items):
            selected_item = items[self.selected_index]
            recipe = self._level.crafting.recipes[selected_item]
            info_y = item_y_start + visible_items * 95 + 10
            info_rect = pygame.Rect(24, info_y, w - 48, 100)
            pygame.draw.rect(panel, (255, 233, 173), info_rect, border_radius=8)
            pygame.draw.rect(panel, (154, 96, 44), info_rect, 2, border_radius=8)

            bahan_list = list(recipe["bahan"].items())
            bahan_start_x = info_rect.x + 12
            bahan_y = info_rect.y + 12
            small_icon_size = 24

            for j, (bahan_name, jumlah) in enumerate(bahan_list):
                bahan_x = bahan_start_x + j * 100

                stok = self._level.inventory.get_item_count(bahan_name)

                bahan_text = f"{bahan_name} x{jumlah}"
                if stok >= jumlah:
                    bahan_color = (36, 92, 35)
                else:
                    bahan_color = (135, 45, 35)

                bahan_render = self._font_small.render(bahan_text, True, bahan_color)
                panel.blit(bahan_render, (bahan_x + small_icon_size + 4, bahan_y + 6))

                stok_text = f"(Stok: {stok})"
                stok_render = self._font_small.render(stok_text, True, (100, 70, 40))
                panel.blit(stok_render, (bahan_x + small_icon_size + 4, bahan_y + 26))

        footer = self._font_small.render(
            "Up/Down : Pilih item  |  ENTER/SPACE : Craft  |  E/Q : Tutup",
            True,
            (78, 48, 23),
        )
        panel.blit(footer, (24, h - 42))

        if self.message and self.message_timer > 0:
            msg_color = (36, 92, 35) if "Berhasil" in self.message else (135, 45, 35)
            msg = self._font_small.render(self.message, True, msg_color)
            panel.blit(msg, (24, h - 70))

        surface.blit(panel, (x, y))

    def _load_item_image(self, image_path, size):
        if os.path.exists(image_path):
            img = pygame.image.load(image_path).convert_alpha()
            return pygame.transform.scale(img, size)
        else:
            name = os.path.splitext(os.path.basename(image_path))[0].lower()
            return self._level.item_image_cache.get(name)

    def update(self, dt: float) -> None:
        """Update timer message"""
        if self.message_timer > 0:
            self.message_timer = max(0.0, self.message_timer - dt)

    def _craft(self, item_name: str) -> None:
        """Craft item"""
        success, msg = self._level.crafting.craft(self._level.inventory, item_name)
        self.message = msg
        self.message_timer = 2.0


class QuestPanel(BaseUIPanel):

    def __init__(self, level: "Level") -> None:
        super().__init__(level)
        self._open = False
        self._W, self._H = 500, 300

    def open(self, *args, **kwargs) -> None:
        self._open = True

    def close(self) -> None:
        self._open = False

    def handle_event(self, event: pygame.Event) -> bool:
        if not self._open:
            return False
        if event.type != pygame.KEYDOWN:
            return False

        key = event.key
        if key in (pygame.K_e, pygame.K_q, pygame.K_ESCAPE):
            self.close()
            return True

        if key == pygame.K_RIGHT:
            self._level.quest_manager.next_quest()
        elif key == pygame.K_LEFT:
            self._level.quest_manager.prev_quest()

        return True

    def draw(self, surface: pygame.Surface) -> None:
        if not self._open:
            return

        quest = self._level.quest_manager.get_current_quest()
        if not quest:
            return

        w, h = self._W, self._H
        x = (SCREEN_WIDTH - w) // 2
        y = (SCREEN_HEIGHT - h) // 2

        shadow = pygame.Surface((w, h), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 110))
        surface.blit(shadow, (x + 5, y + 7))

        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((244, 214, 143, 246))
        pygame.draw.rect(panel, (119, 74, 34), panel.get_rect(), 4, border_radius=14)
        pygame.draw.rect(
            panel,
            (255, 239, 177),
            pygame.Rect(9, 9, w - 18, h - 18),
            2,
            border_radius=10,
        )

        font_big = self._level.clock_ui.font_big
        font = self._level.clock_ui.font_small

        quest_id = quest["id"]
        is_completed = self._level.quest_manager.is_quest_completed(quest_id)
        total = self._level.quest_manager.get_quest_count()
        completed = self._level.quest_manager.get_completed_count()

        title = font_big.render(f"TUTORIAL QUEST", True, (68, 39, 19))
        progress_text = font.render(
            f"Progress: {completed}/{total}", True, (100, 70, 40)
        )
        panel.blit(title, (24, 20))
        panel.blit(progress_text, (w - progress_text.get_width() - 24, 26))

        status = "" if is_completed else ""
        name_color = (36, 92, 35) if is_completed else (56, 34, 18)
        quest_name = font_big.render(f"{status}{quest['name']}", True, name_color)
        panel.blit(quest_name, (24, 70))

        desc_text = self._level.quest_manager.get_progress_text()
        lines = desc_text.split("\n")
        for i, line in enumerate(lines):
            desc = font.render(line, True, (91, 66, 43))
            panel.blit(desc, (24, 110 + i * 25))

        reward = quest.get("reward", {})
        reward_y = 180
        reward_text = f"Reward: {reward.get('money', 0)} koin"
        for item, amount in reward.get("items", {}).items():
            reward_text += f", {amount} {item}"
        reward_render = font.render(reward_text, True, (86, 51, 23))
        panel.blit(reward_render, (24, reward_y))

        nav_y = h - 50
        if quest["id"] > 0:
            prev_text = font.render("← PREV (←)", True, (78, 48, 23))
            panel.blit(prev_text, (24, nav_y))

        if quest["id"] < total - 1:
            next_text = font.render("NEXT (→) →", True, (78, 48, 23))
            panel.blit(next_text, (w - next_text.get_width() - 24, nav_y))

        close_text = font.render("Tutup: E/Q/ESC", True, (78, 48, 23))
        panel.blit(close_text, (w // 2 - close_text.get_width() // 2, nav_y))

        surface.blit(panel, (x, y))

    def update(self, dt: float) -> None:
        """Update method - required by BaseUIPanel"""
        pass
