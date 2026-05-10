"""settings.py — Global constants for Pixel Shot"""

# ── Screen ────────────────────────────────────────────────────────────────────
SCREEN_W  = 960
SCREEN_H  = 540
FPS       = 60
TILE_SIZE = 32

# ── Sci-fi colour palette ─────────────────────────────────────────────────────
C_BLACK     = (  0,   0,   0)
C_WHITE     = (255, 255, 255)
C_BG        = (  6,   8,  18)    # near-black deep space
C_BG2       = ( 10,  14,  28)    # slightly lighter bg

# Neon cyan — player
C_PLAYER    = ( 40, 220, 255)
C_PLAYER2   = (  0, 140, 200)
C_PLAYER_DIM= (  0,  60, 100)

# Neon red — enemy
C_ENEMY     = (255,  50,  70)
C_ENEMY2    = (180,  20,  40)
C_ENEMY_DIM = ( 80,  10,  20)

# Yellow — bullet player
C_BULLET_P  = (255, 230,  30)
C_BULLET_P2 = (255, 160,   0)

# Red-orange — bullet enemy
C_BULLET_E  = (255,  60,  40)
C_BULLET_E2 = (200,  20,   0)

# Tile colours (per level set in level.py)
C_TILE      = ( 28,  36,  55)
C_TILE2     = ( 20,  28,  45)

# UI / HUD
C_ACCENT    = ( 40, 220, 255)    # neon cyan accent
C_ACCENT2   = (160,  80, 255)    # neon purple
C_GREEN     = ( 40, 255, 120)
C_RED       = (255,  50,  70)
C_GRAY      = ( 80,  90, 110)
C_LTGRAY    = (160, 170, 190)
C_HUD_BG    = (  6,   8,  18)
C_FLASH     = (200, 240, 255)

# Grid / glow
C_GRID      = ( 18,  26,  45)
C_GLOW_P    = ( 20, 100, 160)    # player glow
C_GLOW_E    = (120,  10,  20)    # enemy glow
C_EXIT_COL  = ( 40, 255, 140)

# ── Physics ───────────────────────────────────────────────────────────────────
GRAVITY        = 1400
PLAYER_SPEED   = 260
JUMP_VEL       = -560
DASH_SPEED     = 680
DASH_DURATION  = 0.13
DASH_COOLDOWN  = 0.7
DASH_IFRAME    = 0.13

# ── Slow-time ─────────────────────────────────────────────────────────────────
SLOW_SCALE     = 0.25
SLOW_CHARGES   = 3
SLOW_DURATION  = 2.0

# ── Bullets ───────────────────────────────────────────────────────────────────
BULLET_SPEED_P  = 780
BULLET_SPEED_E  = 320
BULLET_INTERCEPT_DIST = 18

# ── Enemy ─────────────────────────────────────────────────────────────────────
GUARD_SPEED     = 100
GUARD_FIRE_RATE = 1.8
GUARD_DETECT_R  = 340

# ── Scoring ───────────────────────────────────────────────────────────────────
SCORE_KILL      = 200
SCORE_BLOCK     = 300
SCORE_DEATH_PEN = 500

# ── Rank thresholds ───────────────────────────────────────────────────────────
RANK_S = 8000
RANK_A = 6000
RANK_B = 4000
RANK_C = 2000

# ── Level tilemap key ─────────────────────────────────────────────────────────
TILE_AIR      = 0
TILE_SOLID    = 1
TILE_PLATFORM = 2
