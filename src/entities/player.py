from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import pygame

from .animation import SpriteAnimation


class PlayerState(str, Enum):
    IDLE = "idle"
    FLAP = "flap"
    FALL = "fall"
    DEAD = "dead"


@dataclass(slots=True)
class PlayerConfig:
    width: int = 56
    height: int = 40
    gravity: float = 1700.0
    flap_velocity: float = -520.0
    glide_window: float = 0.18
    glide_gravity_scale: float = 0.55
    terminal_fall_speed: float = 660.0
    rise_animation_time: float = 0.16
    hitbox_scale: float = 0.78


def _make_surface(size: tuple[int, int], base_color: tuple[int, int, int], accent: tuple[int, int, int]) -> pygame.Surface:
    surface = pygame.Surface(size, pygame.SRCALPHA)
    rect = surface.get_rect()
    pygame.draw.ellipse(surface, base_color, rect.inflate(-4, -4))
    beak = pygame.Rect(rect.right - rect.width // 4, rect.centery - 4, rect.width // 4, 8)
    pygame.draw.rect(surface, accent, beak, border_radius=4)
    pygame.draw.circle(surface, (18, 18, 18), (rect.centerx + 10, rect.centery - 5), 3)
    pygame.draw.circle(surface, (245, 245, 245), (rect.centerx + 10, rect.centery - 5), 1)
    return surface


def make_player_frames(config: PlayerConfig | None = None) -> tuple[list[pygame.Surface], list[pygame.Surface]]:
    config = config or PlayerConfig()
    idle_frames = [
        _make_surface((config.width, config.height), (245, 198, 66), (250, 143, 36)),
        _make_surface((config.width, config.height), (248, 214, 92), (250, 143, 36)),
        _make_surface((config.width, config.height), (238, 186, 58), (250, 143, 36)),
    ]
    flap_frames = [
        _make_surface((config.width, config.height), (242, 160, 58), (242, 107, 42)),
        _make_surface((config.width, config.height), (255, 179, 71), (242, 107, 42)),
        _make_surface((config.width, config.height), (242, 160, 58), (242, 107, 42)),
    ]
    return idle_frames, flap_frames


class Player:
    def __init__(
        self,
        position: tuple[float, float],
        config: PlayerConfig | None = None,
        idle_frames: list[pygame.Surface] | None = None,
        flap_frames: list[pygame.Surface] | None = None,
    ) -> None:
        self.config = config or PlayerConfig()
        default_idle, default_flap = make_player_frames(self.config)
        self.idle_animation = SpriteAnimation(idle_frames or default_idle, fps=7.0, loop=True)
        self.flap_animation = SpriteAnimation(flap_frames or default_flap, fps=11.0, loop=True)
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(0.0, 0.0)
        self.state = PlayerState.IDLE
        self.alive = True
        self._glide_input = False
        self._glide_timer = 0.0
        self._rise_timer = 0.0
        self.rect = self.current_frame.get_rect(center=(round(self.position.x), round(self.position.y)))
        self.hitbox = self.rect.inflate(
            -int(self.rect.width * (1.0 - self.config.hitbox_scale)),
            -int(self.rect.height * (1.0 - self.config.hitbox_scale)),
        )

    @property
    def current_frame(self) -> pygame.Surface:
        if self.state in {PlayerState.FLAP, PlayerState.IDLE} and self._rise_timer > 0:
            return self.flap_animation.current_frame
        if self.velocity.y > 80:
            return self.idle_animation.current_frame
        if self._glide_input and self._glide_timer > 0:
            return self.flap_animation.current_frame
        return self.idle_animation.current_frame

    def set_glide_input(self, is_held: bool) -> None:
        self._glide_input = is_held

    def flap(self) -> None:
        if not self.alive:
            return
        self.velocity.y = self.config.flap_velocity
        self._glide_timer = self.config.glide_window
        self._rise_timer = self.config.rise_animation_time
        self.state = PlayerState.FLAP
        self.flap_animation.reset()

    def kill(self) -> None:
        self.alive = False
        self.state = PlayerState.DEAD

    def reset(self, position: tuple[float, float]) -> None:
        self.position.update(position)
        self.velocity.update(0.0, 0.0)
        self.state = PlayerState.IDLE
        self.alive = True
        self._glide_input = False
        self._glide_timer = 0.0
        self._rise_timer = 0.0
        self.idle_animation.reset()
        self.flap_animation.reset()
        self._sync_rects()

    def update(self, dt: float, world_speed: float = 0.0) -> None:
        if not self.alive:
            self._sync_rects()
            return

        if self._glide_timer > 0:
            self._glide_timer = max(0.0, self._glide_timer - dt)
        if self._rise_timer > 0:
            self._rise_timer = max(0.0, self._rise_timer - dt)

        gravity_scale = self.config.glide_gravity_scale if self._glide_input and self._glide_timer > 0 else 1.0
        self.velocity.y += self.config.gravity * gravity_scale * dt
        if self.velocity.y > self.config.terminal_fall_speed:
            self.velocity.y = self.config.terminal_fall_speed

        self.position.y += self.velocity.y * dt
        self.position.x += 0.0

        if self._rise_timer > 0:
            self.state = PlayerState.FLAP
            self.flap_animation.update(dt)
        elif self.velocity.y > 100.0:
            self.state = PlayerState.FALL
            self.idle_animation.update(dt)
        else:
            self.state = PlayerState.IDLE
            self.idle_animation.update(dt)

        self._sync_rects()

    def _sync_rects(self) -> None:
        frame = self.current_frame
        self.rect = frame.get_rect(center=(round(self.position.x), round(self.position.y)))
        hitbox = self.rect.inflate(
            -int(self.rect.width * (1.0 - self.config.hitbox_scale)),
            -int(self.rect.height * (1.0 - self.config.hitbox_scale)),
        )
        self.hitbox = hitbox

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.current_frame, self.rect)

