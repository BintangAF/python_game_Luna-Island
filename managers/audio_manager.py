import pygame

from config import MENU_MUSIC_PATH, START_VIDEO_AUDIO_PATH


class AudioManager:
    def __init__(self):
        self.available = False
        self.current_track = None
        try:
            pygame.mixer.init()
            self.available = True
        except pygame.error:
            self.available = False

    def play_menu_music(self):
       
        if not self.available or not MENU_MUSIC_PATH.exists():
            return
        if self.current_track == str(MENU_MUSIC_PATH):
            return
        try:
            pygame.mixer.music.load(str(MENU_MUSIC_PATH))
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
            self.current_track = str(MENU_MUSIC_PATH)
        except pygame.error:
            pass

    def play_start_video_audio(self):
        if not self.available:
            return

        self.stop_music()

        if not START_VIDEO_AUDIO_PATH.exists():
            return

        try:
            pygame.mixer.music.load(str(START_VIDEO_AUDIO_PATH))
            pygame.mixer.music.set_volume(0.8)
            pygame.mixer.music.play(0)
            self.current_track = str(START_VIDEO_AUDIO_PATH)
        except pygame.error:
            pass

    def stop_music(self):
       
        if not self.available:
            return
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
        self.current_track = None
