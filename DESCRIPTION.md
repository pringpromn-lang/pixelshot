# PIXEL SHOT — Project Description

## Overview

**Pixel Shot** is a 2D action platformer built with Python and Pygame for the Computer Programming II project (01219116/01219117, 2026/2, Section 450). The player navigates through 5 hand-crafted levels, battling pixel-art enemies using a skill-based combat system that rewards accurate shooting, bullet-blocking, and strategic use of abilities.

All gameplay statistics — shots fired, kills, bullet blocks, dash count, deaths, accuracy, score, and movement distance — are recorded per session and exported to a CSV file. An in-game statistics dashboard visualises this data with line charts, bar charts, scatter plots, and a session table, giving players meaningful insight into their performance across sessions.

---

## Concept

The core design philosophy is **risk-versus-reward skill expression**:

- **Shooting** costs nothing but ammo is rewarded by kill score.
- **Bullet-blocking** (intercepting an enemy bullet with a player bullet mid-air) grants bonus score and screen flash feedback.
- **Dashing** grants brief invincibility, allowing the player to avoid damage, but has a cooldown.
- **Slow-time** halts the entire game world at 25% speed for a limited time, with only 3 charges per session.

Each of the 5 levels has a distinct visual theme and layout:

| Level | Theme | Layout Style |
|---|---|---|
| 1 | Dark blue dungeon | Flat floor, wide gaps, tutorial |
| 2 | Green dungeon | Staircase of ascending platforms |
| 3 | Purple ruins | Vertical towers with platforming |
| 4 | Industrial red | Narrow corridor gauntlet |
| 5 | Icy sky blue | Floating islands, wide jumps |

Enemy **GuardEnemies** operate on a finite-state machine (Idle → Patrol → Alert → Attack → Dead) and shoot back with slight angular inaccuracy, creating reactive and challenging encounters.

---

## UML Class Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                              Game                                    │
│  - screen, state, level_num                                          │
│  - level: Level                                                      │
│  - player: Player                                                    │
│  - camera: Camera                                                    │
│  - bullets: list[Bullet]                                             │
│  - stats: GameStats                                                  │
│  - input: InputHandler                                               │
│  - ui: UIManager                                                     │
│  - stats_screen: StatsScreen                                         │
│  + run(clock)                                                        │
│  + _update_playing(dt, raw_dt)                                       │
│  + _update_bullets(dt)                                               │
│  + _draw()                                                           │
└───────────┬─────────────────────────────────────────────────────────┘
            │ owns / manages
    ┌───────┼────────────────────────────────────────────────┐
    │       │                │           │         │          │
    ▼       ▼                ▼           ▼         ▼          ▼
┌───────┐ ┌───────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────────┐
│ Level │ │  Player   │ │ Camera │ │ Bullet │ │GameStat│ │  UIManager   │
│       │ │           │ │        │ │        │ │        │ │              │
│-level_│ │-x, y      │ │-offset │ │-x, y   │ │-shots  │ │-btn_play     │
│ num   │ │-vel_x/y   │ │-shake  │ │-vel_x/y│ │-kills  │ │-btn_stats    │
│-tiles │ │-dash_*    │ │        │ │-active │ │-deaths │ │-btn_back     │
│-solid_│ │-slow_*    │ │+update │ │        │ │-score  │ │              │
│ rects │ │-is_alive  │ │+apply  │ │+update │ │        │ │+draw_hud     │
│-spawn │ │           │ │+shake  │ │+destroy│ │+record_│ │+draw_start_  │
│-exit_ │ │+update(dt)│ │        │ │+check_ │ │ shot() │ │  screen      │
│ rect  │ │+handle_   │ │        │ │ interc.│ │+export_│ │+show_rank_   │
│-enemie│ │  input    │ │        │ │        │ │  csv() │ │  screen      │
│       │ │+shoot_    │ │        │ │        │ │        │ │              │
│+draw  │ │  toward   │ │        │ │        │ │        │ │+draw_death_  │
│+check_│ │+take_dmg  │ │        │ │        │ │        │ │  screen      │
│  compl│ │+draw      │ │        │ │+draw   │ │        │ │+draw         │
└───┬───┘ └───────────┘ └────────┘ └────────┘ └────────┘ └──────────────┘
    │ contains 0..*
    ▼
┌─────────────────────┐         ┌──────────────────────┐
│    GuardEnemy       │         │   InputHandler       │
│                     │         │                      │
│ - state: FSM        │         │ - key_buffer         │
│   (patrol/alert/    │         │ - curr_state         │
│    attack/dead)     │         │                      │
│ - shoot_timer       │         │ + poll() → bool      │
│ - vel_x, vel_y      │         │ + is_pressed(key)    │
│                     │         │ + is_held(key)       │
│ + update(dt, ...)   │         │ + events (property)  │
│ + detect_player     │         └──────────────────────┘
│ + take_damage       │
│ + draw              │         ┌──────────────────────┐
└─────────────────────┘         │    StatsScreen       │
                                │                      │
                                │ - rows (CSV data)    │
          ┌─────────────────────│                      │
          │                     │ + draw(mouse, events)│
          │ Button              │ + invalidate()       │
          │ - rect              └──────────────────────┘
          │ - text
          │ + is_clicked()
          │ + draw()
          └── used by UIManager & StatsScreen
```

### Key Relationships

- **`Game`** is the central controller. It owns one instance each of `Level`, `Player`, `Camera`, `GameStats`, `InputHandler`, `UIManager`, and `StatsScreen`, and manages a shared `list[Bullet]`.
- **`Level`** owns a list of `GuardEnemy` instances and provides `solid_rects` for physics resolution by both `Player` and `GuardEnemy`.
- **`Player`** and **`GuardEnemy`** both append `Bullet` objects to the shared bullet list managed by `Game`.
- **`Bullet.check_intercept()`** implements bullet-vs-bullet collision, called by `Game._update_bullets()`.
- **`GameStats`** records events during gameplay and exports a row to `data/sessions.csv` at session end.
- **`StatsScreen`** reads `data/sessions.csv` and renders visualisation panels using raw Pygame drawing calls.
- **`UIManager`** contains **`Button`** instances and handles all HUD, menu, and overlay rendering.
- **`InputHandler`** decouples raw Pygame event polling from game logic, providing a clean `is_pressed()` / `events` interface.

---

## Design Patterns Used

| Pattern | Where |
|---|---|
| **State Machine (FSM)** | `Game` (START / PLAYING / DEAD / NEXT_LEVEL / WIN) and `GuardEnemy` (patrol / alert / attack / dead) |
| **Observer / Event Buffer** | `InputHandler` buffers `KEYDOWN` + `MOUSEBUTTONDOWN` events and exposes them via a clean API |
| **Strategy (implicit)** | Each game state has its own `_update_*` and `_draw` branch — behaviour swaps without conditionals in rendering |
| **Composition** | `Game` composes all subsystems rather than inheriting from them |
