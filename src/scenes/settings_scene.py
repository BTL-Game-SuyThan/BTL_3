from __future__ import annotations

import pygame

from src.scenes.base import Scene
from src.ui.theme import Button, draw_text


class SettingsScene(Scene):
    def __init__(self, game_state) -> None:
        super().__init__(game_state)
        self.theme_buttons: list[tuple[Button, str]] = []
        self.difficulty_buttons: list[tuple[Button, str]] = []
        self._setup_buttons()
        self.back_button = Button(pygame.Rect(540, 600, 200, 60), "Back")

    def _setup_buttons(self) -> None:
        btn_width = 240
        btn_height = 60
        spacing = 30
        label_width = 180
        total_width = label_width + (3 * btn_width + 2 * spacing)
        start_x = (1280 - total_width) // 2
        
        # Theme buttons
        themes = ["rural_area", "city_night", "city_destroyed"]
        themes_start_x = start_x + label_width
        for i, theme in enumerate(themes):
            rect = pygame.Rect(themes_start_x + i * (btn_width + spacing), 250, btn_width, btn_height)
            display_name = theme.replace("_", " ").title()
            self.theme_buttons.append((Button(rect, display_name, font_size=24), theme))

        # Difficulty buttons
        difficulties = ["easy", "medium", "hard"]
        diff_start_x = start_x + label_width
        for i, level in enumerate(difficulties):
            rect = pygame.Rect(diff_start_x + i * (btn_width + spacing), 400, btn_width, btn_height)
            self.difficulty_buttons.append((Button(rect, level.title(), font_size=24), level))

    def handle_event(self, event: pygame.event.Event) -> None:
        for button, theme in self.theme_buttons:
            if button.handle_event(event):
                self.game_state.change_theme(theme)
        
        for button, level in self.difficulty_buttons:
            if button.handle_event(event):
                self.game_state.config.set_difficulty(level)
                self.game_state.config.save()
        
        if self.back_button.handle_event(event):
            self.request_scene("menu")
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.request_scene("menu")

    def update(self, dt: float) -> None:
        self.game_state.update_background(dt)
        
        # Update active states
        current_theme = self.game_state.config.background_theme
        for button, theme in self.theme_buttons:
            button.is_active = (theme == current_theme)
            
        current_diff = self.game_state.config.difficulty
        for button, level in self.difficulty_buttons:
            button.is_active = (level == current_diff)

    def render(self, surface: pygame.Surface) -> None:
        self.game_state.render_background(surface)
        
        # Dark overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))
        
        draw_text(surface, "Settings", size=64, color=(255, 255, 255), 
                  pos=(640, 100), anchor="center", bold=True)
        
        # Labels and buttons
        label_x = (1280 - (180 + 3 * 240 + 2 * 30)) // 2
        
        draw_text(surface, "Theme:", size=32, color=(220, 220, 220), 
                  pos=(label_x, 250 + 30), anchor="midleft", bold=True)
        for button, _ in self.theme_buttons:
            button.draw(surface)
            
        draw_text(surface, "Difficulty:", size=32, color=(220, 220, 220), 
                  pos=(label_x, 400 + 30), anchor="midleft", bold=True)
        for button, _ in self.difficulty_buttons:
            button.draw(surface)
            
        self.back_button.draw(surface)
