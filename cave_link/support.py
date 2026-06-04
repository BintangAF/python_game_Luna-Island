import os
import pygame


def get_path(*parts):
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, *parts)


def import_folder(path):
    frames = []
    if not os.path.isdir(path):
        return frames
    for fname in sorted(os.listdir(path)):
        if fname.lower().endswith('.png'):
            try:
                frames.append(pygame.image.load(os.path.join(path, fname)).convert_alpha())
            except Exception:
                pass
    return frames


def load_single(path, scale_to=None):
    if not os.path.exists(path):
        return None
    surf = pygame.image.load(path).convert_alpha()
    if scale_to:
        surf = pygame.transform.scale(surf, scale_to)
    return surf


def crop_alpha_surface(surface, padding=2):
    rect = surface.get_bounding_rect(min_alpha=1)
    if rect.width <= 0 or rect.height <= 0:
        return surface
    rect.inflate_ip(padding * 2, padding * 2)
    rect.clamp_ip(surface.get_rect())
    cropped = pygame.Surface(rect.size, pygame.SRCALPHA)
    cropped.blit(surface, (0, 0), rect)
    return cropped


def draw_panel(surface, rect, fill=(246, 218, 142, 240), border=(124, 82, 38), inner=(255, 239, 191)):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel.fill(fill)
    pygame.draw.rect(panel, border, panel.get_rect(), 4, border_radius=10)
    pygame.draw.rect(panel, inner, pygame.Rect(5, 5, rect.width - 10, rect.height - 10), 2, border_radius=8)
    surface.blit(panel, rect.topleft)
