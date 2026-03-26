from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import pygame


ASSET_ROOT = Path("assets/images")
OGA_ROOT = ASSET_ROOT / "oga"
PIPE_ROOT = ASSET_ROOT / "pipes"


def _make_surface(size: tuple[int, int]) -> pygame.Surface:
    return pygame.Surface(size, pygame.SRCALPHA)


def _player_frame(
    size: tuple[int, int], body_color: tuple[int, int, int], wing_angle: float
) -> pygame.Surface:
    surface = _make_surface(size)
    w, h = size
    pygame.draw.ellipse(surface, body_color, (10, 12, w - 24, h - 20))
    pygame.draw.circle(surface, (255, 255, 255), (w - 24, 20), 8)
    pygame.draw.circle(surface, (22, 22, 22), (w - 22, 20), 4)
    pygame.draw.polygon(
        surface, (255, 187, 51), [(w - 18, 28), (w - 2, 34), (w - 18, 40)]
    )
    wing_origin = pygame.Vector2(w * 0.45, h * 0.52)
    wing_length = 22
    wing_width = 12
    direction = pygame.Vector2(math.cos(wing_angle), math.sin(wing_angle))
    ortho = pygame.Vector2(-direction.y, direction.x)
    points = [
        wing_origin + direction * wing_length,
        wing_origin + ortho * wing_width,
        wing_origin - direction * 8,
        wing_origin - ortho * wing_width,
    ]
    pygame.draw.polygon(surface, (255, 242, 105), points)
    return surface


def _coin_frame(radius: int, pulse: int) -> pygame.Surface:
    surface = _make_surface((radius * 2 + 8, radius * 2 + 8))
    center = pygame.Vector2(surface.get_width() / 2, surface.get_height() / 2)
    pygame.draw.circle(surface, (245, 201, 73), center, radius + pulse)
    pygame.draw.circle(surface, (255, 234, 122), center, radius - 3 + pulse)
    pygame.draw.circle(surface, (215, 170, 47), center, radius // 2 + pulse // 2, 3)
    return surface


def _load_image(path: Path) -> pygame.Surface | None:
    if not path.exists():
        return None
    return pygame.image.load(path.as_posix()).convert_alpha()


def _extract_sheet(
    sheet: pygame.Surface, cell_size: tuple[int, int], row: int, column: int
) -> pygame.Surface | None:
    cell_width, cell_height = cell_size
    frame = pygame.Surface(cell_size, pygame.SRCALPHA)
    frame.blit(
        sheet,
        (0, 0),
        pygame.Rect(column * cell_width, row * cell_height, cell_width, cell_height),
    )
    if frame.get_bounding_rect().width == 0:
        return None
    return frame


def _slice_sheet(
    sheet: pygame.Surface, cell_size: tuple[int, int], row: int, columns: int
) -> list[pygame.Surface]:
    frames: list[pygame.Surface] = []
    for col in range(columns):
        frame = _extract_sheet(sheet, cell_size, row, col)
        if frame is not None:
            frames.append(frame)
    return frames


def _scaled_frames(
    frames: list[pygame.Surface], size: tuple[int, int]
) -> list[pygame.Surface]:
    return [pygame.transform.smoothscale(frame, size) for frame in frames]


def _load_theme_backgrounds(config, theme_folder_name: str) -> list[pygame.Surface]:
    theme_path = ASSET_ROOT / "background" / theme_folder_name
    if not theme_path.exists():
        return []

    image_paths = sorted(theme_path.glob("*.png"))
    layers = []
    for path in image_paths:
        img = _load_image(path)
        if img:
            scale_factor = config.screen_height / img.get_height()
            new_width = max(config.screen_width, int(img.get_width() * scale_factor))
            scaled_img = pygame.transform.smoothscale(
                img, (new_width, config.screen_height)
            )
            layers.append(scaled_img)
    return layers


def _build_external_player_frames() -> (
    tuple[list[pygame.Surface], list[pygame.Surface]] | None
):
    bird_sheet = _load_image(OGA_ROOT / "bird_v001_blue_and_yellow.png")
    if bird_sheet is None:
        return None

    idle_frames = [_extract_sheet(bird_sheet, (48, 32), 6, i) for i in range(8)]
    idle_frames = list(filter(lambda x: x is not None, idle_frames))
    flap_frames = [_extract_sheet(bird_sheet, (48, 32), 5, i) for i in range(8)]
    flap_frames = list(filter(lambda x: x is not None, flap_frames))
    if not idle_frames or not flap_frames:
        return None
    return _scaled_frames(idle_frames[:4], (84, 56)), _scaled_frames(
        flap_frames[:4], (84, 56)
    )


def _build_external_collectible_frames() -> list[pygame.Surface] | None:
    coin_sheet = _load_image(OGA_ROOT / "coin.png")
    if coin_sheet is None:
        return None
    frames = _slice_sheet(coin_sheet, (12, 12), row=0, columns=4)
    if not frames:
        return None
    return _scaled_frames(frames, (34, 34))


@dataclass(slots=True)
class AssetBundle:
    background_sets: dict[str, list[pygame.Surface]]
    player_idle_frames: list[pygame.Surface]
    player_flap_frames: list[pygame.Surface]
    collectible_frames: list[pygame.Surface]
    pipe_img: pygame.Surface | None
    dynamic_pipe_img: pygame.Surface | None
    gravity_pipe_img: pygame.Surface | None
    hud_font: pygame.font.Font
    title_font: pygame.font.Font

    def get_background_layers(self, theme: str) -> list[pygame.Surface]:
        return self.background_sets.get(
            theme, self.background_sets.get("rural_area", [])
        )


def build_placeholder_assets(config) -> AssetBundle:
    background_sets = {
        "city_destroyed": _load_theme_backgrounds(config, "city destroyed"),
        "city_night": _load_theme_backgrounds(config, "city night"),
        "rural_area": _load_theme_backgrounds(config, "rural area"),
    }

    player_frames = _build_external_player_frames()
    collectible_frames = _build_external_collectible_frames()

    if player_frames is None:
        player_idle = [
            _player_frame((68, 56), (255, 136, 77), angle)
            for angle in (0.2, 0.0, -0.2, 0.0)
        ]
        player_flap = [
            _player_frame((68, 56), (255, 136, 77), angle)
            for angle in (-0.7, -0.25, 0.2)
        ]
    else:
        player_idle, player_flap = player_frames

    if collectible_frames is None:
        collectible_frames = [
            _coin_frame(
                config.collectible_radius
                if hasattr(config, "collectible_radius")
                else 20,
                pulse,
            )
            for pulse in (0, 1, 2, 1)
        ]

    pipe_img = _load_image(PIPE_ROOT / "green_pipe.png")
    dynamic_pipe_img = _load_image(PIPE_ROOT / "blue_pipe.png")
    gravity_pipe_img = _load_image(PIPE_ROOT / "red_pipe.png")

    return AssetBundle(
        background_sets=background_sets,
        player_idle_frames=player_idle,
        player_flap_frames=player_flap,
        collectible_frames=collectible_frames,
        pipe_img=pipe_img,
        dynamic_pipe_img=dynamic_pipe_img,
        gravity_pipe_img=gravity_pipe_img,
        hud_font=pygame.font.Font(None, 44),
        title_font=pygame.font.Font(None, 72),
    )
