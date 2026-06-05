import pygame
from tool import Tool

class WateringCan(Tool):
    def __init__(self):
        super().__init__(
            name="Watering Can",
            description="Water plants."
        )
        self.image = pygame.image.load('graphics/tools/watering_can.PNG').convert_alpha()

    def use(self, player):
        # Implement watering can usage logic here
        print(f"{player.name} uses the {self.name} to water the plants.")