from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

import pygame

from .animation import SpriteAnimation


@dataclass(slots=True)
class CollectibleConfig:
    size: int = 26
    points: int = 1
    bob_amplitude: float = 8.0
    bob_frequency: float = 2.1


class CollectibleKind(str, Enum):
    COIN = "coin"
    SHIELD = "shield"


@dataclass(slots=True)
class CollectResult:
    score: int = 0
    granted_shield: bool = False


def _frame(size: int, fill: tuple[int, int, int], accent: tuple[int, int, int], ring: tuple[int, int, int]) -> pygame.Surface:
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    rect = surface.get_rect()
    pygame.draw.circle(surface, ring, rect.center, size // 2 - 1)
    pygame.draw.circle(surface, fill, rect.center, size // 2 - 4)
    pygame.draw.circle(surface, accent, (rect.centerx - 3, rect.centery - 3), size // 5)
    pygame.draw.circle(surface, (255, 255, 255), (rect.centerx + 4, rect.centery - 5), 2)
    return surface


def make_collectible_frames(config: CollectibleConfig | None = None) -> list[pygame.Surface]:
    config = config or CollectibleConfig()
    return [
        _frame(config.size, (246, 205, 55), (255, 236, 140), (182, 139, 18)),
        _frame(config.size, (255, 227, 101), (255, 248, 184), (182, 139, 18)),
        _frame(config.size, (250, 183, 45), (255, 217, 93), (182, 139, 18)),
        _frame(config.size, (255, 227, 101), (255, 248, 184), (182, 139, 18)),
    ]


class Collectible:
    def __init__(
        self,
        position: tuple[float, float],
        speed: float,
        frames: list[pygame.Surface] | None = None,
        config: CollectibleConfig | None = None,
        kind: CollectibleKind = CollectibleKind.COIN,
    ) -> None:
        self.config = config or CollectibleConfig()
        self.kind = kind
        self.animation = SpriteAnimation(frames or make_collectible_frames(self.config), fps=10.0, loop=True)
        self.position = pygame.Vector2(position)
        self.base_y = float(position[1])
        self.speed = speed
        self.alive = True
        self.collected = False
        self.elapsed = 0.0
        self.rect = self.animation.current_frame.get_rect(center=(round(self.position.x), round(self.position.y)))

    @property
    def current_frame(self) -> pygame.Surface:
        return self.animation.current_frame

    def collect(self) -> CollectResult:
        if self.collected:
            return CollectResult()
        self.collected = True
        self.alive = False
        if self.kind == CollectibleKind.SHIELD:
            return CollectResult(score=0, granted_shield=True)
        return CollectResult(score=self.config.points, granted_shield=False)

    def update(self, dt: float, world_speed: float) -> None:
        if not self.alive:
            self._sync_rect()
            return
        self.elapsed += dt
        self.position.x -= world_speed * dt
        self.position.y = self.base_y + self.config.bob_amplitude * math.sin(self.elapsed * self.config.bob_frequency * math.tau)
        self.animation.update(dt)
        self._sync_rect()

    def _sync_rect(self) -> None:
        self.rect = self.current_frame.get_rect(center=(round(self.position.x), round(self.position.y)))

    def draw(self, surface: pygame.Surface) -> None:
        if self.alive:
            surface.blit(self.current_frame, self.rect)
