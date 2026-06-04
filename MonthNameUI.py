
import os
import pygame
from settings import SCREEN_WIDTH
from support import get_path


class MonthNameUI:


    def __init__(self):
        font_path = get_path('font', 'LycheeSoda.ttf')
        if os.path.exists(font_path):
            self.font = pygame.font.Font(font_path, 24)
        else:
            self.font = pygame.font.Font(None, 28)

    def draw(self, surface, month_name):
        text = self.font.render(str(month_name).lower(), True, (18, 18, 18))
        width = max(160, text.get_width() + 74)
        height = 46
        x = (SCREEN_WIDTH - width) // 2
        y = 12

        shadow = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (48, 48, 48, 88), shadow.get_rect(), border_radius=14)
        surface.blit(shadow, (x + 3, y + 4))

        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (201, 201, 201, 248), panel.get_rect(), border_radius=14)
        pygame.draw.rect(panel, (123, 123, 123, 255), panel.get_rect(), 3, border_radius=14)
        inner = pygame.Rect(7, 6, width - 14, height - 12)
        pygame.draw.rect(panel, (233, 233, 233, 220), inner, 2, border_radius=10)
        surface.blit(panel, (x, y))

        surface.blit(
            text,
            (
                x + (width - text.get_width()) // 2,
                y + (height - text.get_height()) // 2 - 1,
            ),
        )
