"""stats_screen.py — In-game statistics dashboard with pygame-drawn graphs"""
import pygame, os, csv, math
from settings import *

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "sessions.csv")

# ── Colour palette ────────────────────────────────────────────────────────────
BG        = ( 10,  10,  18)
PANEL_BG  = ( 18,  18,  30)
PANEL_BDR = ( 45,  45,  65)
COL_WHITE = (230, 230, 240)
COL_GRAY  = (100, 100, 120)
COL_LGRAY = (160, 160, 180)
COL_GOLD  = (255, 215,   0)
COL_GREEN = ( 60, 200,  80)
COL_RED   = (220,  60,  60)
COL_BLUE  = ( 80, 140, 220)
COL_PURP  = (160,  80, 220)
COL_CYAN  = ( 60, 200, 200)
COL_ACCNT = (220, 220,  80)   # yellow accent

RANK_COLS = {
    "S": (255, 215,   0),
    "A": (180, 210,  60),
    "B": (160, 160, 160),
    "C": (180, 130,  80),
    "D": (140,  80,  80),
}

# ── Low-level draw helpers ────────────────────────────────────────────────────
def _panel(surf, rect, title, font_sm):
    pygame.draw.rect(surf, PANEL_BG,  rect, border_radius=6)
    pygame.draw.rect(surf, PANEL_BDR, rect, 1, border_radius=6)
    if title:
        lbl = font_sm.render(title, True, COL_ACCNT)
        surf.blit(lbl, (rect.x + 8, rect.y + 6))

def _hline(surf, colour, x1, y, x2, thick=1):
    pygame.draw.line(surf, colour, (int(x1), int(y)), (int(x2), int(y)), thick)

def _vline(surf, colour, x, y1, y2, thick=1):
    pygame.draw.line(surf, colour, (int(x), int(y1)), (int(x), int(y2)), thick)

def _text(surf, font, text, colour, cx=None, x=None, y=0):
    s = font.render(str(text), True, colour)
    bx = cx - s.get_width()//2 if cx is not None else x
    surf.blit(s, (bx, y))
    return s.get_width()

# ── Graph 1: Line chart — score over sessions ─────────────────────────────────
def draw_score_trend(surf, rect, rows, font_xs):
    _panel(surf, rect, "Score Over Sessions", font_xs)
    if len(rows) < 2:
        _text(surf, font_xs, "Need 2+ sessions", COL_GRAY,
              cx=rect.centerx, y=rect.centery)
        return

    pad_l, pad_r, pad_t, pad_b = 38, 12, 22, 22
    gx = rect.x + pad_l
    gy = rect.y + pad_t
    gw = rect.w - pad_l - pad_r
    gh = rect.h - pad_t - pad_b

    try:
        scores = [int(r["score"]) for r in rows]
    except: return

    mn, mx = min(scores), max(scores)
    rng = max(mx - mn, 1)

    # Axes
    _hline(surf, COL_GRAY, gx, gy + gh, gx + gw)
    _vline(surf, COL_GRAY, gx, gy, gy + gh)

    # Y tick labels
    for i in range(3):
        val = mn + rng * i // 2
        ty  = gy + gh - int(gh * (val - mn) / rng)
        _hline(surf, (35, 35, 50), gx, ty, gx + gw)
        _text(surf, font_xs, f"{val:,}", COL_GRAY, x=rect.x + 2, y=ty - 4)

    # Rolling mean (window=3)
    window = 3
    rolling = []
    for i in range(len(scores)):
        sl = scores[max(0, i - window + 1): i + 1]
        rolling.append(sum(sl) / len(sl))

    # Raw line (faint)
    pts = []
    for i, s in enumerate(scores):
        px = gx + int(i / max(len(scores)-1, 1) * gw)
        py = gy + gh - int((s - mn) / rng * gh)
        pts.append((px, py))
    if len(pts) >= 2:
        pygame.draw.lines(surf, (60, 80, 100), False, pts, 1)

    # Rolling mean line (bright)
    rpts = []
    for i, s in enumerate(rolling):
        px = gx + int(i / max(len(rolling)-1, 1) * gw)
        py = gy + gh - int((s - mn) / rng * gh)
        rpts.append((px, py))
    if len(rpts) >= 2:
        pygame.draw.lines(surf, COL_ACCNT, False, rpts, 2)

    # Dots on latest
    for px, py in pts:
        pygame.draw.circle(surf, COL_BLUE, (px, py), 2)

    # Legend
    pygame.draw.line(surf, (60,80,100), (gx+4, gy+4), (gx+18, gy+4), 1)
    _text(surf, font_xs, "raw", (60,80,100), x=gx+20, y=gy+1)
    pygame.draw.line(surf, COL_ACCNT, (gx+50, gy+4), (gx+64, gy+4), 2)
    _text(surf, font_xs, "avg3", COL_ACCNT, x=gx+66, y=gy+1)

# ── Graph 2: Bar chart — rank distribution ────────────────────────────────────
def draw_rank_bar(surf, rect, rows, font_xs):
    _panel(surf, rect, "Rank Distribution", font_xs)
    if not rows:
        _text(surf, font_xs, "No data", COL_GRAY, cx=rect.centerx, y=rect.centery)
        return

    pad_l, pad_r, pad_t, pad_b = 28, 8, 22, 24
    gx = rect.x + pad_l
    gy = rect.y + pad_t
    gw = rect.w - pad_l - pad_r
    gh = rect.h - pad_t - pad_b

    order = ["S", "A", "B", "C", "D"]
    counts = {r: 0 for r in order}
    for row in rows:
        rk = row.get("rank", "D")
        if rk in counts: counts[rk] += 1

    mx = max(counts.values()) or 1
    bar_w = gw // len(order) - 6

    _hline(surf, COL_GRAY, gx, gy + gh, gx + gw)

    for i, rk in enumerate(order):
        bx  = gx + i * (gw // len(order)) + 3
        bh  = int(counts[rk] / mx * gh)
        by  = gy + gh - bh
        col = RANK_COLS.get(rk, COL_LGRAY)

        if bh > 0:
            pygame.draw.rect(surf, col, (bx, by, bar_w, bh), border_radius=3)
            pygame.draw.rect(surf, (min(col[0]+40,255), min(col[1]+40,255), min(col[2]+40,255)),
                             (bx, by, bar_w, bh), 1, border_radius=3)

        # Label
        _text(surf, font_xs, rk, col,
              cx=bx + bar_w//2, y=gy + gh + 4)
        if counts[rk] > 0:
            _text(surf, font_xs, str(counts[rk]),
                  COL_LGRAY, cx=bx + bar_w//2, y=by - 12)

    # Y axis
    _vline(surf, COL_GRAY, gx, gy, gy + gh)
    for i in range(3):
        val = mx * i // 2
        ty  = gy + gh - int(gh * val / mx)
        _text(surf, font_xs, str(val), COL_GRAY, x=rect.x + 2, y=ty - 4)

# ── Graph 3: Scatter — accuracy vs score ─────────────────────────────────────
def draw_acc_scatter(surf, rect, rows, font_xs):
    _panel(surf, rect, "Accuracy % vs Score", font_xs)
    if len(rows) < 2:
        _text(surf, font_xs, "Need 2+ sessions", COL_GRAY,
              cx=rect.centerx, y=rect.centery)
        return

    pad_l, pad_r, pad_t, pad_b = 38, 10, 22, 22
    gx = rect.x + pad_l
    gy = rect.y + pad_t
    gw = rect.w - pad_l - pad_r
    gh = rect.h - pad_t - pad_b

    try:
        pts_data = [(float(r["accuracy_pct"]), int(r["score"])) for r in rows]
    except: return

    acc_vals  = [p[0] for p in pts_data]
    sc_vals   = [p[1] for p in pts_data]
    acc_mn, acc_mx = 0, max(max(acc_vals), 1)
    sc_mn,  sc_mx  = 0, max(max(sc_vals),  1)

    # Axes
    _hline(surf, COL_GRAY, gx, gy + gh, gx + gw)
    _vline(surf, COL_GRAY, gx, gy, gy + gh)

    # Axis labels
    _text(surf, font_xs, "0%",            COL_GRAY, x=gx,         y=gy+gh+4)
    _text(surf, font_xs, f"{int(acc_mx)}%", COL_GRAY, x=gx+gw-16, y=gy+gh+4)
    _text(surf, font_xs, f"{sc_mx:,}",    COL_GRAY, x=rect.x+1,  y=gy)
    _text(surf, font_xs, "0",             COL_GRAY, x=rect.x+1,  y=gy+gh-8)

    # Grid
    for i in range(1, 4):
        ty = gy + gh * i // 4
        _hline(surf, (30, 30, 48), gx, ty, gx + gw)

    # Points
    screen_pts = []
    for acc, sc in pts_data:
        px = gx + int(acc / acc_mx * gw)
        py = gy + gh - int(sc / sc_mx * gh)
        screen_pts.append((px, py))
        pygame.draw.circle(surf, COL_BLUE, (px, py), 4)
        pygame.draw.circle(surf, COL_WHITE, (px, py), 2)

    # Linear regression line
    if len(pts_data) >= 3:
        n   = len(pts_data)
        sx  = sum(p[0] for p in pts_data)
        sy  = sum(p[1] for p in pts_data)
        sxy = sum(p[0]*p[1] for p in pts_data)
        sx2 = sum(p[0]**2 for p in pts_data)
        denom = n*sx2 - sx*sx
        if abs(denom) > 0.001:
            m = (n*sxy - sx*sy) / denom
            b = (sy - m*sx) / n
            x0, x1 = acc_mn, acc_mx
            y0 = m*x0 + b
            y1 = m*x1 + b
            px0 = gx
            py0 = gy + gh - int(max(0, min(y0, sc_mx)) / sc_mx * gh)
            px1 = gx + gw
            py1 = gy + gh - int(max(0, min(y1, sc_mx)) / sc_mx * gh)
            pygame.draw.line(surf, COL_RED, (px0, py0), (px1, py1), 1)
            # r label
            mean_acc = sx/n;  mean_sc = sy/n
            cov = sum((a-mean_acc)*(s-mean_sc) for a,s in pts_data)/n
            std_a = math.sqrt(sum((a-mean_acc)**2 for a,_ in pts_data)/n or 1)
            std_s = math.sqrt(sum((s-mean_sc)**2 for _,s in pts_data)/n or 1)
            r = cov / (std_a * std_s) if std_a*std_s > 0 else 0
            _text(surf, font_xs, f"r={r:.2f}", COL_RED, x=gx+gw-34, y=gy+4)

# ── Graph 4: Line — bullet-block progression ──────────────────────────────────
def draw_block_trend(surf, rect, rows, font_xs):
    _panel(surf, rect, "Bullet-Block Skill", font_xs)
    if len(rows) < 2:
        _text(surf, font_xs, "Need 2+ sessions", COL_GRAY,
              cx=rect.centerx, y=rect.centery)
        return

    pad_l, pad_r, pad_t, pad_b = 28, 10, 22, 22
    gx = rect.x + pad_l
    gy = rect.y + pad_t
    gw = rect.w - pad_l - pad_r
    gh = rect.h - pad_t - pad_b

    try:
        blocks = [int(r["bullet_blocks"]) for r in rows]
    except: return

    mx = max(max(blocks), 1)
    window = 5
    rolling = []
    for i in range(len(blocks)):
        sl = blocks[max(0, i-window+1): i+1]
        rolling.append(sum(sl)/len(sl))

    _hline(surf, COL_GRAY, gx, gy+gh, gx+gw)
    _vline(surf, COL_GRAY, gx, gy, gy+gh)

    # Y ticks
    for i in range(3):
        val = mx * i // 2
        ty  = gy + gh - int(gh * val / mx)
        _hline(surf, (30,30,48), gx, ty, gx+gw)
        _text(surf, font_xs, str(val), COL_GRAY, x=rect.x+2, y=ty-4)

    # Raw bars (thin)
    for i, b in enumerate(blocks):
        bx = gx + int(i / max(len(blocks)-1,1) * gw)
        by = gy + gh - int(b / mx * gh)
        _vline(surf, (50, 80, 120), bx, by, gy+gh)

    # Rolling mean line
    rpts = [(gx + int(i/max(len(rolling)-1,1)*gw),
             gy + gh - int(v/mx*gh)) for i,v in enumerate(rolling)]
    if len(rpts) >= 2:
        pygame.draw.lines(surf, COL_GREEN, False, rpts, 2)

    # Legend
    pygame.draw.line(surf, (50,80,120), (gx+4, gy+4), (gx+14, gy+4), 1)
    _text(surf, font_xs, "raw", (50,80,120), x=gx+16, y=gy+1)
    pygame.draw.line(surf, COL_GREEN, (gx+42, gy+4), (gx+52, gy+4), 2)
    _text(surf, font_xs, f"avg{window}", COL_GREEN, x=gx+54, y=gy+1)

# ── Graph 5: Stacked bars — shots / kills / blocks per session ────────────────
def draw_combat_bars(surf, rect, rows, font_xs):
    _panel(surf, rect, "Combat per Session", font_xs)
    if not rows:
        _text(surf, font_xs, "No data", COL_GRAY, cx=rect.centerx, y=rect.centery)
        return

    pad_l, pad_r, pad_t, pad_b = 28, 8, 22, 22
    gx = rect.x + pad_l
    gy = rect.y + pad_t
    gw = rect.w - pad_l - pad_r
    gh = rect.h - pad_t - pad_b

    # Show last 15 sessions max
    view = rows[-15:]
    try:
        shots  = [int(r["shots_fired"])    for r in view]
        kills  = [int(r["kill_count"])     for r in view]
        blocks = [int(r["bullet_blocks"])  for r in view]
    except: return

    mx = max(max(shots) if shots else 1, 1)
    n  = len(view)
    bw = max(4, gw // n - 3)

    _hline(surf, COL_GRAY, gx, gy+gh, gx+gw)
    _vline(surf, COL_GRAY, gx, gy, gy+gh)

    for i in range(n):
        bx = gx + int(i / n * gw) + 1
        # Shots (dark)
        sh = int(shots[i] / mx * gh)
        if sh > 0:
            pygame.draw.rect(surf, (50,70,110),
                             (bx, gy+gh-sh, bw, sh), border_radius=2)
        # Kills (mid)
        kh = int(kills[i] / mx * gh)
        if kh > 0:
            pygame.draw.rect(surf, COL_GREEN,
                             (bx, gy+gh-kh, bw, kh), border_radius=2)
        # Blocks (top)
        blh = int(blocks[i] / mx * gh)
        if blh > 0:
            pygame.draw.rect(surf, COL_ACCNT,
                             (bx, gy+gh-blh, min(bw, blh), min(blh,6)),
                             border_radius=1)

    # Y ticks
    for i in range(3):
        val = mx * i // 2
        ty  = gy + gh - int(gh * val / mx)
        _text(surf, font_xs, str(val), COL_GRAY, x=rect.x+2, y=ty-4)

    # Legend
    pygame.draw.rect(surf, (50,70,110), (gx+2, gy+4, 8, 6))
    _text(surf, font_xs, "shots", (50,70,110), x=gx+12, y=gy+1)
    pygame.draw.rect(surf, COL_GREEN,  (gx+46, gy+4, 8, 6))
    _text(surf, font_xs, "kills", COL_GREEN, x=gx+56, y=gy+1)
    pygame.draw.rect(surf, COL_ACCNT, (gx+88, gy+4, 8, 6))
    _text(surf, font_xs, "blocks", COL_ACCNT, x=gx+98, y=gy+1)

# ── Graph 6: Pie — rank share ─────────────────────────────────────────────────
def draw_rank_pie(surf, rect, rows, font_xs):
    _panel(surf, rect, "Rank Share", font_xs)
    if not rows:
        _text(surf, font_xs, "No data", COL_GRAY, cx=rect.centerx, y=rect.centery)
        return

    order = ["S","A","B","C","D"]
    counts = {r: 0 for r in order}
    for row in rows:
        rk = row.get("rank","D")
        if rk in counts: counts[rk] += 1
    total = sum(counts.values()) or 1

    cx = rect.x + rect.w * 2 // 5
    cy = rect.centery + 6
    radius = min(rect.w // 3, rect.h // 2 - 20)

    angle = -math.pi / 2
    for rk in order:
        if counts[rk] == 0: continue
        sweep = 2 * math.pi * counts[rk] / total
        col   = RANK_COLS.get(rk, COL_LGRAY)

        # Draw wedge as polygon
        pts = [(cx, cy)]
        steps = max(3, int(sweep * 20))
        for j in range(steps + 1):
            a = angle + sweep * j / steps
            pts.append((cx + math.cos(a)*radius, cy + math.sin(a)*radius))
        if len(pts) >= 3:
            pygame.draw.polygon(surf, col, pts)
            pygame.draw.polygon(surf, PANEL_BG, pts, 1)

        # Label inside slice
        mid_a = angle + sweep / 2
        lx = cx + math.cos(mid_a) * radius * 0.62
        ly = cy + math.sin(mid_a) * radius * 0.62
        pct = counts[rk] * 100 // total
        if pct >= 8:
            _text(surf, font_xs, f"{pct}%", PANEL_BG,
                  cx=int(lx), y=int(ly)-4)

        angle += sweep

    # Border circle
    pygame.draw.circle(surf, PANEL_BDR, (cx, cy), radius, 1)

    # Legend (right side)
    lx = rect.x + rect.w * 2 // 3
    ly = rect.y + 22
    for rk in order:
        if counts[rk] == 0: continue
        col = RANK_COLS.get(rk, COL_LGRAY)
        pygame.draw.rect(surf, col, (lx, ly, 10, 10), border_radius=2)
        _text(surf, font_xs, f"{rk}  {counts[rk]}", col, x=lx+14, y=ly)
        ly += 16


# ── Summary stat cards ────────────────────────────────────────────────────────
def draw_summary_cards(surf, rect, rows, font_sm, font_xs):
    """Draw a row of 5 summary stat cards."""
    if not rows:
        return

    try:
        scores    = [int(r["score"])           for r in rows]
        deaths    = [int(r["deaths"])           for r in rows]
        blocks    = [int(r["bullet_blocks"])    for r in rows]
        accs      = [float(r["accuracy_pct"])  for r in rows]
        kills     = [int(r["kill_count"])       for r in rows]
        sessions  = len(rows)
    except:
        return

    cards = [
        ("SESSIONS",  str(sessions),                  COL_LGRAY),
        ("BEST SCORE", f"{max(scores):,}",             COL_GOLD),
        ("AVG SCORE",  f"{sum(scores)//sessions:,}",   COL_ACCNT),
        ("AVG ACC",    f"{sum(accs)/sessions:.1f}%",   COL_CYAN),
        ("TOTAL KILLS",f"{sum(kills)}",                COL_GREEN),
        ("BEST BLOCKS",f"{max(blocks)}",               COL_PURP),
    ]

    cw = rect.w // len(cards)
    for i, (label, value, col) in enumerate(cards):
        cr = pygame.Rect(rect.x + i*cw + 3, rect.y, cw - 6, rect.h)
        pygame.draw.rect(surf, PANEL_BG,  cr, border_radius=5)
        pygame.draw.rect(surf, PANEL_BDR, cr, 1, border_radius=5)
        _text(surf, font_sm, value, col,  cx=cr.centerx, y=cr.y + 8)
        _text(surf, font_xs, label, COL_GRAY, cx=cr.centerx, y=cr.y + cr.h - 14)


# ── Main StatsScreen class ────────────────────────────────────────────────────
class StatsScreen:
    TAB_GRAPHS = 0
    TAB_TABLE  = 1

    def __init__(self, screen):
        self.screen     = screen
        self.font_xl    = pygame.font.SysFont("monospace", 26, bold=True)
        self.font_sm    = pygame.font.SysFont("monospace", 13, bold=True)
        self.font_xs    = pygame.font.SysFont("monospace", 10)
        self._tab       = self.TAB_GRAPHS
        self._scroll    = 0
        self._rows      = []
        self._dirty     = True   # reload CSV next draw

    def invalidate(self):
        """Call after a new session is recorded."""
        self._dirty = True

    def _load(self):
        self._rows = []
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, newline="") as f:
                    self._rows = list(csv.DictReader(f))
            except Exception:
                pass
        self._dirty = False

    # ── Draw ─────────────────────────────────────────────────────────────────
    def draw(self, mouse_pos, events):
        """Returns 'back' or None."""
        if self._dirty:
            self._load()

        sw, sh = self.screen.get_width(), self.screen.get_height()
        rows   = self._rows
        surf   = self.screen

        surf.fill(BG)

        # ── Title bar ─────────────────────────────────────────────────────────
        pygame.draw.rect(surf, (16, 16, 28), (0, 0, sw, 40))
        pygame.draw.line(surf, (45, 45, 65), (0, 40), (sw, 40), 1)
        _text(surf, self.font_xl, "PIXEL SHOT  —  STATISTICS", COL_ACCNT,
              cx=sw//2, y=8)
        sess_lbl = self.font_xs.render(
            f"{len(rows)} session{'s' if len(rows)!=1 else ''}", True, COL_GRAY)
        surf.blit(sess_lbl, (sw - sess_lbl.get_width() - 10, 14))

        # ── Tab bar ───────────────────────────────────────────────────────────
        tab_y = 42
        for i, lbl in enumerate(["GRAPHS", "TABLE"]):
            tw   = 90
            tx   = 12 + i * (tw + 6)
            active = (i == self._tab)
            col  = (30, 30, 50) if not active else (50, 50, 80)
            brd  = COL_ACCNT if active else (45, 45, 65)
            r    = pygame.Rect(tx, tab_y, tw, 22)
            pygame.draw.rect(surf, col, r, border_radius=4)
            pygame.draw.rect(surf, brd, r, 1, border_radius=4)
            _text(surf, self.font_xs, lbl,
                  COL_ACCNT if active else COL_GRAY,
                  cx=r.centerx, y=r.y+6)

        # ── Summary cards ─────────────────────────────────────────────────────
        cards_rect = pygame.Rect(0, 68, sw, 52)
        draw_summary_cards(surf, cards_rect, rows, self.font_sm, self.font_xs)

        content_y = 124

        # ── Handle tab clicks ─────────────────────────────────────────────────
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                for i in range(2):
                    tw = 90
                    tx = 12 + i * (tw + 6)
                    if pygame.Rect(tx, tab_y, tw, 22).collidepoint(mx, my):
                        self._tab    = i
                        self._scroll = 0
            if e.type == pygame.MOUSEWHEEL:
                self._scroll -= e.y * 22

        # ── GRAPHS tab ────────────────────────────────────────────────────────
        if self._tab == self.TAB_GRAPHS:
            self._draw_graphs(surf, content_y, sw, sh, rows)

        # ── TABLE tab ─────────────────────────────────────────────────────────
        else:
            self._draw_table(surf, content_y, sw, sh, rows)

        # ── Back button ───────────────────────────────────────────────────────
        btn = pygame.Rect(sw - 90, sh - 36, 80, 28)
        hovered = btn.collidepoint(mouse_pos)
        pygame.draw.rect(surf, (40,40,60) if not hovered else (70,70,100),
                         btn, border_radius=5)
        pygame.draw.rect(surf, COL_ACCNT if hovered else (60,60,90),
                         btn, 1, border_radius=5)
        _text(surf, self.font_xs, "BACK",
              COL_ACCNT if hovered else COL_LGRAY,
              cx=btn.centerx, y=btn.y+8)

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if btn.collidepoint(e.pos):
                    return "back"
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return "back"

        return None

    # ── Graphs layout ─────────────────────────────────────────────────────────
    def _draw_graphs(self, surf, y0, sw, sh, rows):
        pad = 8
        half_w = (sw - pad * 3) // 2
        third_w = (sw - pad * 4) // 3
        row_h1 = (sh - y0 - pad * 3) * 55 // 100
        row_h2 = (sh - y0 - pad * 3) * 45 // 100

        # Row 1: score trend (wide) + rank bar
        r1a = pygame.Rect(pad, y0, half_w, row_h1)
        r1b = pygame.Rect(pad*2+half_w, y0, half_w, row_h1)
        draw_score_trend(surf, r1a, rows, self.font_xs)
        draw_rank_bar   (surf, r1b, rows, self.font_xs)

        # Row 2: acc scatter + block trend + pie
        y2 = y0 + row_h1 + pad
        r2a = pygame.Rect(pad,              y2, third_w, row_h2)
        r2b = pygame.Rect(pad*2+third_w,    y2, third_w, row_h2)
        r2c = pygame.Rect(pad*3+third_w*2,  y2, third_w, row_h2)
        draw_acc_scatter (surf, r2a, rows, self.font_xs)
        draw_block_trend (surf, r2b, rows, self.font_xs)
        draw_rank_pie    (surf, r2c, rows, self.font_xs)

        # No-data notice
        if not rows:
            msg = self.font_sm.render("Play some games first to see graphs!", True, COL_GRAY)
            surf.blit(msg, (sw//2 - msg.get_width()//2, y0 + 80))

    # ── Table layout ──────────────────────────────────────────────────────────
    def _draw_table(self, surf, y0, sw, sh, rows):
        COLS = [
            ("#",              None,               34,  True),
            ("SESSION",        "session_id",       68,  False),
            ("LVL",            "level_id",         32,  True),
            ("SCORE",          "score",             68,  True),
            ("RNK",            "rank",              34,  True),
            ("KILLS",          "kill_count",        46,  True),
            ("BLOCKS",         "bullet_blocks",     52,  True),
            ("SHOTS",          "shots_fired",       48,  True),
            ("ACC%",           "accuracy_pct",      48,  True),
            ("DEATHS",         "deaths",            50,  True),
            ("DASHES",         "dash_count",        54,  True),
            ("SLOW",           "slow_time_uses",    42,  True),
            ("TIME(s)",        "completion_time_ms",62,  True),
            ("DIST(px)",       "pixels_moved",      68,  True),
        ]
        total_w = sum(c[2] for c in COLS)
        sx      = max(8, (sw - total_w) // 2)
        row_h   = 18
        hdr_y   = y0
        content_h = sh - hdr_y - row_h - 44

        max_scroll = max(0, len(rows) * row_h - content_h)
        self._scroll = max(0, min(self._scroll, max_scroll))

        # Header
        pygame.draw.rect(surf, (28, 28, 46), (0, hdr_y, sw, row_h))
        x = sx
        for hdr, _, w, right in COLS:
            lbl = self.font_xs.render(hdr, True, COL_ACCNT)
            bx  = x + w - lbl.get_width() - 2 if right else x + 2
            surf.blit(lbl, (bx, hdr_y + 3))
            x  += w
        pygame.draw.line(surf, (50,50,70), (0, hdr_y+row_h), (sw, hdr_y+row_h), 1)

        # Clip
        clip = pygame.Rect(0, hdr_y+row_h, sw, content_h)
        surf.set_clip(clip)

        if not rows:
            msg = self.font_sm.render("No data yet — play a game first!", True, COL_GRAY)
            surf.blit(msg, (sw//2 - msg.get_width()//2,
                            hdr_y + row_h + content_h//2))
        else:
            for ri, row in enumerate(reversed(rows)):
                ry = hdr_y + row_h + ri*row_h - self._scroll
                if ry+row_h < hdr_y+row_h or ry > hdr_y+row_h+content_h:
                    continue
                bg = (20,20,34) if ri%2==0 else (14,14,26)
                pygame.draw.rect(surf, bg, (0, ry, sw, row_h))

                x = sx
                for ci, (_, key, w, right) in enumerate(COLS):
                    if key is None:
                        val = str(len(rows) - ri)
                    elif key == "completion_time_ms":
                        try:    val = f"{int(row[key])/1000:.1f}"
                        except: val = row.get(key,"")
                    elif key == "accuracy_pct":
                        try:    val = f"{float(row[key]):.1f}"
                        except: val = row.get(key,"")
                    elif key == "pixels_moved":
                        try:    val = f"{int(row[key]):,}"
                        except: val = row.get(key,"")
                    elif key == "score":
                        try:    val = f"{int(row[key]):,}"
                        except: val = row.get(key,"")
                    else:
                        val = row.get(key,"")

                    col = COL_LGRAY
                    if key == "rank":
                        col = RANK_COLS.get(val, COL_LGRAY)
                    elif key == "score":
                        try:
                            sc = int(row.get("score",0))
                            col = COL_GOLD if sc>=RANK_S else COL_ACCNT if sc>=RANK_A else COL_LGRAY
                        except: pass

                    lbl = self.font_xs.render(str(val), True, col)
                    bx  = x + w - lbl.get_width() - 2 if right else x + 2
                    surf.blit(lbl, (bx, ry+3))
                    x += w

                pygame.draw.line(surf, (28,28,44), (0, ry+row_h-1), (sw, ry+row_h-1), 1)

        surf.set_clip(None)

        # Scrollbar
        if rows and max_scroll > 0:
            bar_h = max(16, int(content_h**2 / (len(rows)*row_h)))
            bar_y = hdr_y+row_h + int(self._scroll/max_scroll*(content_h-bar_h))
            pygame.draw.rect(surf, (40,40,60), (sw-5, hdr_y+row_h, 4, content_h), border_radius=2)
            pygame.draw.rect(surf, COL_GRAY,   (sw-5, bar_y, 4, bar_h), border_radius=2)

        hint = self.font_xs.render("scroll: mouse wheel", True, (40,40,60))
        surf.blit(hint, (10, sh-20))
