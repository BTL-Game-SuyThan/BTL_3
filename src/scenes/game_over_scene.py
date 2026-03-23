from __future__ import annotations

from typing import Any

import pygame

from .base import Scene
from src.ui.prompts import PromptCard, draw_accent_background


def _read_attr(target: Any, *names: str, default=None):
    for name in names:
        if hasattr(target, name):
            return getattr(target, name)
    return default


class GameOverScene(Scene):
    name = "game_over"

    def __init__(self, game_state) -> None:
        super().__init__(game_state=game_state)
        self.card = PromptCard(
            title="Game Over",
            lines=(
                "Press Space to try again",
                "Esc returns to the menu",
            ),
            accent=(255, 118, 118),
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            _call_reset = getattr(self.game_state, "reset", None)
            if callable(_call_reset):
                _call_reset()
            self.request_scene("play")
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.request_scene("menu")

    def update(self, dt: float) -> None:
        _ = dt

    def render(self, surface: pygame.Surface) -> None:
        draw_accent_background(surface, (22, 16, 26), (80, 38, 54))

        width, height = surface.get_size()
        score = _read_attr(self.game_state, "score", default=0)
        best = _read_attr(self.game_state, "best_score", "high_score", default=None)

        self.card.draw(
            surface,
            (width // 2, height // 2 - 6),
            footer=f"Score: {score}" + (f"   Best: {best}" if best is not None else ""),
        )


def _call_if_present(target: Any, name: str, *args, **kwargs):
    func = getattr(target, name, None)
    if callable(func):
        return func(*args, **kwargs)
    return None
