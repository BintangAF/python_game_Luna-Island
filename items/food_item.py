# items/food_item.py
from .item import Item


class FoodItem(Item):
    """Item makanan untuk memulihkan energi"""
    
    def __init__(self, name: str, energy_restore: int, buy_price: int, sell_price: int, icon_path: str = None):
        super().__init__(name, f"Makanan yang memulihkan {energy_restore} energi", icon_path)
        self.energy_restore = energy_restore
        self.buy_price = buy_price
        self.sell_price = sell_price
    
    def use(self, target) -> bool:
        """Makan makanan untuk restore energy"""
        if hasattr(target, 'energy') and hasattr(target, 'max_energy'):
            if target.energy < target.max_energy:
                target.energy = min(target.energy + self.energy_restore, target.max_energy)
                return True
        return False