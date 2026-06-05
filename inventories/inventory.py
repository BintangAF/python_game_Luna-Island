from typing import List, Dict, Optional
from items.item import Item
from items.tool import Tool


class Inventory:
    """Sistem inventory dengan OOP"""

    def __init__(self, max_slots: int = 20):
        self._items: List[Item] = []
        self._max_slots = max_slots
        self._money = 120

    @property
    def money(self) -> int:
        return self._money

    @money.setter
    def money(self, value: int):
        self._money = max(0, value)

    @property
    def items(self) -> List[Item]:
        return self._items.copy()

    @property
    def is_full(self) -> bool:
        return len(self._items) >= self._max_slots

    @property
    def empty_slots(self) -> int:
        return self._max_slots - len(self._items)

    def add_item(self, item: Item, quantity: int = 1) -> bool:
        """Tambah item ke inventory"""

        for i in range(quantity):
            if len(self._items) >= self._max_slots:
                return False
            self._items.append(item)
        return True

    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """Hapus item dari inventory berdasarkan nama"""
        removed = 0
        for i in range(len(self._items) - 1, -1, -1):
            if self._items[i].name == item_name and removed < quantity:
                self._items.pop(i)
                removed += 1
        return removed == quantity

    def has_item(self, item_name: str, quantity: int = 1) -> bool:
        """Cek apakah memiliki item tertentu"""
        count = self.get_item_count(item_name)
        return count >= quantity

    def get_item_count(self, item_name: str) -> int:
        """Dapatkan jumlah item tertentu"""
        return sum(1 for item in self._items if item.name == item_name)

    def get_items_by_type(self, item_type: type) -> List[Item]:
        """Dapatkan semua item dengan tipe tertentu"""
        return [item for item in self._items if isinstance(item, item_type)]

    def get_item(self, item_name: str) -> Optional[Item]:
        """Dapatkan item pertama dengan nama tertentu"""
        for item in self._items:
            if item.name == item_name:
                return item
        return None

    def get_all_items_grouped(self) -> Dict[str, int]:
        """Dapatkan semua item yang dikelompokkan berdasarkan nama"""
        grouped = {}
        for item in self._items:
            grouped[item.name] = grouped.get(item.name, 0) + 1
        return grouped

    def add_money(self, amount: int):
        """Tambah uang"""
        self._money += amount

    def remove_money(self, amount: int) -> bool:
        """Kurang uang, return False jika tidak cukup"""
        if self._money >= amount:
            self._money -= amount
            return True
        return False

    def can_afford(self, amount: int) -> bool:
        """Cek apakah uang cukup"""
        return self._money >= amount

    def clear(self):
        """Kosongkan inventory"""
        self._items.clear()

    def __len__(self):
        return len(self._items)

    def __contains__(self, item_name: str):
        return self.has_item(item_name)
