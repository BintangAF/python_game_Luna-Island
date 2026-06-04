import pygame


from settings import *

T_GRASS = 0
T_FIELD = 1
T_PATH = 2
T_YARD = 3
T_WATER = 4
T_SAND = 5


def _fill_rect(grid, x, y, w, h, tile_id):
    for ty in range(y, y + h):
        if 0 <= ty < len(grid):
            for tx in range(x, x + w):
                if 0 <= tx < len(grid[0]):
                    grid[ty][tx] = tile_id


def _distance_to_water(grid, tx, ty, max_dist=3):
    for dist in range(1, max_dist + 1):
        for ny in range(max(0, ty - dist), min(len(grid), ty + dist + 1)):
            for nx in range(max(0, tx - dist), min(len(grid[0]), tx + dist + 1)):
                if max(abs(nx - tx), abs(ny - ty)) != dist:
                    continue
                if grid[ny][nx] == T_WATER:
                    return dist
    return None


def build_map():
    """Membuat map awal tanpa mengubah posisi pulau.

    Air tetap berada di luar pulau.
    Pasir pantai dibuat otomatis pada tepi air.
    Area field tetap pada posisi awal.
    """
    grid = [[T_WATER] * MAP_W for _ in range(MAP_H)]

    land_rects = [
        (8, 5, 68, 33),
        (6, 3, 18, 12),
        (27, 3, 18, 10),
        (55, 4, 15, 10),
        (7, 14, 13, 10),
        (44, 14, 27, 10),
        (9, 24, 27, 13),
        (52, 25, 18, 11),
        (34, 20, 15, 10),
        (37, 37, 3, 4),
    ]
    for rect in land_rects:
        _fill_rect(grid, *rect, T_GRASS)

    coast_cuts = [
        (8, 3, 2, 3), (8, 36, 2, 2), (18, 3, 2, 2),
        (27, 3, 2, 2), (43, 3, 2, 2), (57, 4, 2, 2), (67, 4, 2, 2),
        (74, 5, 2, 5), (74, 31, 2, 4),
        (10, 37, 5, 1), (30, 37, 4, 1), (53, 36, 3, 2), (68, 36, 2, 2),
        (7, 18, 1, 4), (7, 30, 1, 3),
    ]
    for cut in coast_cuts:
        _fill_rect(grid, *cut, T_WATER)

    for ty in range(MAP_H):
        for tx in range(MAP_W):
            if grid[ty][tx] != T_GRASS:
                continue
            dist = _distance_to_water(grid, tx, ty, max_dist=3)
            if dist is not None and dist <= 3:
                grid[ty][tx] = T_SAND

    _fill_rect(grid, 6, 5, 18, 10, T_GRASS)
    _fill_rect(grid, 55, 5, 14, 8, T_GRASS)

    _fill_rect(grid, 11, 27, 22, 7, T_FIELD)
    _fill_rect(grid, 37, 22, 10, 6, T_FIELD)
    _fill_rect(grid, 55, 29, 12, 5, T_FIELD)

    _fill_rect(grid, 7, 6, 16, 8, T_FIELD)
    _fill_rect(grid, 30, 6, 7, 4, T_FIELD)
    _fill_rect(grid, 56, 6, 12, 6, T_FIELD)

    return grid

def make_beach_tiles(self):
    tiles = []
    palettes = [
        ((230, 203, 142), (214, 182, 120), (242, 221, 170)),
        ((224, 196, 136), (207, 176, 116), (236, 214, 162)),
        ((235, 208, 148), (218, 186, 126), (246, 224, 174)),
    ]
    for base, dot, shell in palettes:
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill(base)
        for y in range(0, TILE_SIZE, 4):
            for x in range(0, TILE_SIZE, 4):
                if (x + y) % 8 == 0:
                    surf.set_at((x, y), dot)
                elif (x * 3 + y) % 11 == 0:
                    surf.set_at((x, y), shell)
        tiles.append(surf)
    return tiles
