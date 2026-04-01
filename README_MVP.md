
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
- [x] Particle effects on flap (feather style)
- [x] Advanced mechanics (gravity shift)
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

