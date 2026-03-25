from __future__ import annotations

import unittest

import pygame

from src.entities.collectibles import Collectible
from src.entities.obstacles import Obstacle, ObstacleKind
from src.entities.player import Player
from src.systems.collision import collect_player_collectibles


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
        score_once = collect_player_collectibles(player, [collectible])
        score_twice = collect_player_collectibles(player, [collectible])
        self.assertEqual(score_once, 1)
        self.assertEqual(score_twice, 0)

    def test_laser_is_not_collidable_until_warning_ends(self) -> None:
        obstacle = Obstacle(
            kind=ObstacleKind.LASER,
            x=400,
            screen_height=720,
            gap_center_y=320,
            gap_size=210,
            scroll_speed=0.0,
            width=88,
        )
        self.assertEqual(obstacle.collision_rects, [])
        obstacle.update(1.0, 0.0)
        self.assertEqual(len(obstacle.collision_rects), 1)


if __name__ == "__main__":
    unittest.main()
