from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(slots=True)
class GameConfig:
    screen_width: int = 1280
    screen_height: int = 720
    ground_height: int = 120
    target_fps: int = 60
    background_theme: str = "rural_area"
    background_speed_multipliers: tuple[float, ...] = (0.05, 0.15, 0.25, 0.45, 1.0)
    player_start_x: int = 220
    player_start_y: int = 360
    gravity: float = 1700.0
    flap_velocity: float = -440.0
    glide_window: float = 0.14
    glide_gravity_scale: float = 0.55
    terminal_fall_speed: float = 660.0
    gravity_shift_cooldown: float = 0.45
    obstacle_speed: float = 260.0
    obstacle_speed_cap: float = 390.0
    speed_step_per_second: float = 7.0
    spawn_interval: float = 1.35
    min_spawn_interval: float = 0.88
    gap_min: float = 180.0
    gap_max: float = 248.0
    gap_floor: float = 160.0
    gap_ceiling: float = 278.0
    pipe_width: int = 92
    pillar_width: int = 70
    laser_width: int = 88
    laser_warning_duration: float = 0.85
    moving_pillar_amplitude: float = 44.0
    moving_pillar_frequency: float = 1.15
    collectible_offset: float = 0.0
    collectible_points: int = 1
    particle_burst_min: int = 3
    particle_burst_max: int = 5
    particle_lifetime_min: float = 0.22
    particle_lifetime_max: float = 0.40
    pipe_weight: float = 0.62
    pillar_weight: float = 0.24
    laser_weight: float = 0.14
    pillar_unlock_time: float = 8.0
    laser_unlock_time: float = 16.0
    difficulty_ramp_seconds: float = 15.0
    score_per_collectible: int = 1

    def save(self, path: str = "config.json") -> None:
        data = {"background_theme": self.background_theme}
        try:
            with open(path, "w") as f:
                json.dump(data, f)
        except IOError:
            pass

    @classmethod
    def load(cls, path: str = "config.json") -> GameConfig:
        instance = cls()
        if Path(path).exists():
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    if "background_theme" in data:
                        instance.background_theme = data["background_theme"]
            except (json.JSONDecodeError, IOError):
                pass
        return instance
