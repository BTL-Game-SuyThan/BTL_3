from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

from src.entities.collectibles import (
    Collectible,
    CollectibleConfig,
    CollectibleKind,
    make_collectible_frames,
)
from src.entities.obstacles import Obstacle, ObstacleConfig, ObstacleKind
from src.systems.config import GameConfig
from src.systems.difficulty import DifficultyState


@dataclass(slots=True)
class SpawnResult:
    obstacle: Obstacle
    collectibles: list[Collectible]


def choose_obstacle_kind(
    state: DifficultyState,
    rng: random.Random,
    *,
    windmill_enabled: bool,
    windmill_weight: float,
) -> ObstacleKind:
    choices: list[tuple[ObstacleKind, float]] = [
        (ObstacleKind.PIPE, state.pipe_weight),
        (ObstacleKind.DYNAMIC_PIPE, state.dynamic_pipe_weight),
        (ObstacleKind.GRAVITY_PIPE, state.gravity_pipe_weight),
    ]
    if windmill_enabled and windmill_weight > 0:
        choices.append((ObstacleKind.WINDMILL, windmill_weight))
    total = sum(weight for _, weight in choices)
    if total <= 0:
        return ObstacleKind.PIPE

    roll = rng.random() * total
    acc = 0.0
    for kind, weight in choices:
        acc += weight
        if roll <= acc:
            return kind
    return choices[-1][0]


def _make_shield_frames(shield_img: pygame.Surface | None, size: int) -> list[pygame.Surface]:
    if shield_img is None:
        frame = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(frame, (92, 182, 255), (size // 2, size // 2), max(2, size // 2 - 2), 2)
        pygame.draw.circle(frame, (158, 219, 255), (size // 2, size // 2), max(2, size // 2 - 6), 2)
        return [frame]
    scaled = pygame.transform.smoothscale(shield_img, (size, size))
    return [scaled]


class Spawner:
    def __init__(
        self,
        config: GameConfig | None = None,
        collectible_frames: list[pygame.Surface] | None = None,
        assets=None,
    ) -> None:
        self.config = config or GameConfig()
        self.cooldown = self.config.spawn_interval
        self.assets = assets
        self.collectible_frames = collectible_frames or make_collectible_frames(
            CollectibleConfig(points=self.config.collectible_points)
        )
        self.shield_frames = _make_shield_frames(
            self.assets.shield_img if self.assets else None,
            int(self.config.pipe_width * 0.42),
        )
        self.pipe_spawn_count = 0

    def reset(self) -> None:
        self.cooldown = self.config.spawn_interval
        self.pipe_spawn_count = 0

    def update(
        self,
        dt: float,
        state: DifficultyState,
        rng: random.Random,
        screen_rect: pygame.Rect,
        obstacles_passed: int,
        gravity_direction: float,
    ) -> list[SpawnResult]:
        self.cooldown -= dt
        results: list[SpawnResult] = []
        while self.cooldown <= 0:
            results.append(
                self.spawn_one(
                    state, rng, screen_rect, obstacles_passed, gravity_direction
                )
            )
            self.cooldown += state.spawn_interval
        return results

    def spawn_one(
        self,
        state: DifficultyState,
        rng: random.Random,
        screen_rect: pygame.Rect,
        obstacles_passed: int,
        gravity_direction: float,
    ) -> SpawnResult:
        windmill_enabled = (
            self.config.windmill_enabled
            and obstacles_passed >= self.config.windmill_unlock_obstacles
            and gravity_direction > 0.0
        )
        kind = choose_obstacle_kind(
            state,
            rng,
            windmill_enabled=windmill_enabled,
            windmill_weight=self.config.windmill_weight,
        )
        gap_size = rng.uniform(state.min_gap, state.max_gap)
        gap_center = rng.uniform(screen_rect.height * 0.24, screen_rect.height * 0.72)
        x = float(screen_rect.width + 10)

        # Default to green pipe if assets missing
        pipe_img = self.assets.pipe_img if self.assets else None
        
        # Build dynamic obstacle config based on current game config
        obs_config = ObstacleConfig(
            pipe_width=self.config.pipe_width,
            dynamic_pipe_width=self.config.dynamic_pipe_width,
            gravity_pipe_width=self.config.gravity_pipe_width,
            windmill_width=self.config.windmill_width,
            moving_pillar_amplitude=self.config.moving_pillar_amplitude,
            moving_pillar_frequency=self.config.moving_pillar_frequency,
            windmill_house_height=self.config.windmill_house_height,
            windmill_rotor_size=self.config.windmill_rotor_size,
            windmill_rotor_radius=self.config.windmill_rotor_radius,
            windmill_spin_speed=self.config.windmill_spin_speed,
        )

        if kind == ObstacleKind.DYNAMIC_PIPE:
            if self.assets and self.assets.dynamic_pipe_img:
                pipe_img = self.assets.dynamic_pipe_img
            obstacle = Obstacle(
                kind=kind,
                x=x,
                screen_height=screen_rect.height,
                gap_center_y=gap_center,
                gap_size=gap_size,
                scroll_speed=state.scroll_speed,
                width=self.config.dynamic_pipe_width,
                pipe_img=pipe_img,
                config=obs_config,
                moving=True,
                motion_amplitude=self.config.moving_pillar_amplitude,
                motion_frequency=self.config.moving_pillar_frequency,
            )
        elif kind == ObstacleKind.GRAVITY_PIPE:
            if self.assets and self.assets.gravity_pipe_img:
                pipe_img = self.assets.gravity_pipe_img
            obstacle = Obstacle(
                kind=kind,
                x=x,
                screen_height=screen_rect.height,
                gap_center_y=gap_center,
                gap_size=gap_size,
                scroll_speed=state.scroll_speed,
                width=self.config.gravity_pipe_width,
                pipe_img=pipe_img,
                config=obs_config,
            )
        elif kind == ObstacleKind.WINDMILL:
            obstacle = Obstacle(
                kind=kind,
                x=x,
                screen_height=screen_rect.height,
                gap_center_y=gap_center,
                gap_size=gap_size,
                scroll_speed=state.scroll_speed,
                width=self.config.windmill_width,
                config=obs_config,
                windmill_house_img=self.assets.windmill_house_img if self.assets else None,
                windmill_rotor_img=self.assets.windmill_rotor_img if self.assets else None,
            )
        else:  # ObstacleKind.PIPE
            obstacle = Obstacle(
                kind=kind,
                x=x,
                screen_height=screen_rect.height,
                gap_center_y=gap_center,
                gap_size=gap_size,
                scroll_speed=state.scroll_speed,
                width=self.config.pipe_width,
                pipe_img=pipe_img,
                config=obs_config,
            )

        collectible_y = gap_center + self.config.collectible_offset
        is_pipe_obstacle = kind in {
            ObstacleKind.PIPE,
            ObstacleKind.DYNAMIC_PIPE,
            ObstacleKind.GRAVITY_PIPE,
        }
        next_pipe_count = self.pipe_spawn_count + (1 if is_pipe_obstacle else 0)
        spawn_shield = (
            is_pipe_obstacle
            and self.config.shield_spawn_interval > 0
            and next_pipe_count % self.config.shield_spawn_interval == 0
        )
        # Place shield events in the horizontal lane BETWEEN two obstacle columns.
        # This avoids placing shield directly under/inside a pipe column.
        predicted_column_spacing = max(
            120.0, state.scroll_speed * state.spawn_interval - obstacle.width
        )
        lane_start_x = x + obstacle.width + 28.0
        lane_usable = max(80.0, predicted_column_spacing - 56.0)
        if spawn_shield:
            shield_x = lane_start_x + lane_usable * 0.50
            collectibles = [
                Collectible(
                    position=(x + obstacle.width * 0.5, collectible_y),
                    speed=state.scroll_speed,
                    frames=self.collectible_frames,
                    config=CollectibleConfig(points=self.config.collectible_points),
                    kind=CollectibleKind.COIN,
                ),
                Collectible(
                    position=(shield_x, collectible_y),
                    speed=state.scroll_speed,
                    frames=self.shield_frames,
                    config=CollectibleConfig(points=self.config.collectible_points),
                    kind=CollectibleKind.SHIELD,
                )
            ]
        else:
            collectibles = [
                Collectible(
                    position=(x + obstacle.width * 0.5, collectible_y),
                    speed=state.scroll_speed,
                    frames=self.collectible_frames,
                    config=CollectibleConfig(points=self.config.collectible_points),
                    kind=CollectibleKind.COIN,
                )
            ]
        if is_pipe_obstacle:
            self.pipe_spawn_count += 1
        return SpawnResult(obstacle=obstacle, collectibles=collectibles)
