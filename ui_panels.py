from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING

import pygame
import os
from base import BaseUIPanel
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from seed import Seed
from support import get_path, load_single
from items.material_item import MaterialItem

if TYPE_CHECKING:
    from level import Level


class ShopPanel(BaseUIPanel):
    """Panel pembelian item dari NPC pedagang biasa."""

    def __init__(self, level: "Level") -> None:
        super().__init__(level)
        self.active_npc = None
        self.selected_index = 0
        self.scroll_offset = 0
        self.message = ""
        self.message_timer = 0.0
        self._VISIBLE = 5
        self._W, self._H = 620, 580

    def open(self, npc) -> None:
        self._open = True
        self.active_npc = npc
        self.selected_index = 0
        self.scroll_offset = 0
        self.message = "Pilih item yang ingin dibeli"
        self.message_timer = 2.0

    def close(self) -> None:
        self._open = False
        self.active_npc = None
        self.message = ""
        self.message_timer = 0.0
        self.selected_index = 0
        self.scroll_offset = 0

    def handle_event(self, event: pygame.Event) -> bool:
        if not self._open:
            return False
        if event.type != pygame.KEYDOWN:
            return False

        key = event.key
        if key in (pygame.K_e, pygame.K_q, pygame.K_ESCAPE):
            self.close()
            return True

        items = self.active_npc.shop_items if self.active_npc else []
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
            self._buy(self.selected_index)

        return True

    def draw(self, surface: pygame.Surface) -> None:
        if not self._open or not self.active_npc:
            return

        npc = self.active_npc
        w, h = self._W, self._H
        x = (SCREEN_WIDTH - w) // 2
        y = (SCREEN_HEIGHT - h) // 2

        self._draw_shadow(surface, x, y, w, h)
        panel = self._make_panel_surface(w, h)

        title = self._font_big.render(f"{npc.name} — Shop", True, (68, 39, 19))
        coin = self._font_small.render(f"Koin: {self._level.money}", True, (68, 39, 19))
        panel.blit(title, (24, 20))
        panel.blit(coin, (w - coin.get_width() - 28, 26))

        items = npc.shop_items
        item_y_start = 70
        for i in range(self._VISIBLE):
            idx = self.scroll_offset + i
            if idx >= len(items):
                break
            item = items[idx]
            row_y = item_y_start + i * 70
            row_rect = pygame.Rect(24, row_y, w - 48, 60)
            bg = (255, 233, 173) if idx == self.selected_index else (245, 220, 160)
            pygame.draw.rect(panel, bg, row_rect, border_radius=8)
            pygame.draw.rect(panel, (154, 96, 44), row_rect, 2, border_radius=8)

            panel.blit(
                self._font_small.render(item["name"], True, (56, 34, 18)),
                (row_rect.x + 12, row_rect.y + 6),
            )
            panel.blit(
                self._font_small.render(item["desc"], True, (91, 66, 43)),
                (row_rect.x + 12, row_rect.y + 28),
            )

            price_txt = self._font_small.render(
                f"{item['price']} koin", True, (86, 51, 23)
            )
            panel.blit(
                price_txt,
                (row_rect.right - price_txt.get_width() - 12, row_rect.y + 38),
            )

            stock = item.get("stock")
            if stock is not None:
                sc = (135, 45, 35) if stock <= 0 else (36, 92, 35)
                panel.blit(
                    self._font_small.render(f"Tersedia: {stock}", True, sc),
                    (row_rect.x + 12, row_rect.y + 46),
                )
            else:
                panel.blit(
                    self._font_small.render("Stok: ∞", True, (100, 70, 40)),
                    (row_rect.x + 12, row_rect.y + 46),
                )

        if items and 0 <= self.selected_index < len(items):
            sel = items[self.selected_index]
            info_y = item_y_start + self._VISIBLE * 70 + 10
            ir = pygame.Rect(24, info_y, w - 48, 80)
            pygame.draw.rect(panel, (255, 233, 173), ir, border_radius=8)
            pygame.draw.rect(panel, (154, 96, 44), ir, 2, border_radius=8)
            panel.blit(
                self._font_small.render(
                    f"Tekan ENTER untuk membeli {sel['name']}", True, (56, 34, 18)
                ),
                (ir.x + 12, ir.y + 12),
            )
            panel.blit(
                self._font_small.render(
                    f"Harga: {sel['price']} koin", True, (86, 51, 23)
                ),
                (ir.x + 12, ir.y + 36),
            )
            if sel.get("stock", 1) <= 0:
                panel.blit(
                    self._font_small.render("HABIS!", True, (255, 0, 0)),
                    (ir.x + 12, ir.y + 56),
                )

        panel.blit(
            self._font_small.render(
                "Up/Down : Pilih  |  ENTER : Beli  |  E/Q : Tutup", True, (78, 48, 23)
            ),
            (24, h - 62),
        )
        panel.blit(
            self._font_small.render(
                "Tips: Beli bahan untuk crafting di Pengrajin!", True, (100, 70, 40)
            ),
            (24, h - 38),
        )

        if self.message and self.message_timer > 0:
            mc = (36, 92, 35) if "berhasil" in self.message else (135, 45, 35)
            panel.blit(self._font_small.render(self.message, True, mc), (24, h - 88))

        surface.blit(panel, (x, y))

    def update(self, dt: float) -> None:
        if self.message_timer > 0:
            self.message_timer = max(0.0, self.message_timer - dt)
            if self.message_timer <= 0 and not self._open:
                self.message = ""

    def _buy(self, index: int) -> None:
        npc = self.active_npc
        if not npc or not (0 <= index < len(npc.shop_items)):
            return
        item = npc.shop_items[index]
        if item.get("stock", 1) <= 0:
            self._show_msg(f"{item['name']} sedang habis!")
            return
        if self._level.money < item["price"]:
            self._show_msg(f"Koin tidak cukup untuk membeli {item['name']}.")
            return
        self._level.money -= item["price"]
        seed = self._create_seed_from_shop_item(item)
        if seed:
            self._level.inventory.add_item(seed)
        else:
            self._level.inventory.add_item(item["name"])
        if "stock" in item:
            item["stock"] -= 1
        self._show_msg(f"{item['name']} berhasil dibeli.")

    def _create_seed_from_shop_item(self, item: dict) -> Seed | None:
        name = item.get("name")
        image_path = item.get("image")
        if not name or not image_path:
            return None
        if not (name.lower().startswith("biji ") or "seed" in image_path.lower()):
            return None

        surf = load_single(get_path(image_path), (32, 32))
        return Seed(name=name, description=item.get("desc", ""), image=surf or image_path)

    def _show_msg(self, text: str) -> None:
        self.message = text
        self.message_timer = 2.0


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
        self._W, self._H = 620, 570

    def open(self, npc) -> None:
        self._open = True
        self.active_npc = npc
        self.selected_index = 0
        self.scroll_offset = 0
        self.message = "Pilih item yang ingin dibuat"
        self.message_timer = 2.0

    def close(self) -> None:
        self._open = False
        self.active_npc = None
        self.message = ""
        self.message_timer = 0.0
        self.selected_index = 0
        self.scroll_offset = 0

    def handle_event(self, event: pygame.Event) -> bool:
        if not self._open:
            return False
        if event.type != pygame.KEYDOWN:
            return False

        key = event.key
        if key in (pygame.K_e, pygame.K_q, pygame.K_ESCAPE):
            self.close()
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

        w, h = self._W, self._H
        x = (SCREEN_WIDTH - w) // 2
        y = (SCREEN_HEIGHT - h) // 2

        self._draw_shadow(surface, x, y, w, h)
        panel = self._make_panel_surface(w, h)

        title = self._font_big.render(
            f"{self.active_npc.name} — Crafting", True, (68, 39, 19)
        )
        coin = self._font_small.render(f"Koin: {self._level.money}", True, (68, 39, 19))
        panel.blit(title, (24, 20))
        panel.blit(coin, (w - coin.get_width() - 28, 26))

        items = list(self._level.crafting.recipes.keys())
        item_y_start = 70
        for i in range(self._VISIBLE):
            idx = self.scroll_offset + i
            if idx >= len(items):
                break
            item = items[idx]
            recipe = self._level.crafting.recipes[item]
            row_y = item_y_start + i * 60
            bg = (255, 233, 173) if idx == self.selected_index else (245, 220, 160)
            rr = pygame.Rect(24, row_y, w - 48, 54)
            pygame.draw.rect(panel, bg, rr, border_radius=8)
            pygame.draw.rect(panel, (154, 96, 44), rr, 2, border_radius=8)

            panel.blit(
                self._font_small.render(item, True, (56, 34, 18)), (rr.x + 12, rr.y + 6)
            )

            bahan_txt = ", ".join(f"{b}x{j}" for b, j in recipe["bahan"].items())
            panel.blit(
                self._font_small.render(f"Bahan: {bahan_txt}", True, (91, 66, 43)),
                (rr.x + 12, rr.y + 28),
            )

            can, _ = self._level.crafting.can_craft(self._level.inventory, item)
            sc = (36, 92, 35) if can else (135, 45, 35)
            status = "✓ Bisa dibuat" if can else " Bahan kurang"
            st = self._font_small.render(status, True, sc)
            panel.blit(st, (rr.right - st.get_width() - 12, rr.y + 20))

        if items and 0 <= self.selected_index < len(items):
            sel = items[self.selected_index]
            info_y = item_y_start + self._VISIBLE * 60 + 10
            ir = pygame.Rect(24, info_y, w - 48, 100)
            pygame.draw.rect(panel, (255, 233, 173), ir, border_radius=8)
            pygame.draw.rect(panel, (154, 96, 44), ir, 2, border_radius=8)
            for i, line in enumerate(
                self._level.crafting.get_recipe_info(sel).split("\n")
            ):
                panel.blit(
                    self._font_small.render(line, True, (56, 34, 18)),
                    (ir.x + 12, ir.y + 12 + i * 22),
                )

        panel.blit(
            self._font_small.render(
                "Up/Down : Pilih  |  ENTER : Craft  |  E/Q : Tutup", True, (78, 48, 23)
            ),
            (24, h - 62),
        )
        panel.blit(
            self._font_small.render(
                "Tips: Kumpulkan bahan dari alam untuk membuat item baru!",
                True,
                (100, 70, 40),
            ),
            (24, h - 38),
        )

        if self.message and self.message_timer > 0:
            mc = (36, 92, 35) if "Berhasil" in self.message else (135, 45, 35)
            panel.blit(self._font_small.render(self.message, True, mc), (24, h - 88))

        surface.blit(panel, (x, y))

    def update(self, dt: float) -> None:
        if self.message_timer > 0:
            self.message_timer = max(0.0, self.message_timer - dt)

    def _craft(self, item_name: str) -> None:
        success, msg = self._level.crafting.craft(self._level.inventory, item_name)
        self.message = msg
        self.message_timer = 2.0


class InventoryBar(BaseUIPanel):

    _SLOTS = 10
    _SLOT_SIZE = 42
    _GAP = 6
    _PAD = 8

    def __init__(self, level: "Level") -> None:
        super().__init__(level)
        self._bar_slots: list[str | None] = [None] * self._SLOTS
        self.active_slot: int | None = None

    def open(self, *args, **kwargs) -> None:
        self._open = True

    def close(self) -> None:
        self._open = False

    def handle_event(self, event: pygame.Event) -> bool:
        return False

    def assign_slot(self, slot: int, item_name: str) -> None:
        if 0 <= slot < self._SLOTS:
            self._bar_slots[slot] = item_name

    def set_active_slot(self, slot: int) -> None:
        if 0 <= slot < self._SLOTS and self._bar_slots[slot] is not None:
            self.active_slot = slot
        else:
            self.active_slot = None

    def get_active_item(self) -> str | None:
        if self.active_slot is None:
            return None
        return self._bar_slots[self.active_slot]

    def _sync_slots(self) -> None:
        for i, item_name in enumerate(self._bar_slots):
            if item_name is not None and self._level.inventory.get(item_name, 0) <= 0:
                self._bar_slots[i] = None
                if self.active_slot == i:
                    self.active_slot = None

    def draw(self, surface: pygame.Surface) -> None:
        self._sync_slots()
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

        font = self._font_small
        icon_size = 28

        for i in range(self._SLOTS):
            sx = pad + i * (ss + gs)
            sy = pad
            sr = pygame.Rect(sx, sy, ss, ss)
            ir = pygame.Rect(sx + 3, sy + 3, ss - 6, ss - 6)

            if self.active_slot == i:
                pygame.draw.rect(panel, (0, 0, 0), sr, 3, border_radius=6)
            else:
                pygame.draw.rect(panel, (170, 115, 58), sr, border_radius=6)

            pygame.draw.rect(panel, (113, 70, 24), sr, 2, border_radius=6)
            pygame.draw.rect(panel, (241, 205, 139), ir, border_radius=5)
            pygame.draw.rect(panel, (199, 151, 86), ir, 1, border_radius=5)

            label = font.render(str((i + 1) % 10), True, (107, 65, 30))
            panel.blit(label, (sx + 4, sy + 4))

            item_name = self._bar_slots[i]
            if item_name:
                count = self._level.inventory.get(item_name, 0)
                short = item_name[:4]
                nt = font.render(short, True, (60, 39, 24))
                ct = font.render(str(count), True, (60, 39, 24))
                panel.blit(
                    ct, (sx + ss - ct.get_width() - 4, sy + ss - ct.get_height() - 2)
                )

        # draw tool box to the left of the inventory bar
        tool_ss = ss
        tool_gs = gs
        tool_x = x - tool_ss - tool_gs - 8
        tool_y = y
        # background
        trect = pygame.Rect(tool_x, tool_y, tool_ss, tool_ss)
        pygame.draw.rect(surface, (239, 195, 118, 240), trect, border_radius=8)
        pygame.draw.rect(surface, (122, 72, 27), trect, 3, border_radius=8)
        # tool image and name
        if getattr(self._level, 'tools', None):
            tool = self._level.tools[self._level.current_tool_index]
            if getattr(tool, 'image', None):
                try:
                    img = pygame.transform.smoothscale(tool.image, (tool_ss - 8, tool_ss - 8))
                    surface.blit(img, (tool_x + 4, tool_y + 4))
                except Exception:
                    pass

        surface.blit(panel, (x, y))

        coin_txt = font.render(f"Koin: {self._level.money}", True, (255, 239, 177))
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

class InventoryMenu(BaseUIPanel):
    """Menu inventaris penuh dengan detail item. Modal, bisa dibuka/tutup."""

    _VISIBLE = 6
    _W, _H = 520, 520

    def __init__(self, level: "Level") -> None:
        super().__init__(level)
        self.selected_index = 0
        self.scroll_offset = 0
        self.message = ""
        self.message_timer = 0.0

    def open(self, *args, **kwargs) -> None:
        self._open = True
        self.selected_index = 0
        self.scroll_offset = 0
        self.message = "Menu inventaris dibuka"
        self.message_timer = 1.6

    def close(self) -> None:
        self._open = False
        self.selected_index = 0
        self.scroll_offset = 0
        self.message = ""
        self.message_timer = 0.0

    def handle_event(self, event: pygame.Event) -> bool:
        if not self._open:
            return False
        if event.type != pygame.KEYDOWN:
            return False

        key = event.key
        if key in (pygame.K_e, pygame.K_q, pygame.K_TAB):
            self.close()
            return True

        items = list(self._level.inventory.inventory.items())
        if not items:
            return True

        if key in (pygame.K_w, pygame.K_UP):
            self.selected_index = max(0, self.selected_index - 1)
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index
        elif key in (pygame.K_s, pygame.K_DOWN):
            self.selected_index = min(len(items) - 1, self.selected_index + 1)
            if self.selected_index >= self.scroll_offset + self._VISIBLE:
                self.scroll_offset = self.selected_index - self._VISIBLE + 1
        elif pygame.K_0 <= key <= pygame.K_9:
            if self.selected_index < len(items):
                slot = 9 if key == pygame.K_0 else key - pygame.K_1
                item_name, _ = items[self.selected_index]
                self._level.inventory_bar.assign_slot(slot, item_name)
                self._show_msg(f"{item_name} dipasang ke bar slot {slot + 1}")
        elif key == pygame.K_r:
            # hapus item
            if self.selected_index < len(items):
                item_name, _ = items[self.selected_index]
                self._level.inventory.remove_item(item_name)
                self._show_msg(f"{item_name} dihapus dari inventaris")
            
        return True

    def draw(self, surface: pygame.Surface) -> None:
        if not self._open:
            return

        w, h = self._W, self._H
        x = (SCREEN_WIDTH - w) // 2
        y = (SCREEN_HEIGHT - h) // 2

        self._draw_shadow(surface, x, y, w, h)
        panel = self._make_panel_surface(w, h)

        title = self._font_big.render("Inventory", True, (68, 39, 19))
        panel.blit(title, (24, 20))

        items = list(self._level.inventory.inventory.items())
        item_y_start = 78
        for i in range(self._VISIBLE):
            idx = self.scroll_offset + i
            if idx >= len(items):
                break
            name, count = items[idx]
            row_y = item_y_start + i * 56
            row_rect = pygame.Rect(24, row_y, w - 48, 50)
            bg = (255, 233, 173) if idx == self.selected_index else (245, 220, 160)
            pygame.draw.rect(panel, bg, row_rect, border_radius=8)
            pygame.draw.rect(panel, (154, 96, 44), row_rect, 2, border_radius=8)

            panel.blit(
                self._font_small.render(f"{name}", True, (56, 34, 18)),
                (row_rect.x + 12, row_rect.y + 8),
            )
            panel.blit(
                self._font_small.render(f"x{count}", True, (91, 66, 43)),
                (row_rect.right - 60, row_rect.y + 8),
            )

            assigned_slot = self._level.inventory_bar._bar_slots.index(name) + 1 if name in self._level.inventory_bar._bar_slots else None
            if assigned_slot is not None:
                assign_txt = self._font_small.render(
                    f"Slot {assigned_slot}", True, (36, 92, 35)
                )
                panel.blit(assign_txt, (row_rect.right - assign_txt.get_width() - 12, row_rect.y + 28))

        if not items:
            empty_txt = self._font_small.render(
                "Inventaris kosong.", True, (110, 60, 30)
            )
            panel.blit(empty_txt, (24, item_y_start))

        panel.blit(
            self._font_small.render(
                "W/S: Pilih | R: Buang | 0-9: Pasang ke slot bar | TAB: Tutup",
                True,
                (78, 48, 23),
            ),
            (24, h - 62),
        )

        if self.message and self.message_timer > 0:
            panel.blit(self._font_small.render(self.message, True, (36, 92, 35)), (24, h - 88))

        surface.blit(panel, (x, y))

    def update(self, dt: float) -> None:
        if self.message_timer > 0:
            self.message_timer = max(0.0, self.message_timer - dt)

    def _show_msg(self, text: str) -> None:
        self.message = text
        self.message_timer = 1.8

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


class BattleUnlockPanel(BaseUIPanel):
    """Panel sederhana untuk menunjukan unlock battle mode dari tanaman."""

    def __init__(self, level: "Level") -> None:
        super().__init__(level)
        self.plant_type: str | None = None
        self._W, self._H = 440, 160

    def open(self, plant_type: str) -> None:
        self._open = True
        self.plant_type = plant_type

    def close(self) -> None:
        self._open = False
        self.plant_type = None

    def handle_event(self, event: pygame.Event) -> bool:
        if not self._open:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_e, pygame.K_q, pygame.K_ESCAPE):
                self.close()
            return True
        return True

    def draw(self, surface: pygame.Surface) -> None:
        if not self._open or not self.plant_type:
            return

        x = (SCREEN_WIDTH - self._W) // 2
        y = (SCREEN_HEIGHT - self._H) // 2
        self._draw_shadow(surface, x, y, self._W, self._H)
        panel = self._make_panel_surface(self._W, self._H)

        title = self._font_big.render("Battle Mode Terbuka!", True, (68, 39, 19))
        message = self._font_small.render(
            f"Tanaman {self.plant_type} berhasil terbuka untuk battle mode.",
            True,
            (36, 92, 35),
        )
        hint = self._font_small.render("Tekan E atau Q untuk menutup.", True, (78, 48, 23))

        panel.blit(title, (24, 24))
        panel.blit(message, (24, 68))
        panel.blit(hint, (24, 112))

        surface.blit(panel, (x, y))

    def update(self, dt: float) -> None:
        pass


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
            for item_name, count in self._level.inventory.inventory.items():
                buy_price = (
                    self.active_npc.get_buy_price(item_name) if self.active_npc else 0
                )
                if buy_price > 0 and count > 0:
                    inventory_items.append(
                        {
                            "name": item_name,
                            "count": count,
                            "sell_price": buy_price,
                            "desc": f"Jual {item_name} seharga {buy_price} koin",
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

        if self._level.money < item_data["price"]:
            self._show_msg(f"Koin tidak cukup untuk membeli {item_data['name']}.")
            return

        self._level.money -= item_data["price"]

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
        current_count = self._level.inventory.get(item_name, 0)

        if current_count <= 0:
            self._show_msg(f"Anda tidak memiliki {item_name}!")
            return

        self._level.inventory[item_name] -= 1
        if self._level.inventory[item_name] <= 0:
            del self._level.inventory[item_name]

        self._level.money += sell_price
        self._show_msg(f"✓ {item_name} terjual! +{sell_price} koin")

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

        w, h = self._W, self._H
        x = (SCREEN_WIDTH - w) // 2
        y = (SCREEN_HEIGHT - h) // 2

        self._draw_shadow(surface, x, y, w, h)
        panel = self._make_panel_surface(w, h)

        title = self._font_big.render(
            f"{self.active_npc.name} — Crafting", True, (68, 39, 19)
        )
        coin = self._font_small.render(f"Koin: {self._level.money}", True, (68, 39, 19))
        panel.blit(title, (24, 20))
        panel.blit(coin, (w - coin.get_width() - 28, 26))

        items = list(self._level.crafting.recipes.keys())
        item_y_start = 70
        for i in range(self._VISIBLE):
            idx = self.scroll_offset + i
            if idx >= len(items):
                break
            item = items[idx]
            recipe = self._level.crafting.recipes[item]
            row_y = item_y_start + i * 60
            bg = (255, 233, 173) if idx == self.selected_index else (245, 220, 160)
            rr = pygame.Rect(24, row_y, w - 48, 54)
            pygame.draw.rect(panel, bg, rr, border_radius=8)
            pygame.draw.rect(panel, (154, 96, 44), rr, 2, border_radius=8)

            panel.blit(
                self._font_small.render(item, True, (56, 34, 18)), (rr.x + 12, rr.y + 6)
            )

            bahan_txt = ", ".join(f"{b}x{j}" for b, j in recipe["bahan"].items())
            panel.blit(
                self._font_small.render(f"Bahan: {bahan_txt}", True, (91, 66, 43)),
                (rr.x + 12, rr.y + 28),
            )

            can, _ = self._level.crafting.can_craft(self._level.inventory, item)
            sc = (36, 92, 35) if can else (135, 45, 35)
            status = "✓ Bisa dibuat" if can else " Bahan kurang"
            st = self._font_small.render(status, True, sc)
            panel.blit(st, (rr.right - st.get_width() - 12, rr.y + 20))

        if items and 0 <= self.selected_index < len(items):
            sel = items[self.selected_index]
            info_y = item_y_start + self._VISIBLE * 60 + 10
            ir = pygame.Rect(24, info_y, w - 48, 100)
            pygame.draw.rect(panel, (255, 233, 173), ir, border_radius=8)
            pygame.draw.rect(panel, (154, 96, 44), ir, 2, border_radius=8)
            for i, line in enumerate(
                self._level.crafting.get_recipe_info(sel).split("\n")
            ):
                panel.blit(
                    self._font_small.render(line, True, (56, 34, 18)),
                    (ir.x + 12, ir.y + 12 + i * 22),
                )

        panel.blit(
            self._font_small.render(
                "Up/Down : Pilih  |  ENTER : Craft  |  E/Q : Tutup", True, (78, 48, 23)
            ),
            (24, h - 62),
        )
        panel.blit(
            self._font_small.render(
                "Tips: Kumpulkan bahan dari alam untuk membuat item baru!",
                True,
                (100, 70, 40),
            ),
            (24, h - 38),
        )

        if self.message and self.message_timer > 0:
            mc = (36, 92, 35) if "Berhasil" in self.message else (135, 45, 35)
            panel.blit(self._font_small.render(self.message, True, mc), (24, h - 88))

        surface.blit(panel, (x, y))

    def update(self, dt: float) -> None:
        if self.message_timer > 0:
            self.message_timer = max(0.0, self.message_timer - dt)

    def _craft(self, item_name: str) -> None:
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


class PauseMenu(BaseUIPanel):
    """Menu pause - muncul saat tekan ESC, dengan tombol resume, main menu, dan exit."""

    _BUTTON_WIDTH = 200
    _BUTTON_HEIGHT = 50
    _BUTTON_GAP = 20
    _W = 400
    _H = 300

    def __init__(self, level: "Level") -> None:
        super().__init__(level)
        self.selected_button = 0  # 0: Resume, 1: Main Menu, 2: Exit
        self.buttons = ["Resume", "Main Menu", "Exit Game"]
        self.hovered_button = None

    def open(self, *args, **kwargs) -> None:
        self._open = True
        self.selected_button = 0
        self.hovered_button = None

    def close(self) -> None:
        self._open = False
        self.selected_button = 0
        self.hovered_button = None

    def handle_event(self, event: pygame.Event) -> bool:
        if not self._open:
            return False

        if event.type == pygame.KEYDOWN:
            # Navigate dengan arrow keys atau WASD
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_button = (self.selected_button - 1) % len(self.buttons)
                return True
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_button = (self.selected_button + 1) % len(self.buttons)
                return True
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._on_button_pressed(self.selected_button)
                return True
            elif event.key == pygame.K_ESCAPE:
                # ESC untuk resume
                self._on_button_pressed(0)
                return True

        elif event.type == pygame.MOUSEMOTION:
            # Detect hover
            self.hovered_button = self._get_button_at_pos(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                button_idx = self._get_button_at_pos(event.pos)
                if button_idx is not None:
                    self._on_button_pressed(button_idx)
                    return True

        return False

    def draw(self, surface: pygame.Surface) -> None:
        if not self._open:
            return

        # Background gelap
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Panel
        x = (SCREEN_WIDTH - self._W) // 2
        y = (SCREEN_HEIGHT - self._H) // 2
        self._draw_shadow(surface, x, y, self._W, self._H)
        panel = self._make_panel_surface(self._W, self._H)

        # Title
        title = self._font_big.render("PAUSED", True, (68, 39, 19))
        title_x = (self._W - title.get_width()) // 2
        panel.blit(title, (title_x, 30))

        # Buttons
        button_y_start = 100
        for i, button_text in enumerate(self.buttons):
            self._draw_button(
                panel,
                button_text,
                i,
                button_y_start + i * (self._BUTTON_HEIGHT + self._BUTTON_GAP),
            )

        surface.blit(panel, (x, y))

    def _draw_button(
        self,
        panel: pygame.Surface,
        text: str,
        index: int,
        y: int,
    ) -> None:
        """Draw single button dengan highlight jika selected atau hovered."""
        is_selected = index == self.selected_button
        is_hovered = index == self.hovered_button

        x = (self._W - self._BUTTON_WIDTH) // 2

        # Button background
        button_rect = pygame.Rect(x, y, self._BUTTON_WIDTH, self._BUTTON_HEIGHT)

        if is_selected or is_hovered:
            # Highlight color
            bg_color = (255, 200, 100)
            border_color = (200, 120, 30)
            text_color = (68, 39, 19)
        else:
            bg_color = (200, 170, 120)
            border_color = (120, 70, 30)
            text_color = (68, 39, 19)

        pygame.draw.rect(panel, bg_color, button_rect, border_radius=8)
        pygame.draw.rect(panel, border_color, button_rect, 3, border_radius=8)

        # Button text
        font = self._font_small
        text_surf = font.render(text, True, text_color)
        text_x = x + (self._BUTTON_WIDTH - text_surf.get_width()) // 2
        text_y = y + (self._BUTTON_HEIGHT - text_surf.get_height()) // 2
        panel.blit(text_surf, (text_x, text_y))

    def _get_button_at_pos(self, mouse_pos: tuple) -> int | None:
        """Get button index at mouse position, atau None jika di luar."""
        x = (SCREEN_WIDTH - self._W) // 2
        y = (SCREEN_HEIGHT - self._H) // 2

        for i in range(len(self.buttons)):
            button_y = y + 100 + i * (self._BUTTON_HEIGHT + self._BUTTON_GAP)
            button_x = x + (self._W - self._BUTTON_WIDTH) // 2
            button_rect = pygame.Rect(
                button_x, button_y, self._BUTTON_WIDTH, self._BUTTON_HEIGHT
            )
            if button_rect.collidepoint(mouse_pos):
                return i
        return None

    def _on_button_pressed(self, button_index: int) -> None:
        """Handle button press."""
        if button_index == 0:
            # Resume
            self.close()
        elif button_index == 1:
            # Main Menu
            self._level.go_back_to_menu()
            self.close()
        elif button_index == 2:
            # Exit Game
            self._level.app.running = False
            self.close()

    def update(self, dt: float) -> None:
        """Update method - required by BaseUIPanel"""
        pass
