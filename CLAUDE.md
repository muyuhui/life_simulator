# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**熬过去 (AoGuoQu)** — a Chinese-language life simulation web game. Core mechanic: it's very hard to die; each crisis has a high probability of triggering a "turning point" that saves the player.

## Commands

```bash
# Run the Flask backend (default port 5000)
pip install flask flask-cors
python server.py

# Run with debug mode
LIFE_SIMULATOR_DEBUG=1 python server.py

# Run standalone text prototype (auto mode for testing)
python game.py --auto --years 20

# Run Tkinter GUI version
python gui.py

# Serve static frontend only (no backend)
cd web && python -m http.server 8080
```

No test suite or linters are configured.

## Architecture

Three layers, with `core.py` as the single source of truth for game rules:

### 1. `config.py` — Static game data
Backgrounds, talents, personalities, difficulties, turning point events (generic + background-specific), key age choices at ages 18/22/25/28/35/50, and utility functions (`clamp`, `format_money`). Imported by `core.py`.

### 2. `core.py` — Game rules engine
The `GameState` class holds all game logic in one place. Key design:
- **`to_dict()` / `from_dict()`** for serialization (schema version 1), used for save/load across both Flask sessions and the frontend's localStorage.
- **`next_year()`** — the main tick: applies annual stat decay (modified by personality/talent/pets/house), income calculation (education × job × career), then checks death → key age choices → turning points → small events → holiday events (in that priority order).
- **`apply_action()`** — dispatches quick actions (hospital, psychologist, lottery, dating, buy_property, get_pet, travel, stock, find_job).
- **`check_achievements()`** — called after every mutation to detect newly unlocked achievements.
- **Turning point logic**: triggers when health < 20, money < -50000, or happiness < 10. Uses difficulty-specific `turningRate`. Background-specific events take 80% priority over generic ones. Consecutive turning points may trigger a "人生逆袭" super event.
- **Death check**: health ≤ 0 gives 10% death / 90% turning point.

### 3. `server.py` — Flask API
Thin REST layer. All game logic delegates to `core.GameState`. Game state stored in Flask server-side sessions (`session["game"]`). Key API pattern:
- `with_game()` helper loads session game or returns 404.
- `finish()` helper saves game back to session, checks achievements, returns unified response.
- Response envelope: `{success, game, result, newAchievements}`.

### 4. Web frontend — Vue 3 SPA (`web/`)
- `index.html` loads Vue 3 from CDN (no build step) and mounts the app.
- `web/js/game-vue.js` — single-file Vue app. Talks to Flask API by default; auto-degrades to read-only local mode when backend is unreachable.
- `web/css/style.css` — dark theme with CSS custom properties.
- Frontend is purely a display layer — all game rules execute server-side via API calls.

### Legacy prototypes
- **`game.py`** — standalone text-mode prototype with its own `Player` class. Has duplicated game logic (not using core.py). Supports `--auto` mode for automated testing.
- **`gui.py`** — Tkinter GUI with its own `Player` class and duplicated logic. Not maintained in sync with core.py.
- **`archive/`** — older versions of `game.js`, `index-vue.html`, and `server.py.bak`.

## Key conventions

- All configuration values use string keys (`"1"`, `"2"`, etc.) for backgrounds/talents/personalities/difficulties.
- `clamp()` enforces 0–100 range for health/happiness/career; money has no cap.
- `format_money()` uses Chinese units (万 for 10k+, 亿 for 100M+).
- The `specialBuffs` dict in GameState tracks buffs from key age choices (socialBonus, careerGrowth, entrepreneurBonus, earlyRetire, etc.).
- `spouseType` maps to one of `SPOUSE_TYPES` (frugal/optimistic/career/family) with different gameplay effects.
