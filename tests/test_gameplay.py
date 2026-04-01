from __future__ import annotations

import random
import unittest

import pygame

from src.entities.collectibles import Collectible, CollectibleKind
from src.entities.obstacles import Obstacle, ObstacleConfig, ObstacleKind
from src.entities.player import Player
from src.systems.collision import collect_player_collectibles
from src.systems.config import GameConfig
from src.systems.difficulty import DifficultyState
from src.systems.spawning import Spawner, choose_obstacle_kind


class GameplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()

    def test_player_flap_moves_upward(self) -> None:
        player = Player((220, 320))
        start_y = player.position.y
        player.flap()
        player.update(0.05)
        self.assertLess(player.position.y, start_y)

    def test_gravity_shift_changes_flap_direction(self) -> None:
        player = Player((220, 320))
        start_y = player.position.y
        player.shift_gravity()
        player.flap()
        player.update(0.05)
        self.assertGreater(player.position.y, start_y)

    def test_collectible_scores_once(self) -> None:
        player = Player((220, 320))
        collectible = Collectible((220, 320), speed=0.0)
        score_once = collect_player_collectibles(player, [collectible]).score
        score_twice = collect_player_collectibles(player, [collectible]).score
        self.assertEqual(score_once, 1)
        self.assertEqual(score_twice, 0)

    def test_shield_collectible_grants_shield_without_score(self) -> None:
        player = Player((220, 320))
        shield = Collectible((220, 320), speed=0.0, kind=CollectibleKind.SHIELD)
        outcome = collect_player_collectibles(player, [shield])
        self.assertEqual(outcome.score, 0)
        self.assertTrue(outcome.granted_shield)

    def test_shield_collision_detects_obstacle_hit(self) -> None:
        player = Player((220, 320))
        obstacle = Obstacle(
            kind=ObstacleKind.PIPE,
            x=200,
            screen_height=720,
            gap_center_y=540,
            gap_size=120,
            scroll_speed=0.0,
            width=92,
        )
        hit = any(player.hitbox.colliderect(rect) for rect in obstacle.collision_rects)
        self.assertTrue(hit)

    def test_windmill_kind_allowed_when_enabled(self) -> None:
        state = DifficultyState(
            elapsed=0.0,
            scroll_speed=260.0,
            spawn_interval=1.3,
            min_gap=180.0,
            max_gap=240.0,
            pipe_weight=0.0,
            dynamic_pipe_weight=0.0,
            gravity_pipe_weight=0.0,
            dynamic_pipes_enabled=True,
            gravity_pipes_enabled=True,
        )
        choice = choose_obstacle_kind(
            state,
            random.Random(0),
            pipe_wheel_enabled=False,
            pipe_wheel_weight=0.0,
            windmill_enabled=True,
            windmill_weight=1.0,
        )
        self.assertEqual(choice, ObstacleKind.WINDMILL)

    def test_pipe_wheel_kind_allowed_when_enabled(self) -> None:
        state = DifficultyState(
            elapsed=0.0,
            scroll_speed=260.0,
            spawn_interval=1.3,
            min_gap=180.0,
            max_gap=240.0,
            pipe_weight=0.0,
            dynamic_pipe_weight=0.0,
            gravity_pipe_weight=0.0,
            dynamic_pipes_enabled=True,
            gravity_pipes_enabled=True,
        )
        choice = choose_obstacle_kind(
            state,
            random.Random(0),
            pipe_wheel_enabled=True,
            pipe_wheel_weight=1.0,
            windmill_enabled=False,
            windmill_weight=0.0,
        )
        self.assertEqual(choice, ObstacleKind.PIPE_WHEEL)

    def test_windmill_kind_blocked_when_disabled(self) -> None:
        state = DifficultyState(
            elapsed=0.0,
            scroll_speed=260.0,
            spawn_interval=1.3,
            min_gap=180.0,
            max_gap=240.0,
            pipe_weight=1.0,
            dynamic_pipe_weight=0.0,
            gravity_pipe_weight=0.0,
            dynamic_pipes_enabled=True,
            gravity_pipes_enabled=True,
        )
        choice = choose_obstacle_kind(
            state,
            random.Random(0),
            pipe_wheel_enabled=False,
            pipe_wheel_weight=0.0,
            windmill_enabled=False,
            windmill_weight=1.0,
        )
        self.assertEqual(choice, ObstacleKind.PIPE)

    def test_pipe_wheel_kind_blocked_when_disabled(self) -> None:
        state = DifficultyState(
            elapsed=0.0,
            scroll_speed=260.0,
            spawn_interval=1.3,
            min_gap=180.0,
            max_gap=240.0,
            pipe_weight=1.0,
            dynamic_pipe_weight=0.0,
            gravity_pipe_weight=0.0,
            dynamic_pipes_enabled=True,
            gravity_pipes_enabled=True,
        )
        choice = choose_obstacle_kind(
            state,
            random.Random(0),
            pipe_wheel_enabled=False,
            pipe_wheel_weight=1.0,
            windmill_enabled=False,
            windmill_weight=0.0,
        )
        self.assertEqual(choice, ObstacleKind.PIPE)

    def test_shield_spawns_on_pipe_interval(self) -> None:
        config = GameConfig()
        config.shield_spawn_interval = 1
        spawner = Spawner(config=config, assets=None)
        state = DifficultyState(
            elapsed=0.0,
            scroll_speed=260.0,
            spawn_interval=1.3,
            min_gap=180.0,
            max_gap=240.0,
            pipe_weight=1.0,
            dynamic_pipe_weight=0.0,
            gravity_pipe_weight=0.0,
            dynamic_pipes_enabled=True,
            gravity_pipes_enabled=True,
        )
        result = spawner.spawn_one(
            state,
            random.Random(2),
            pygame.Rect(0, 0, 1280, 720),
            obstacles_passed=0,
            gravity_direction=1.0,
        )
        self.assertEqual(len(result.collectibles), 2)
        self.assertEqual(
            [c.kind for c in result.collectibles],
            [CollectibleKind.COIN, CollectibleKind.SHIELD],
        )

    def test_pipe_wheel_spawns_four_diagonal_coins(self) -> None:
        config = GameConfig()
        config.pipe_wheel_enabled = True
        config.pipe_wheel_weight = 1.0
        config.pipe_wheel_unlock_obstacles = 0
        config.pipe_wheel_spawn_interval = 15
        config.windmill_enabled = False
        config.shield_spawn_interval = 99
        spawner = Spawner(config=config, assets=None)
        state = DifficultyState(
            elapsed=0.0,
            scroll_speed=260.0,
            spawn_interval=1.3,
            min_gap=180.0,
            max_gap=240.0,
            pipe_weight=0.0,
            dynamic_pipe_weight=0.0,
            gravity_pipe_weight=0.0,
            dynamic_pipes_enabled=True,
            gravity_pipes_enabled=True,
        )
        result = spawner.spawn_one(
            state,
            random.Random(4),
            pygame.Rect(0, 0, 1280, 720),
            obstacles_passed=14,
            gravity_direction=1.0,
        )
        self.assertEqual(result.obstacle.kind, ObstacleKind.PIPE_WHEEL)
        self.assertEqual(result.obstacle.gap_center_y, 360.0)
        self.assertEqual(result.obstacle.width, config.pipe_wheel_width)
        self.assertEqual(len(result.collectibles), 4)
        center_x = result.obstacle.x + result.obstacle.width * 0.5
        center_y = result.obstacle.gap_center_y
        coin_quadrants = {
            (coin.position.x < center_x, coin.position.y < center_y)
            for coin in result.collectibles
        }
        self.assertEqual(
            coin_quadrants,
            {(True, True), (False, True), (True, False), (False, False)},
        )

    def test_pipe_wheel_rotation_scales_with_world_speed(self) -> None:
        slow = Obstacle(
            kind=ObstacleKind.PIPE_WHEEL,
            x=1000,
            screen_height=720,
            gap_center_y=360,
            gap_size=0,
            scroll_speed=260.0,
            width=620,
        )
        fast = Obstacle(
            kind=ObstacleKind.PIPE_WHEEL,
            x=1000,
            screen_height=720,
            gap_center_y=360,
            gap_size=0,
            scroll_speed=260.0,
            width=620,
        )
        slow.update(1.0, 140.0)
        fast.update(1.0, 360.0)
        self.assertGreater(fast.rotation, slow.rotation)

    def test_pipe_wheel_aligns_to_safe_angle_at_player_lane(self) -> None:
        config = ObstacleConfig(
            pipe_wheel_width=620,
            pipe_wheel_arm_width=88,
            pipe_wheel_arm_length=320,
            pipe_wheel_hub_radius=34.0,
            pipe_wheel_collision_thickness=20.0,
            pipe_wheel_spin_speed=40.0,
            pipe_wheel_sync_x=400.0,
            pipe_wheel_safe_angle=0.0,
        )
        obstacle = Obstacle(
            kind=ObstacleKind.PIPE_WHEEL,
            x=90.0,
            screen_height=720,
            gap_center_y=360.0,
            gap_size=0.0,
            scroll_speed=260.0,
            width=620,
            config=config,
        )
        obstacle.rotation = 47.0
        obstacle.update(0.0, 260.0)
        self.assertEqual(obstacle.rotation, 0.0)

    def test_pipe_wheel_adds_followup_spacing(self) -> None:
        config = GameConfig()
        config.pipe_wheel_enabled = True
        config.pipe_wheel_weight = 1.0
        config.pipe_wheel_unlock_obstacles = 0
        config.pipe_wheel_spawn_interval = 15
        config.windmill_enabled = False
        spawner = Spawner(config=config, assets=None)
        spawner.cooldown = 0.0
        state = DifficultyState(
            elapsed=0.0,
            scroll_speed=260.0,
            spawn_interval=1.3,
            min_gap=180.0,
            max_gap=240.0,
            pipe_weight=0.0,
            dynamic_pipe_weight=0.0,
            gravity_pipe_weight=0.0,
            dynamic_pipes_enabled=True,
            gravity_pipes_enabled=True,
        )
        results = spawner.update(
            0.0,
            state,
            random.Random(7),
            pygame.Rect(0, 0, 1280, 720),
            obstacles_passed=14,
            gravity_direction=1.0,
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].obstacle.kind, ObstacleKind.PIPE_WHEEL)
        self.assertGreater(spawner.cooldown, state.spawn_interval)

    def test_pipe_wheel_does_not_spawn_before_interval(self) -> None:
        config = GameConfig()
        config.pipe_wheel_enabled = True
        config.pipe_wheel_weight = 1.0
        config.pipe_wheel_unlock_obstacles = 0
        config.pipe_wheel_spawn_interval = 15
        config.windmill_enabled = False
        spawner = Spawner(config=config, assets=None)
        state = DifficultyState(
            elapsed=0.0,
            scroll_speed=260.0,
            spawn_interval=1.3,
            min_gap=180.0,
            max_gap=240.0,
            pipe_weight=1.0,
            dynamic_pipe_weight=0.0,
            gravity_pipe_weight=0.0,
            dynamic_pipes_enabled=True,
            gravity_pipes_enabled=True,
        )
        result = spawner.spawn_one(
            state,
            random.Random(9),
            pygame.Rect(0, 0, 1280, 720),
            obstacles_passed=13,
            gravity_direction=1.0,
        )
        self.assertNotEqual(result.obstacle.kind, ObstacleKind.PIPE_WHEEL)

    def test_windmill_disabled_in_spawner(self) -> None:
        config = GameConfig()
        config.pipe_wheel_enabled = False
        config.shield_spawn_interval = 1
        spawner = Spawner(config=config, assets=None)
        state = DifficultyState(
            elapsed=0.0,
            scroll_speed=260.0,
            spawn_interval=1.3,
            min_gap=180.0,
            max_gap=240.0,
            pipe_weight=0.0,
            dynamic_pipe_weight=0.0,
            gravity_pipe_weight=0.0,
            dynamic_pipes_enabled=True,
            gravity_pipes_enabled=True,
        )
        result = spawner.spawn_one(
            state,
            random.Random(3),
            pygame.Rect(0, 0, 1280, 720),
            obstacles_passed=40,
            gravity_direction=1.0,
        )
        self.assertEqual(result.obstacle.kind, ObstacleKind.PIPE)


if __name__ == "__main__":
    unittest.main()
