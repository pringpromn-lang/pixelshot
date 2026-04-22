"""ui_manager.py — HUD, menus, rank screen, stats screen"""
import pygame, os, csv
from settings import *

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "sessions.csv")

# ── Simple button helper ──────────────────────────────────────────────────────
class Button:
    def __init__(self, x, y, w, h, text, font):
        self.rect   = pygame.Rect(x, y, w, h)
        self.text   = text
        self.font   = font
        self.hovered = False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.rect.collidepoint(e.pos):
                    return True
        return False

    def draw(self, surface):
        bg  = (60, 60, 80) if not self.hovered else (100, 100, 140)
        border = C_ACCENT if self.hovered else C_LTGRAY
        pygame.draw.rect(surface, bg,     self.rect, border_radius=6)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=6)
        lbl = self.font.render(self.text, True, C_WHITE if not self.hovered else C_ACCENT)
        surface.blit(lbl, (self.rect.centerx - lbl.get_width() // 2,
                           self.rect.centery - lbl.get_height() // 2))


class UIManager:
    def __init__(self, screen):
        self.screen     = screen
        self._font_xl   = pygame.font.SysFont("monospace", 38, bold=True)
        self._font_lg   = pygame.font.SysFont("monospace", 28, bold=True)
        self._font_md   = pygame.font.SysFont("monospace", 16, bold=True)
        self._font_sm   = pygame.font.SysFont("monospace", 12)
        self._font_xs   = pygame.font.SysFont("monospace", 10)
        self._combo      = 0
        self._combo_timer = 0.0

        cx = screen.get_width() // 2
        cy = screen.get_height() // 2

        # Start screen buttons
        self.btn_play  = Button(cx - 110, cy + 20,  100, 40, "PLAY",  self._font_md)
        self.btn_stats = Button(cx + 10,  cy + 20,  100, 40, "STATS", self._font_md)

        # Stats screen button
        self.btn_back  = Button(cx - 50, screen.get_height() - 55, 100, 36, "BACK", self._font_md)

        # Stats screen scroll
        self._stats_scroll = 0

    # ── Button accessors (game.py checks these) ───────────────────────────────
    def update_buttons(self, mouse_pos, events):
        """Call each frame; returns 'play', 'stats', 'back', or None."""
        self.btn_play.update(mouse_pos)
        self.btn_stats.update(mouse_pos)
        self.btn_back.update(mouse_pos)
        if self.btn_play.is_clicked(events):  return "play"
        if self.btn_stats.is_clicked(events): return "stats"
        if self.btn_back.is_clicked(events):  return "back"
        return None

    # ── Combo ─────────────────────────────────────────────────────────────────
    def add_combo(self):
        self._combo += 1
        self._combo_timer = 1.2

    def update(self, dt):
        self._combo_timer = max(0, self._combo_timer - dt)
        if self._combo_timer <= 0:
            self._combo = 0

    # ── HUD ───────────────────────────────────────────────────────────────────
    def draw_hud(self, score, slow_charges, slow_active, slow_timer,
                 dash_cooldown, kills, bullet_blocks, deaths):
        sw = self.screen.get_width()

        bar = pygame.Surface((sw, 36), pygame.SRCALPHA)
        bar.fill((10, 10, 20, 200))
        self.screen.blit(bar, (0, 0))

        s = self._font_md.render(f"SCORE  {score:>7}", True, C_ACCENT)
        self.screen.blit(s, (12, 9))

        stats = self._font_sm.render(
            f"KILLS:{kills}  BLOCKS:{bullet_blocks}  DEATHS:{deaths}", True, C_LTGRAY)
        self.screen.blit(stats, (sw // 2 - stats.get_width() // 2, 12))

        for i in range(SLOW_CHARGES):
            col = C_ACCENT if i < slow_charges else C_GRAY
            if slow_active and i == slow_charges:
                col = C_FLASH
            pygame.draw.rect(self.screen, col,
                             (sw - 20 - i * 22, 10, 16, 16), border_radius=3)
            if i >= slow_charges and not slow_active:
                pygame.draw.rect(self.screen, C_GRAY,
                                 (sw - 20 - i * 22, 10, 16, 16), 1, border_radius=3)

        sl = self._font_sm.render("SLOW", True, C_GRAY)
        self.screen.blit(sl, (sw - 20 - SLOW_CHARGES * 22 - sl.get_width() - 4, 12))

        bar_w = 100
        filled = int(bar_w * (1 - min(dash_cooldown / DASH_COOLDOWN, 1)))
        pygame.draw.rect(self.screen, C_GRAY,  (12, SCREEN_H - 20, bar_w, 8), border_radius=4)
        if filled > 0:
            pygame.draw.rect(self.screen, C_WHITE, (12, SCREEN_H - 20, filled, 8), border_radius=4)
        dash_lbl = self._font_sm.render("DASH", True, C_GRAY)
        self.screen.blit(dash_lbl, (12, SCREEN_H - 34))

        if slow_active:
            tint = pygame.Surface((sw, SCREEN_H), pygame.SRCALPHA)
            tint.fill((80, 80, 180, 22))
            self.screen.blit(tint, (0, 0))
            slbl = self._font_md.render("SLOW", True, C_ACCENT)
            self.screen.blit(slbl, (sw // 2 - slbl.get_width() // 2, SCREEN_H - 30))

        if self._combo >= 2 and self._combo_timer > 0:
            ct = self._font_lg.render(f"x{self._combo} COMBO!", True, C_ACCENT)
            alpha = int(min(255, self._combo_timer / 1.2 * 255))
            ct.set_alpha(alpha)
            self.screen.blit(ct, (sw // 2 - ct.get_width() // 2, 60))

        hints = ["WASD/ARROWS: move", "SPACE/W: jump",
                 "SHIFT: dash", "Z/J: shoot", "X/K: slow-time"]
        for i, h in enumerate(hints):
            hl = self._font_xs.render(h, True, (60, 60, 80))
            self.screen.blit(hl, (sw - hl.get_width() - 8,
                                  SCREEN_H - 14 - (len(hints) - i) * 12))

    # ── Block flash ───────────────────────────────────────────────────────────
    def show_block_flash(self, x, y):
        lbl = self._font_md.render("BLOCK!", True, C_ACCENT)
        self.screen.blit(lbl, (x - lbl.get_width() // 2, y - 30))

    # ── Next level screen ────────────────────────────────────────────────────
    def draw_next_level_screen(self, completed_level, summary):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2
        t1 = self._font_lg.render(f"LEVEL {completed_level} CLEAR!", True, C_GREEN)
        t2 = self._font_md.render(f"Loading Level {completed_level + 1}...", True, C_ACCENT)
        if summary:
            t3 = self._font_sm.render(
                f"Score: {summary['score']:,}   Rank: {summary['rank']}   Kills: {summary['kill_count']}",
                True, C_LTGRAY)
            self.screen.blit(t3, (cx - t3.get_width() // 2, cy + 20))
        self.screen.blit(t1, (cx - t1.get_width() // 2, cy - 40))
        self.screen.blit(t2, (cx - t2.get_width() // 2, cy))

    # ── Death screen ──────────────────────────────────────────────────────────
    def draw_death_screen(self, respawn_timer):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((120, 20, 20, 160))
        self.screen.blit(overlay, (0, 0))
        t1 = self._font_lg.render("YOU DIED", True, C_WHITE)
        t2 = self._font_md.render(f"Respawning in {respawn_timer:.1f}s...", True, C_LTGRAY)
        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2
        self.screen.blit(t1, (cx - t1.get_width() // 2, cy - 30))
        self.screen.blit(t2, (cx - t2.get_width() // 2, cy + 10))

    # ── Rank / win screen ─────────────────────────────────────────────────────
    def show_rank_screen(self, summary):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2
        rank_col = {
            "S": (255, 215, 0), "A": (200, 200, 60),
            "B": (160, 160, 160), "C": (180, 120, 80), "D": (120, 80, 80)
        }.get(summary["rank"], C_WHITE)
        lines = [
            (f"ALL LEVELS COMPLETE!", self._font_lg, C_GREEN,   -110),
            (f"RANK  {summary['rank']}",   self._font_lg, rank_col,  -65),
            (f"SCORE   {summary['score']:,}", self._font_md, C_ACCENT, -20),
            (f"KILLS   {summary['kill_count']}",          self._font_sm, C_LTGRAY, 16),
            (f"BLOCKS  {summary['bullet_blocks']}",       self._font_sm, C_LTGRAY, 32),
            (f"DEATHS  {summary['deaths']}",              self._font_sm, C_LTGRAY, 48),
            (f"ACCURACY {summary['accuracy_pct']:.1f}%", self._font_sm, C_LTGRAY, 64),
            (f"TIME    {summary['completion_time_ms']/1000:.1f}s", self._font_sm, C_LTGRAY, 80),
            ("Press R to restart  |  ESC to quit",        self._font_sm, C_GRAY,   120),
        ]
        for text, font, col, dy in lines:
            surf = font.render(text, True, col)
            self.screen.blit(surf, (cx - surf.get_width() // 2, cy + dy))

    # ── Start screen ──────────────────────────────────────────────────────────
    def draw_start_screen(self, mouse_pos, events):
        """Draw start screen with PLAY and STATS buttons.
        Returns 'play', 'stats', or None."""
        sw, sh = self.screen.get_width(), self.screen.get_height()
        cx, cy = sw // 2, sh // 2

        self.screen.fill(C_BG)

        # Decorative grid lines
        for x in range(0, sw, 48):
            pygame.draw.line(self.screen, (25, 25, 38), (x, 0), (x, sh), 1)
        for y in range(0, sh, 48):
            pygame.draw.line(self.screen, (25, 25, 38), (0, y), (sw, y), 1)

        # Title
        title = self._font_xl.render("PIXEL SHOT", True, C_ACCENT)
        self.screen.blit(title, (cx - title.get_width() // 2, cy - 90))

        # Subtitle
        sub = self._font_md.render("High-Speed Gun Action Platformer", True, C_LTGRAY)
        self.screen.blit(sub, (cx - sub.get_width() // 2, cy - 38))

        # Divider
        pygame.draw.line(self.screen, C_GRAY,
                         (cx - 160, cy - 12), (cx + 160, cy - 12), 1)

        # Buttons
        self.btn_play.update(mouse_pos)
        self.btn_stats.update(mouse_pos)
        self.btn_play.draw(self.screen)
        self.btn_stats.draw(self.screen)

        # Controls hint
        hints = [
            "WASD / ARROWS  — move & jump",
            "LEFT CLICK / Z — shoot toward cursor",
            "LEFT SHIFT     — dash",
            "X / K          — slow-time",
        ]
        for i, h in enumerate(hints):
            hl = self._font_xs.render(h, True, (70, 70, 90))
            self.screen.blit(hl, (cx - hl.get_width() // 2, cy + 80 + i * 14))

        # Version
        ver = self._font_xs.render("v1.0  |  5 levels", True, (50, 50, 70))
        self.screen.blit(ver, (sw - ver.get_width() - 8, sh - 18))

        return self.update_buttons(mouse_pos, events)

    # ── Statistics screen ─────────────────────────────────────────────────────
    def draw_stats_screen(self, mouse_pos, events, scroll_events):
        """Draw the session statistics table from sessions.csv.
        Returns 'back' or None."""
        sw, sh = self.screen.get_width(), self.screen.get_height()
        cx = sw // 2

        self.screen.fill((10, 10, 18))

        # Handle scroll
        for e in scroll_events:
            if e.type == pygame.MOUSEWHEEL:
                self._stats_scroll -= e.y * 22

        # Load CSV
        rows = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

        # Title bar
        pygame.draw.rect(self.screen, (20, 20, 35), (0, 0, sw, 44))
        pygame.draw.line(self.screen, C_GRAY, (0, 44), (sw, 44), 1)
        title = self._font_md.render("SESSION STATISTICS", True, C_ACCENT)
        self.screen.blit(title, (cx - title.get_width() // 2, 12))
        count_lbl = self._font_sm.render(
            f"{len(rows)} session{'s' if len(rows) != 1 else ''} recorded", True, C_GRAY)
        self.screen.blit(count_lbl, (sw - count_lbl.get_width() - 12, 16))

        # Column definitions: (header, csv_key, width, right_align)
        COLS = [
            ("#",            None,               38,  True),
            ("SESSION",      "session_id",       72,  False),
            ("LVL",          "level_id",         36,  True),
            ("SCORE",        "score",             70,  True),
            ("RNK",          "rank",              36,  True),
            ("KILLS",        "kill_count",        50,  True),
            ("BLOCKS",       "bullet_blocks",     55,  True),
            ("SHOTS",        "shots_fired",       52,  True),
            ("ACC%",         "accuracy_pct",      52,  True),
            ("DEATHS",       "deaths",            55,  True),
            ("DASHES",       "dash_count",        58,  True),
            ("TIME(s)",      "completion_time_ms",68,  True),
        ]

        total_w = sum(c[2] for c in COLS)
        start_x = max(8, (sw - total_w) // 2)
        header_y = 52
        row_h    = 20
        content_h = sh - header_y - row_h - 60   # viewport height

        # ── Summary bar ───────────────────────────────────────────────────────
        if rows:
            try:
                scores  = [int(r["score"])       for r in rows]
                deaths  = [int(r["deaths"])       for r in rows]
                blocks  = [int(r["bullet_blocks"])for r in rows]
                accs    = [float(r["accuracy_pct"]) for r in rows]
                summary_txt = (
                    f"Avg Score: {sum(scores)//len(scores):,}   "
                    f"Best: {max(scores):,}   "
                    f"Avg Acc: {sum(accs)/len(accs):.1f}%   "
                    f"Total Kills: {sum(int(r['kill_count']) for r in rows)}   "
                    f"Total Blocks: {sum(blocks)}"
                )
                sl = self._font_xs.render(summary_txt, True, C_LTGRAY)
                pygame.draw.rect(self.screen, (18, 18, 30), (0, header_y - 16, sw, 15))
                self.screen.blit(sl, (cx - sl.get_width() // 2, header_y - 14))
            except Exception:
                pass

        # ── Column headers ────────────────────────────────────────────────────
        pygame.draw.rect(self.screen, (30, 30, 50), (0, header_y, sw, row_h))
        x = start_x
        for hdr, _, w, right in COLS:
            lbl = self._font_xs.render(hdr, True, C_ACCENT)
            bx  = x + w - lbl.get_width() - 2 if right else x + 2
            self.screen.blit(lbl, (bx, header_y + 4))
            x  += w
        pygame.draw.line(self.screen, C_GRAY, (0, header_y + row_h), (sw, header_y + row_h), 1)

        # ── Scrollable clip region ────────────────────────────────────────────
        data_y_start = header_y + row_h + 1
        clip_rect = pygame.Rect(0, data_y_start, sw, content_h)
        self.screen.set_clip(clip_rect)

        # Clamp scroll
        max_scroll = max(0, len(rows) * row_h - content_h)
        self._stats_scroll = max(0, min(self._stats_scroll, max_scroll))

        if not rows:
            no_data = self._font_md.render("No data yet — play a game first!", True, C_GRAY)
            self.screen.blit(no_data, (cx - no_data.get_width() // 2,
                                       data_y_start + content_h // 2 - 10))
        else:
            rank_colours = {
                "S": (255, 215,  0), "A": (180, 200,  60),
                "B": (160, 160, 160),"C": (180, 120,  80), "D": (120, 80, 80)
            }
            # Newest first
            for ri, row in enumerate(reversed(rows)):
                ry = data_y_start + ri * row_h - self._stats_scroll
                if ry + row_h < data_y_start or ry > data_y_start + content_h:
                    continue

                bg = (22, 22, 36) if ri % 2 == 0 else (16, 16, 28)
                pygame.draw.rect(self.screen, bg, (0, ry, sw, row_h))

                x = start_x
                for col_i, (_, key, w, right) in enumerate(COLS):
                    if key is None:
                        val = str(len(rows) - ri)
                    elif key == "completion_time_ms":
                        try:    val = f"{int(row[key])//1000}.{(int(row[key])%1000)//100}"
                        except: val = row.get(key, "")
                    elif key == "accuracy_pct":
                        try:    val = f"{float(row[key]):.1f}"
                        except: val = row.get(key, "")
                    else:
                        val = row.get(key, "")

                    col = C_LTGRAY
                    if key == "rank":
                        col = rank_colours.get(val, C_LTGRAY)
                    elif key == "score":
                        try:
                            sc = int(val)
                            col = (255,215,0) if sc>=RANK_S else (180,200,60) if sc>=RANK_A else C_LTGRAY
                        except: pass

                    lbl = self._font_xs.render(str(val), True, col)
                    bx  = x + w - lbl.get_width() - 2 if right else x + 2
                    self.screen.blit(lbl, (bx, ry + 5))
                    x += w

                pygame.draw.line(self.screen, (30, 30, 48),
                                 (0, ry + row_h - 1), (sw, ry + row_h - 1), 1)

        self.screen.set_clip(None)

        # ── Scroll bar ────────────────────────────────────────────────────────
        if rows and max_scroll > 0:
            bar_h    = max(20, int(content_h * content_h / (len(rows) * row_h)))
            bar_y    = data_y_start + int(self._stats_scroll / max_scroll * (content_h - bar_h))
            pygame.draw.rect(self.screen, (50, 50, 70),
                             (sw - 6, data_y_start, 4, content_h), border_radius=2)
            pygame.draw.rect(self.screen, C_GRAY,
                             (sw - 6, bar_y, 4, bar_h), border_radius=2)

        # ── Scroll hint ───────────────────────────────────────────────────────
        hint = self._font_xs.render("scroll: mouse wheel", True, (50, 50, 70))
        self.screen.blit(hint, (12, sh - 20))

        # ── Back button ───────────────────────────────────────────────────────
        self.btn_back.update(mouse_pos)
        self.btn_back.draw(self.screen)

        return self.update_buttons(mouse_pos, events)
