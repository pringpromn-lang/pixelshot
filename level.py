"""level.py — Loads and renders the tilemap, manages spawns and exit"""
import pygame
from settings import *
from enemy import GuardEnemy

# ── Tilemaps ──────────────────────────────────────────────────────────────────
# Key: 0=air  1=solid  S=player spawn  E=enemy  X=exit

# Level 1 — Tutorial: flat floor, simple gaps, 4 enemies
LEVEL_1_MAP = [
    "111111111111111111111111111111111111111111111111",
    "100000000000000000000000000000000000000000000001",
    "100000000000000000000000000000000000000000000001",
    "100000000000000000000000000000000000000000000001",
    "100000000S000000000000000000000000000000000000X1",
    "100000000000001111000000000000111100000000000001",
    "100000000000000000000000E00000000000000000000001",
    "100000000000000000011110000000000001111000000001",
    "100E0000000000000000000000E0000000000000000E0001",
    "111111111111111111111111111111111111111111111111",
]

# Level 2 — Staircase: ascending platforms, enemies on each step
LEVEL_2_MAP = [
    "111111111111111111111111111111111111111111111111",
    "100000000000000000000000000000000000000000000001",
    "100000000000000000000000000000000000000000000001",
    "100000000000000000000000000000000001111111111X01",
    "100000000000000000000000000001111100000000000001",
    "100000000000000000000000011110000000000E0000E001",
    "1000000000000000000001111000000000000000000E0001",
    "10000000000000001111100000000E0000000000000E0001",
    "1S0000E000011110000000000E000000000000000000E001",
    "111111111111111111111111111111111111111111111111",
]

# Level 3 — Towers: tall columns, platforms at different heights, gaps to cross
LEVEL_3_MAP = [
    "111111111111111111111111111111111111111111111111",
    "100000000001000000000100000000010000000001000001",
    "100000000001000000000100000000010000000001000001",
    "100000S00001000000000100000000010000000001000X01",
    "111111110001000110000100001100010000110001000001",
    "100000000000000000000000000000000000000000000001",
    "100E000000000E0000000000E0000000000E00000000E001",
    "100000001100000000011000000001100000000011000001",
    "100000000000000000000000000000000000000000000001",
    "111111111111111111111111111111111111111111111111",
]

# Level 4 — Gauntlet: narrow corridors, enemies in tight spaces
LEVEL_4_MAP = [
    "111111111111111111111111111111111111111111111111",
    "100000000000000000000000000000000000000000000001",
    "111111110000000001111111100000000111111110000001",
    "100000000000E00000000000000E000000000000000E0001",
    "100001111111111110000111111111110000011111111101",
    "10S000000000000000000000000000000000000000000X01",
    "100001111111111110000111111111110000011111111101",
    "100000000E0000000000000000E00000000000000E000001",
    "111111110000000001111111100000000111111110000001",
    "111111111111111111111111111111111111111111111111",
]

# Level 5 — Sky Fortress: floating islands, wide gaps, dense enemies
LEVEL_5_MAP = [
    "111111111111111111111111111111111111111111111111",
    "100000000000000000000000000000000000000000000001",
    "100000000000000000000000000000000000000000000001",
    "1000S000000000000000000000000000000000000000X001",
    "100011100000001110000000011100000001110000011101",
    "100000000000000000000000000000000000000000000001",
    "100000E000000000E0000000E000000000E000000000E001",
    "100000000011100000000111000000011100000001110001",
    "100000000000000000000000000000000000000000000001",
    "111111111111111111111111111111111111111111111111",
]

ALL_MAPS = [LEVEL_1_MAP, LEVEL_2_MAP, LEVEL_3_MAP, LEVEL_4_MAP, LEVEL_5_MAP]

# Per-level visual theme (bg, tile1, tile2, edge)
LEVEL_THEMES = [
    ((18,  18,  28), (45,  45,  60), (35,  35,  50), (60,  60,  80)),   # L1 dark blue
    ((10,  22,  14), (30,  55,  35), (22,  44,  28), (40,  80,  50)),   # L2 green dungeon
    ((20,  12,  28), (55,  35,  65), (44,  28,  52), (80,  50,  90)),   # L3 purple ruins
    ((28,  12,  10), (65,  30,  28), (52,  22,  20), (90,  40,  38)),   # L4 industrial red
    ((10,  20,  30), (30,  55,  75), (22,  44,  62), (50,  80, 110)),   # L5 icy sky blue
]


class Level:
    def __init__(self, level_num=1):
        self.level_num   = max(1, min(level_num, len(ALL_MAPS)))
        self.tile_map    = []
        self.solid_rects = []
        self.spawn_pos   = (100, 100)
        self.exit_rect   = None
        self.enemies     = []
        self.width       = 0
        self.height      = 0
        self._raw_map    = ALL_MAPS[self.level_num - 1]
        self._theme      = LEVEL_THEMES[self.level_num - 1]
        self._font       = None
        self._load(self._raw_map)

    # ── Load ──────────────────────────────────────────────────────────────────
    def _load(self, raw_map):
        self.tile_map    = []
        self.solid_rects = []
        self.enemies     = []
        self.width  = len(raw_map[0]) * TILE_SIZE
        self.height = len(raw_map)    * TILE_SIZE

        for row_i, row in enumerate(raw_map):
            tile_row = []
            for col_i, ch in enumerate(row):
                tx = col_i * TILE_SIZE
                ty = row_i * TILE_SIZE
                tr = pygame.Rect(tx, ty, TILE_SIZE, TILE_SIZE)

                if ch == '1':
                    tile_row.append(TILE_SOLID)
                    self.solid_rects.append(tr)
                elif ch == 'S':
                    tile_row.append(TILE_AIR)
                    self.spawn_pos = (tx, ty - TILE_SIZE // 2)
                elif ch == 'E':
                    tile_row.append(TILE_AIR)
                    self.enemies.append(GuardEnemy(tx, ty - GuardEnemy.H))
                elif ch == 'X':
                    tile_row.append(TILE_AIR)
                    self.exit_rect = pygame.Rect(tx, ty - TILE_SIZE, TILE_SIZE, TILE_SIZE * 2)
                else:
                    tile_row.append(TILE_AIR)
            self.tile_map.append(tile_row)

    def reset(self):
        self._load(self._raw_map)

    def check_completion(self, player_rect):
        return self.exit_rect is not None and player_rect.colliderect(self.exit_rect)

    @property
    def is_last_level(self):
        return self.level_num >= len(ALL_MAPS)

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surface, camera):
        bg, tile_c, tile_c2, edge_c = self._theme

        surface.fill(bg)

        # Faint vertical grid lines
        for x in range(0, self.width, TILE_SIZE * 4):
            sx, _ = camera.apply_point(x, 0)
            if -TILE_SIZE < sx < surface.get_width() + TILE_SIZE:
                r, g, b = bg
                line_c = (min(r+8, 255), min(g+8, 255), min(b+8, 255))
                pygame.draw.line(surface, line_c,
                                 (sx, 0), (sx, surface.get_height()), 1)

        # Tiles
        for row_i, row in enumerate(self.tile_map):
            for col_i, tile in enumerate(row):
                if tile == TILE_AIR:
                    continue
                tx = col_i * TILE_SIZE
                ty = row_i * TILE_SIZE
                sr = camera.apply(pygame.Rect(tx, ty, TILE_SIZE, TILE_SIZE))
                if sr.right < 0 or sr.left > surface.get_width():  continue
                if sr.bottom < 0 or sr.top > surface.get_height(): continue

                shade = tile_c if (row_i + col_i) % 2 == 0 else tile_c2
                pygame.draw.rect(surface, shade, sr)
                pygame.draw.rect(surface, edge_c, sr, 1)

        # Exit marker
        if self.exit_rect:
            er = camera.apply(self.exit_rect)
            exit_surf = pygame.Surface((er.w, er.h), pygame.SRCALPHA)
            exit_surf.fill((60, 220, 80, 70))
            surface.blit(exit_surf, er)
            pygame.draw.rect(surface, C_GREEN, er, 2)
            if self._font is None:
                self._font = pygame.font.SysFont("monospace", 11, bold=True)
            lbl = self._font.render("EXIT", True, C_GREEN)
            surface.blit(lbl, (er.x + er.w//2 - lbl.get_width()//2, er.y + 4))

        # Level indicator
        if self._font is None:
            self._font = pygame.font.SysFont("monospace", 11, bold=True)
        lbl = self._font.render(f"LEVEL {self.level_num} / {len(ALL_MAPS)}", True,
                                tuple(min(c+80, 255) for c in tile_c))
        surface.blit(lbl, (8, 40))
