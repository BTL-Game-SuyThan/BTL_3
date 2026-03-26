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


class Button:
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font_size: int = 32,
        base_color=(60, 60, 60, 200),
        hover_color=(90, 90, 90, 230),
        text_color=(255, 255, 255),
    ) -> None:
        self.rect = rect
        self.text = text
        self.font_size = font_size
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        color = self.hover_color if self.is_hovered else self.base_color

        # Draw background with alpha support
        s = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(s, color, s.get_rect(), border_radius=12)
        pygame.draw.rect(
            s, (255, 255, 255, 100), s.get_rect(), width=2, border_radius=12
        )
        surface.blit(s, self.rect)

        draw_text(
            surface,
            self.text,
            size=self.font_size,
            color=self.text_color,
            pos=self.rect.center,
            anchor="center",
            bold=True,
        )
