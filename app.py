import sys
import pygame

from config import WINDOW_TITLE, WIDTH, HEIGHT, FPS
from components.video_background import AnimatedVideoBackground
from managers.audio_manager import AudioManager
from scenes.menu_scene import MenuScene


class GameApp:
    def __init__(self):
        pygame.init()
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        
        pygame.display.set_caption(WINDOW_TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.audio = AudioManager()
        self.background = AnimatedVideoBackground()
        self.current_scene = MenuScene(self)

    def change_scene(self, new_scene):
        """Method untuk berpindah scene"""
        self.current_scene = new_scene

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            self.current_scene.handle_events(events)
            self.current_scene.update(dt)
            self.current_scene.draw(self.screen)
            pygame.display.flip()

        self.audio.stop_music()
        pygame.quit()
        sys.exit()