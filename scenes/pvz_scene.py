import pygame
import random
import sys
from pygame.locals import *
import pytmx

from tumbuhan.utils import Projectile, Sun, Particle, ParticleBurst, MushroomProjectile
from tumbuhan.plants import Peashooter, Sunflower, Walnut, Mushroom
from tumbuhan.zombies import Zombie


class PVZScene:
    """Plants vs Zombies Game Scene - SAMA PERSIS dengan Game class asli"""
    
    def __init__(self, app):
        self.app = app
        
        # Ukuran display untuk PVZ
        self.pvz_width = 480
        self.pvz_height = 320
        self.display = pygame.Surface((self.pvz_width, self.pvz_height))
        
        # Assets - SAMA PERSIS
        self.assets = {
            "plants":{
                "peashooter":pygame.image.load("assets/images/plants/peashooter.png"),
                "sunflower":pygame.image.load("assets/images/plants/sunflower.png"),
                "walnut":[pygame.image.load("assets/images/plants/walnut.png").subsurface((0,0,16,32)),
                          pygame.image.load("assets/images/plants/walnut.png").subsurface((16,0,16,32)),
                          pygame.image.load("assets/images/plants/walnut.png").subsurface((32,0,16,32)),],
                "mushroom": pygame.image.load("assets/images/plants/jamur.png")
            },
            "seeds":{
                "peashooter":pygame.image.load("assets/images/seeds/peashooter.png"),
                "sunflower":pygame.image.load("assets/images/seeds/sunflower.png"),
                "walnut":pygame.image.load("assets/images/seeds/walnut.png"),
                "mushroom":pygame.image.load("assets/images/seeds/mushroom.png")
            },
            "zombies":{
                "normal":pygame.image.load("assets/images/zombies/normal.png")
            },
            "projectiles":{
                "pea":pygame.image.load("assets/images/projectiles/pea.png"),
                "mushroom":pygame.image.load("assets/images/projectiles/Mushroom.png")
            },
            "sun":pygame.image.load("assets/images/sun.png"),
            "sfx":{
                "splat":[pygame.mixer.Sound("assets/sounds/splat.ogg"),
                         pygame.mixer.Sound("assets/sounds/splat2.ogg"),
                         pygame.mixer.Sound("assets/sounds/splat3.ogg")],
                "plant":[pygame.mixer.Sound("assets/sounds/plant.ogg"),
                         pygame.mixer.Sound("assets/sounds/plant2.ogg")],
                "gulp":pygame.mixer.Sound("assets/sounds/gulp.ogg"),
                "swing":pygame.mixer.Sound("assets/sounds/swing.ogg"),
                "shoop":pygame.mixer.Sound("assets/sounds/shoop.ogg"),
                "chomp":[pygame.mixer.Sound("assets/sounds/chomp.ogg"),
                         pygame.mixer.Sound("assets/sounds/chomp2.ogg")],
                "throw":[pygame.mixer.Sound("assets/sounds/throw.ogg"),
                         pygame.mixer.Sound("assets/sounds/throw2.ogg")],
                "losemusic":pygame.mixer.Sound("assets/sounds/losemusic.ogg"),
                "losescream":pygame.mixer.Sound("assets/sounds/scream.ogg"),
                "seedlift":pygame.mixer.Sound("assets/sounds/seedlift.ogg"),
                "buzzer":pygame.mixer.Sound("assets/sounds/buzzer.ogg"),
                "points":pygame.mixer.Sound("assets/sounds/points.ogg")
            }
        }
        
        self.font16 = pygame.font.Font("assets/m6x11.ttf", 16)
        self.font32 = pygame.font.Font("assets/m6x11.ttf", 32)
        self.font48 = pygame.font.Font("assets/m6x11.ttf", 48)
    
        self.tmx_map = pytmx.load_pygame("assets/maps/untitled.tmx")
        
        # Game state - SAMA PERSIS
        self.cur_plant = ""
        self.mouse_pos = (0,0)
        self.game_finished = False  # Tambahan untuk scene management

        self.grid = [[0,0,0,0,0,0,0,0,0],
                     [0,0,0,0,0,0,0,0,0],
                     [0,0,0,0,0,0,0,0,0],
                     [0,0,0,0,0,0,0,0,0],
                     [0,0,0,0,0,0,0,0,0],
                     [0,0,0,0,0,0,0,0,0]]
        
        self.entities = []
        self.particles = []
        self.projectiles = []
        self.zombies = []
        self.zombie_lanes = [False, False, False, False, False, False]

        # Musik
        pygame.mixer.music.load("assets/music/grasswalk.mp3")
        pygame.mixer.music.play(-1, 0, 100)
        pygame.mixer.music.set_volume(0.4)

        self.level_timer = 0

        self.zombie_time = 600
        self.zombie_timer = 600
        self.zombie_max = 1
        self.zombie_max_limit = 10
        self.zombie_last_lane = 5

        self.sun = 100
        self.sun_time = 300
        self.sun_timer = 60

        self.seed_collider_1 = pygame.Rect(438, 7, 36, 57) 
        self.seed_collider_2 = pygame.Rect(396, 7, 36, 57)  
        self.seed_collider_3 = pygame.Rect(354, 7, 36, 57)  
        self.seed_collider_4 = pygame.Rect(312, 7, 36, 57)

    def draw_map(self, surface):
        for layer in self.tmx_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_map.get_tile_image_by_gid(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmx_map.tilewidth,
                                            y * self.tmx_map.tileheight))

    def handle_events(self, events):
        for event in events:
            if event.type == QUIT:
                self.app.running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.game_finished = True
                    from scenes.menu_scene import MenuScene
                    self.app.change_scene(MenuScene(self.app))
                    return
                if event.key == K_1:
                    self.cur_plant = "peashooter"
                if event.key == K_2:
                    self.cur_plant = "sunflower"
                if event.key == K_3:
                    self.cur_plant = "walnut"
                # Tombol 4 untuk mushroom (tambahan)
                if event.key == K_4:
                    self.cur_plant = "mushroom"
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.seed_collider_1.collidepoint(self.mouse_pos[0], self.mouse_pos[1]):
                        if self.sun >= 50:
                            self.cur_plant = "walnut"
                            self.assets["sfx"]["seedlift"].play()
                        else:
                            self.assets["sfx"]["buzzer"].play()
                    if self.seed_collider_2.collidepoint(self.mouse_pos[0], self.mouse_pos[1]):
                        if self.sun >= 50:
                            self.cur_plant = "sunflower"
                            self.assets["sfx"]["seedlift"].play()
                        else:
                            self.assets["sfx"]["buzzer"].play()
                    if self.seed_collider_3.collidepoint(self.mouse_pos[0], self.mouse_pos[1]):
                        if self.sun >= 100:
                            self.cur_plant = "peashooter"
                            self.assets["sfx"]["seedlift"].play()
                        else:
                            self.assets["sfx"]["buzzer"].play()
                    if self.seed_collider_4.collidepoint(self.mouse_pos[0], self.mouse_pos[1]):
                        if self.sun >= 150:
                            self.cur_plant = "mushroom"
                            self.assets["sfx"]["seedlift"].play()
                        else:
                            self.assets["sfx"]["buzzer"].play()
                if event.button == 3:
                    self.cur_plant = ""

    def update(self, dt):
        # Update mouse position (scaled ke ukuran PVZ)
        mouse_pos = pygame.mouse.get_pos()
        self.mouse_pos = (mouse_pos[0] * (self.pvz_width / self.app.screen.get_width()),
                         mouse_pos[1] * (self.pvz_height / self.app.screen.get_height()))

        self.level_timer += 1

        # Zombie spawn
        self.zombie_timer -= 1 + (random.random()-0.5)
        if self.zombie_timer <= 0:
            if self.zombie_time >= 30:
                self.zombie_time -= 20
            self.zombie_timer = self.zombie_time
            if len(self.zombies) < self.zombie_max:
                lanes = [0,1,2,3,4,5]
                try:
                    lanes.remove(self.zombie_last_lane)
                except:
                    pass
                lane = random.choice(lanes)
                self.zombie_last_lane = lane
                self.zombies.append(Zombie(self, "normal", lane))
        if (self.level_timer%2400) == 0 and self.zombie_max < self.zombie_max_limit:
            self.zombie_max += 1

        # Sun spawn
        self.sun_timer -= 1 + (random.random()-0.5)
        if self.sun_timer <= 0:
            self.sun_timer = self.sun_time
            self.projectiles.append(Sun(self, [random.randint(60, 390), -19], [0, 0.1]))

        y = 0
        for row in self.grid:
            x = 0
            for tile in row:
                if tile != 0:
                    tile.update(((x*42) + 52, (y*42) + 58))
                    if tile.health <= 0:
                        self.grid[y][x] = 0
                        self.assets["sfx"]["gulp"].play()
                
                # Plant placement
                tile_rect = pygame.Rect((x*42) + 52, (y*42) + 58, 42, 42)
                if self.cur_plant != "" and tile_rect.collidepoint(self.mouse_pos[0], self.mouse_pos[1]) and tile == 0:
                    if pygame.mouse.get_pressed()[0]:
                        if self.cur_plant == "peashooter" and self.sun >= 100:
                            self.sun -= 100
                            self.grid[y][x] = Peashooter(self, [x,y])
                            random.choice(self.assets["sfx"]["plant"]).play()
                        elif self.cur_plant == "sunflower" and self.sun >= 50:
                            self.sun -= 50
                            self.grid[y][x] = Sunflower(self, [x,y])
                            random.choice(self.assets["sfx"]["plant"]).play()
                        elif self.cur_plant == "walnut" and self.sun >= 50:
                            self.sun -= 50
                            self.grid[y][x] = Walnut(self, [x,y])
                            random.choice(self.assets["sfx"]["plant"]).play()
                        elif self.cur_plant == "mushroom" and self.sun >= 150:
                            self.sun -= 150
                            self.grid[y][x] = Mushroom(self, [x,y])
                            random.choice(self.assets["sfx"]["plant"]).play()
                        else:
                            self.assets["sfx"]["buzzer"].play()
                        self.cur_plant = ""
                        if self.grid[y][x] != 0:
                            self.particles += ParticleBurst((self.grid[y][x].rect().centerx, self.grid[y][x].rect().bottom), 0.2, 0.1, 270, 20, 10, [(115,23,45),(20,160,46),(26,122,62)], 40, 10, 2, 1, True)
                            self.particles += ParticleBurst((self.grid[y][x].rect().centerx, self.grid[y][x].rect().bottom), 0.2, 0.1, 90, 20, 10, [(115,23,45),(20,160,46),(26,122,62)], 40, 10, 2, 1, True)
                x += 1
            y += 1

        self.entities = self.projectiles + self.zombies

        # Update zombies
        self.zombie_lanes = [False, False, False, False, False, False]
        for i, zombie in sorted(enumerate(self.zombies), reverse=True):
            zombie.update()
            zombie.draw(self.display)
            self.zombie_lanes[zombie.lane] = True
            for a, projectile in sorted(enumerate(self.projectiles), reverse=True):
                if isinstance(projectile, (Projectile, MushroomProjectile)):
                    if zombie.rect().colliderect(projectile.rect()):
                        zombie.health -= projectile.damage
                        self.projectiles.pop(a)
                        random.choice(self.assets["sfx"]["splat"]).play()
                        self.particles += ParticleBurst(projectile.rect().center, 0.5, 0.3, 0, 180, random.randint(8, 12), [(156,219,67),(89,193,53),(20,160,46)], 16, 8, 2, 1)
            if zombie.health <= 0:
                self.zombies.pop(i)
                self.particles += ParticleBurst(zombie.rect().center, 0.7, 0.4, 0, 180, random.randint(24, 32), [(50,132,100),(35,103,78),(115,23,45),(115,23,45),(115,23,45)], 32, 8, 3, 2, True, True)
            if zombie.pos[0] <= 4:
                self.dead()
                return

        # Update projectiles
        for i, projectile in sorted(enumerate(self.projectiles), reverse=True):
            projectile.update()
            if -32 > projectile.pos[0] or projectile.pos[0] > 528 or -32 > projectile.pos[1] or projectile.pos[1] > 377:  
                self.projectiles.pop(i)
            if isinstance(projectile, Sun):
                if projectile.rect().collidepoint(self.mouse_pos) and pygame.mouse.get_pressed()[0]:
                    self.projectiles.pop(i)
                    self.sun += projectile.value
                    self.assets["sfx"]["points"].play()
                    self.particles += ParticleBurst(projectile.rect().center, 0.5, 0.3, 0, 180, random.randint(10, 14), [(249,163,27),(255,213,65)], 24, 8, 3, 1)

        # Update particles
        for particle in self.particles:
            particle.update()

    def draw(self, surface):
        self.display.fill((0,0,0))
        self.draw_map(self.display)

        y = 0
        for row in self.grid:
            x = 0
            for tile in row:
                if tile != 0:
                    tile.draw(self.display, ((x*42) + 52, (y*42) + 58))
                
                if self.cur_plant != "":
                    try:
                        plant_overlay = pygame.Surface(self.assets["plants"][self.cur_plant].get_size())
                    except:
                        plant_overlay = pygame.Surface(self.assets["plants"][self.cur_plant][0].get_size())
                    plant_overlay.set_colorkey((0,0,0))
                    try:
                        plant_overlay.blit(self.assets["plants"][self.cur_plant], (0,0))
                    except:
                        plant_overlay.blit(self.assets["plants"][self.cur_plant][0], (0,0))
                    self.display.blit(plant_overlay, (self.mouse_pos[0]-12, self.mouse_pos[1]-43))
                    
                    tile_rect = pygame.Rect((x*42) + 52, (y*42) + 58, 42, 42)
                    if tile_rect.collidepoint(self.mouse_pos[0], self.mouse_pos[1]) and tile == 0:
                        plant_overlay.set_alpha(40)
                        self.display.blit(plant_overlay, ((x*42) + 52, (y*42) + 58))
                x += 1
            y += 1

        for projectile in self.projectiles:
            projectile.draw(self.display)
        
        for zombie in self.zombies:
            zombie.draw(self.display)
        
        for particle in self.particles:
            particle.draw(self.display)

        self.display.blit(self.assets["sun"], (6, 7))
        self.display.blit(self.font16.render("{:,}".format(self.sun), False, (255,255,255)), (40, 14)) 
        self.display.blit(self.assets["seeds"]["peashooter"], (354, 7))   
        self.display.blit(self.assets["seeds"]["sunflower"], (396, 7))    
        self.display.blit(self.assets["seeds"]["walnut"], (438, 7))
        self.display.blit(self.assets["seeds"]["mushroom"], (321, 7))

        # Scale ke main screen
        scaled = pygame.transform.scale(self.display, (self.app.screen.get_width(), self.app.screen.get_height()))
        surface.blit(scaled, (0, 0))

    def dead(self):
        """Game over - kembali ke menu utama"""
        self.game_finished = True
        from scenes.menu_scene import MenuScene
        self.app.change_scene(MenuScene(self.app))