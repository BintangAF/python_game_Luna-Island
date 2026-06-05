import pygame


class Inventory:
    def __init__(self):
        self.slot = 20
        self.inventory: dict[str, int] = {}
        self.item_meta: dict[str, object] = {}
        self.font = pygame.font.SysFont('Arial', 24)

    def add_item(self, item):
        name = item if isinstance(item, str) else getattr(item, 'name', None)
        if name is None:
            return

        if len(self.inventory) >= self.slot and name not in self.inventory:
            print('Inventory is full!')
            return

        self.inventory[name] = self.inventory.get(name, 0) + 1
        if not isinstance(item, str):
            self.item_meta[name] = item

    def remove_item(self, item):
        name = item if isinstance(item, str) else getattr(item, 'name', None)
        if name is None:
            return

        if name in self.inventory:
            self.inventory[name] -= 1
            if self.inventory[name] <= 0:
                del self.inventory[name]
                self.item_meta.pop(name, None)
        else:
            print(f'{name} not found in inventory!')

    def get_item(self, item_name, default=None):
        return self.item_meta.get(item_name, default)

    def get(self, item_name, default=0):
        return self.inventory.get(item_name, default)

    def items(self):
        return self.inventory.items()

    def keys(self):
        return self.inventory.keys()

    def __getitem__(self, item_name):
        return self.inventory[item_name]

    def __setitem__(self, item_name, value):
        self.inventory[item_name] = value

    def __delitem__(self, item_name):
        del self.inventory[item_name]

    def __iter__(self):
        return iter(self.inventory)

    def __len__(self):
        return len(self.inventory)
