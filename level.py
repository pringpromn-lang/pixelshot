"""level.py — Professional level design with upgraded sci-fi graphics"""
import pygame, math, random
from settings import *
from enemy import GuardEnemy

# ─────────────────────────────────────────────────────────────────────────────
# Physics reference (TILE=32px, player H=28px):
#   Max jump height : 3 tiles  — platforms never 4+ tiles above another
#   Max walk gap    : 6 tiles  — safe horizontal gap without dash
#   Max dash gap    : 13 tiles — requires dash ability
# ─────────────────────────────────────────────────────────────────────────────

# ── LEVEL 1 — Orbital Station ─────────────────────────────────────────────────
# EASY TUTORIAL. Wide open space, clear sight lines, gentle floor gaps.
# Three enemies patrolling the floor zone.
# Route: spawn left → hop two mid platforms → cross gap → collect exit right.
LEVEL_1_MAP = [
    "111111111111111111111111111111111111111111111111",  # ceiling
    "100000000000000000000000000000000000000000000001",
    "100000000000000000000000000000000000000000000001",
    "100000000000000000000000000000000000000000000001",
    "100000000000000000000000000000000000000000000001",
    "1S00000000001111100000000000011111000000000000X1",  # main path level
    "100000000000000000000000000000000000000000000001",
    "100000E00000000000000E000000000000000E0000000001",  # 3 patrolling enemies
    "111111111110000001111111110000001111111111000001",  # floor: 2 gaps to fall in
    "111111111111111111111111111111111111111111111111",
]

# ── LEVEL 2 — Bio Dome ────────────────────────────────────────────────────────
# EASY → MEDIUM. Staircase ascending left to right. Exit is elevated top-right.
# Teaches: riding rising platforms, 3-step staircase, precision 2-tile hops.
# Optional: low path bottom has extra enemy for bonus score.
LEVEL_2_MAP = [
    "111111111111111111111111111111111111111111111111",
    "100000000000000000000000000000000000000000000001",
    "100000000000000000000000000000000000000000000001",
    "100000000000000000000000000000000000000000111X01",  # exit top-right
    "100000000000000000000000000000000001111111000001",  # stair step 3 (wide)
    "100000000000000000000000000011111110000000000001",  # stair step 2 (wide)
    "10000000000000000000011111110000000000000000E001",  # stair step 1 + enemy
    "1S000000E00000111100000000000E000000000000000001",  # spawn + low platform
    "100000000000000000000000000000000000000000000001",  # open bottom
    "111111111111111111111111111111111111111111111111",
]

# ── LEVEL 3 — Ancient Ruins ───────────────────────────────────────────────────
# MEDIUM. Spawn top-right, exit top-left — must traverse whole level in reverse.
# Column towers to climb, gaps between towers, hidden alcove at exit.
# Four enemies spread across low ground.
LEVEL_3_MAP = [
    "111111111111111111111111111111111111111111111111",
    "100000000000000000000000000000000000000000000001",
    "100X00000000000000000000000000000000000000S00001",  # exit top-L, spawn top-R
    "101110000000000011100000000001110000000000011101",  # alcove + column caps
    "100000000000000000000000000000000000000000000001",
    "100000001110000000000011100000000001110000000001",  # mid column platforms
    "100000000000000000000000000000000000000000000001",
    "100E000000000000000E000000000000000E0000000E0001",  # 4 enemies low
    "111110000001111100000001111100000001111100000111",  # floor w/ column bases
    "111111111111111111111111111111111111111111111111",
]

# ── LEVEL 4 — Lava Forge ─────────────────────────────────────────────────────
# MEDIUM-HARD. Horizontal gauntlet: upper corridor and lower corridor.
# Player spawns low-left. Must navigate which route to take.
# Upper route: ceiling platforms, exit at top-right — shorter but enemies above.
# Lower route: floor platforms — longer but safer.
# Narrow 1-tile-high corridors demand precise timing vs enemies.
LEVEL_4_MAP = [
    "111111111111111111111111111111111111111111111111",
    "100000000000000000000000000000000000000000000001",
    "1111111111100000000011111111100000000111111111X1",  # upper ceiling, exit
    "100000000000000E0000000000000000E000000000000001",  # upper corridor narrow
    "100011111111111110000111111111110000011111111101",  # upper floor wall
    "1S0000000000000000000000000000000000000000000001",  # player lower open
    "100001111111111110000111111111110000011111111101",  # lower ceiling wall
    "100000000000000E0000000000000000E000000000000001",  # lower corridor narrow
    "111111111100000000001111111100000000001111111111",  # lower floor gaps
    "111111111111111111111111111111111111111111111111",
]

# ── LEVEL 5 — Cryo Fortress ───────────────────────────────────────────────────
# HARD. Floating island chains. Main path row3 has a long dash-jump gap.
# Lower island chain row7 is an optional riskier route with more enemies.
# Five enemies total. Demands dash mastery and bullet-blocking under pressure.
# Secret: upper rows 1-2 are open — a speedrunner can dash across the top edge.
LEVEL_5_MAP = [
    "111111111111111111111111111111111111111111111111",
    "100000000000000000000000000000000000000000000001",  # secret dash lane (open)
    "100000000000000000000000000000000000000000000001",  # secret dash lane (open)
    "1S000000000000000000000000000000000000000000X001",  # main path: long open gap
    "100000001110000000001110000000001110000000011101",  # main islands (3-tile wide)
    "100000000000000000000000000000000000000000000001",
    "100000E000000000E000000E000000E000000000E0000001",  # enemies on low floor
    "110000000111000000000111000000000111000000001101",  # lower bonus islands
    "100000000000000000000000000000000000000000000001",
    "111111111111111111111111111111111111111111111111",
]

ALL_MAPS = [LEVEL_1_MAP, LEVEL_2_MAP, LEVEL_3_MAP, LEVEL_4_MAP, LEVEL_5_MAP]

# Theme: (bg1, bg2, tile_dark, tile_mid, tile_light, glow, grid, accent)
LEVEL_THEMES = [
    ((4,6,16),  (8,12,24),  (12,22,45),(18,32,60),(24,45,80), (40,130,255),(14,24,48),(40,180,255)),
    ((4,12,6),  (6,18,10),  (10,35,16),(14,50,22),(18,65,30), (40,220,80), (8,26,12), (60,255,100)),
    ((10,4,16), (16,8,26),  (38,16,55),(52,22,75),(68,30,95), (160,60,255),(24,10,38),(200,80,255)),
    ((16,4,4),  (24,8,6),   (60,16,14),(80,22,18),(100,30,22),(255,80,30), (38,10,8), (255,120,40)),
    ((6,14,22), (10,20,32), (18,42,68),(24,56,88),(32,72,110),(60,210,255),(12,28,48),(100,230,255)),
]

LEVEL_NAMES = [
    "SECTOR 1  —  ORBITAL STATION",
    "SECTOR 2  —  BIO DOME",
    "SECTOR 3  —  ANCIENT RUINS",
    "SECTOR 4  —  LAVA FORGE",
    "SECTOR 5  —  CRYO FORTRESS",
]


def _build_tile_variants(theme, ts):
    _, _, tile_dark, tile_mid, tile_light, glow, _, accent = theme
    def make(is_top, is_left, is_right):
        surf = pygame.Surface((ts, ts))
        w, h, pad = ts, ts, 3
        surf.fill(tile_dark)
        pygame.draw.rect(surf, tile_mid, (pad, pad, w-pad*2, h-pad*2), border_radius=2)
        pygame.draw.line(surf, tile_light, (pad, pad),     (w-pad-1, pad), 1)
        pygame.draw.line(surf, tile_light, (pad, pad),     (pad, h-pad-1), 1)
        pygame.draw.line(surf, tile_dark,  (w-pad-1, pad), (w-pad-1, h-pad-1), 1)
        pygame.draw.line(surf, tile_dark,  (pad, h-pad-1), (w-pad-1, h-pad-1), 1)
        for dx in range(pad+3, w-pad-3, 6):
            pygame.draw.line(surf, tile_dark, (dx, h//2), (dx+3, h//2), 1)
        for bx2, by2 in [(pad+2,pad+2),(w-pad-3,pad+2),(pad+2,h-pad-3),(w-pad-3,h-pad-3)]:
            pygame.draw.circle(surf, tile_light, (bx2, by2), 1)
        if is_top:
            pygame.draw.rect(surf, glow,   (0, 0, w, 3))
            pygame.draw.rect(surf, accent, (1, 0, w-2, 1))
        if is_left:  pygame.draw.rect(surf, glow, (0, 0, 2, h))
        if is_right: pygame.draw.rect(surf, glow, (w-2, 0, 2, h))
        pygame.draw.rect(surf, glow, (0, 0, w, h), 1)
        return surf
    return {
        "plain":    make(False, False, False),
        "top":      make(True,  False, False),
        "left":     make(False, True,  False),
        "right":    make(False, False, True),
        "topleft":  make(True,  True,  False),
        "topright": make(True,  False, True),
    }


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
        self._stars      = []
        self._nebula_pts = []
        self._tiles      = {}
        self._load(self._raw_map)
        self._gen_bg()
        self._tiles = _build_tile_variants(self._theme, TILE_SIZE)

    def _gen_bg(self):
        random.seed(self.level_num * 31337)
        self._stars = [{"x": random.uniform(0, SCREEN_W),
                        "y": random.uniform(0, SCREEN_H),
                        "r": random.choice([1,1,1,2]),
                        "layer": random.choice([0.08, 0.18, 0.32]),
                        "speed": random.uniform(0.4, 1.8),
                        "phase": random.uniform(0, math.pi*2)}
                       for _ in range(120)]
        gc = self._theme[7]
        self._nebula_pts = [{"x": random.uniform(0, SCREEN_W),
                             "y": random.uniform(0, SCREEN_H*0.8),
                             "r": random.randint(18, 55),
                             "col": gc if random.random()>0.5 else tuple(v//4 for v in gc)}
                            for _ in range(50)]

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
                if ch == '1':
                    tile_row.append(TILE_SOLID)
                    self.solid_rects.append(pygame.Rect(tx, ty, TILE_SIZE, TILE_SIZE))
                elif ch == 'S':
                    tile_row.append(TILE_AIR)
                    self.spawn_pos = (tx, ty - TILE_SIZE//2)
                elif ch == 'E':
                    tile_row.append(TILE_AIR)
                    self.enemies.append(GuardEnemy(tx, ty - GuardEnemy.H))
                elif ch == 'X':
                    tile_row.append(TILE_AIR)
                    self.exit_rect = pygame.Rect(tx, ty-TILE_SIZE, TILE_SIZE, TILE_SIZE*2)
                else:
                    tile_row.append(TILE_AIR)
            self.tile_map.append(tile_row)

    def reset(self):        self._load(self._raw_map)
    def check_completion(self, r): return self.exit_rect and r.colliderect(self.exit_rect)

    @property
    def is_last_level(self): return self.level_num >= len(ALL_MAPS)

    def _solid(self, ri, ci):
        if ri < 0 or ri >= len(self.tile_map):    return False
        if ci < 0 or ci >= len(self.tile_map[0]): return False
        return self.tile_map[ri][ci] == TILE_SOLID

    def draw(self, surface, camera):
        bg1, bg2, _, _, _, glow, grid_col, accent = self._theme
        t  = pygame.time.get_ticks() / 1000.0
        sw, sh = surface.get_width(), surface.get_height()

        # Background gradient
        for y in range(0, sh, 3):
            ratio = y / sh
            c = tuple(int(bg1[i]+(bg2[i]-bg1[i])*ratio) for i in range(3))
            pygame.draw.line(surface, c, (0,y), (sw,y))

        # Nebula
        for neb in self._nebula_pts:
            nx = (neb["x"] - camera.offset_x*0.04) % (sw+80) - 40
            ny = (neb["y"] - camera.offset_y*0.02) % (sh+80) - 40
            col, r = neb["col"], neb["r"]
            for dr in range(r, r//3, -(max(1,r//3))):
                fade = dr/r
                c = tuple(max(0,min(255,int(v*fade*0.10))) for v in col)
                if any(v>2 for v in c):
                    pygame.draw.circle(surface, c, (int(nx),int(ny)), dr)

        # Stars
        for star in self._stars:
            px = (star["x"] - camera.offset_x*star["layer"]) % (sw+4) - 2
            py = (star["y"] - camera.offset_y*star["layer"]*0.25) % (sh+4) - 2
            tw = int(abs(math.sin(t*star["speed"]+star["phase"]))*55)
            br = 70+tw
            pygame.draw.circle(surface, (br, br, min(br+30,255)), (int(px),int(py)), star["r"])

        # Grid
        gs = TILE_SIZE*3
        for x in range(0, self.width, gs):
            sx2,_ = camera.apply_point(x,0)
            if -2 < sx2 < sw+2:
                pygame.draw.line(surface, grid_col, (int(sx2),0),(int(sx2),sh),1)
        for y in range(0, self.height, gs):
            _,sy2 = camera.apply_point(0,y)
            if -2 < sy2 < sh+2:
                pygame.draw.line(surface, grid_col, (0,int(sy2)),(sw,int(sy2)),1)

        # Tiles
        rows = len(self.tile_map)
        cols = len(self.tile_map[0]) if rows else 0
        for ri in range(rows):
            for ci in range(cols):
                if self.tile_map[ri][ci] != TILE_SOLID: continue
                sr = camera.apply(pygame.Rect(ci*TILE_SIZE, ri*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                if sr.right<0 or sr.left>sw: continue
                if sr.bottom<0 or sr.top>sh: continue

                is_top   = not self._solid(ri-1, ci)
                is_left  = not self._solid(ri, ci-1)
                is_right = not self._solid(ri, ci+1)

                if   is_top and is_left:  key = "topleft"
                elif is_top and is_right: key = "topright"
                elif is_top:              key = "top"
                elif is_left:             key = "left"
                elif is_right:            key = "right"
                else:                     key = "plain"
                surface.blit(self._tiles[key], sr)

                if is_top:
                    pulse = int(abs(math.sin(t*1.4+ci*0.28))*45)
                    pc = tuple(min(glow[i]+pulse,255) for i in range(3))
                    pygame.draw.rect(surface, pc, (sr.x, sr.y, sr.w, 2))
                    for gi in range(1,5):
                        fc = tuple(max(0,glow[i]-gi*35) for i in range(3))
                        if any(v>4 for v in fc):
                            pygame.draw.line(surface, fc, (sr.x,sr.y-gi),(sr.x+sr.w,sr.y-gi))

                if is_top and (ci % 6 == self.level_num % 6):
                    pipe_col = tuple(max(0,v-30) for v in glow)
                    px2 = sr.x + sr.w//2
                    pygame.draw.line(surface, pipe_col, (px2,sr.y+5),(px2,sr.y+sr.h-5),2)
                    pygame.draw.circle(surface, glow, (px2,sr.y+6), 2)
                    pygame.draw.circle(surface, glow, (px2,sr.y+sr.h-6), 2)

        # Exit portal
        if self.exit_rect:
            er    = camera.apply(self.exit_rect)
            pulse = abs(math.sin(t*2.5))
            col   = C_EXIT_COL
            for gi,gap in enumerate([12,7,3]):
                rc = tuple(max(0,min(col[i]-gi*20,255)) for i in range(3))
                pygame.draw.rect(surface, rc, er.inflate(gap*2,gap*2), 1, border_radius=4)
            fill_c = tuple(max(0,min(v//5+int(pulse*25),255)) for v in col)
            pygame.draw.rect(surface, fill_c, er, border_radius=2)
            scan_off = int(t*28)%8
            for ly in range(er.y+scan_off, er.y+er.h, 8):
                if er.y <= ly <= er.y+er.h:
                    pygame.draw.line(surface, tuple(min(v//3,255) for v in col),
                                     (er.x,ly),(er.x+er.w,ly))
            pygame.draw.rect(surface, col, er, 2, border_radius=2)
            ic = tuple(min(v+int(pulse*100),255) for v in col)
            pygame.draw.rect(surface, ic, er.inflate(-4,-4), 1)
            blen=10
            for cx2,cy2,dx,dy in [(er.x,er.y,1,1),(er.x+er.w-1,er.y,-1,1),
                                   (er.x,er.y+er.h-1,1,-1),(er.x+er.w-1,er.y+er.h-1,-1,-1)]:
                pygame.draw.line(surface,C_WHITE,(cx2,cy2),(cx2+dx*blen,cy2),2)
                pygame.draw.line(surface,C_WHITE,(cx2,cy2),(cx2,cy2+dy*blen),2)
            bx2 = er.x+er.w//2
            bb  = int(100+pulse*120)
            pygame.draw.line(surface,(min(col[0],255),min(bb,255),min(bb,255)),
                             (bx2,er.y+3),(bx2,er.y+er.h-3),2)
            if self._font is None:
                self._font = pygame.font.SysFont("monospace",11,bold=True)
            lbl = self._font.render("[ EXIT ]", True, col)
            surface.blit(lbl,(er.x+er.w//2-lbl.get_width()//2, er.y-16))

        # Level name
        if self._font is None:
            self._font = pygame.font.SysFont("monospace",11,bold=True)
        lbl = self._font.render(LEVEL_NAMES[self.level_num-1], True, glow)
        surface.blit(lbl,(8,42))
