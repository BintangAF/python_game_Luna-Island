# items/material_item.py
from .item import Item


class MaterialItem(Item):
    """Item bahan untuk crafting"""
    
    def __init__(self, name: str, buy_price: int, sell_price: int, icon_path: str = None):
        super().__init__(name, f"Bahan {name} untuk crafting", icon_path)
        self.buy_price = buy_price
        self.sell_price = sell_price
    
    def use(self, target) -> bool:
        """Bahan biasanya tidak bisa digunakan langsung"""
        return False