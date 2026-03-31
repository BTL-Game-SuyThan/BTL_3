from __future__ import annotations

from typing import Any

import pygame

from .base import Scene
from src.ui.hud import HUD


def _call_if_present(target: Any, name: str, *args, **kwargs):
    func = getattr(target, name, None)
    if callable(func):
        return func(*args, **kwargs)
    return None


def _read_attr(target: Any, *names: str, default=None):
    for name in names:
        if hasattr(target, name):
            return getattr(target, name)
    return default


class PlayScene(Scene):
    name = "play"

    def __init__(self, game_state) -> None:
        super().__init__(game_state=game_state)
        self.hud = HUD()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.request_scene("menu")
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            _call_if_present(self.game_state, "start")
            _call_if_present(self.game_state, "flap")
            _call_if_present(self.game_state, "handle_input", "flap")
            return

    def update(self, dt: float) -> None:
        _call_if_present(self.game_state, "update", dt)

        if _read_attr(self.game_state, "game_over", "is_game_over", default=False):
            self.request_scene("game_over")

    def render(self, surface: pygame.Surface) -> None:
        renderer = _read_attr(self.game_state, "render", "draw", default=None)
        if callable(renderer):
            renderer(surface)
        else:
            surface.fill((14, 18, 28))

        score = _read_attr(self.game_state, "score", default=0)
        best = _read_attr(self.game_state, "best_score", "high_score", default=None)
        has_shield = _read_attr(self.game_state, "has_shield", default=False)
        self.hud.draw(surface, score=score, best_score=best, has_shield=has_shield)
