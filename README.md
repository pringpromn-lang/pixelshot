# PIXEL SHOT

A 2D pixel-art action platformer built with Python and Pygame. Dash, shoot, and block enemy bullets across 5 levels — all while your performance data is tracked and visualised in real time.

---

## Requirements

- Python 3.10 or higher
- pip

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/pixelshot.git
cd pixelshot
```

### 2. Create and activate a virtual environment (recommended)

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Game

```bash
python main.py
```

The game window (960 × 540) will open. Use the **PLAY** button on the start screen to begin, or **STATS** to view your session history and data visualisations.

---

## Controls

| Action | Key / Input |
|---|---|
| Move left / right | `A` / `D` or `←` / `→` |
| Jump | `W`, `↑`, or `Space` |
| Shoot | Left mouse click, `J`, or `Z` (aims at cursor) |
| Dash | `Left Shift` |
| Slow-time | `K` or `X` |
| Restart (after death / win) | `R` |
| Quit to menu | `Escape` |

---

## Data

Session statistics are automatically saved to `data/sessions.csv` each time you complete or quit a session. The **STATS** screen reads this file and renders live charts and tables.

---

## Project Structure

```
pixelshot/
├── main.py            # Entry point
├── game.py            # Game loop and state manager
├── player.py          # Player character (movement, dash, slow-time)
├── enemy.py           # GuardEnemy with FSM AI
├── bullet.py          # Projectile and bullet-block logic
├── camera.py          # Smooth-follow camera with screenshake
├── level.py           # Tilemap loader and renderer (5 levels)
├── game_stats.py      # Session statistics recorder and CSV exporter
├── ui_manager.py      # HUD, menus, buttons, rank screen
├── stats_screen.py    # Data visualisation dashboard
├── input_handler.py   # Decoupled input polling
├── settings.py        # Global constants and configuration
├── data/
│   └── sessions.csv   # Persistent session data (auto-generated)
├── requirements.txt
└── README.md
```
