from __future__ import annotations

import pygame

from .theme import draw_text, get_font


class HUD:
    def __init__(self) -> None:
        self.score_font = get_font(26, bold=True)
        self.info_font = get_font(18, bold=False)

    def draw(
        self,
        surface: pygame.Surface,
        *,
        score: int,
        best_score=None,
        has_shield: bool = False,
    ) -> None:
        width, _ = surface.get_size()

        # Panel background with rounded corners
        panel_rect = pygame.Rect(14, 14, 240, 94)
        panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (8, 12, 20, 170), panel.get_rect(), border_radius=14)
        pygame.draw.rect(
            panel, (255, 255, 255, 22), panel.get_rect(), 1, border_radius=14
        )
        surface.blit(panel, panel_rect.topleft)

        draw_text(
            surface,
            f"Score: {score}",
            size=26,
            color=(245, 247, 255),
            pos=(28, 24),
            bold=True,
        )
        if best_score is not None:
            draw_text(
                surface,
                f"Best: {best_score}",
                size=18,
                color=(184, 198, 226),
                pos=(28, 52),
            )
        shield_text = "Shield: ON" if has_shield else "Shield: OFF"
        shield_color = (138, 224, 255) if has_shield else (160, 166, 182)
        draw_text(
            surface,
            shield_text,
            size=16,
            color=shield_color,
            pos=(28, 74),
        )
