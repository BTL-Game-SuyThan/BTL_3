from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class SpriteAnimation:
    frames: list[pygame.Surface]
    fps: float
    loop: bool = True

    def __post_init__(self) -> None:
        if self.fps <= 0:
            raise ValueError("fps must be positive")
        if not self.frames:
            raise ValueError("frames must not be empty")
        self._frame_time = 1.0 / self.fps
        self._elapsed = 0.0
        self._index = 0
        self._finished = False

    def reset(self) -> None:
        self._elapsed = 0.0
        self._index = 0
        self._finished = False

    def update(self, dt: float) -> None:
        if self._finished:
            return
        self._elapsed += dt
        while self._elapsed >= self._frame_time and not self._finished:
            self._elapsed -= self._frame_time
            self._index += 1
            if self._index >= len(self.frames):
                if self.loop:
                    self._index = 0
                else:
                    self._index = len(self.frames) - 1
                    self._finished = True

    @property
    def current_frame(self) -> pygame.Surface:
        return self.frames[self._index]

    @property
    def frame_index(self) -> int:
        return self._index

