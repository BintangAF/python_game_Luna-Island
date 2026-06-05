import pygame

""" 
Image Path
1. Pea Seed: 'pea_seed.png'
2. Mushroom Seed: 'mushroom_seed.png'
3. Sunflower Seed: 'sunflower_seed.png'
4. Walnut Seed: 'walnut_seed.png'

"""

class Seed:
    def __init__(self, name, description, image):
        self.name = name
        self.description = description
        self.image = image