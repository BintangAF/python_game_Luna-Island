# items/weapon.py
from .tool import Tool


class Weapon(Tool):
    """Senjata untuk bertarung"""
    
    def __init__(self, name: str, damage: int, durability: int, icon_path: str = None):
        super().__init__(name, f"{name} - Menyerang dengan damage {damage}", durability, icon_path)
        self.damage = damage
    
    def _use_impl(self, target) -> bool:
        """Serang target dengan weapon"""
        if hasattr(target, 'take_damage'):
            target.take_damage(self.damage)
            return True
        return False
    
    def attack(self, target) -> int:
        """Alias untuk _use_impl"""
        if self.durability <= 0:
            return 0
        self.durability -= 1
        return self.damage