from __future__ import annotations

import json
import math
import random
from pathlib import Path

import pygame

from src.core.assets import AssetBundle
from src.core.audio import AudioManager
from src.core.parallax import ParallaxLayer
from src.entities.collectibles import Collectible
from src.entities.obstacles import Obstacle, ObstacleKind
from src.entities.particles import ParticleSystem
from src.entities.player import Player, PlayerConfig
from src.systems.cleanup import cull_offscreen_collectibles, cull_offscreen_obstacles
from src.systems.collision import (
    collect_player_collectibles,
    first_collided_obstacle,
    player_hits_bounds,
)
from src.systems.config import GameConfig
from src.systems.difficulty import DifficultyManager, DifficultyState
from src.systems.spawning import SpawnResult, Spawner


class GameWorld:
    def __init__(
        self, config: GameConfig, assets: AssetBundle, audio: AudioManager
    ) -> None:
        self.config = config
        self.assets = assets
        self.audio = audio
        self.screen_rect = pygame.Rect(0, 0, config.screen_width, config.screen_height)
        self.rng = random.Random()

        self.high_scores = self._load_high_scores()
        self.best_score = self.high_scores.get(self.config.difficulty, 0)

        self.layers: list[ParallaxLayer] = []
        self.change_theme(config.background_theme)

        player_position = (config.player_start_x, config.player_start_y)
        idle_frames, flap_frames = assets.get_player_frames(config.bird_color)
        self.player = Player(
            player_position,
            config=PlayerConfig(
                gravity=config.gravity,
                flap_velocity=config.flap_velocity,
                glide_window=config.glide_window,
                glide_gravity_scale=config.glide_gravity_scale,
                terminal_fall_speed=config.terminal_fall_speed,
                gravity_shift_cooldown=config.gravity_shift_cooldown,
                damage_immunity_duration=config.damage_immunity_duration,
                damage_blink_frequency=config.damage_blink_frequency,
            ),
            idle_frames=idle_frames,
            flap_frames=flap_frames,
        )
        self.spawner = Spawner(
            config, collectible_frames=assets.collectible_frames, assets=assets
        )
        self.difficulty = DifficultyManager(config)
        self.particles = ParticleSystem()

        self.started = False
        self.game_over = False
        self.score = 0
        self.has_shield = False
        self.obstacles_passed = 0
        self.collectibles_collected = 0
        self.obstacles: list[Obstacle] = []
        self.collectibles: list[Collectible] = []
        self.current_difficulty = self.difficulty.update(0.0)
        self.water_wave_phase = 0.0
        self.reset()

    def _load_high_scores(self) -> dict[str, int]:
        path = Path("high_score.json")
        default = {"easy": 0, "medium": 0, "hard": 0}
        if path.exists():
            try:
                data = json.loads(path.read_text())
                if isinstance(data, dict):
                    # Ensure all keys exist
                    for k in default:
                        if k not in data:
                            data[k] = 0
                    return data
                elif isinstance(data, int):
                    # Migration from old format
                    default["medium"] = data
                    return default
            except (json.JSONDecodeError, IOError, ValueError):
                pass
        return default

    def _save_high_scores(self) -> None:
        path = Path("high_score.json")
        try:
            path.write_text(json.dumps(self.high_scores))
        except IOError:
            pass

    def start(self) -> None:
        self.started = True

    def change_theme(self, theme: str) -> None:
        self.config.background_theme = theme
        self.config.save()
        layer_images = self.assets.get_background_layers(theme)
        num_layers = len(layer_images)

        if num_layers > 0:
            if num_layers == len(self.config.background_speed_multipliers):
                multipliers = self.config.background_speed_multipliers
            else:
                min_m, max_m = 0.05, 1.0
                if num_layers == 1:
                    multipliers = (max_m,)
                else:
                    multipliers = tuple(
                        min_m + (i / (num_layers - 1)) * (max_m - min_m)
                        for i in range(num_layers)
                    )

            self.layers = [
                ParallaxLayer(image=img, speed_multiplier=m)
                for img, m in zip(layer_images, multipliers)
            ]
        else:
            self.layers = []

    def flap(self) -> None:
        if self.game_over:
            return
        self.started = True
        self.player.flap()
        self.audio.play_flap()
        self.particles.emit_feather_burst(
            self.player.tail_position(), count=self.rng.randint(4, 7)
        )

    def toggle_gravity(self) -> None:
        if self.game_over:
            return
        self.started = True
        shifted = self.player.shift_gravity()
        if shifted:
            self.particles.emit_feather_burst(
                self.player.rect.center, count=self.rng.randint(6, 9)
            )

    def handle_input(self, action: str) -> None:
        pass

    def reset(self) -> None:
        self.started = False
        self.game_over = False
        self.score = 0
        self.has_shield = False
        self.obstacles_passed = 0
        self.collectibles_collected = 0
        self.obstacles.clear()
        self.collectibles.clear()
        self.particles.particles.clear()
        self.player.reset((self.config.player_start_x, self.config.player_start_y))
        self.spawner.reset()
        self.difficulty.reset()
        self.current_difficulty = self.difficulty.update(0.0)
        # Update best_score for current difficulty in case it changed in settings
        self.best_score = self.high_scores.get(self.config.difficulty, 0)
        for layer in self.layers:
            layer.offset_x = 0.0
        self.water_wave_phase = 0.0

    def update_background(self, dt: float) -> None:
        world_speed = self.config.obstacle_speed * 0.2
        for layer in self.layers:
            layer.update(dt, world_speed)

    def update(self, dt: float) -> None:
        self.player.set_glide_input(bool(pygame.key.get_pressed()[pygame.K_SPACE]))

        if self.game_over:
            for layer in self.layers:
                layer.update(dt, self.current_difficulty.scroll_speed * 0.2)
            self.player.update(dt)
            self.particles.update(dt)
            return

        if self.started:
            self.current_difficulty = self.difficulty.update(dt)
        else:
            self.current_difficulty = self.difficulty.update(0.0)
        self.water_wave_phase += dt * 2.6

        world_speed = self.current_difficulty.scroll_speed if self.started else 0.0

        for layer in self.layers:
            layer.update(dt, world_speed)

        if self.started or self.game_over:
            self.player.update(dt)

        if self.started:
            self._spawn_entities(dt)
            for obstacle in self.obstacles:
                obstacle.update(dt, world_speed)
            for collectible in self.collectibles:
                collectible.update(dt, world_speed)
            self.particles.update(dt)
            self._check_obstacle_passed()

            collected = collect_player_collectibles(self.player, self.collectibles)
            if collected.granted_shield:
                self.has_shield = True
            if collected.score > 0:
                self.audio.play_coin()
            self.score += collected.score
            self.collectibles_collected = self.score
            self.obstacles = cull_offscreen_obstacles(self.obstacles)
            self.collectibles = cull_offscreen_collectibles(self.collectibles)

            if player_hits_bounds(self.player, self.screen_rect):
                self._trigger_game_over()
            else:
                collided_obstacle = first_collided_obstacle(self.player, self.obstacles)
                if collided_obstacle is not None:
                    if self.has_shield:
                        self.has_shield = False
                        self.player.trigger_damage_immunity()
                        self.particles.emit_pop_burst(
                            (float(self.player.hitbox.centerx), float(self.player.hitbox.centery)),
                            count=self.rng.randint(9, 14),
                        )
                    elif self.player.is_damage_immune:
                        pass
                    else:
                        self._trigger_game_over()
        else:
            self.particles.update(dt)

    def _spawn_entities(self, dt: float) -> None:
        spawn_results = self.spawner.update(
            dt,
            self.current_difficulty,
            self.rng,
            self.screen_rect,
            self.obstacles_passed,
            self.player.gravity_direction,
        )
        for result in spawn_results:
            self.obstacles.append(result.obstacle)
            self.collectibles.extend(result.collectibles)

    def _trigger_game_over(self) -> None:
        self.game_over = True
        self.player.kill()
        self.audio.play_die()

        diff = self.config.difficulty
        if self.score > self.high_scores.get(diff, 0):
            self.high_scores[diff] = self.score
            self.best_score = self.score
            self._save_high_scores()

    def _check_obstacle_passed(self) -> None:
        player_x = self.player.hitbox.left
        for obstacle in self.obstacles:
            if (
                obstacle.alive
                and not obstacle.passed_player
                and obstacle.x + obstacle.width < player_x
            ):
                obstacle.passed_player = True
                self.obstacles_passed += 1
                self.audio.play_pass()
                if obstacle.kind == ObstacleKind.GRAVITY_PIPE:
                    self.toggle_gravity()

    def render_background(self, surface: pygame.Surface) -> None:
        surface.fill((183, 224, 255))
        for layer in self.layers:
            layer.draw(surface)
        if self.config.background_theme == "rural_area":
            self._draw_river_water_effect(surface)

    def _draw_river_water_effect(self, surface: pygame.Surface) -> None:
        river_top = int(self.config.screen_height * 0.72)
        river_bottom = int(self.config.screen_height * 0.92)
        river_height = max(1, river_bottom - river_top)
        water_overlay = pygame.Surface(
            (self.config.screen_width, river_height), pygame.SRCALPHA
        )

        for y in range(river_height):
            t = y / max(1, river_height - 1)
            alpha = int(40 + t * 52)
            color = (
                int(88 - t * 24),
                int(152 - t * 34),
                int(198 - t * 26),
                alpha,
            )
            pygame.draw.line(
                water_overlay, color, (0, y), (self.config.screen_width, y)
            )

        width = self.config.screen_width
        for band, intensity in ((8, 78), (19, 55), (31, 34)):
            points: list[tuple[int, int]] = []
            for x in range(0, width + 12, 12):
                y = int(
                    river_height * 0.32
                    + band
                    + 7
                    * math.sin(x * 0.024 + self.water_wave_phase * (1.3 + band * 0.03))
                )
                points.append((x, y))
            if len(points) >= 2:
                pygame.draw.lines(
                    water_overlay, (220, 243, 255, intensity), False, points, 2
                )

        shimmer_speed = 170
        for i in range(14):
            x = (
                int((i * 118 + self.water_wave_phase * shimmer_speed) % (width + 120))
                - 60
            )
            y = int(river_height * (0.24 + (i % 5) * 0.11))
            pygame.draw.ellipse(water_overlay, (235, 250, 255, 38), (x, y, 40, 6))

        surface.blit(water_overlay, (0, river_top))

    def render(self, surface: pygame.Surface) -> None:
        self.render_background(surface)

        for obstacle in self.obstacles:
            obstacle.draw(surface)
        for collectible in self.collectibles:
            collectible.draw(surface)
        self.particles.draw(surface)
        self.player.draw(surface)
