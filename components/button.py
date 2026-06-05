import pygame


class MenuButton:
    def __init__(self, images: dict, center, action: str):
        self.images = images
        self.center = pygame.Vector2(center)
        self.action = action
        self.scale = 1.0
        self.target_scale = 1.0
        self.pressed = False
        self.click_timer = 0
        self.enabled = True
        self.alpha = 255

    def get_rect(self):
        img = self.images["normal"]
        w = int(img.get_width() * self.scale)
        h = int(img.get_height() * self.scale)
        return pygame.Rect(0, 0, w, h).move(self.center.x - w // 2, self.center.y - h // 2)

    def is_hovered(self, mouse_pos):
        return self.get_rect().collidepoint(mouse_pos)

    def handle_event(self, event):
        if not self.enabled:
            return None

        mouse_pos = pygame.mouse.get_pos()
        hovering = self.is_hovered(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and hovering:
            self.pressed = True
            self.click_timer = 12
            self.target_scale = 0.92

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and hovering:
                self.pressed = False
                return self.action
            self.pressed = False

        return None

    def update(self):
        hovering = self.is_hovered(pygame.mouse.get_pos())

        if self.click_timer > 0:
            self.click_timer -= 1
            self.target_scale = 0.92 if self.click_timer > 6 else 1.06
        elif hovering:
            self.target_scale = 1.04
        else:
            self.target_scale = 1.0

        self.scale += (self.target_scale - self.scale) * 0.25

    def draw(self, surface):
        hovering = self.is_hovered(pygame.mouse.get_pos())
        state = "pressed" if self.pressed else "hover" if hovering else "normal"
        img = self.images[state]

        w = max(1, int(img.get_width() * self.scale))
        h = max(1, int(img.get_height() * self.scale))
        scaled = pygame.transform.smoothscale(img, (w, h))
        scaled.set_alpha(self.alpha)
        rect = scaled.get_rect(center=(int(self.center.x), int(self.center.y)))

       
        surface.blit(scaled, rect)
