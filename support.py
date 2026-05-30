import os
import pygame


def import_folder(path):
    """Load all .png images in a folder, sorted by filename."""
    frames = []
    if not os.path.exists(path):
        return frames
    for fname in sorted(os.listdir(path)):
        if fname.lower().endswith('.png'):
            full = os.path.join(path, fname)
            try:
                surf = pygame.image.load(full).convert_alpha()
                frames.append(surf)
            except Exception:
                pass
    return frames


def get_path(*parts):
    """Return an absolute path relative to this file's directory."""
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, *parts)


def load_tile(rel_path, size=None):
    """Load a single tile image; optionally scale it."""
    path = get_path(rel_path)
    if not os.path.exists(path):
        return None
    surf = pygame.image.load(path).convert_alpha()
    if size:
        surf = pygame.transform.scale(surf, size)
    return surf
