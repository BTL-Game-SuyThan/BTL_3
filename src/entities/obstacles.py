from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

import pygame


class ObstacleKind(str, Enum):
    PIPE = "pipe"
    DYNAMIC_PIPE = "dynamic_pipe"
    GRAVITY_PIPE = "gravity_pipe"


@dataclass(slots=True)
class ObstacleConfig:
    pipe_width: int = 92
    dynamic_pipe_width: int = 92
    gravity_pipe_width: int = 92
    moving_pillar_amplitude: float = 44.0
    moving_pillar_frequency: float = 1.15


class Obstacle:
    def __init__(
        self,
        kind: ObstacleKind,
        x: float,
        screen_height: int,
        gap_center_y: float,
        gap_size: float,
        scroll_speed: float,
        width: int,
        pipe_img: pygame.Surface,
        config: ObstacleConfig | None = None,
        moving: bool = False,
        motion_amplitude: float = 0.0,
        motion_frequency: float = 0.0,
    ) -> None:
        self.kind = kind
        self.x = float(x)
        self.scroll_speed = float(scroll_speed)
        self.width = width
        self.screen_height = screen_height
        self.gap_center_y = float(gap_center_y)
        self.gap_size = float(gap_size)
        self.moving = moving
        self.motion_amplitude = motion_amplitude
        self.motion_frequency = motion_frequency
        self.base_gap_center_y = float(gap_center_y)
        self.elapsed = 0.0
        self.alive = True
        self.passed_player = False
        self.config = config or ObstacleConfig()

        # Prepare scaled images
        scale_factor = self.width / pipe_img.get_width()
        scaled_w = self.width
        scaled_h = int(pipe_img.get_height() * scale_factor)
        self.bottom_source = pygame.transform.smoothscale(
            pipe_img, (scaled_w, scaled_h)
        )
        self.top_source = pygame.transform.rotate(self.bottom_source, 180)

        self._build_rects()

    def _build_rects(self) -> None:
        gap_top = self.gap_center_y - self.gap_size / 2
        gap_bottom = self.gap_center_y + self.gap_size / 2
        self.top_rect = pygame.Rect(int(self.x), 0, self.width, max(0, int(gap_top)))
        self.bottom_rect = pygame.Rect(
            int(self.x),
            int(gap_bottom),
            self.width,
            max(0, int(self.screen_height - gap_bottom)),
        )

    @property
    def collision_rects(self) -> list[pygame.Rect]:
        rects = []
        if self.top_rect.height > 0:
            rects.append(self.top_rect)
        if self.bottom_rect.height > 0:
            rects.append(self.bottom_rect)
        return rects

    def update(self, dt: float, world_speed: float) -> None:
        if not self.alive:
            return
        self.elapsed += dt
        self.x -= world_speed * dt
        if self.moving:
            offset = (
                math.sin(self.elapsed * self.motion_frequency * math.tau)
                * self.motion_amplitude
            )
            self.gap_center_y = self.base_gap_center_y + offset

        self._build_rects()
        if self.x + self.width < -50:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return

        # Draw Top Pipe
        if self.top_rect.height > 0:
            # Head is at the bottom of top_source.
            # We need the bottom 'height' pixels of top_source.
            h = self.top_rect.height
            src_h = self.top_source.get_height()
            crop_h = min(h, src_h)
            area = pygame.Rect(0, src_h - crop_h, self.width, crop_h)
            # If obstacle is taller than source, it might look cut off at the top,
            # but per requirements we just crop.
            dest_y = self.top_rect.bottom - crop_h
            surface.blit(self.top_source, (self.top_rect.x, dest_y), area)

        # Draw Bottom Pipe
        if self.bottom_rect.height > 0:
            # Head is at the top of bottom_source.
            # We need the top 'height' pixels of bottom_source.
            h = self.bottom_rect.height
            src_h = self.bottom_source.get_height()
            crop_h = min(h, src_h)
            area = pygame.Rect(0, 0, self.width, crop_h)
            surface.blit(self.bottom_source, (self.bottom_rect.x, self.bottom_rect.y), area)
