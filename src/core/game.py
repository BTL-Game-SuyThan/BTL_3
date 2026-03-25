from __future__ import annotations

import pygame

from src.core.assets import build_placeholder_assets
from src.core.audio import AudioManager
from src.core.game_world import GameWorld
from src.scenes.base import Scene
from src.scenes.game_over_scene import GameOverScene
from src.scenes.menu_scene import MenuScene
from src.scenes.play_scene import PlayScene
from src.systems.config import GameConfig


class InfiniteFlyerGame:
    def __init__(self, config: GameConfig) -> None:
        self.config = config
        self.screen = pygame.display.set_mode((config.screen_width, config.screen_height))
        pygame.display.set_caption("Infinite Flyer")
        self.clock = pygame.time.Clock()
        self.assets = build_placeholder_assets(config)
        self.audio = AudioManager()
        self.audio.play_music()
        self.game_world = GameWorld(config, self.assets, self.audio)
        self.scenes = self._build_scenes()
        self.current_scene: Scene = self.scenes["menu"]

    def _build_scenes(self) -> dict[str, Scene]:
        return {
            "menu": MenuScene(self.game_world),
            "play": PlayScene(self.game_world),
            "game_over": GameOverScene(self.game_world),
        }

    def _switch_to(self, name: str) -> None:
        if name == "quit":
            raise SystemExit(0)
        if name == "play":
            self.game_world.reset()
        self.current_scene = self.scenes[name]
        self.current_scene.reset()

    def run(self) -> None:
        while True:
            dt = self.clock.tick(self.config.target_fps) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                self.current_scene.handle_event(event)
                next_scene = self.current_scene.consume_scene_request()
                if next_scene == "quit":
                    return
                if next_scene:
                    self._switch_to(next_scene)

            self.current_scene.update(dt)
            next_scene = self.current_scene.consume_scene_request()
            if next_scene == "quit":
                return
            if next_scene:
                self._switch_to(next_scene)
            self.current_scene.render(self.screen)
            pygame.display.flip()
