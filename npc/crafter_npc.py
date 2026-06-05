from base import *

class CrafterNPC(BaseNPC):
    def __init__(self, center_pos, image, groups, name):
        super().__init__(center_pos, image, groups, name)
        self.type = "crafter"

    def move():
        pass
    
    def interact(self, level) -> None:
        level.crafting_panel.open(self)
        level._freeze_player()
