import pygame

from config import ASSET_DIR, START_BUTTON_POS, EXIT_BUTTON_POS, LOGO_PATH, LOGO_MAX_WIDTH, LOGO_MAX_HEIGHT, LOGO_POS, WIDTH, HEIGHT
from components.button import MenuButton


class MenuScene:
    def __init__(self, app):
        self.app = app
        self.app.audio.play_menu_music()

        self.buttons = [
            MenuButton(self._load_button_images("start"), START_BUTTON_POS, "start"),
            MenuButton(self._load_button_images("exit"), EXIT_BUTTON_POS, "exit"),
        ]

        self.state = "menu"
        self.fade_alpha = 0
        self.logo = self._load_logo()

    def _load_button_images(self, name: str):
        return {
            "normal": pygame.image.load(str(ASSET_DIR / f"button_{name}_normal.png")).convert_alpha(),
            "hover": pygame.image.load(str(ASSET_DIR / f"button_{name}_hover.png")).convert_alpha(),
            "pressed": pygame.image.load(str(ASSET_DIR / f"button_{name}_pressed.png")).convert_alpha(),
        }

    def _load_logo(self):
        if not LOGO_PATH.exists():
            return None
        logo = pygame.image.load(str(LOGO_PATH)).convert_alpha()
        w, h = logo.get_size()
        ratio = min(LOGO_MAX_WIDTH / w, LOGO_MAX_HEIGHT / h)
        new_size = (max(1, int(w * ratio)), max(1, int(h * ratio)))
        return pygame.transform.smoothscale(logo, new_size)

    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                result = button.handle_event(event)
                if result == "exit":
                    self.app.running = False
                elif result == "start":
                    self.state = "fade_to_game"
                    self.fade_alpha = 0
                    for item in self.buttons:
                        item.enabled = False

    def update(self, dt):
        self.app.background.update(dt)

        for button in self.buttons:
            button.update()

        if self.state == "fade_to_game":
            self.fade_alpha += 7
            for button in self.buttons:
                button.alpha = max(0, 255 - self.fade_alpha * 2)
            if self.fade_alpha >= 255:
                # Setelah klik START GAME, masuk ke scene video pembuka.
                from scenes.start_video_scene import StartVideoScene
                self.app.change_scene(StartVideoScene(self.app))

    def draw(self, surface):
        self.app.background.draw(surface)

        for button in self.buttons:
            button.draw(surface)

        self._draw_logo(surface)

        if self.state == "fade_to_game":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, min(255, self.fade_alpha)))
            surface.blit(overlay, (0, 0))

    def _draw_logo(self, surface):
        if self.logo is None:
            return
        rect = self.logo.get_rect(center=LOGO_POS)
        surface.blit(self.logo, rect)
