from base import *
from settings import *
import pygame


class QuestNPC(BaseNPC):

    def __init__(self, center_pos, image, groups, name):
        super().__init__(center_pos, image, groups, name)
        self.type = "quest"
        self.dialog_index = 0
        self.showing_quest = False
        self.quest_completed = False

        self.quest_name = "Selamat Datang di Monster Island"
        self.quest_description = "Bicaralah dengan Pedagang Biji Tanaman"
        self.quest_requirement = 1
        self.quest_progress = 0
        self.quest_reward = {"money": 50, "items": {"Biji Wortel": 2}}
        
    def move():
        pass

    def interact(self, level) -> None:
        """Interaksi dengan NPC Quest"""
        if self.quest_completed:
            level.show_temporary_message(
                f"{self.name}: Selamat! Kamu sudah menyelesaikan quest!",
                (100, 255, 100),
                3.0,
            )
            return

        if self._check_quest_completion(level):
            self._complete_quest(level)
        else:

            self.showing_quest = True
            self.dialog_index = 0
            level._freeze_player()

    def _check_quest_completion(self, level) -> bool:
        """Cek apakah quest sudah selesai"""

        return self.quest_progress >= self.quest_requirement

    def _complete_quest(self, level):
        """Selesaikan quest dan beri reward"""
        self.quest_completed = True

        level.money += self.quest_reward["money"]
        for item_name, amount in self.quest_reward["items"].items():
            level.inventory[item_name] = level.inventory.get(item_name, 0) + amount

        level.show_temporary_message(
            f"Quest selesai! Reward: {self.quest_reward['money']} koin",
            (100, 255, 100),
            3.0,
        )

    def update_progress(self, level):
        """Update progress quest (dipanggil saat player melakukan aksi)"""
        if self.quest_completed:
            return

        if level.has_talked_to_farmer:
            self.quest_progress = 1

    def update(self, dt: float) -> None:
        """Update - dipanggil oleh pygame"""
        pass

    def handle_event(self, event: pygame.event.Event, level) -> bool:
        """Handle event untuk dialog quest"""
        if not self.showing_quest:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self._next_dialog(level)
                return True
            elif event.key == pygame.K_q:
                self._close_dialog(level)
                return True

        return False

    def _next_dialog(self, level):
        """Pindah ke dialog berikutnya"""
        dialogs = [
            f"{self.name}: Halo petani baru! Selamat datang di Monster Island!",
            f"{self.name}: Aku akan membantumu belajar bertani.",
            f"{self.name}: Pertama, temui Pedagang Biji Tanaman di sebelah timur!",
            "Tekan SPACE untuk lanjut, ESC untuk tutup",
        ]

        if self.dialog_index < len(dialogs) - 1:
            self.dialog_index += 1
        else:
            self._close_dialog(level)

    def _close_dialog(self, level):
        """Tutup dialog quest"""
        self.showing_quest = False
        self.dialog_index = 0
        level._restore_player_controls()

    def draw(self, surface: pygame.Surface, level) -> None:
        """Draw dialog quest di layar"""
        if not self.showing_quest:
            return

        dialogs = [
            f"{self.name}: Halo! Selamat datang di Monster Island!",
            f"{self.name}: Aku akan membantumu belajar bertani.",
            f"{self.name}: Pertama, temui Pedagang Biji Tanaman di sebelah timur!",
            "Tekan SPACE untuk lanjut, Q untuk tutup",
        ]
        current_dialog = dialogs[min(self.dialog_index, len(dialogs) - 1)]

        w = 600
        h = 150
        x = (SCREEN_WIDTH - w) // 2
        y = SCREEN_HEIGHT - h - 50

        shadow = pygame.Surface((w, h), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 110))
        surface.blit(shadow, (x + 5, y + 7))

        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((244, 214, 143, 246))
        pygame.draw.rect(panel, (119, 74, 34), panel.get_rect(), 4, border_radius=14)
        pygame.draw.rect(
            panel,
            (255, 239, 177),
            pygame.Rect(9, 9, w - 18, h - 18),
            2,
            border_radius=10,
        )

        font = level.clock_ui.font_small

        name_text = level.clock_ui.font_big.render(f"{self.name}", True, (68, 39, 19))
        panel.blit(name_text, (20, 15))

        dialog_text = font.render(current_dialog, True, (56, 34, 18))
        panel.blit(dialog_text, (20, 60))

        hint_text = font.render(
            "SPACE/ENTER : Next  |  Q : Tutup", True, (78, 48, 23)
        )
        panel.blit(hint_text, (w - hint_text.get_width() - 20, h - 30))

        surface.blit(panel, (x, y))
