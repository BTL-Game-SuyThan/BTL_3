from __future__ import annotations

from dataclasses import dataclass
import random

from .config import GameConfig


@dataclass(slots=True)
class DifficultyState:
    elapsed: float
    scroll_speed: float
    spawn_interval: float
    min_gap: float
    max_gap: float
    pipe_weight: float
    dynamic_pipe_weight: float
    gravity_pipe_weight: float
    dynamic_pipes_enabled: bool
    gravity_pipes_enabled: bool


class DifficultyManager:
    def __init__(self, config: GameConfig | None = None) -> None:
        self.config = config or GameConfig()
        self.elapsed = 0.0

    def reset(self) -> None:
        self.elapsed = 0.0

    def update(self, dt: float) -> DifficultyState:
        self.elapsed += dt
        ramp = self.elapsed / max(1.0, self.config.difficulty_ramp_seconds)
        scroll_speed = min(
            self.config.obstacle_speed_cap,
            self.config.obstacle_speed + self.config.speed_step_per_second * self.elapsed,
        )
        spawn_interval = max(
            self.config.min_spawn_interval, self.config.spawn_interval - 0.08 * ramp
        )
        min_gap = max(self.config.gap_floor, self.config.gap_min - 18.0 * ramp)
        max_gap = max(min_gap + 40.0, self.config.gap_max - 10.0 * ramp)

        dynamic_pipes_enabled = self.elapsed >= self.config.dynamic_pipe_unlock_time
        gravity_pipes_enabled = self.elapsed >= self.config.gravity_pipe_unlock_time

        pipe_weight = self.config.pipe_weight
        dynamic_pipe_weight = (
            self.config.dynamic_pipe_weight if dynamic_pipes_enabled else 0.0
        )
        gravity_pipe_weight = (
            self.config.gravity_pipe_weight if gravity_pipes_enabled else 0.0
        )

        total = pipe_weight + dynamic_pipe_weight + gravity_pipe_weight
        if total <= 0:
            pipe_weight = 1.0
            total = 1.0

        return DifficultyState(
            elapsed=self.elapsed,
            scroll_speed=scroll_speed,
            spawn_interval=spawn_interval,
            min_gap=min_gap,
            max_gap=max_gap,
            pipe_weight=pipe_weight / total,
            dynamic_pipe_weight=dynamic_pipe_weight / total,
            gravity_pipe_weight=gravity_pipe_weight / total,
            dynamic_pipes_enabled=dynamic_pipes_enabled,
            gravity_pipes_enabled=gravity_pipes_enabled,
        )

    def random_gap_size(self, state: DifficultyState, rng: random.Random) -> float:
        low = int(state.min_gap)
        high = int(state.max_gap)
        return float(rng.randint(low, high))
