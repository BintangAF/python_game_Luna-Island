from config import *
from settings import *
import pygame


def draw_crafting_menu(self):
    if not self.crafting_open or not self.active_shop_npc:
        return

    font_big = self.clock_ui.font_big
    font = self.clock_ui.font_small
    w, h = 620, 570
    x = (SCREEN_WIDTH - w) // 2
    y = (SCREEN_HEIGHT - h) // 2

    shadow = pygame.Surface((w, h), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 110))
    self.display_surface.blit(shadow, (x + 5, y + 7))

    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((244, 214, 143, 246))
    pygame.draw.rect(panel, (119, 74, 34), panel.get_rect(), 4, border_radius=14)
    pygame.draw.rect(
        panel, (255, 239, 177), pygame.Rect(9, 9, w - 18, h - 18), 2, border_radius=10
    )

    title = font_big.render(
        f"{self.active_shop_npc.name} - Crafting", True, (68, 39, 19)
    )
    coin = font.render(f"Koin: {self.money}", True, (68, 39, 19))
    panel.blit(title, (24, 20))
    panel.blit(coin, (w - coin.get_width() - 28, 26))

    crafting_items = list(self.crafting.recipes.keys())
    item_y_start = 70
    visible_items = 5

    for i in range(visible_items):
        idx = self.crafting_scroll_offset + i
        if idx >= len(crafting_items):
            break

        item = crafting_items[idx]
        recipe = self.crafting.recipes[item]
        row_y = item_y_start + i * 60

        bg_color = (
            (255, 233, 173) if idx == self.crafting_selected_index else (245, 220, 160)
        )
        row_rect = pygame.Rect(24, row_y, w - 48, 54)
        pygame.draw.rect(panel, bg_color, row_rect, border_radius=8)
        pygame.draw.rect(panel, (154, 96, 44), row_rect, 2, border_radius=8)

        name = font.render(item, True, (56, 34, 18))
        panel.blit(name, (row_rect.x + 12, row_rect.y + 6))

        bahan_text = ", ".join([f"{b}x{j}" for b, j in recipe["bahan"].items()])
        bahan = font.render(f"Bahan: {bahan_text}", True, (91, 66, 43))
        panel.blit(bahan, (row_rect.x + 12, row_rect.y + 28))

        can_craft, _ = self.crafting.can_craft(self.inventory, item)
        status_color = (36, 92, 35) if can_craft else (135, 45, 35)
        status_text = "✓ Bisa dibuat" if can_craft else " Bahan kurang"
        status = font.render(status_text, True, status_color)
        panel.blit(status, (row_rect.right - status.get_width() - 12, row_rect.y + 20))

    if crafting_items and 0 <= self.crafting_selected_index < len(crafting_items):
        selected_item = crafting_items[self.crafting_selected_index]
        recipe_info = self.crafting.get_recipe_info(selected_item)

        info_x = 24
        info_y = item_y_start + visible_items * 60 + 10
        info_rect = pygame.Rect(info_x, info_y, w - 48, 100)
        pygame.draw.rect(panel, (255, 233, 173), info_rect, border_radius=8)
        pygame.draw.rect(panel, (154, 96, 44), info_rect, 2, border_radius=8)

        lines = recipe_info.split("\n")
        for i, line in enumerate(lines):
            info_text = font.render(line, True, (56, 34, 18))
            panel.blit(info_text, (info_x + 12, info_y + 12 + i * 22))

    footer1 = font.render(
        "↑/↓ : Pilih item | ENTER/SPACE : Craft | E/Q : Tutup", True, (78, 48, 23)
    )
    footer2 = font.render(
        "Tips: Kumpulkan bahan dari alam untuk membuat item baru!", True, (100, 70, 40)
    )
    panel.blit(footer1, (24, h - 62))
    panel.blit(footer2, (24, h - 38))

    if self.crafting_message and self.crafting_message_timer > 0:
        msg_color = (
            (36, 92, 35) if "Berhasil" in self.crafting_message else (135, 45, 35)
        )
        msg = font.render(self.crafting_message, True, msg_color)
        panel.blit(msg, (24, h - 88))
    self.display_surface.blit(panel, (x, y))

    if self.crafting_message_timer > 0:
        self.crafting_message_timer = max(0, self.crafting_message_timer - 0.016)
