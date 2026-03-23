from __future__ import annotations

from dataclasses import dataclass
import random

import pygame

from src.entities.collectibles import Collectible, CollectibleConfig, make_collectible_frames
from src.entities.obstacles import (
    Obstacle,
    ObstacleConfig,
    ObstacleKind,
    make_laser_frames,
    make_pipe_frames,
    make_pillar_frames,
)
from .config import GameConfig
from .difficulty import DifficultyState


@dataclass(slots=True)
class SpawnResult:
    obstacle: Obstacle
    collectible: Collectible | None


def choose_obstacle_kind(state: DifficultyState, rng: random.Random) -> ObstacleKind:
    roll = rng.random()
    if roll < state.pipe_weight:
        return ObstacleKind.PIPE
    if roll < state.pipe_weight + state.pillar_weight:
        return ObstacleKind.PILLAR
    return ObstacleKind.LASER


class Spawner:
    def __init__(self, config: GameConfig | None = None, collectible_frames: list[pygame.Surface] | None = None) -> None:
        self.config = config or GameConfig()
        self.cooldown = self.config.spawn_interval
        self.pipe_frames = make_pipe_frames(self.config.pipe_width, 220)
        self.pillar_frames = make_pillar_frames(self.config.pillar_width, 240)
        self.laser_frames = make_laser_frames(self.config.laser_width, 180)
        self.collectible_frames = collectible_frames or make_collectible_frames(
            CollectibleConfig(points=self.config.collectible_points)
        )
        self.obstacle_config = ObstacleConfig(
            pipe_width=self.config.pipe_width,
            pillar_width=self.config.pillar_width,
            laser_width=self.config.laser_width,
            laser_warning_duration=self.config.laser_warning_duration,
        )

    def reset(self) -> None:
        self.cooldown = self.config.spawn_interval

    def update(
        self,
        dt: float,
        state: DifficultyState,
        rng: random.Random,
        screen_rect: pygame.Rect,
    ) -> list[SpawnResult]:
        self.cooldown -= dt
        results: list[SpawnResult] = []
        while self.cooldown <= 0:
            results.append(self.spawn_one(state, rng, screen_rect))
            self.cooldown += state.spawn_interval
        return results

    def spawn_one(self, state: DifficultyState, rng: random.Random, screen_rect: pygame.Rect) -> SpawnResult:
        kind = choose_obstacle_kind(state, rng)
        gap_size = rng.uniform(state.min_gap, state.max_gap)
        gap_center = rng.uniform(screen_rect.height * 0.24, screen_rect.height * 0.72)
        x = float(screen_rect.width + 10)

        if kind == ObstacleKind.PIPE:
            obstacle = Obstacle(
                kind=kind,
                x=x,
                screen_height=screen_rect.height,
                gap_center_y=gap_center,
                gap_size=gap_size,
                scroll_speed=state.scroll_speed,
                width=self.config.pipe_width,
                top_surface=self.pipe_frames[0],
                bottom_surface=self.pipe_frames[0],
                config=self.obstacle_config,
            )
        elif kind == ObstacleKind.PILLAR:
            obstacle = Obstacle(
                kind=kind,
                x=x,
                screen_height=screen_rect.height,
                gap_center_y=gap_center,
                gap_size=gap_size,
                scroll_speed=state.scroll_speed,
                width=self.config.pillar_width,
                top_surface=self.pillar_frames[0],
                bottom_surface=self.pillar_frames[0],
                config=self.obstacle_config,
                moving=True,
                motion_amplitude=self.config.moving_pillar_amplitude,
                motion_frequency=self.config.moving_pillar_frequency,
            )
        else:
            obstacle = Obstacle(
                kind=kind,
                x=x,
                screen_height=screen_rect.height,
                gap_center_y=gap_center,
                gap_size=gap_size,
                scroll_speed=state.scroll_speed,
                width=self.config.laser_width,
                top_surface=self.laser_frames[0],
                bottom_surface=self.laser_frames[0],
                config=self.obstacle_config,
                laser_warning_duration=self.config.laser_warning_duration,
            )

        collectible_y = gap_center + self.config.collectible_offset
        collectible = Collectible(
            position=(x + obstacle.width * 0.55, collectible_y),
            speed=state.scroll_speed,
            frames=self.collectible_frames,
            config=CollectibleConfig(points=self.config.collectible_points),
        )
        return SpawnResult(obstacle=obstacle, collectible=collectible)
