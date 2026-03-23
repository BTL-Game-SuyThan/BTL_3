from __future__ import annotations

import pygame

from src.entities.collectibles import Collectible
from src.entities.obstacles import Obstacle
from src.entities.player import Player


def player_hits_bounds(player: Player, bounds: pygame.Rect) -> bool:
    return player.hitbox.top <= bounds.top or player.hitbox.bottom >= bounds.bottom


def player_hits_obstacles(player: Player, obstacles: list[Obstacle]) -> bool:
    for obstacle in obstacles:
        for rect in obstacle.collision_rects:
            if player.hitbox.colliderect(rect):
                return True
    return False


def collect_player_collectibles(player: Player, collectibles: list[Collectible]) -> int:
    score = 0
    for collectible in collectibles:
        if collectible.alive and player.hitbox.colliderect(collectible.rect):
            score += collectible.collect()
    return score

