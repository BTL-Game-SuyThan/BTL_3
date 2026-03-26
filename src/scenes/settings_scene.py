from __future__ import annotations

import pygame

from src.scenes.base import Scene
from src.ui.theme import Button, draw_text


class SettingsScene(Scene):
    def __init__(self, game_state) -> None:
        super().__init__(game_state)
        self.buttons: list[tuple[Button, str]] = []
        self._setup_buttons()
        self.back_button = Button(pygame.Rect(540, 600, 200, 60), "Back")

    def _setup_buttons(self) -> None:
        themes = ["rural_area", "city_night", "city_destroyed", "legacy"]
        for i, theme in enumerate(themes):
            rect = pygame.Rect(440, 200 + i * 80, 400, 60)
            display_name = theme.replace("_", " ").title()
            self.buttons.append((Button(rect, display_name), theme))

    def handle_event(self, event: pygame.event.Event) -> None:
        for button, theme in self.buttons:
            if button.handle_event(event):
                self.game_state.change_theme(theme)
        
        if self.back_button.handle_event(event):
            self.request_scene("menu")
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.request_scene("menu")

    def update(self, dt: float) -> None:
        self.game_state.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.game_state.render(surface)
        
        # Dark overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        draw_text(surface, "Settings", size=64, color=(255, 255, 255), 
                  pos=(640, 100), anchor="center", bold=True)
        
        draw_text(surface, f"Current Theme: {self.game_state.config.background_theme.replace('_', ' ').title()}", 
                  size=24, color=(200, 200, 200), pos=(640, 160), anchor="center")

        for button, _ in self.buttons:
            button.draw(surface)
        self.back_button.draw(surface)
