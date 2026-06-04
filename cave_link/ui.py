import pygame
from .settings import *
from .support import draw_panel


class CaveUI:
    def __init__(self, screen, fonts, assets, face):
        self.screen = screen
        self.font_big = fonts['big']
        self.font_small = fonts['small']
        self.assets = assets
        self.face = face

    def _draw_grey_panel(self, rect):
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel.fill((86, 88, 92, 218))
        pygame.draw.rect(panel, (38, 39, 43), panel.get_rect(), 3, border_radius=8)
        pygame.draw.rect(panel, (145, 148, 154), pygame.Rect(4, 4, rect.width - 8, rect.height - 8), 2, border_radius=6)
        self.screen.blit(panel, rect.topleft)

    def draw_hearts(self, hearts):
        left_panel = pygame.Rect(24, 22, 360, 64)
        draw_panel(self.screen, left_panel)
        face_frame = pygame.Rect(32, 30, 58, 50)
        pygame.draw.rect(self.screen, (96, 58, 31), face_frame, border_radius=8)
        pygame.draw.rect(self.screen, (255, 238, 173), face_frame.inflate(-4, -4), 2, border_radius=7)
        if self.face:
            self.screen.blit(self.face, (34, 32))
        heart_x = 98
        for i in range(hearts):
            x = heart_x + i * 34
            y = 37
            pygame.draw.circle(self.screen, (216, 42, 55), (x + 7, y + 7), 7)
            pygame.draw.circle(self.screen, (216, 42, 55), (x + 17, y + 7), 7)
            pygame.draw.polygon(self.screen, (216, 42, 55), [(x + 1, y + 10), (x + 23, y + 10), (x + 12, y + 26)])
            pygame.draw.circle(self.screen, (255, 124, 132), (x + 8, y + 5), 2)

    def draw_center_counter_and_key(self, rooms_passed, key_count):
        
        rect = pygame.Rect(SCREEN_WIDTH // 2 - 66, 18, 132, 42)
        self._draw_grey_panel(rect)

        room_txt = self.font_small.render(str(max(0, rooms_passed)), True, (235, 237, 240))
        self.screen.blit(room_txt, (rect.x + 28 - room_txt.get_width() // 2, rect.y + 12))

        if self.assets.get('cave_icon'):
            icon = pygame.transform.scale(self.assets['cave_icon'], (26, 26))
            self.screen.blit(icon, (rect.x + 47, rect.y + 8))


        if key_count > 0 and self.assets.get('gold_key'):
            key = pygame.transform.scale(self.assets['gold_key'], (22, 22))
            self.screen.blit(key, (rect.x + 96, rect.y + 10))

    def draw_energy_bar(self, energy, energy_max):

        bar_w, bar_h = 34, 172
        x = SCREEN_WIDTH - 58
        y = SCREEN_HEIGHT - bar_h - 28

  
        pygame.draw.rect(self.screen, (185, 94, 19), (x, y, bar_w, bar_h), border_radius=8)
        pygame.draw.rect(self.screen, (255, 197, 43), (x + 4, y + 4, bar_w - 8, bar_h - 8), border_radius=6)

      
        inner = pygame.Rect(x + 9, y + 23, bar_w - 18, bar_h - 34)
        pygame.draw.rect(self.screen, (55, 110, 49), inner, border_radius=4)


        fill_h = int(inner.height * (energy / max(1, energy_max)))
        fill_rect = pygame.Rect(
            inner.x + 2,
            inner.bottom - fill_h + 2,
            inner.width - 4,
            max(0, fill_h - 4)
        )
        pygame.draw.rect(self.screen, (88, 231, 70), fill_rect, border_radius=3)

     
        pygame.draw.rect(self.screen, (113, 70, 24), (x + 8, y - 17, 18, 24), border_radius=4)
        txt = self.font_small.render('E', True, (69, 38, 16))
        self.screen.blit(txt, (x + 12, y - 14))

    def draw_inventory(self):
        slots = 10
        slot_size = 42
        gap = 6
        pad = 8
        frame_w = slots * slot_size + (slots - 1) * gap + pad * 2
        frame_h = slot_size + pad * 2
        x = (SCREEN_WIDTH - frame_w) // 2
        y = SCREEN_HEIGHT - frame_h - 18
        frame = pygame.Rect(x, y, frame_w, frame_h)
        draw_panel(self.screen, frame)

        for i in range(slots):
            sx = x + pad + i * (slot_size + gap)
            sy = y + pad
            slot = pygame.Rect(sx, sy, slot_size, slot_size)
            pygame.draw.rect(self.screen, (247, 205, 135), slot, border_radius=7)
            pygame.draw.rect(self.screen, (127, 79, 31), slot, 3, border_radius=7)
            pygame.draw.rect(self.screen, (255, 232, 177), slot.inflate(-6, -6), 1, border_radius=5)

        if self.assets.get('pickaxe'):
            self.screen.blit(self.assets['pickaxe'], (x + pad + 7, y + pad + 7))

    def draw_notice(self, text, timer):
     
        return

    def draw_all(self, hearts, rooms_passed, key_count, energy, energy_max, notice_text, notice_timer):
        self.draw_hearts(hearts)
        self.draw_center_counter_and_key(rooms_passed, key_count)
        self.draw_inventory()
        self.draw_energy_bar(energy, energy_max)
        self.draw_notice(notice_text, notice_timer)
