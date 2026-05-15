import pygame, sys
from settings import *
from player import Player
from camera_group import CameraGroup
from gameMap import GameMap
from map1 import MAP1

class Game():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)        

        self.clock = pygame.time.Clock()
        self.fps = FPS

        self.running = True

        self.dt = 0

        self.bg_color = (30, 30, 30)

        # Inisialisasi objek game disini
        self.player = Player(3 * TILE_SIZE, 3 * TILE_SIZE, "Player1", 100, PLAYER_IMAGE, PLAYER_SIZE)
        self.player_group = pygame.sprite.GroupSingle(self.player)

        self.camera_group = CameraGroup(self.player)

        self.game_map = GameMap(MAP1)        

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                self.on_key_down(event)

            if event.type == pygame.KEYUP:
                self.on_key_up(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.on_mouse_down(event)
    
    def on_key_down(self, event):
        pass
    
    def on_key_up(self, event):
        pass

    def on_mouse_down(self, event):
        pass

    def update(self):
        self.player_group.update(self.game_map.walls)

    def draw(self):
        self.screen.fill(self.bg_color)

        # Masukkan/gambar objek disini
        self.camera_group.custom_draw(self.player, self.game_map)

        pygame.display.flip()

    def run(self):
        while self.running:

            # Delta time dalam detik
            self.dt = self.clock.tick(self.fps) / 1000

            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()