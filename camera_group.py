import math
import pygame
from settings import *


class CameraGroup(pygame.sprite.Group):
   

    def __init__(self, world_width=None, world_height=None, background_color=COL_BG, center_small_world=False):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.zoom = CAMERA_ZOOM
        self.world_width = world_width or (MAP_W * TILE_SIZE)
        self.world_height = world_height or (MAP_H * TILE_SIZE)
        self.background_color = background_color
        self.center_small_world = center_small_world
        self._rebuild_view_surface()

    def _rebuild_view_surface(self):
        self.view_width = math.ceil(SCREEN_WIDTH / self.zoom)
        self.view_height = math.ceil(SCREEN_HEIGHT / self.zoom)
        self.world_surface = pygame.Surface((self.view_width, self.view_height), pygame.SRCALPHA)

    def set_world_bounds(self, width, height):
        self.world_width = width
        self.world_height = height

    def set_zoom(self, value):
        new_zoom = max(CAMERA_ZOOM_MIN, min(CAMERA_ZOOM_MAX, value))
        if abs(new_zoom - self.zoom) > 0.001:
            self.zoom = new_zoom
            self._rebuild_view_surface()

    def change_zoom(self, direction):
        if direction > 0:
            self.set_zoom(self.zoom + CAMERA_ZOOM_STEP)
        elif direction < 0:
            self.set_zoom(self.zoom - CAMERA_ZOOM_STEP)

    def reset_zoom(self):
        self.set_zoom(CAMERA_ZOOM)

    def update_camera(self, target):
        if self.center_small_world and self.world_width <= self.view_width:
            self.offset.x = -(self.view_width - self.world_width) / 2
        else:
            self.offset.x = target.rect.centerx - self.view_width / 2
            self.offset.x = max(0, min(self.offset.x, max(0, self.world_width - self.view_width)))

        if self.center_small_world and self.world_height <= self.view_height:
            self.offset.y = -(self.view_height - self.world_height) / 2
        else:
            self.offset.y = target.rect.centery - self.view_height / 2
            self.offset.y = max(0, min(self.offset.y, max(0, self.world_height - self.view_height)))

    def world_to_screen(self, pos):
        wx, wy = pos
        sx = int((wx - self.offset.x) * self.zoom)
        sy = int((wy - self.offset.y) * self.zoom)
        return sx, sy

    def custom_draw(self, target):
        self.update_camera(target)
        self.world_surface.fill(self.background_color)

        for layer_name in sorted(LAYERS, key=lambda k: LAYERS[k]):
            layer_val = LAYERS[layer_name]
            sprites_in_layer = [
                s for s in self.sprites()
                if getattr(s, 'z', LAYERS['objects']) == layer_val
            ]
            sprites_in_layer.sort(key=lambda s: s.rect.centery)
            for sprite in sprites_in_layer:
                draw_x = int(sprite.rect.x - self.offset.x)
                draw_y = int(sprite.rect.y - self.offset.y)
                self.world_surface.blit(sprite.image, (draw_x, draw_y))

        scaled_surface = pygame.transform.scale(self.world_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.display_surface.blit(scaled_surface, (0, 0))

