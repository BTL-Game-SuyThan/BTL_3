from __future__ import annotations

import pygame

from .base import Scene
from src.ui.prompts import PromptCard, draw_accent_background


class MenuScene(Scene):
    name = "menu"

    def __init__(self, game_state=None) -> None:
        super().__init__(game_state=game_state)
        self.title = "Infinite Flyer"
        self.subtitle = "Flap, glide, and thread the gap."
        self.prompt = PromptCard(
            title="Press Space to Start",
            lines=(
                "Space: flap / glide",
                "Collect coins and survive as long as possible",
            ),
            accent=(255, 194, 92),
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.request_scene("play")
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.request_scene("quit")

    def update(self, dt: float) -> None:
        _ = dt

    def render(self, surface: pygame.Surface) -> None:
        draw_accent_background(surface, (18, 24, 38), (44, 58, 92))

        width, height = surface.get_size()
        title_font = pygame.font.SysFont("verdana", 58, bold=True)
        subtitle_font = pygame.font.SysFont("verdana", 22)

        title_surf = title_font.render(self.title, True, (245, 247, 255))
        subtitle_surf = subtitle_font.render(self.subtitle, True, (190, 202, 227))

        title_rect = title_surf.get_rect(center=(width // 2, height // 3 - 22))
        subtitle_rect = subtitle_surf.get_rect(center=(width // 2, height // 3 + 28))
        surface.blit(title_surf, title_rect)
        surface.blit(subtitle_surf, subtitle_rect)

        self.prompt.draw(surface, (width // 2, height // 2 + 70))
