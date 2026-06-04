import pygame
import sys

from level import Level


class GameScene:
    """
    GAME SCENE

    Scene ini adalah game utama (Level)
    """

    def __init__(self, app):
        self.app = app
        self.level = Level(app)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.app.running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    if (
                        not getattr(self.level, "shop_open", False)
                        and getattr(self.level, "mode", "outside") != "cave"
                    ):
                        self.back_to_menu()
                        return

            self.level.handle_event(event)

    def update(self, dt):
        self.level.run(dt)

        if hasattr(self.level, "game_over") and self.level.game_over:
            self.back_to_menu()

    def draw(self, surface):

        pass

    def back_to_menu(self):
        """Kembali ke menu utama"""
        from scenes.menu_scene import MenuScene

        self.app.audio.stop_music()
        self.app.audio.play_menu_music()
        self.app.change_scene(MenuScene(self.app))
