"""game_stats.py — Session statistics recorder and CSV exporter"""
import csv, uuid, time, os
from settings import *

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "sessions.csv")

FIELDNAMES = [
    "session_id", "timestamp", "level_id",
    "shots_fired", "bullet_blocks", "accuracy_pct",
    "dash_count", "deaths", "kill_count",
    "completion_time_ms", "pixels_moved", "slow_time_uses", "score", "rank"
]

class GameStats:
    def __init__(self):
        self.session_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()
        self.shots_fired      = 0
        self.bullet_blocks    = 0
        self.dash_count       = 0
        self.deaths           = 0
        self.kill_count       = 0
        self.slow_time_uses   = 0
        self.pixels_moved     = 0.0
        self._last_px         = None
        self._last_py         = None

    # ── Event recorders ───────────────────────────────────────────────────────
    def record_shot(self):         self.shots_fired   += 1
    def record_block(self):        self.bullet_blocks += 1
    def record_dash(self):         self.dash_count    += 1
    def record_death(self):        self.deaths        += 1
    def record_kill(self):         self.kill_count    += 1
    def record_slow(self):         self.slow_time_uses += 1

    def record_position(self, px, py):
        import math
        if self._last_px is not None:
            self.pixels_moved += math.hypot(px - self._last_px, py - self._last_py)
        self._last_px, self._last_py = px, py

    # ── Summary ───────────────────────────────────────────────────────────────
    def get_summary(self):
        elapsed_ms = int((time.time() - self.start_time) * 1000)
        acc = 0.0
        if self.shots_fired > 0:
            acc = round(self.kill_count / self.shots_fired * 100, 1)
        score = max(0, int(
            500
            + self.kill_count    * SCORE_KILL
            + self.bullet_blocks * SCORE_BLOCK
            - self.deaths        * SCORE_DEATH_PEN
        ))
        rank = self._calc_rank(score)
        return {
            "session_id":          self.session_id,
            "timestamp":           int(self.start_time),
            "level_id":            1,
            "shots_fired":         self.shots_fired,
            "bullet_blocks":       self.bullet_blocks,
            "accuracy_pct":        acc,
            "dash_count":          self.dash_count,
            "deaths":              self.deaths,
            "kill_count":          self.kill_count,
            "completion_time_ms":  elapsed_ms,
            "pixels_moved":        int(self.pixels_moved),
            "slow_time_uses":      self.slow_time_uses,
            "score":               score,
            "rank":                rank,
        }

    def _calc_rank(self, score):
        if score >= RANK_S: return "S"
        if score >= RANK_A: return "A"
        if score >= RANK_B: return "B"
        if score >= RANK_C: return "C"
        return "D"

    # ── CSV export ────────────────────────────────────────────────────────────
    def export_csv(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        summary = self.get_summary()
        write_header = not os.path.exists(DATA_FILE)
        with open(DATA_FILE, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            if write_header:
                writer.writeheader()
            writer.writerow(summary)
        return summary
