from pygame.math import Vector2

WINDOW_TITLE = 'Monster Island'
FPS          = 60

SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
TILE_SIZE     = 32

CAMERA_ZOOM      = 1.20
CAMERA_ZOOM_MIN  = 0.85
CAMERA_ZOOM_MAX  = 2.20
CAMERA_ZOOM_STEP = 0.08

PLAYER_SPEED = 180

MAP_W = 84
MAP_H = 50


SPAWN_X = 13 * TILE_SIZE + TILE_SIZE // 2
SPAWN_Y = 15 * TILE_SIZE + TILE_SIZE // 2

LAYERS = {
    'ground':  0,
    'objects': 1,
    'player':  2,
    'rain floor': 3,
    'rain drops': 4,
    'ui':      5,
}

COL_BG     = (96, 185, 198)
COL_UI_BG  = (0, 0, 0, 160)
COL_WHITE  = (255, 255, 255)
COL_YELLOW = (255, 220, 60)
COL_GREEN  = (80, 200, 80)
