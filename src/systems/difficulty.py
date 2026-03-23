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
    pillar_weight: float
    laser_weight: float
    pillars_enabled: bool
    lasers_enabled: bool


class DifficultyManager:
    def __init__(self, config: GameConfig | None = None) -> None:
        self.config = config or GameConfig()
        self.elapsed = 0.0

    def reset(self) -> None:
        self.elapsed = 0.0

    def update(self, dt: float) -> DifficultyState:
        self.elapsed += dt
        ramp = self.elapsed / max(1.0, self.config.difficulty_ramp_seconds)
        scroll_speed = min(self.config.obstacle_speed_cap, self.config.obstacle_speed + self.config.speed_step_per_second * self.elapsed)
        spawn_interval = max(self.config.min_spawn_interval, self.config.spawn_interval - 0.08 * ramp)
        min_gap = max(self.config.gap_floor, self.config.gap_min - 18.0 * ramp)
        max_gap = max(min_gap + 40.0, self.config.gap_max - 10.0 * ramp)
        pillars_enabled = self.elapsed >= self.config.pillar_unlock_time
        lasers_enabled = self.elapsed >= self.config.laser_unlock_time

        pipe_weight = self.config.pipe_weight
        pillar_weight = self.config.pillar_weight if pillars_enabled else 0.0
        laser_weight = self.config.laser_weight if lasers_enabled else 0.0
        total = pipe_weight + pillar_weight + laser_weight
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
            pillar_weight=pillar_weight / total,
            laser_weight=laser_weight / total,
            pillars_enabled=pillars_enabled,
            lasers_enabled=lasers_enabled,
        )

    def random_gap_size(self, state: DifficultyState, rng: random.Random) -> float:
        low = int(state.min_gap)
        high = int(state.max_gap)
        return float(rng.randint(low, high))

