import pygame
from settings import *

class CameraGroup(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)
        self.display_surface = pygame.display.get_surface()

        # camera offset
        self.offset = pygame.math.Vector2(100, 100)
        self.half_screen_w = self.display_surface.get_size()[0] // 2
        self.half_screen_h = self.display_surface.get_size()[1] // 2

    def center_target_camera(self, target, game_map):
        self.offset.x = target.rect.centerx - self.half_screen_w
        self.offset.y = target.rect.centery - self.half_screen_h

        map_width = len(game_map.map_data[0]) * TILE_SIZE
        map_height = len(game_map.map_data) * TILE_SIZE

        max_offset_x = max(map_width - self.display_surface.get_width(), 0)
        max_offset_y = max(map_height - self.display_surface.get_height(), 0)

        self.offset.x = max(0, min(self.offset.x, max_offset_x))
        self.offset.y = max(0, min(self.offset.y, max_offset_y))

    def custom_draw(self, player, game_map):        
        self.center_target_camera(player, game_map)
        
        game_map.draw(self.display_surface, self.offset)

        for sprite in sorted(self.sprites(), key = lambda sprite : sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)