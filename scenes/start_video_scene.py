import pygame

from config import WIDTH, HEIGHT
from components.start_video_player import StartVideoPlayer


class StartVideoScene:

    def __init__(self, app):
        self.app = app
        self.video = StartVideoPlayer()
        self.font = pygame.font.Font(None, 32)

        self.app.audio.stop_music()
        self.app.audio.play_start_video_audio()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    self.go_to_game()

                if event.key == pygame.K_ESCAPE:
                    self.app.audio.stop_music()
                    from scenes.menu_scene import MenuScene

                    self.app.change_scene(MenuScene(self.app))

    def update(self, dt):
        self.video.update(dt)

        if self.video.finished:
            self.go_to_game()

    def draw(self, surface):
        self.video.draw(surface)

        hint = self.font.render("Tekan SPACE untuk skip video", True, (230, 230, 230))
        shadow = self.font.render("Tekan SPACE untuk skip video", True, (0, 0, 0))
        rect = hint.get_rect(center=(WIDTH // 2, HEIGHT - 38))
        surface.blit(shadow, rect.move(2, 2))
        surface.blit(hint, rect)

    def go_to_game(self):
        self.app.audio.stop_music()
        from scenes.game_scene import GameScene

        self.app.change_scene(GameScene(self.app))
