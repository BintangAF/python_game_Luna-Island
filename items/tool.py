# items/tool.py
from abc import abstractmethod
from .item import Item


class Tool(Item):
    """Base class untuk semua alat"""
    
    def __init__(self, name: str, description: str, durability: int, icon_path: str = None):
        super().__init__(name, description, icon_path)
        self.max_durability = durability
        self.durability = durability
    
    def use(self, target) -> bool:
        """Gunakan alat"""
        if self.durability <= 0:
            return False
        result = self._use_impl(target)
        if result:
            self.durability -= 1
        return result
    
    @abstractmethod
    def _use_impl(self, target) -> bool:
        """Implementasi penggunaan alat oleh subclass"""
        pass
    
    def repair(self, amount: int = None):
        """Perbaiki alat"""
        if amount is None:
            self.durability = self.max_durability
        else:
            self.durability = min(self.max_durability, self.durability + amount)
    
    def get_durability_percent(self) -> float:
        """Dapatkan persentase durability"""
        return self.durability / self.max_durability if self.max_durability > 0 else 0