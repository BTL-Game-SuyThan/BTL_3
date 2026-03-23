from __future__ import annotations

from functools import lru_cache

import pygame


@lru_cache(maxsize=16)
def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont("verdana", size, bold=bold)


def draw_text(
    surface: pygame.Surface,
    text: str,
    *,
    size: int,
    color,
    pos,
    anchor: str = "topleft",
    bold: bool = False,
) -> pygame.Rect:
    font = get_font(size, bold=bold)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    setattr(rect, anchor, pos)
    surface.blit(rendered, rect)
    return rect
