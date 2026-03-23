from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import pygame


ASSET_ROOT = Path("assets/images")
KENNEY_ROOT = ASSET_ROOT / "kenney"
OGA_ROOT = ASSET_ROOT / "oga"


def _make_surface(size: tuple[int, int]) -> pygame.Surface:
    return pygame.Surface(size, pygame.SRCALPHA)


def _player_frame(size: tuple[int, int], body_color: tuple[int, int, int], wing_angle: float) -> pygame.Surface:
    surface = _make_surface(size)
    w, h = size
    pygame.draw.ellipse(surface, body_color, (10, 12, w - 24, h - 20))
    pygame.draw.circle(surface, (255, 255, 255), (w - 24, 20), 8)
    pygame.draw.circle(surface, (22, 22, 22), (w - 22, 20), 4)
    pygame.draw.polygon(surface, (255, 187, 51), [(w - 18, 28), (w - 2, 34), (w - 18, 40)])
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


def _background_layer(size: tuple[int, int], sky_color: tuple[int, int, int], hill_color: tuple[int, int, int], depth: int) -> pygame.Surface:
    width, height = size
    surface = _make_surface(size)
    surface.fill(sky_color)
    band_height = max(100, 160 - depth * 15)
    base_y = height - band_height
    for idx in range(7):
        peak_x = idx * (width // 6) + (depth * 20)
        peak_height = 40 + ((idx + depth) % 3) * 25 + depth * 8
        points = [
            (peak_x - 160, height),
            (peak_x - 70, base_y + 25),
            (peak_x, base_y - peak_height),
            (peak_x + 80, base_y + 35),
            (peak_x + 170, height),
        ]
        pygame.draw.polygon(surface, hill_color, points)
    return surface


def _load_image(path: Path) -> pygame.Surface | None:
    if not path.exists():
        return None
    return pygame.image.load(path.as_posix()).convert_alpha()


def _slice_sheet(sheet: pygame.Surface, cell_size: tuple[int, int], row: int, columns: int) -> list[pygame.Surface]:
    cell_width, cell_height = cell_size
    frames: list[pygame.Surface] = []
    for col in range(columns):
        frame = pygame.Surface(cell_size, pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), pygame.Rect(col * cell_width, row * cell_height, cell_width, cell_height))
        if frame.get_bounding_rect().width == 0:
            continue
        frames.append(frame)
    return frames


def _scaled_frames(frames: list[pygame.Surface], size: tuple[int, int]) -> list[pygame.Surface]:
    return [pygame.transform.smoothscale(frame, size) for frame in frames]


def _build_layer_surface(layer_width: int, layer_height: int) -> pygame.Surface:
    return pygame.Surface((layer_width, layer_height), pygame.SRCALPHA)


def _tint_surface(surface: pygame.Surface, color: tuple[int, int, int]) -> pygame.Surface:
    tinted = surface.copy()
    tinted.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted


def _build_external_backgrounds(config) -> list[pygame.Surface] | None:
    _ = config
    return None


def _build_external_player_frames() -> tuple[list[pygame.Surface], list[pygame.Surface]] | None:
    bird_sheet = _load_image(OGA_ROOT / "bird_v001_blue_and_yellow.png")
    if bird_sheet is None:
        return None

    idle_frames = _slice_sheet(bird_sheet, (48, 32), row=2, columns=6)
    flap_frames = _slice_sheet(bird_sheet, (48, 32), row=6, columns=6)
    if not idle_frames or not flap_frames:
        return None
    return _scaled_frames(idle_frames[:4], (84, 56)), _scaled_frames(flap_frames[:4], (84, 56))


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
    background_layers: list[pygame.Surface]
    player_idle_frames: list[pygame.Surface]
    player_flap_frames: list[pygame.Surface]
    collectible_frames: list[pygame.Surface]
    hud_font: pygame.font.Font
    title_font: pygame.font.Font


def build_placeholder_assets(config) -> AssetBundle:
    background_layers = _build_external_backgrounds(config)
    player_frames = _build_external_player_frames()
    collectible_frames = _build_external_collectible_frames()

    if background_layers is None:
        sky = _background_layer((config.screen_width, config.screen_height), (182, 223, 255), (164, 205, 235), 1)
        mid = _background_layer((config.screen_width, config.screen_height), (0, 0, 0, 0), (115, 146, 178), 2)
        ground = _background_layer((config.screen_width, config.screen_height), (0, 0, 0, 0), (86, 120, 90), 3)
        background_layers = [sky, mid, ground]

    if player_frames is None:
        player_idle = [_player_frame((68, 56), (255, 136, 77), angle) for angle in (0.2, 0.0, -0.2, 0.0)]
        player_flap = [_player_frame((68, 56), (255, 136, 77), angle) for angle in (-0.7, -0.25, 0.2)]
    else:
        player_idle, player_flap = player_frames

    if collectible_frames is None:
        collectible_frames = [_coin_frame(config.collectible_radius if hasattr(config, "collectible_radius") else 20, pulse) for pulse in (0, 1, 2, 1)]

    return AssetBundle(
        background_layers=background_layers,
        player_idle_frames=player_idle,
        player_flap_frames=player_flap,
        collectible_frames=collectible_frames,
        hud_font=pygame.font.Font(None, 44),
        title_font=pygame.font.Font(None, 72),
    )
