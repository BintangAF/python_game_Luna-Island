from .base_npc import BaseNPC


class QuestNPC(BaseNPC):
    """NPC yang memberikan quest (untuk development selanjutnya)"""

    def __init__(self, center_pos, image, groups, name, quest_data):
        super().__init__(center_pos, image, groups, name)
        self.quest_data = quest_data
        self.is_completed = False
        self.type = "quest"

    def interact(self, level) -> None:
        """Buka dialog quest"""

        print(
            f"[Quest] {self.name} memberikan quest: {self.quest_data.get('title', 'Unknown')}"
        )
