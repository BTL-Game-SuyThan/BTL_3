from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

import pygame


class ObstacleKind(str, Enum):
    PIPE = "pipe"
    DYNAMIC_PIPE = "dynamic_pipe"
    GRAVITY_PIPE = "gravity_pipe"
    WINDMILL = "windmill"


@dataclass(slots=True)
class ObstacleConfig:
    pipe_width: int = 92
    dynamic_pipe_width: int = 92
    gravity_pipe_width: int = 92
    moving_pillar_amplitude: float = 44.0
    moving_pillar_frequency: float = 1.15
    windmill_width: int = 130
    windmill_house_height: int = 186
    windmill_rotor_size: int = 162
    windmill_rotor_radius: float = 52.0
    windmill_spin_speed: float = 110.0


def _default_pipe_surface(width: int = 96, height: int = 620) -> pygame.Surface:
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surface, (78, 176, 88), (0, 0, width, height), border_radius=10)
    pygame.draw.rect(surface, (46, 120, 58), (0, 0, width, 14), border_radius=8)
    pygame.draw.rect(surface, (110, 210, 120), (6, 14, 10, height - 20), border_radius=4)
    return surface


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
        pipe_img: pygame.Surface | None = None,
        config: ObstacleConfig | None = None,
        moving: bool = False,
        motion_amplitude: float = 0.0,
        motion_frequency: float = 0.0,
        windmill_house_img: pygame.Surface | None = None,
        windmill_rotor_img: pygame.Surface | None = None,
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
        self.rotation = 0.0
        self._collision_rects: list[pygame.Rect] = []
        self._house_img: pygame.Surface | None = None
        self._rotor_img: pygame.Surface | None = None
        self._house_rect = pygame.Rect(0, 0, 0, 0)
        self._rotor_center = pygame.Vector2(0.0, 0.0)
        self._windmill_kill_margin = 30.0

        if self.kind == ObstacleKind.WINDMILL:
            self._init_windmill_images(windmill_house_img, windmill_rotor_img)
        else:
            if pipe_img is None:
                pipe_img = _default_pipe_surface(self.width)
            scale_factor = self.width / pipe_img.get_width()
            scaled_w = self.width
            scaled_h = int(pipe_img.get_height() * scale_factor)
            self.bottom_source = pygame.transform.smoothscale(
                pipe_img, (scaled_w, scaled_h)
            )
            self.top_source = pygame.transform.rotate(self.bottom_source, 180)

        self._build_rects()

    def _init_windmill_images(
        self,
        windmill_house_img: pygame.Surface | None,
        windmill_rotor_img: pygame.Surface | None,
    ) -> None:
        house_target_h = self.config.windmill_house_height
        if windmill_house_img is not None:
            house_scale = house_target_h / max(1, windmill_house_img.get_height())
            house_size = (
                max(1, int(windmill_house_img.get_width() * house_scale)),
                house_target_h,
            )
            self._house_img = pygame.transform.smoothscale(windmill_house_img, house_size)
        else:
            self._house_img = pygame.Surface((self.config.windmill_width, house_target_h), pygame.SRCALPHA)
            pygame.draw.rect(self._house_img, (122, 96, 70), self._house_img.get_rect(), border_radius=10)

        rotor_target = self.config.windmill_rotor_size
        if windmill_rotor_img is not None:
            self._rotor_img = pygame.transform.smoothscale(
                windmill_rotor_img, (rotor_target, rotor_target)
            )
        else:
            self._rotor_img = pygame.Surface((rotor_target, rotor_target), pygame.SRCALPHA)
            center = pygame.Vector2(rotor_target / 2, rotor_target / 2)
            for angle in (0, 90, 180, 270):
                tip = center + pygame.Vector2(1, 0).rotate(angle) * (rotor_target * 0.45)
                left = center + pygame.Vector2(1, 0).rotate(angle + 15) * (rotor_target * 0.2)
                right = center + pygame.Vector2(1, 0).rotate(angle - 15) * (rotor_target * 0.2)
                pygame.draw.polygon(self._rotor_img, (224, 224, 224), [tip, left, center, right])
            pygame.draw.circle(self._rotor_img, (116, 116, 116), center, max(4, rotor_target // 16))

    def _build_rects(self) -> None:
        if self.kind == ObstacleKind.WINDMILL:
            self._build_windmill_rects()
            return

        gap_top = self.gap_center_y - self.gap_size / 2
        gap_bottom = self.gap_center_y + self.gap_size / 2
        self.top_rect = pygame.Rect(int(self.x), 0, self.width, max(0, int(gap_top)))
        self.bottom_rect = pygame.Rect(
            int(self.x),
            int(gap_bottom),
            self.width,
            max(0, int(self.screen_height - gap_bottom)),
        )

    def _build_windmill_rects(self) -> None:
        house_w = 0 if self._house_img is None else self._house_img.get_width()
        house_h = 0 if self._house_img is None else self._house_img.get_height()
        house_x = int(self.x)
        house_y = self.screen_height - house_h
        self._house_rect = pygame.Rect(house_x, house_y, house_w, house_h)
        self._rotor_center.update(house_x + house_w * 0.5, self.gap_center_y)
        rotor_collision_radius = int(self.config.windmill_rotor_radius)
        self._collision_rects = [
            pygame.Rect(
                int(self._rotor_center.x - rotor_collision_radius),
                int(self._rotor_center.y - rotor_collision_radius),
                rotor_collision_radius * 2,
                rotor_collision_radius * 2,
            )
        ]
        if house_h > 0:
            self._collision_rects.append(
                pygame.Rect(
                    self._house_rect.left + int(self._house_rect.width * 0.2),
                    self._house_rect.top + int(self._house_rect.height * 0.35),
                    int(self._house_rect.width * 0.6),
                    int(self._house_rect.height * 0.65),
                )
            )

    @property
    def collision_rects(self) -> list[pygame.Rect]:
        if self.kind == ObstacleKind.WINDMILL:
            return list(self._collision_rects)
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
        if self.kind == ObstacleKind.WINDMILL:
            self.rotation = (self.rotation + self.config.windmill_spin_speed * dt) % 360.0

        self._build_rects()
        kill_width = self.width if self.kind != ObstacleKind.WINDMILL else (
            0 if self._house_img is None else self._house_img.get_width()
        )
        if self.x + kill_width < -self._windmill_kill_margin:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return
        if self.kind == ObstacleKind.WINDMILL:
            self._draw_windmill(surface)
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

    def _draw_windmill(self, surface: pygame.Surface) -> None:
        if self._house_img is not None:
            surface.blit(self._house_img, self._house_rect)
        if self._rotor_img is None:
            return
        rotated = pygame.transform.rotozoom(self._rotor_img, -self.rotation, 1.0)
        rotor_rect = rotated.get_rect(
            center=(round(self._rotor_center.x), round(self._rotor_center.y))
        )
        surface.blit(rotated, rotor_rect)
