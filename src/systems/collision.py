from __future__ import annotations

from dataclasses import dataclass

import pygame

from src.entities.collectibles import Collectible
from src.entities.obstacles import Obstacle
from src.entities.player import Player


@dataclass(slots=True)
class CollectionOutcome:
    score: int = 0
    granted_shield: bool = False


def player_hits_bounds(player: Player, bounds: pygame.Rect) -> bool:
    return player.hitbox.top <= bounds.top or player.hitbox.bottom >= bounds.bottom


def player_hits_obstacles(player: Player, obstacles: list[Obstacle]) -> bool:
    return first_collided_obstacle(player, obstacles) is not None


def first_collided_obstacle(player: Player, obstacles: list[Obstacle]) -> Obstacle | None:
    for obstacle in obstacles:
        for rect in obstacle.collision_rects:
            if player.hitbox.colliderect(rect):
                return obstacle
    return None


def collect_player_collectibles(
    player: Player, collectibles: list[Collectible]
) -> CollectionOutcome:
    outcome = CollectionOutcome()
    for collectible in collectibles:
        if collectible.alive and player.hitbox.colliderect(collectible.rect):
            result = collectible.collect()
            outcome.score += result.score
            outcome.granted_shield = outcome.granted_shield or result.granted_shield
    return outcome
