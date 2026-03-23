from __future__ import annotations

from typing import Optional

import pygame


class Scene:
    """Lightweight base class for scene switching and common behavior."""

    name = "scene"

    def __init__(self, game_state=None) -> None:
        self.game_state = game_state
        self.next_scene: Optional[str] = None

    def handle_event(self, event: pygame.event.Event) -> None:
        raise NotImplementedError

    def update(self, dt: float) -> None:
        raise NotImplementedError

    def render(self, surface: pygame.Surface) -> None:
        raise NotImplementedError

    def reset(self) -> None:
        self.next_scene = None

    def request_scene(self, scene_name: str) -> None:
        self.next_scene = scene_name

    def consume_scene_request(self) -> Optional[str]:
        scene_name = self.next_scene
        self.next_scene = None
        return scene_name
