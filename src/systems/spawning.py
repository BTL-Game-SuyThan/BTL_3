from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

from src.entities.collectibles import (
    Collectible,
    CollectibleConfig,
    make_collectible_frames,
)
from src.entities.obstacles import Obstacle, ObstacleConfig, ObstacleKind
from src.systems.config import GameConfig
from src.systems.difficulty import DifficultyState


@dataclass(slots=True)
class SpawnResult:
    obstacle: Obstacle
    collectible: Collectible | None


def choose_obstacle_kind(state: DifficultyState, rng: random.Random) -> ObstacleKind:
    roll = rng.random()
    if roll < state.pipe_weight:
        return ObstacleKind.PIPE
    if roll < state.pipe_weight + state.dynamic_pipe_weight:
        return ObstacleKind.DYNAMIC_PIPE
    return ObstacleKind.GRAVITY_PIPE


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

    def spawn_one(
        self, state: DifficultyState, rng: random.Random, screen_rect: pygame.Rect
    ) -> SpawnResult:
        kind = choose_obstacle_kind(state, rng)
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
            moving_pillar_amplitude=self.config.moving_pillar_amplitude,
            moving_pillar_frequency=self.config.moving_pillar_frequency,
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
        collectible = Collectible(
            position=(x + obstacle.width * 0.55, collectible_y),
            speed=state.scroll_speed,
            frames=self.collectible_frames,
            config=CollectibleConfig(points=self.config.collectible_points),
        )
        return SpawnResult(obstacle=obstacle, collectible=collectible)
