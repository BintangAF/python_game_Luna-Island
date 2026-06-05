import pygame

""" 
Image Path
1. Pea: 'peashooter.png'
2. Mushroom: 'jamur.png'
3. Sunflower: 'sunflower.png'
4. Walnut: 'walnut.png'

"""

# hanya untuk tampilan tanaman yang sudah tumbuh, bukan untuk benihnya
class Plant:
    def __init__(self, name, image, growth_time):
        self.name = name
        self.image = image
        self.growth_time = growth_time  # waktu yang dibutuhkan untuk tumbuh (dalam detik)