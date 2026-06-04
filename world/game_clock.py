import random
import os
import pygame
from support import *
from config import *
from settings import *

class GameClock:
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
        self.season_mode = 'normal'  # normal, rain, snow, autumn
        self.font_big = pygame.font.Font(get_path('font', 'LycheeSoda.ttf'), 26) if os.path.exists(get_path('font', 'LycheeSoda.ttf')) else pygame.font.Font(None, 30)
        self.font_small = pygame.font.Font(get_path('font', 'LycheeSoda.ttf'), 20) if os.path.exists(get_path('font', 'LycheeSoda.ttf')) else pygame.font.Font(None, 22)

    def toggle_speed(self):
        self.time_speed_fast = not self.time_speed_fast
        self.minute_seconds = self.minute_seconds_fast if self.time_speed_fast else self.minute_seconds_normal

    def update(self, dt):
        day_changed = False
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
                day_changed = True
        return day_changed

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

        if self.season_mode == 'snow':
            pygame.draw.ellipse(surface, (222, 235, 245), (icon_x + 7, icon_y + 4, 35, 18))
            pygame.draw.ellipse(surface, (238, 247, 252), (icon_x + 19, icon_y, 25, 19))
            for dx, dy in ((14, 28), (27, 34), (40, 27)):
                pygame.draw.circle(surface, (250, 253, 255), (icon_x + dx, icon_y + dy), 3)
        elif self.season_mode == 'rain':
            pygame.draw.ellipse(surface, (116, 145, 170), (icon_x + 7, icon_y + 4, 35, 18))
            pygame.draw.ellipse(surface, (137, 161, 184), (icon_x + 19, icon_y, 25, 19))
            for dx in (12, 25, 38):
                pygame.draw.line(surface, (45, 91, 158), (icon_x + dx, icon_y + 26), (icon_x + dx - 4, icon_y + 38), 2)
        elif self.season_mode == 'autumn':
            for dx, dy, col in ((12, 18, (204, 88, 32)), (28, 24, (229, 143, 42)), (40, 15, (153, 79, 31))):
                pygame.draw.ellipse(surface, col, (icon_x + dx, icon_y + dy, 10, 6))

    def draw(self, surface, date_text=None):
        w, h = 190, 104
        x, y = SCREEN_WIDTH - w - 16, 14
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((244, 214, 143, 235))
        pygame.draw.rect(panel, (119, 74, 34), panel.get_rect(), 4, border_radius=12)
        pygame.draw.rect(panel, (255, 239, 177), pygame.Rect(8, 8, w - 16, h - 16), 2, border_radius=10)
        surface.blit(panel, (x, y))

        top_label = date_text if date_text else f'Hari {self.day}'
        day_txt = self.font_small.render(top_label, True, (78, 43, 20))
        time_txt = self.font_big.render(self.time_text(), True, (54, 31, 18))
        phase_txt = self.font_small.render(self.phase(), True, (78, 43, 20))
        speed_label = ' x10' if self.time_speed_fast else ''
        
        if self.season_mode == 'snow':
            weather_label = 'Salju'
        elif self.season_mode == 'rain':
            weather_label = 'Hujan'
        elif self.season_mode == 'autumn':
            weather_label = 'Gugur'
        else:
            weather_label = 'Cerah'
        weather_txt = self.font_small.render(weather_label + speed_label, True, (43, 64, 85))
        surface.blit(day_txt, (x + 18, y + 14))
        surface.blit(time_txt, (x + 18, y + 39))
        surface.blit(phase_txt, (x + 18, y + 75))
        surface.blit(weather_txt, (x + 105, y + 75))

        self._draw_phase_icon(surface, x + 126, y + 15)
