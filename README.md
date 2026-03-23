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
- `Esc`: return to menu or quit from the menu

## Implemented Gameplay

- 3-layer seamless parallax background
- Animated player with flap and fall states
- Hybrid flap-and-glide control that stays easy to play
- Procedural obstacle spawning
- 3 obstacle families: pipes, moving pillars, laser gates
- Animated collectibles
- Score, game over, restart loop
- Flap particles
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

- Bird sprite sheet: `assets/images/oga/bird_v001_blue_and_yellow.png`
  Source: [Bird by rmazanek](https://opengameart.org/content/bird-2)
  License: `CC0`
  Usage: player idle and flap animation frames
- Coin sprite sheet: `assets/images/oga/coin.png`
  Source: [coin by kotnaszynce](https://opengameart.org/content/coin-2)
  License: `CC0`
  Usage: collectible animation frames

Included in the repository for future background polish:

- Kenney Background Elements pack files under `assets/images/kenney/`
  Source: [Background Elements by Kenney](https://kenney.nl/assets/background-elements)
  License: `CC0`
  Usage status: downloaded and staged in the repo, but the active parallax background still uses the cleaner procedural version for now

Notes:

- No external audio is included yet.
- Obstacles, particles, and the active parallax layers are currently generated in code.

## Assignment Checklist

### MVP Status

- [x] Infinite horizontal scrolling background
- [x] Minimum 3 parallax layers with distinct speeds
- [x] Seamless looping background
- [x] Player animation driven by delta time
- [x] Player input and gravity-based physics
- [x] Procedural obstacle spawning with randomized vertical placement
- [x] Animated collectibles spawned with obstacles
- [x] Off-screen cleanup for obstacles and collectibles
- [x] Collision with obstacles, ceiling, and floor triggers game over
- [x] Collectibles increase score

### Extension Status

- [x] Dynamic obstacles via moving pillars
- [x] Particle effects on flap
- [x] Difficulty scaling over survival time

### Submission / Polish Status

- [x] README includes controls
- [x] README explains the parallax system
- [x] README documents current asset status
- [ ] Final external art/audio pass
- [ ] Final presentation prep and gameplay capture

## Test Notes

Quick checks currently available:

```bash
python3 -m unittest
```

The automated tests cover a few core behaviors:

- player flap applies upward motion
- collectibles only score once
- laser gates become collidable only after their warning period
