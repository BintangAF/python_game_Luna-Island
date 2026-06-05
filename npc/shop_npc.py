
from .base_npc import BaseNPC

class ShopNPC(BaseNPC):
    
    def __init__(self, center_pos, image, groups, name, items, buy_items=None):
        super().__init__(center_pos, image, groups, name)
        self.shop_items = items 
        self.buy_items = buy_items or []
        self.type = "shop"
    
    def interact(self, level) -> None:
        level.shop_panel.open(self)
        level._freeze_player()
    
    def get_buy_price(self, item_name: str) -> int:
        for item in self.buy_items:
            if item["name"] == item_name:
                return item["buy_price"]
        return 0 
    
    def can_buy_from_player(self, item_name: str) -> bool:
        return self.get_buy_price(item_name) > 0