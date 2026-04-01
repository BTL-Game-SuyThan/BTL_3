from __future__ import annotations

import pygame

from src.scenes.base import Scene
from src.ui.theme import Button, draw_text


class InstructionScene(Scene):
    def __init__(self, game_state) -> None:
        super().__init__(game_state)
        self.back_button = Button(pygame.Rect(540, 600, 200, 60), "Back")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.back_button.handle_event(event):
            self.request_scene("menu")
        if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
            self.request_scene("menu")

    def update(self, dt: float) -> None:
        self.game_state.update_background(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.game_state.render_background(surface)
        
        # Dark overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))
        
        draw_text(surface, "How to Play", size=64, color=(255, 255, 255), 
                  pos=(640, 100), anchor="center", bold=True)
        
        instructions = [
            "Press SPACE to flap and stay in the air.",
            "Pass through red pipes to invert gravity!",
            "Avoid green and blue pipes.",
            "Collect coins for extra points.",
            "The further you go, the faster it gets!"
        ]
        
        for i, line in enumerate(instructions):
            draw_text(surface, "• " + line, size=30, color=(230, 230, 230), 
                      pos=(640, 220 + i * 54), anchor="center")
            
        self.back_button.draw(surface)
