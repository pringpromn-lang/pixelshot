"""settings.py — Global constants for Pixel Shot"""

# ── Screen ────────────────────────────────────────────────────────────────────
SCREEN_W  = 960
SCREEN_H  = 540
FPS       = 60
TILE_SIZE = 32

# ── Colours (R, G, B) ─────────────────────────────────────────────────────────
C_BLACK   = (  0,   0,   0)
C_WHITE   = (255, 255, 255)
C_BG      = ( 18,  18,  28)   # deep dark blue-black
C_TILE    = ( 45,  45,  60)   # dark tile
C_TILE2   = ( 35,  35,  50)   # alternate tile shade
C_ACCENT  = (220, 220,  80)   # yellow accent
C_RED     = (220,  50,  50)
C_GREEN   = ( 60, 200,  80)
C_GRAY    = (120, 120, 140)
C_LTGRAY  = (180, 180, 200)
C_PLAYER  = (230, 230, 255)
C_BULLET_P= (255, 240,  60)   # player bullet
C_BULLET_E= (255,  80,  80)   # enemy bullet
C_ENEMY   = (200,  80,  80)
C_FLASH   = (255, 255, 200)
C_HUD_BG  = ( 10,  10,  20)

# ── Physics ───────────────────────────────────────────────────────────────────
GRAVITY        = 1400   # px/s²
PLAYER_SPEED   = 260    # px/s
JUMP_VEL       = -560   # px/s
DASH_SPEED     = 680    # px/s
DASH_DURATION  = 0.13   # seconds
DASH_COOLDOWN  = 0.7    # seconds
DASH_IFRAME    = 0.13   # invincibility during dash

# ── Slow-time ─────────────────────────────────────────────────────────────────
SLOW_SCALE     = 0.25
SLOW_CHARGES   = 3
SLOW_DURATION  = 2.0    # seconds per charge

# ── Bullets ───────────────────────────────────────────────────────────────────
BULLET_SPEED_P  = 780   # player bullet px/s
BULLET_SPEED_E  = 320   # enemy bullet px/s
BULLET_INTERCEPT_DIST = 18  # px radius for bullet-block

# ── Enemy ─────────────────────────────────────────────────────────────────────
GUARD_SPEED     = 100
GUARD_FIRE_RATE = 1.8   # seconds between shots
GUARD_DETECT_R  = 340   # detection radius

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
# 0 = air, 1 = solid tile, 2 = platform (one-way), S = player spawn,
# E = enemy spawn, X = exit
TILE_AIR      = 0
TILE_SOLID    = 1
TILE_PLATFORM = 2
