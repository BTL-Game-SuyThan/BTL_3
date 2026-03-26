from __future__ import annotations

import pygame

from .base import Scene
from src.ui.theme import Button, draw_text
from src.ui.prompts import draw_accent_background


class MenuScene(Scene):
    name = "menu"

    def __init__(self, game_state=None) -> None:
        super().__init__(game_state=game_state)
        self.title = "Infinite Flyer"
        self.subtitle = "Flap, glide, and thread the gap."
        
        button_width = 320
        button_height = 60
        start_y = 360
        spacing = 80
        
        self.buttons = {
            "play": Button(pygame.Rect((1280 - button_width) // 2, start_y, button_width, button_height), "Start Game"),
            "instructions": Button(pygame.Rect((1280 - button_width) // 2, start_y + spacing, button_width, button_height), "Instructions"),
            "settings": Button(pygame.Rect((1280 - button_width) // 2, start_y + spacing * 2, button_width, button_height), "Settings"),
            "quit": Button(pygame.Rect((1280 - button_width) // 2, start_y + spacing * 3, button_width, button_height), "Quit")
        }

    def handle_event(self, event: pygame.event.Event) -> None:
        for action, button in self.buttons.items():
            if button.handle_event(event):
                self.request_scene(action)
                
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.request_scene("play")
            elif event.key == pygame.K_ESCAPE:
                self.request_scene("quit")

    def update(self, dt: float) -> None:
        # We can update the game world in the background for a live menu feel
        if self.game_state:
            self.game_state.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        if self.game_state:
            self.game_state.render(surface)
            # Darken the background a bit for readability
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 80))
            surface.blit(overlay, (0, 0))
        else:
            draw_accent_background(surface, (18, 24, 38), (44, 58, 92))

        width, height = surface.get_size()
        
        draw_text(surface, self.title, size=82, color=(255, 255, 255), 
                  pos=(width // 2, height // 3 - 40), anchor="center", bold=True)
        draw_text(surface, self.subtitle, size=28, color=(200, 210, 230), 
                  pos=(width // 2, height // 3 + 50), anchor="center")

        for button in self.buttons.values():
            button.draw(surface)
