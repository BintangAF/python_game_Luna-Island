from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assets"
FRAME_DIR = ASSET_DIR / "video_frames"

WINDOW_TITLE = "Monster Island - UNESA Menu"
WIDTH = 1280
HEIGHT = 720
FPS = 60
VIDEO_FRAME_FPS = 12

START_BUTTON_POS = (WIDTH // 2, 505)
EXIT_BUTTON_POS = (WIDTH // 2, 615)
PVZ_BUTTON_POS = (WIDTH // 2, HEIGHT // 2 + 50)
LOGO_POS = (WIDTH - 120, HEIGHT - 100)
LOGO_MAX_WIDTH = 140
LOGO_MAX_HEIGHT = 140

MENU_MUSIC_PATH = ASSET_DIR / "menu_music.mp3"
LOGO_PATH = ASSET_DIR / "unesa_logo.png"
REFERENCE_FRAME_PATH = ASSET_DIR / "reference_frame.png"



START_VIDEO_FRAME_DIR = ASSET_DIR / "start_video_frames"
START_VIDEO_AUDIO_PATH = ASSET_DIR / "playgame_audio.mp3"
START_VIDEO_FPS = 24
