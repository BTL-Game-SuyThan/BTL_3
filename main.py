from __future__ import annotations

import pygame

from src.core.game import InfiniteFlyerGame
from src.systems.config import GameConfig


def main() -> int:
    pygame.init()
    try:
        game = InfiniteFlyerGame(GameConfig())
        game.run()
    finally:
        pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
