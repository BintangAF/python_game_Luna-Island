import pygame
from tool import Tool

class Hoe(Tool):
    def __init__(self):
        super().__init__(
            name="Hoe",
            description="Dig holes for planting seeds."            
        )
        self.image = pygame.image.load('graphics/tools/hoe.PNG').convert_alpha()

    def use(self, player):
        # Implement hoe usage logic here
        print(f"{player.name} uses the {self.name} to till the soil.")