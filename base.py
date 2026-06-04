from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from settings import *

import pygame

if TYPE_CHECKING:
    from level import Level


class Updatable(ABC):

    @abstractmethod
    def update(self, dt: float) -> None: ...


class Drawable(ABC):

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None: ...


class EventHandler(ABC):

    @abstractmethod
    def handle_event(self, event: pygame.Event) -> bool:
        ...


class BaseManager(Updatable, ABC):
    def __init__(self, level: "Level") -> None:
        self._level = level

    @property
    def display_surface(self) -> pygame.Surface:
        return self._level.display_surface

    @property
    def player(self):
        return self._level.player

    def setup(self) -> None:
        """Override untuk setup satu-kali setelah konstruksi."""


class BaseUIPanel(Drawable, EventHandler, ABC):
    def __init__(self, level: "Level") -> None:
        self._level = level
        self._open = False

    @property
    def is_open(self) -> bool:
        return self._open

    @abstractmethod
    def open(self, *args, **kwargs) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @property
    def _font_big(self):
        return self._level.clock_ui.font_big

    @property
    def _font_small(self):
        return self._level.clock_ui.font_small

    def _make_panel_surface(
        self,
        w: int,
        h: int,
        fill=(244, 214, 143, 246),
        border=(119, 74, 34),
        inner=(255, 239, 177),
    ) -> pygame.Surface:
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill(fill)
        pygame.draw.rect(surf, border, surf.get_rect(), 4, border_radius=14)
        pygame.draw.rect(
            surf, inner, pygame.Rect(9, 9, w - 18, h - 18), 2, border_radius=10
        )
        return surf

    def _draw_shadow(
        self, surface: pygame.Surface, x: int, y: int, w: int, h: int
    ) -> None:
        shadow = pygame.Surface((w, h), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 110))
        surface.blit(shadow, (x + 5, y + 7))


class BaseWorldBuilder(ABC):

    def __init__(self, level: "Level") -> None:
        self._level = level

    @abstractmethod
    def build(self) -> None:
        ...

    @property
    def _all_sprites(self):
        return self._level.all_sprites

    @property
    def _collision_sprites(self):
        return self._level.collision_sprites

    @property
    def _grid(self):
        return self._level.grid

    @property
    def _season_mode(self) -> str:
        return self._level.season_mode

    def _season_surface(self, normal, snow, autumn):
        mode = self._season_mode
        if mode == "snow":
            return snow
        if mode == "autumn":
            return autumn
        return normal


class BaseNPC(pygame.sprite.Sprite, ABC):
    def __init__(self, center_pos, image, groups, name):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(center=center_pos)
        self.z = LAYERS["player"]
        self.name = name
        self.hitbox = self.rect.inflate(-16, -12)
        self.hitbox.height = max(14, self.hitbox.height // 2)
        self.hitbox.bottom = self.rect.bottom
        self.interact_rect = self.rect.inflate(76, 60)

    @abstractmethod
    def interact(self, level) -> None:
        pass

    def update(self, dt):
        pass


class BaseWeatherEffect(ABC):

    def __init__(self):
        self.active = False
        self.display_surface = pygame.display.get_surface()

    @abstractmethod
    def draw(self, dt: float) -> None:
        """Draw efek cuaca ke display surface"""
        pass

    def update(self, dt: float) -> None:
        if self.active:
            self.draw(dt)

    def set_active(self, active: bool) -> None:
        self.active = active

    def draw_darkness(self, alpha: int) -> None:
        pass
