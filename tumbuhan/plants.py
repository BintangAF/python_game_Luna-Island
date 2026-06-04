import pygame, random
from tumbuhan.utils import Projectile, Sun, MushroomProjectile

class Plant:
    def __init__(self, game, type, pos, max_health):
        self.game = game
        self.type = type
        self.pos = pos
        self.img = game.assets["plants"][type]
        self.max_health = max_health
        self.health = max_health
        self.damage_cooldown = 30

    def rect(self):
        return pygame.Rect((self.pos[0]*42) + 52, (self.pos[1]*42) + 58, 42, 42)

    def update(self, draw_pos):
        self.damage_cooldown -= 1

    def draw(self, display, draw_pos):
        display.blit(self.img, draw_pos)

    def damage(self):
        if self.damage_cooldown <= 0:
            self.health -= 1
            self.damage_cooldown = 30
            random.choice(self.game.assets["sfx"]["chomp"]).play()

class Peashooter(Plant):
    def __init__(self, game, pos):
        super().__init__(game, "peashooter", pos, 8)
        self.cooldown = 120

    def update(self, draw_pos):
        if self.game.zombie_lanes[self.pos[1]]:
            self.cooldown -= random.random()*2
            if self.cooldown <= 0:
                self.game.projectiles.append(Projectile(self.game, "pea", (draw_pos[0]+(random.random()*4 + 10), draw_pos[1]+(random.random()*4 + 15)), [2, 0], 1))
                self.cooldown = 120
                random.choice(self.game.assets["sfx"]["throw"]).play()
        super().update(draw_pos)

    def draw(self, display, draw_pos):
        super().draw(display, draw_pos)

class Sunflower(Plant):
    def __init__(self, game, pos):
        super().__init__(game, "sunflower", pos, 8)
        self.cooldown = 120

    def update(self, draw_pos):
        self.cooldown -= random.random()*2
        if self.cooldown <= 0:
            self.game.projectiles.append(Sun(self.game, [draw_pos[0]+random.randint(-4,4), draw_pos[1]+16+random.randint(-2,2)], [0, 0.02], wave=False))
            self.cooldown = 780
        super().update(draw_pos)

    def draw(self, display, draw_pos):
        if self.cooldown <= 60:
            img_mask = pygame.mask.from_surface(self.img)
            img_mask = img_mask.to_surface()
            img_mask.set_colorkey((0,0,0))
            img_mask.set_alpha(30)
            super().draw(display, draw_pos)
            display.blit(img_mask, draw_pos)
        else:
            super().draw(display, draw_pos)

class Walnut(Plant):
    def __init__(self, game, pos):
        self.game = game
        self.type = "walnut"
        self.pos = pos
        self.max_health = 30
        self.health = 30
        self.img = game.assets["plants"]["walnut"][0]
        self.damage_cooldown = 30

    def update(self, draw_pos):
        if self.health <= 20:
            self.img = self.game.assets["plants"]["walnut"][1]
            if self.health <= 10:
                self.img = self.game.assets["plants"]["walnut"][2]
        return super().update(draw_pos)

    def draw(self, display, draw_pos):
        super().draw(display, draw_pos)
        
class Mushroom(Plant):
    def __init__(self, game, pos):
        super().__init__(game, "mushroom", pos, 10)
        self.cooldown = 180

    def update(self, draw_pos):
        if self.game.zombie_lanes[self.pos[1]]:
            self.cooldown -= 1
            if self.cooldown <= 0:
                self.game.projectiles.append(
                    MushroomProjectile(self.game,
                    [draw_pos[0]+10, draw_pos[1]+8])
                )
                self.cooldown = 180
        super().update(draw_pos)

    def draw(self, display, draw_pos):
        super().draw(display, draw_pos)