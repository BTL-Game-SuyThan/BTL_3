from __future__ import annotations

import pygame

from src.scenes.base import Scene
from src.ui.theme import Button, draw_text


class SettingsScene(Scene):
    def __init__(self, game_state) -> None:
        super().__init__(game_state)
        self.theme_buttons: list[tuple[Button, str]] = []
        self.difficulty_buttons: list[tuple[Button, str]] = []
        self.color_buttons: list[tuple[Button, str]] = []
        self._setup_buttons()
        self.back_button = Button(pygame.Rect(540, 640, 200, 60), "Back")

    def _setup_buttons(self) -> None:
        btn_width = 240
        btn_height = 60
        spacing = 30
        label_width = 180
        
        # Calculate total width for center alignment based on 3 buttons
        row_width = 3 * btn_width + 2 * spacing
        total_width = label_width + row_width
        start_x = (1280 - total_width) // 2
        
        # Theme buttons
        themes = ["rural_area", "city_night", "city_destroyed"]
        themes_start_x = start_x + label_width
        for i, theme in enumerate(themes):
            rect = pygame.Rect(themes_start_x + i * (btn_width + spacing), 180, btn_width, btn_height)
            display_name = theme.replace("_", " ").title()
            self.theme_buttons.append((Button(rect, display_name, font_size=24), theme))

        # Difficulty buttons
        difficulties = ["easy", "medium", "hard"]
        diff_start_x = start_x + label_width
        for i, level in enumerate(difficulties):
            rect = pygame.Rect(diff_start_x + i * (btn_width + spacing), 280, btn_width, btn_height)
            self.difficulty_buttons.append((Button(rect, level.title(), font_size=24), level))

        # Color buttons
        colors = ["blue", "brown", "green", "orange", "pink", "red", "white"]
        color_btn_width = 140
        color_btn_height = 60
        color_spacing = 15
        
        # Split color buttons into two rows if they don't fit
        colors_per_row = 4
        colors_start_x = start_x + label_width
        
        for i, color in enumerate(colors):
            row = i // colors_per_row
            col = i % colors_per_row
            rect = pygame.Rect(
                colors_start_x + col * (color_btn_width + color_spacing),
                380 + row * (color_btn_height + color_spacing),
                color_btn_width,
                color_btn_height
            )
            
            # Get preview frame for this color
            idle_frames, _ = self.game_state.assets.get_player_frames(color)
            icon = None
            if idle_frames:
                # Scale down for icon
                icon = pygame.transform.smoothscale(idle_frames[0], (32, 32))
                
            self.color_buttons.append((Button(rect, color.title(), font_size=18, icon=icon), color))

    def handle_event(self, event: pygame.event.Event) -> None:
        for button, theme in self.theme_buttons:
            if button.handle_event(event):
                self.game_state.change_theme(theme)
        
        for button, level in self.difficulty_buttons:
            if button.handle_event(event):
                self.game_state.config.set_difficulty(level)
                self.game_state.config.save()

        for button, color in self.color_buttons:
            if button.handle_event(event):
                self.game_state.config.bird_color = color
                self.game_state.config.save()
                # Need to update current player frames
                idle, flap = self.game_state.assets.get_player_frames(color)
                self.game_state.player.idle_animation.frames = idle
                self.game_state.player.flap_animation.frames = flap
        
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

        current_color = self.game_state.config.bird_color
        for button, color in self.color_buttons:
            button.is_active = (color == current_color)

    def render(self, surface: pygame.Surface) -> None:
        self.game_state.render_background(surface)
        
        # Dark overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))
        
        draw_text(surface, "Settings", size=64, color=(255, 255, 255), 
                  pos=(640, 80), anchor="center", bold=True)
        
        # Labels and buttons
        label_x = (1280 - (180 + 3 * 240 + 2 * 30)) // 2
        
        draw_text(surface, "Theme:", size=32, color=(220, 220, 220), 
                  pos=(label_x, 180 + 30), anchor="midleft", bold=True)
        for button, _ in self.theme_buttons:
            button.draw(surface)
            
        draw_text(surface, "Difficulty:", size=32, color=(220, 220, 220), 
                  pos=(label_x, 280 + 30), anchor="midleft", bold=True)
        for button, _ in self.difficulty_buttons:
            button.draw(surface)

        draw_text(surface, "Bird Color:", size=32, color=(220, 220, 220), 
                  pos=(label_x, 380 + 30), anchor="midleft", bold=True)
        for button, _ in self.color_buttons:
            button.draw(surface)
            
        self.back_button.draw(surface)
