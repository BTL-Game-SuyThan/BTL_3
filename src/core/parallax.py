from __future__ import annotations

from dataclasses import dataclass

import math

import pygame


@dataclass(slots=True)
class ParallaxLayer:
    image: pygame.Surface
    speed_multiplier: float
    y: int = 0
    offset_x: float = 0.0

    def update(self, dt: float, world_speed: float) -> None:
        self.offset_x = (self.offset_x + world_speed * self.speed_multiplier * dt) % self.image.get_width()

    def draw(self, surface: pygame.Surface) -> None:
        width = self.image.get_width()
        first_x = -math.floor(self.offset_x)
        second_x = first_x + width
        surface.blit(self.image, (first_x, self.y))
        surface.blit(self.image, (second_x, self.y))

