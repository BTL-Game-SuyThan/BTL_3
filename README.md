# Infinite Flyer

`Infinite Flyer` is a `pygame` endless runner that blends the clean one-button rhythm of Flappy Bird with a small jetpack-style glide window. Press `Space` to flap upward; keep holding it very briefly after the flap to soften gravity and get a smoother line through tight gaps.

The current build mixes local procedural art with downloaded free assets so the game is runnable without a separate asset pipeline. The project is organized around scenes, gameplay entities, and systems rather than a single monolithic file.

## Run

```bash
python3 main.py
```

Optional setup with dependencies:

```bash
python3 -m pip install pygame
```

## Controls

- `Space`: start, flap, restart
- `G`: gravity shift during gameplay
- `Esc`: return to menu or quit from the menu

## Implemented Gameplay

- 3-layer seamless parallax background
- Cloud layer integrated into the sky parallax
- Animated player with flap and fall states
- Hybrid flap-and-glide control that stays easy to play
- Gravity-shift mechanic with cooldown
- Procedural obstacle spawning
- 3 obstacle families: pipes, moving pillars, laser gates
- Animated collectibles
- Score, game over, restart loop
- Feather flap particles
- Procedural background music + gameplay SFX (flap, pass, death)
- Difficulty scaling over time

## Project Structure

```text
main.py
src/
  core/
  scenes/
  entities/
  systems/
  ui/
assets/
tests/
```

## Parallax Scrolling Notes

The background uses three independent layers with different speed multipliers. Each layer owns a single wide surface and is drawn twice every frame. As the world scrolls left, the layer advances by `world_speed * multiplier * dt`; once the offset reaches the surface width it wraps back to the beginning. Drawing the same surface at `-offset` and `width - offset` keeps the layer seamless without visible gaps.

## Asset Credits

Active in-game assets:

- Birds sprite sheet: `assets/images/birds/*.png`
  Source: [Birds by MegaCrash](https://megacrash.itch.io/flappy-bird-assets)

- Pipes sprite sheet: `assets/images/pipes/*.png`
  Source: [Pipes by MegaCrash](https://megacrash.itch.io/flappy-bird-assets)

- Coin sprite sheet: `assets/images/oga/coin.png`
  Source: [coin by kotnaszynce](https://opengameart.org/content/coin-2)

- Shield icon:
  Source: [Free Shield and Amulet RPG Icons](https://free-game-assets.itch.io/free-shield-and-amulet-rpg-icons)

Background assets (actively used in-game):

- Parallax background from `assets/images/background/`
  Source: [Parallax (Country side, city night, city destroyed)](https://bongseng.itch.io/parallax-country-side-city-night-city-destroyed)

Notes:

- Audio is generated procedurally in code (no external sound files).
- Obstacles are generated in code with updated stylized surfaces.

## Additional Credits

Windmill: https://senderin.itch.io/2d-windmill
