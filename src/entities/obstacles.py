from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

import pygame

class ObstacleKind(str, Enum):
    PIPE = "pipe"
    PILLAR = "pillar"
    LASER = "laser"


@dataclass(slots=True)
class ObstacleConfig:
    pipe_width: int = 92
    pillar_width: int = 70
    laser_width: int = 88
    pipe_color: tuple[int, int, int] = (82, 165, 72)
    pipe_edge: tuple[int, int, int] = (44, 105, 42)
    pillar_color: tuple[int, int, int] = (102, 142, 216)
    pillar_edge: tuple[int, int, int] = (48, 73, 143)
    laser_color: tuple[int, int, int] = (240, 72, 72)
    laser_warning: tuple[int, int, int] = (255, 217, 102)
    laser_thickness: int = 16
    laser_warning_duration: float = 0.85
    laser_active_pulse: float = 1.0


def _solid_surface(size: tuple[int, int], fill: tuple[int, int, int], edge: tuple[int, int, int], tube: bool = False) -> pygame.Surface:
    surface = pygame.Surface(size, pygame.SRCALPHA)
    rect = surface.get_rect()
    pygame.draw.rect(surface, fill, rect, border_radius=10 if tube else 6)
    pygame.draw.rect(surface, edge, rect, width=4, border_radius=10 if tube else 6)
    band_y = rect.height // 4
    pygame.draw.rect(surface, (*edge, 160), pygame.Rect(4, band_y, rect.width - 8, 8), border_radius=4)
    pygame.draw.rect(surface, (*edge, 160), pygame.Rect(4, rect.height - band_y - 8, rect.width - 8, 8), border_radius=4)
    return surface


def make_pipe_frames(width: int = 92, height: int = 200) -> list[pygame.Surface]:
    return [_solid_surface((width, height), (82, 165, 72), (44, 105, 42), tube=True)]


def make_pillar_frames(width: int = 70, height: int = 220) -> list[pygame.Surface]:
    return [_solid_surface((width, height), (102, 142, 216), (48, 73, 143), tube=False)]


def make_laser_frames(width: int = 88, height: int = 170) -> list[pygame.Surface]:
    return [_solid_surface((width, height), (240, 72, 72), (135, 31, 31), tube=False)]


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
        top_surface: pygame.Surface | None = None,
        bottom_surface: pygame.Surface | None = None,
        config: ObstacleConfig | None = None,
        moving: bool = False,
        motion_amplitude: float = 0.0,
        motion_frequency: float = 0.0,
        laser_warning_duration: float | None = None,
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
        self.config = config or ObstacleConfig()
        self.top_surface = top_surface
        self.bottom_surface = bottom_surface
        self.warning_remaining = laser_warning_duration if laser_warning_duration is not None else self.config.laser_warning_duration
        self.laser_active = kind != ObstacleKind.LASER
        self.laser_pulse_elapsed = 0.0
        self._build_rects()

    def _build_rects(self) -> None:
        gap_top = self.gap_center_y - self.gap_size / 2
        gap_bottom = self.gap_center_y + self.gap_size / 2
        self.top_rect = pygame.Rect(int(self.x), 0, self.width, max(0, int(gap_top)))
        self.bottom_rect = pygame.Rect(int(self.x), int(gap_bottom), self.width, max(0, int(self.screen_height - gap_bottom)))
        self.laser_rect = pygame.Rect(int(self.x), int(self.gap_center_y - self.config.laser_thickness / 2), self.width, self.config.laser_thickness)
        self.laser_post_left = pygame.Rect(int(self.x), int(gap_top) - 8, 12, int(self.gap_size) + 16)
        self.laser_post_right = pygame.Rect(int(self.x + self.width - 12), int(gap_top) - 8, 12, int(self.gap_size) + 16)

    @property
    def collision_rects(self) -> list[pygame.Rect]:
        if self.kind == ObstacleKind.LASER:
            if self.laser_active:
                return [self.laser_rect]
            return []
        return [self.top_rect, self.bottom_rect]

    def update(self, dt: float, world_speed: float) -> None:
        if not self.alive:
            return
        self.elapsed += dt
        self.x -= world_speed * dt
        if self.kind == ObstacleKind.PILLAR and self.moving:
            offset = math.sin(self.elapsed * self.motion_frequency * math.tau) * self.motion_amplitude
            self.gap_center_y = self.base_gap_center_y + offset
        if self.kind == ObstacleKind.LASER:
            self.laser_pulse_elapsed += dt
            if self.warning_remaining > 0:
                self.warning_remaining = max(0.0, self.warning_remaining - dt)
                self.laser_active = self.warning_remaining <= 0
        self._build_rects()
        if self.x + self.width < -20:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return
        if self.kind == ObstacleKind.LASER:
            self._draw_laser(surface)
        else:
            self._draw_solid(surface)

    def _draw_solid(self, surface: pygame.Surface) -> None:
        if self.top_surface is None or self.bottom_surface is None:
            return
        top = pygame.transform.scale(self.top_surface, (self.width, max(1, self.top_rect.height)))
        bottom = pygame.transform.scale(self.bottom_surface, (self.width, max(1, self.bottom_rect.height)))
        surface.blit(top, self.top_rect)
        surface.blit(bottom, self.bottom_rect)

    def _draw_laser(self, surface: pygame.Surface) -> None:
        color = self.config.laser_color if self.laser_active else self.config.laser_warning
        pulse = 1.0 + 0.08 * math.sin(self.laser_pulse_elapsed * 9.0)
        beam = pygame.Surface((self.width, self.config.laser_thickness), pygame.SRCALPHA)
        pygame.draw.rect(beam, color, beam.get_rect(), border_radius=4)
        pygame.draw.rect(beam, (255, 255, 255, 80), beam.get_rect().inflate(-8, -6), width=2, border_radius=4)
        if self.laser_active:
            glow = pygame.transform.smoothscale(beam, (int(self.width * pulse), self.config.laser_thickness))
            glow_rect = glow.get_rect(center=self.laser_rect.center)
            surface.blit(glow, glow_rect)
        else:
            surface.blit(beam, self.laser_rect)
        if self.laser_active:
            surface.blit(beam, self.laser_rect)
        left_post = pygame.Surface((12, self.laser_post_left.height), pygame.SRCALPHA)
        right_post = pygame.Surface((12, self.laser_post_right.height), pygame.SRCALPHA)
        pygame.draw.rect(left_post, (112, 112, 124), left_post.get_rect(), border_radius=4)
        pygame.draw.rect(right_post, (112, 112, 124), right_post.get_rect(), border_radius=4)
        surface.blit(left_post, self.laser_post_left)
        surface.blit(right_post, self.laser_post_right)
