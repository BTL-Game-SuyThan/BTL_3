from __future__ import annotations

from dataclasses import dataclass

import pygame

from .theme import draw_text, get_font


def draw_accent_background(surface: pygame.Surface, top_color, bottom_color) -> None:
    width, height = surface.get_size()
    surface.fill(bottom_color)

    gradient = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        blend = y / max(1, height - 1)
        r = int(top_color[0] * (1.0 - blend) + bottom_color[0] * blend)
        g = int(top_color[1] * (1.0 - blend) + bottom_color[1] * blend)
        b = int(top_color[2] * (1.0 - blend) + bottom_color[2] * blend)
        pygame.draw.line(gradient, (r, g, b), (0, y), (width, y))
    surface.blit(gradient, (0, 0))


@dataclass
class PromptCard:
    title: str
    lines: tuple[str, ...]
    accent: tuple[int, int, int] = (255, 194, 92)

    def draw(self, surface: pygame.Surface, center, footer: str | None = None) -> None:
        width, height = surface.get_size()
        card_width = min(560, width - 48)
        card_height = 196 if footer else 176
        card = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        card.fill((10, 14, 24, 190))
        pygame.draw.rect(card, self.accent, card.get_rect(), 2, border_radius=18)
        pygame.draw.rect(card, (255, 255, 255, 28), card.get_rect(), 1, border_radius=18)

        title_font = get_font(34, bold=True)
        line_font = get_font(21, bold=False)
        footer_font = get_font(18, bold=False)

        title_surf = title_font.render(self.title, True, (245, 247, 255))
        card.blit(title_surf, title_surf.get_rect(center=(card_width // 2, 40)))

        y = 82
        for line in self.lines:
            surf = line_font.render(line, True, (192, 204, 228))
            card.blit(surf, surf.get_rect(center=(card_width // 2, y)))
            y += 30

        if footer:
            footer_surf = footer_font.render(footer, True, (225, 233, 247))
            card.blit(footer_surf, footer_surf.get_rect(center=(card_width // 2, card_height - 28)))

        rect = card.get_rect(center=center)
        surface.blit(card, rect)

