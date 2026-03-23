from __future__ import annotations

import random

import pygame

from src.core.assets import AssetBundle
from src.core.parallax import ParallaxLayer
from src.entities.collectibles import Collectible
from src.entities.obstacles import Obstacle
from src.entities.particles import ParticleSystem
from src.entities.player import Player, PlayerConfig
from src.systems.cleanup import cull_offscreen_collectibles, cull_offscreen_obstacles
from src.systems.collision import (
    collect_player_collectibles,
    player_hits_bounds,
    player_hits_obstacles,
)
from src.systems.config import GameConfig
from src.systems.difficulty import DifficultyManager, DifficultyState
from src.systems.spawning import SpawnResult, Spawner


class GameWorld:
    def __init__(self, config: GameConfig, assets: AssetBundle) -> None:
        self.config = config
        self.assets = assets
        self.screen_rect = pygame.Rect(0, 0, config.screen_width, config.screen_height)
        self.rng = random.Random()
        self.best_score = 0

        self.layers = [
            ParallaxLayer(image=layer, speed_multiplier=multiplier)
            for layer, multiplier in zip(assets.background_layers, config.background_speed_multipliers, strict=True)
        ]
        player_position = (config.player_start_x, config.player_start_y)
        self.player = Player(
            player_position,
            config=PlayerConfig(
                gravity=config.gravity,
                flap_velocity=config.flap_velocity,
                glide_window=config.glide_window,
                glide_gravity_scale=config.glide_gravity_scale,
                terminal_fall_speed=config.terminal_fall_speed,
            ),
            idle_frames=assets.player_idle_frames,
            flap_frames=assets.player_flap_frames,
        )
        self.spawner = Spawner(config, collectible_frames=assets.collectible_frames)
        self.difficulty = DifficultyManager(config)
        self.particles = ParticleSystem()

        self.started = False
        self.game_over = False
        self.score = 0
        self.collectibles_collected = 0
        self.obstacles: list[Obstacle] = []
        self.collectibles: list[Collectible] = []
        self.current_difficulty = self.difficulty.update(0.0)
        self.reset()

    def start(self) -> None:
        self.started = True

    def flap(self) -> None:
        if self.game_over:
            return
        self.started = True
        self.player.flap()
        self.particles.emit_flap_burst(self.player.rect.midleft, count=self.rng.randint(3, 5))

    def handle_input(self, action: str) -> None:
        _ = action

    def reset(self) -> None:
        self.started = False
        self.game_over = False
        self.score = 0
        self.collectibles_collected = 0
        self.obstacles.clear()
        self.collectibles.clear()
        self.particles.particles.clear()
        self.player.reset((self.config.player_start_x, self.config.player_start_y))
        self.spawner.reset()
        self.difficulty.reset()
        self.current_difficulty = self.difficulty.update(0.0)
        for layer in self.layers:
            layer.offset_x = 0.0

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

        world_speed = self.current_difficulty.scroll_speed if self.started else self.config.obstacle_speed * 0.2

        for layer in self.layers:
            layer.update(dt, world_speed)

        self.player.update(dt)

        if self.started:
            self._spawn_entities(dt)
            for obstacle in self.obstacles:
                obstacle.update(dt, world_speed)
            for collectible in self.collectibles:
                collectible.update(dt, world_speed)
            self.particles.update(dt)

            self.score += collect_player_collectibles(self.player, self.collectibles)
            self.collectibles_collected = self.score
            self.obstacles = cull_offscreen_obstacles(self.obstacles)
            self.collectibles = cull_offscreen_collectibles(self.collectibles)

            if player_hits_bounds(self.player, self.screen_rect) or player_hits_obstacles(self.player, self.obstacles):
                self._trigger_game_over()
        else:
            self.particles.update(dt)

    def _spawn_entities(self, dt: float) -> None:
        spawn_results = self.spawner.update(dt, self.current_difficulty, self.rng, self.screen_rect)
        for result in spawn_results:
            self.obstacles.append(result.obstacle)
            if result.collectible is not None:
                self.collectibles.append(result.collectible)

    def _trigger_game_over(self) -> None:
        self.game_over = True
        self.player.kill()
        self.best_score = max(self.best_score, self.score)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((183, 224, 255))
        for layer in self.layers:
            layer.draw(surface)

        if not self.started:
            self._draw_idle_world_hint(surface)

        for obstacle in self.obstacles:
            obstacle.draw(surface)
        for collectible in self.collectibles:
            collectible.draw(surface)
        self.particles.draw(surface)
        self.player.draw(surface)

    def _draw_idle_world_hint(self, surface: pygame.Surface) -> None:
        hint_rect = pygame.Rect(48, self.config.screen_height - 86, 400, 42)
        overlay = pygame.Surface(hint_rect.size, pygame.SRCALPHA)
        overlay.fill((10, 14, 24, 145))
        pygame.draw.rect(overlay, (255, 255, 255, 24), overlay.get_rect(), width=1, border_radius=14)
        surface.blit(overlay, hint_rect)
        text = self.assets.hud_font.render("Tap Space to flap, hold briefly to glide", True, (236, 241, 249))
        surface.blit(text, text.get_rect(midleft=(hint_rect.x + 18, hint_rect.centery)))
