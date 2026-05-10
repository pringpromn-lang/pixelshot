# Project Description

## 1. Project Overview

- **Project Name:** Pixel Shot

- **Brief Description:**
  Pixel Shot is a high-speed, pixel-art 2D action platformer built entirely in Python using the Pygame library. Players control a sci-fi mech suit gunslinger who must fight through five handcrafted levels — from an Orbital Station to a Cryo Fortress — using precise shooting, aggressive dashing, and a unique bullet-block mechanic that lets players destroy incoming enemy bullets mid-air with their own shots.

  The game features a complete statistical tracking system that records every session to a CSV file and visualises the data through an in-game dashboard with six live-rendered graphs. The project combines game development with data collection and analysis, making it both a playable game and a data-driven software system.

- **Problem Statement:**
  Most student game projects focus purely on gameplay with no data layer. Pixel Shot solves this by embedding a full statistical recording and visualisation pipeline directly into the game, producing real session data that can be analysed to study player behaviour, skill progression, and level difficulty — all without leaving the application.

- **Target Users:**
  - Students and casual players who enjoy fast-paced precision platformers
  - Instructors and evaluators reviewing data collection and OOP implementation
  - The developer, for tuning level difficulty using real session data

- **Key Features:**
  - One-hit-kill gun combat with a bullet-vs-bullet interception (bullet-block) mechanic
  - Dash ability with invincibility frames and thruster particle effects
  - Slow-time ability that reduces game speed to 25% for 3 charges per run
  - Five unique sci-fi themed levels with professional platformer design progression
  - Enemy AI using a Finite State Machine (Patrol → Alert → Attack)
  - Full session statistics saved to `sessions.csv` after every run
  - In-game statistics dashboard with 6 pygame-drawn graphs and a scrollable data table
  - S/A/B/C/D rank system based on kills, bullet-blocks, deaths, and time
  - Sci-fi visual theme: neon tile glow, parallax star field, animated exit portal

---

## 2. Concept

### 2.1 Background

- **Why this project exists:**
  The project was created to fulfil a programming course requirement that combines object-oriented design with statistical data collection. Rather than building a generic tool, the goal was to make something that is genuinely engaging to use while still demonstrating all required technical concepts.

- **What inspired the project:**
  The game is directly inspired by *Katana Zero* (Askiisoft, 2019), a commercial 2D action platformer praised for its precise one-hit-kill combat and tight controls. Pixel Shot reinterprets that concept by replacing melee slash-and-deflect with gun-based combat and a bullet-interception system, and by adding a full data analysis layer that Katana Zero does not have.

- **Importance of solving this problem:**
  Fast-paced precision platformers demand that every mechanic be carefully balanced. Without data on how players actually perform — how often they die, where they die, how many bullets they block — balancing is purely guesswork. Pixel Shot makes that data visible and actionable through its built-in statistics system.

### 2.2 Objectives

- Build a fully playable 2D action platformer in Python using Pygame with no external game engine
- Implement a clean object-oriented architecture with clearly separated classes for player, enemies, bullets, levels, camera, UI, and statistics
- Design five handcrafted levels with a clear difficulty progression (easy → medium → hard) verified against real player physics limits
- Record at least 10 statistical features per gameplay session and export them to CSV automatically
- Visualise session data inside the game using six different chart types drawn entirely in Pygame (no matplotlib at runtime)
- Achieve an S/A/B/C/D ranking system that meaningfully reflects player performance

---

## 3. UML Class Diagram

The UML class diagram shows all 9 implemented classes, their attributes (public `+` and private `-`), key methods, inheritance from `GameObject`, and association relationships between classes.

**Diagram file:** [PixelShot_UML.pdf](PixelShot_UML.pdf)

Key relationships:
- `Player`, `Enemy`, and `Bullet` all inherit from `GameObject`
- `GuardEnemy` and `SniperEnemy` extend `Enemy`
- `Bullet` contains bullet-block interception logic (previously a separate `BulletBlock` class, merged per design review feedback)
- `GameStats` feeds data to `UIManager` / `StatsScreen` for display
- `InputHandler` decouples raw Pygame events from game logic

---

## 4. Object-Oriented Programming Implementation

- **Player** — Represents the player-controlled mech suit. Manages movement, shooting toward mouse cursor, dash with invincibility frames, slow-time activation, coyote-time jump buffering, thruster particle effects, and one-hit death handling.

- **Enemy (GuardEnemy)** — Sci-fi drone enemy controlled by a Finite State Machine with four states: Patrol, Alert, Attack, and Dead. Detects the player by proximity, switches states, fires bullets with slight angle noise, and has animated scanner eye and status strip indicators.

- **Bullet** — Represents any projectile (player or enemy). Stores a position trail for visual rendering, updates position each frame, handles tile collision, and contains `check_intercept()` for bullet-vs-bullet collision detection that destroys both bullets on contact.

- **Level** — Loads a level from a character map string, constructs solid collision rects, places enemy and player spawn points, and manages the exit trigger. Renders a layered sci-fi background (gradient, nebula, parallax stars, grid), pre-cached tile variants with neon edge strips, and an animated holographic exit portal.

- **Camera** — Follows the player with smooth interpolation clamped to level bounds. Applies screenshake via a decaying random offset triggered on hit or death events.

- **GameStats** — Records all session statistics in memory during a run using event-driven recorder methods. Exports one CSV row per session to `data/sessions.csv` at run end using Python's built-in `csv` and `uuid` modules.

- **StatsScreen** — Renders the full statistics dashboard in two tabs: a Graphs tab with six pygame-drawn charts (score trend line, rank bar chart, accuracy scatter with regression, bullet-block skill line, combat stacked bar, rank pie), and a Table tab with a scrollable session history of 14 columns.

- **UIManager** — Draws the in-game HUD (score, kills, blocks, deaths, dash cooldown bar, slow-time charges), the start screen with Play/Stats buttons, death screen, next-level transition screen, and end-of-game rank screen.

- **InputHandler** — Polls Pygame's event queue once per frame and stores both `KEYDOWN` and `MOUSEBUTTONDOWN` events in a buffer. Decouples input from game logic to enable reliable jump buffering and action chaining without missed inputs.

---

## 5. Statistical Data

### 5.1 Data Recording Method

Data is recorded using the `GameStats` class, which accumulates counters in memory throughout a session via event-driven recorder methods called by the game loop:

- `record_shot()` — called each time the player fires
- `record_block()` — called each time a bullet intercept succeeds
- `record_dash()` — called each time dash is activated
- `record_kill()` — called each time an enemy is destroyed
- `record_death()` — called on player death
- `record_slow()` — called each time slow-time is activated
- `record_position(x, y)` — called every frame to accumulate pixels moved

At session end (level complete or quit), `GameStats.export_csv()` appends one row to `data/sessions.csv` using Python's `csv.DictWriter`. The header is written only if the file does not yet exist, so data accumulates safely across runs. Each session is identified by a UUID generated with Python's `uuid` module.

### 5.2 Data Features

| Feature (CSV Column) | Description | Type | Possible Range |
|---|---|---|---|
| `session_id` | Unique UUID for the session | String | — |
| `timestamp` | Unix timestamp of session start | Integer | — |
| `level_id` | Level number played | Integer | 1 – 5 |
| `shots_fired` | Total bullets fired by the player | Integer | 0 – unlimited |
| `bullet_blocks` | Successful bullet-vs-bullet intercepts | Integer | 0 – unlimited |
| `accuracy_pct` | Enemy-hitting shots / total shots × 100 | Float | 0.0 – 100.0 |
| `dash_count` | Times dash was activated | Integer | 0 – unlimited |
| `deaths` | Times the player died in a session | Integer | 0 – unlimited |
| `kill_count` | Enemies defeated | Integer | 0 – N (enemies in level) |
| `completion_time_ms` | Milliseconds from start to exit | Integer | 0 – unlimited |
| `pixels_moved` | Total pixel distance travelled | Integer | 0 – unlimited |
| `slow_time_uses` | Times slow-time was activated | Integer | 0 – unlimited |
| `score` | Final composite score | Integer | 0 – unlimited |
| `rank` | Letter rank (S/A/B/C/D) | Categorical | D, C, B, A, S |

---

## 6. Changed Proposed Features

| Proposed | Final | Reason |
|---|---|---|
| `BulletBlock` as a separate class | Merged into `Bullet.check_intercept()` | Reviewer feedback: a normal function/method is sufficient; a dedicated class added unnecessary complexity |
| Slash/melee combat (Katana Zero style) | Gun-based combat with bullet-block | Design decision to differentiate from the reference game and create a more unique mechanic |
| matplotlib for data graphs | All graphs drawn in Pygame directly | Keeps the stats dashboard inside the game window with no external dependency at runtime |
| `SniperEnemy` subclass | Only `GuardEnemy` implemented | Time constraint; FSM complexity was sufficient for prototype scope |
| `BulletBlock` tracked as separate class | Tracked via `Bullet` events in `GameStats` | Follows the merged class design |

---

## 7. External Sources

- **Pygame** — Game library for Python. [https://www.pygame.org](https://www.pygame.org) — LGPL License
- **Python Standard Library** (`csv`, `uuid`, `math`, `random`, `os`) — Used for data recording, unique session IDs, physics calculations, procedural generation, and file I/O. [https://docs.python.org](https://docs.python.org) — PSF License
- **Katana Zero** (Askiisoft, 2019) — Conceptual inspiration for one-hit-kill platformer design. No code, assets, or direct content from this game was used.
- All pixel art, level design, sound effects, and code were created originally for this project.
- No external music, art assets, or third-party code libraries beyond Pygame were used.
