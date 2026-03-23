from __future__ import annotations

import pygame

from src.entities.collectibles import Collectible
from src.entities.obstacles import Obstacle
from src.entities.particles import Particle, ParticleSystem


def cull_offscreen_obstacles(obstacles: list[Obstacle], margin: int = 48) -> list[Obstacle]:
    return [obstacle for obstacle in obstacles if obstacle.alive and obstacle.x + obstacle.width >= -margin]


def cull_offscreen_collectibles(collectibles: list[Collectible], margin: int = 48) -> list[Collectible]:
    return [collectible for collectible in collectibles if collectible.alive and collectible.rect.right >= -margin]


def cull_particles(particles: list[Particle]) -> list[Particle]:
    return [particle for particle in particles if particle.alive]

