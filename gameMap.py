import pygame
from settings import *

TILE_COLORS = {
    0: (0, 0, 0),      # dinding pembatas kamera (hitam pekat)
    1: (30, 30, 30),      # dinding (hampir hitam)
    2: (60, 60, 60),     # air yang tidak bisa dilewati (abu gelap)
    5: (100, 60, 30),     # tile pintu
    6: (60, 60, 60),     # lantai (abu gelap)
    7: (50, 150, 50),     # rumput (hijau)
    8: (30, 60, 150),    # air yang bisa dilewati (biru gelap)
}

class GameMap():
    def __init__(self, map_data):
        self.map_data = map_data
        self.walls = []
        self._build()

    def _build(self):
        for row_i, row in enumerate(self.map_data):
            for col_i, tile in enumerate(row):
                if tile == 0 or tile == 1 or tile == 2:
                    self.walls.append(pygame.Rect(col_i * TILE_SIZE, row_i * TILE_SIZE, TILE_SIZE, TILE_SIZE))                

    def draw(self, screen, offset_pos):
        for row_i, row in enumerate(self.map_data):
            for col_i, tile in enumerate(row):
                color = TILE_COLORS.get(tile, (60, 60, 60))
                pygame.draw.rect(
                    screen,
                    color,
                    ((col_i * TILE_SIZE) - offset_pos.x, (row_i * TILE_SIZE) - offset_pos.y, TILE_SIZE, TILE_SIZE)
                )

                if tile == 1:
                    pygame.draw.rect(
                        screen,
                        (20, 20, 20),
                        ((col_i * TILE_SIZE) - offset_pos.x, (row_i * TILE_SIZE) - offset_pos.y, TILE_SIZE, TILE_SIZE),
                        1
                    )