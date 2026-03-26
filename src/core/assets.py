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
            scaled_img = pygame.transform.smoothscale(img, (new_width, config.screen_height))
            layers.append(scaled_img)
    return layers


def _build_external_backgrounds(config) -> list[pygame.Surface] | None:
    sky_sheet = _load_image(KENNEY_ROOT / "sky.png")
    clouds_strip = _load_image(KENNEY_ROOT / "clouds1.png")
    cloud_1 = _load_image(KENNEY_ROOT / "cloud1.png")
    cloud_5 = _load_image(KENNEY_ROOT / "cloud5.png")
    cloud_9 = _load_image(KENNEY_ROOT / "cloud9.png")
    mountains_strip = _load_image(KENNEY_ROOT / "pointy_mountains.png")
    hills_strip = _load_image(KENNEY_ROOT / "hills1.png")
    mountain_1 = _load_image(KENNEY_ROOT / "mountain1.png")
    mountain_2 = _load_image(KENNEY_ROOT / "mountain2.png")
    mountain_3 = _load_image(KENNEY_ROOT / "mountain3.png")

    required = [sky_sheet, clouds_strip, mountains_strip, hills_strip]
    if any(asset is None for asset in required):
        return None

    layer_width = max(config.screen_width + 500, 2002)
    layer_height = config.screen_height

    sky_layer = _build_layer_surface(layer_width, layer_height)
    sky_tex = pygame.transform.smoothscale(sky_sheet, (layer_width, layer_height))
    sky_layer.blit(sky_tex, (0, 0))
    cloud_band = pygame.transform.smoothscale(clouds_strip, (1001, 206))
    for x in range(0, layer_width + 1001, 1001):
        sky_layer.blit(cloud_band, (x, 28))
    cloud_assets = [cloud_1, cloud_5, cloud_9]
    cloud_positions = [(140, 98), (540, 72), (920, 130), (1320, 84), (1720, 118)]
    for idx, (x, y) in enumerate(cloud_positions):
        cloud = cloud_assets[idx % len(cloud_assets)]
        if cloud is None:
            continue
        scale = 0.9 + (idx % 3) * 0.15
        resized = pygame.transform.smoothscale(
            cloud, (int(cloud.get_width() * scale), int(cloud.get_height() * scale))
        )
        sky_layer.blit(resized, (x, y))

    mountain_layer = _build_layer_surface(layer_width, layer_height)
    mountain_band = pygame.transform.smoothscale(mountains_strip, (1001, 168))
    mountain_band = _tint_surface(mountain_band, (196, 214, 232))
    for x in range(0, layer_width + 1001, 1001):
        mountain_layer.blit(mountain_band, (x, layer_height - 360))
    for idx, mount in enumerate([mountain_1, mountain_2, mountain_3, mountain_2, mountain_1]):
        if mount is None:
            continue
        scale = 0.95 + (idx % 2) * 0.16
        resized = pygame.transform.smoothscale(
            mount, (int(mount.get_width() * scale), int(mount.get_height() * scale))
        )
        mountain_layer.blit(resized, (160 + idx * 360, layer_height - resized.get_height() - 170))

    ground_layer = _build_layer_surface(layer_width, layer_height)
    hills_band = pygame.transform.smoothscale(hills_strip, (1001, 128))
    hills_band = _tint_surface(hills_band, (95, 132, 87))
    for x in range(0, layer_width + 1001, 1001):
        ground_layer.blit(hills_band, (x, layer_height - 238))
    ground_top = layer_height - config.ground_height
    pygame.draw.rect(ground_layer, (111, 156, 83), pygame.Rect(0, ground_top, layer_width, 160))
    pygame.draw.rect(ground_layer, (86, 120, 61), pygame.Rect(0, ground_top + 18, layer_width, 140))
    for stripe in range(0, layer_width, 74):
        pygame.draw.rect(ground_layer, (74, 104, 54), pygame.Rect(stripe, ground_top + 36, 34, 84), border_radius=10)
    pygame.draw.line(ground_layer, (188, 226, 128), (0, ground_top + 2), (layer_width, ground_top + 2), 4)

    return [sky_layer, mountain_layer, ground_layer]


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
    background_sets: dict[str, list[pygame.Surface]]
    player_idle_frames: list[pygame.Surface]
    player_flap_frames: list[pygame.Surface]
    collectible_frames: list[pygame.Surface]
    hud_font: pygame.font.Font
    title_font: pygame.font.Font

    def get_background_layers(self, theme: str) -> list[pygame.Surface]:
        return self.background_sets.get(theme, self.background_sets.get("rural_area", []))


def build_placeholder_assets(config) -> AssetBundle:
    background_sets = {
        "city_destroyed": _load_theme_backgrounds(config, "city destroyed"),
        "city_night": _load_theme_backgrounds(config, "city night"),
        "rural_area": _load_theme_backgrounds(config, "rural area"),
    }

    legacy_bg = _build_external_backgrounds(config)
    if legacy_bg is None:
        sky = _background_layer((config.screen_width, config.screen_height), (182, 223, 255), (164, 205, 235), 1)
        mid = _background_layer((config.screen_width, config.screen_height), (0, 0, 0, 0), (115, 146, 178), 2)
        ground = _background_layer((config.screen_width, config.screen_height), (0, 0, 0, 0), (86, 120, 90), 3)
        legacy_bg = [sky, mid, ground]
    background_sets["legacy"] = legacy_bg

    player_frames = _build_external_player_frames()
    collectible_frames = _build_external_collectible_frames()

    if player_frames is None:
        player_idle = [_player_frame((68, 56), (255, 136, 77), angle) for angle in (0.2, 0.0, -0.2, 0.0)]
        player_flap = [_player_frame((68, 56), (255, 136, 77), angle) for angle in (-0.7, -0.25, 0.2)]
    else:
        player_idle, player_flap = player_frames

    if collectible_frames is None:
        collectible_frames = [_coin_frame(config.collectible_radius if hasattr(config, "collectible_radius") else 20, pulse) for pulse in (0, 1, 2, 1)]

    return AssetBundle(
        background_sets=background_sets,
        player_idle_frames=player_idle,
        player_flap_frames=player_flap,
        collectible_frames=collectible_frames,
        hud_font=pygame.font.Font(None, 44),
        title_font=pygame.font.Font(None, 72),
    )
