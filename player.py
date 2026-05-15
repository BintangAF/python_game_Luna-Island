import pygame
from settings import *
from character import Character

class Player(Character):
    def __init__(self, x, y, name, hp, image_path, size):
        super().__init__(x, y, name, hp, image_path, size)
        self.speed = PLAYER_SPEED
        
    def move(self, walls):
        dx = 0
        dy = 0
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1

        # normalisasi
        if dx != 0 or dy != 0:
            length = (dx**2 + dy**2) ** 0.5
            dx /= length
            dy /= length

        self.rect.x += dx * self.speed
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0:
                    self.rect.right = wall.left
                elif dx < 0:
                    self.rect.left = wall.right    
                break

        self.rect.y += dy * self.speed
        for wall in walls:
            if self.rect.colliderect(wall):
                if dy > 0:
                    self.rect.bottom = wall.top
                elif dy < 0:
                    self.rect.top = wall.bottom
                break

    def update(self, walls):
        self.move(walls)

    def draw(self, screen):
        screen.blit(self.image, self.rect)