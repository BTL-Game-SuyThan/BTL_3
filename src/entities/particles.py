from __future__ import annotations

from dataclasses import dataclass, field
import random

import pygame


@dataclass(slots=True)
class Particle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    color: tuple[int, int, int]
    width: float
    height: float
    spin: float
    angle: float
    lifetime: float
    age: float = 0.0

    @property
    def alive(self) -> bool:
        return self.age < self.lifetime

    def update(self, dt: float) -> None:
        self.age += dt
        self.position += self.velocity * dt
        self.velocity.x *= 0.99
        self.velocity.y += 480.0 * dt
        self.angle += self.spin * dt

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return
        alpha = max(0, 255 - int(255 * (self.age / self.lifetime)))
        color = (*self.color[:3], alpha)
        feather = pygame.Surface((int(self.width + 6), int(self.height + 6)), pygame.SRCALPHA)
        feather_rect = feather.get_rect()
        pygame.draw.ellipse(feather, color, feather_rect.inflate(-6, -6))
        pygame.draw.line(
            feather,
            (255, 255, 255, min(255, alpha)),
            (feather_rect.width // 2, 4),
            (feather_rect.width // 2, feather_rect.height - 4),
            1,
        )
        rotated = pygame.transform.rotate(feather, self.angle)
        surface.blit(rotated, rotated.get_rect(center=(round(self.position.x), round(self.position.y))))


@dataclass
class ParticleSystem:
    particles: list[Particle] = field(default_factory=list)

    def emit_feather_burst(self, origin: tuple[float, float], count: int = 5) -> None:
        for _ in range(count):
            angle = random.uniform(-170.0, -10.0)
            speed = random.uniform(90.0, 210.0)
            velocity = pygame.Vector2(1, 0).rotate(angle) * speed
            velocity.x -= 36.0
            self.particles.append(
                Particle(
                    position=pygame.Vector2(origin),
                    velocity=velocity,
                    color=random.choice([(255, 232, 166), (255, 214, 148), (255, 241, 206)]),
                    width=random.uniform(4.0, 8.0),
                    height=random.uniform(8.0, 14.0),
                    spin=random.uniform(-180.0, 180.0),
                    angle=random.uniform(-20.0, 20.0),
                    lifetime=random.uniform(0.30, 0.55),
                )
            )

    def emit_flap_burst(self, origin: tuple[float, float], count: int = 4) -> None:
        self.emit_feather_burst(origin, count=count)
        # pass

    def emit_pop_burst(self, origin: tuple[float, float], count: int = 10) -> None:
        for _ in range(count):
            angle = random.uniform(0.0, 360.0)
            speed = random.uniform(120.0, 260.0)
            velocity = pygame.Vector2(1, 0).rotate(angle) * speed
            self.particles.append(
                Particle(
                    position=pygame.Vector2(origin),
                    velocity=velocity,
                    color=random.choice([(255, 242, 170), (255, 220, 140), (246, 199, 120)]),
                    width=random.uniform(3.0, 5.0),
                    height=random.uniform(5.0, 8.0),
                    spin=random.uniform(-260.0, 260.0),
                    angle=random.uniform(0.0, 360.0),
                    lifetime=random.uniform(0.18, 0.32),
                )
            )

    def update(self, dt: float) -> None:
        for particle in self.particles:
            particle.update(dt)
        self.particles = [particle for particle in self.particles if particle.alive]

    def draw(self, surface: pygame.Surface) -> None:
        for particle in self.particles:
            particle.draw(surface)
