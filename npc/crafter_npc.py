from .base_npc import BaseNPC


class CrafterNPC(BaseNPC):
    """NPC untuk crafting (Pengrajin)"""

    def __init__(self, center_pos, image, groups, name):
        super().__init__(center_pos, image, groups, name)
        self.type = "crafter"

    def interact(self, level) -> None:
        """Buka crafting panel"""
        level.crafting_panel.open(self)
        level._freeze_player()
