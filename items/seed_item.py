# items/seed_item.py
from .item import Item


class SeedItem(Item):
    """Item benih untuk ditanam"""
    
    def __init__(self, name: str, plant_type: str, growth_time: int, buy_price: int, sell_price: int, icon_path: str = None):
        super().__init__(name, f"Bibit {name} untuk ditanam", icon_path)
        self.plant_type = plant_type
        self.growth_time = growth_time
        self.buy_price = buy_price
        self.sell_price = sell_price
    
    def use(self, target) -> bool:
        """Tanam benih di farm"""
        if hasattr(target, 'plant_seed'):
            return target.plant_seed(self)
        return False
    
    def plant(self):
        """Buat tanaman dari benih"""
        # Akan diimplementasikan saat sistem farm selesai
        return None