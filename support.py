import os
import pygame


def import_folder(path):
  
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
   
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, *parts)


def load_single(path, scale_to=None):
    if not os.path.exists(path):
        return None
    try:
        surf = pygame.image.load(path).convert_alpha()
    except Exception:
        return None
    if scale_to:
        surf = pygame.transform.scale(surf, scale_to)
    return surf


def load_tile_variants(tile_dir, prefix, ids, scale_to=None):
    surfs = []
    for i in ids:
        surf = load_single(os.path.join(tile_dir, f'{prefix}_{i:02d}.png'), scale_to)
        if surf:
            surfs.append(surf)
    return surfs


def load_folder_scaled(path, fixed_size=None, min_size=24):
    surfs = []
    if not os.path.isdir(path):
        return surfs
    for fname in sorted(os.listdir(path)):
        if not fname.lower().endswith('.png'):
            continue
        surf = load_single(os.path.join(path, fname))
        if not surf:
            continue
        if fixed_size:
            surf = pygame.transform.scale(surf, fixed_size)
        else:
            w, h = surf.get_size()
            scale = max(1, min_size // max(1, max(w, h)))
            surf = pygame.transform.scale(surf, (max(min_size, w * scale), max(min_size, h * scale)))
        surfs.append(surf)
    return surfs

