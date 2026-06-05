import pygame, random

class Zombie:

    def __init__(self, game, type, lane):
        self.game = game
        self.type = type
        self.lane = lane
        self.pos = [480, (lane*42) + 62]
        self.img = game.assets["zombies"][type]

        self.speed = 0.1
        self.moving = True

        self.health = 10

    def rect(self):
        return pygame.Rect(self.pos[0]+5, self.pos[1]+16, 6, 16)

    def update(self):
        self.moving = True
        for plant in self.game.grid[self.lane]:
            if plant != 0:
                if self.rect().colliderect(plant.rect()):
                    self.moving = False
                    plant.damage()
        if self.moving:
            self.pos[0] -= self.speed

    def draw(self, display):
        display.blit(self.img, (int(self.pos[0]), int(self.pos[1])))