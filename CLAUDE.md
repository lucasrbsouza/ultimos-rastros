# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About the Project

**Últimos Rastros** is a 2D platformer built with Python and Pygame, themed around Brazilian folklore. The player controls the Curupira collecting memories across a tile-based level.

## Running the Game

```bash
python main.py
```

Requires `pygame` installed:
```bash
pip install pygame
```

There are no tests or linting setup in this project.

## Architecture Overview

### Game Loop & State Machine (`main.py`)
`Game` manages a simple state machine with states: `MENU`, `GAMEPLAY`, `GAMEOVER`, `VICTORY`, `CREDITS`. State transitions also handle BGM switching. On each frame, it calls `handle_events → update → draw` in sequence. The level is re-instantiated on retry/new game.

### Level System (`level.py`, `levels.py`)
`Level` owns all sprite groups and orchestrates the game loop logic:
- Reads `LEVEL_MAP` from `levels.py` (a list of strings) and parses each character into the appropriate sprite
- Runs collision detection manually each frame (horizontal first, then vertical via `apply_gravity`)
- Camera scrolling is done by shifting all sprite `rect.x` values via `world_shift` (not a real camera)
- Returns `"GAMEOVER"` or `"VICTORY"` strings from `run()` to signal state changes

**Level map legend:** `X`=grass tile, `D`=dirt, `P`=player spawn, `E`=enemy, `M`=memory collectible, `G`=goal, `W`=water, `1-3`=trees, `4-6`=bushes

### Player (`player.py`)
Extends `pygame.sprite.Sprite`. Key mechanics:
- **Coyote time**: `coyote_timer` allows jumping for a few frames after walking off a ledge
- **Jump buffer**: `jump_buffer_timer` remembers jump input for a few frames before landing
- **Double-tap to run**: `handle_event()` tracks key timing; two taps within `_double_tap_window` ms activates running
- **Knockback**: `take_damage()` sets `is_invincible=True` and applies directional impulse; input is blocked during invincibility frames
- The player hitbox (`rect`) is separate from the visual sprite (`image`); visual is aligned to `rect.midbottom`

### Sprites (`sprites.py`)
- `BaseTile` extracts tiles from `assets/Tileset.png` using a 16px grid, then scales to `TILE_SIZE` (60px)
- `Enemy` uses a two-state AI: `patrol` (bounces within `patrol_range` of spawn) → `chase` (pursues player within `detect_range`); `player_ref` is injected by `Level` after instantiation. Has 3 HP; flashes on hit. Animation frames are loaded automatically from `assets/enemies/fly/fly_XX.png` — just add/remove files and the count adjusts with no code changes
- `FireArrow` is the player's projectile: loaded from `assets/player_power/Fire Arrow/PNG/Fire Arrow_Frame_XX.png` (8 frames), travels horizontally, auto-destroys off-screen. Deals 1 damage per hit
- `Memory` is an animated sprite (spritesheet); `Goal` triggers victory on collision

### Background & UI
- `ParallaxBackground` (`background.py`): 5-layer parallax using `assets/background_parallax/1-5.png`, driven by `world_shift`
- `HUD` (`ui.py`): draws health bar and memory counter directly onto the display surface each frame
- `menu.py`: `MainMenu`, `GameOverMenu`, `VictoryMenu`, `CreditsMenu` — each is a self-contained class with `handle_event`, `update`, and `draw`

### Settings (`settings.py`, `levels.py`)
`settings.py` imports from `levels.py` and re-exports all constants. Key values: `TILE_SIZE=60`, `SCREEN_WIDTH=1280`, `SCREEN_HEIGHT=680`, `FPS=60`. Player spritesheet frame dimensions are configured here.

## Asset Structure

```
assets/
  player_spritesheet/   # Idle.png, Walk.png, Run.png, Jump.png
  sounds/               # menu_bgm.mp3, game_bgm.mp3, jump.mp3, damage.mp3, collect.wav, gameover.mp3, victory.mp3
  background_parallax/  # 1.png through 5.png (layered, back to front)
  backgrounds_statics/  # bg_menu.png, bg_gameover.png, bg_victory.png
  objetos/              # Trees/1-3.png, Bushes/4-6.png
  Tileset.png           # 16px grid spritesheet for tiles
  Rune.png              # Memory collectible spritesheet (4 frames)
  enemy.svg             # Enemy sprite
  goal.png              # Goal/exit sprite
```

Missing assets print warnings but use colored fallback surfaces — the game will still run.
