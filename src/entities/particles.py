from __future__ import annotations

from dataclasses import dataclass, field
import random

import pygame


@dataclass(slots=True)
class Particle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    color: tuple[int, int, int]
    radius: float
    lifetime: float
    age: float = 0.0

    @property
    def alive(self) -> bool:
        return self.age < self.lifetime

    def update(self, dt: float) -> None:
        self.age += dt
        self.position += self.velocity * dt
        self.velocity.y += 640.0 * dt

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return
        alpha = max(0, 255 - int(255 * (self.age / self.lifetime)))
        color = (*self.color[:3], alpha)
        overlay = pygame.Surface((int(self.radius * 2 + 4), int(self.radius * 2 + 4)), pygame.SRCALPHA)
        pygame.draw.circle(overlay, color, overlay.get_rect().center, int(self.radius))
        surface.blit(overlay, overlay.get_rect(center=(round(self.position.x), round(self.position.y))))


@dataclass
class ParticleSystem:
    particles: list[Particle] = field(default_factory=list)

    def emit_flap_burst(self, origin: tuple[float, float], count: int = 4) -> None:
        for _ in range(count):
            angle = random.uniform(-150.0, -30.0)
            speed = random.uniform(80.0, 220.0)
            velocity = pygame.Vector2(1, 0).rotate(angle) * speed
            velocity.x -= 40.0
            self.particles.append(
                Particle(
                    position=pygame.Vector2(origin),
                    velocity=velocity,
                    color=random.choice([(255, 171, 82), (255, 214, 102), (255, 120, 68)]),
                    radius=random.uniform(2.0, 4.0),
                    lifetime=random.uniform(0.22, 0.4),
                )
            )

    def update(self, dt: float) -> None:
        for particle in self.particles:
            particle.update(dt)
        self.particles = [particle for particle in self.particles if particle.alive]

    def draw(self, surface: pygame.Surface) -> None:
        for particle in self.particles:
            particle.draw(surface)
