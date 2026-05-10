"""bullet.py — Projectile with bullet-block intercept + neon trail"""
import pygame, math
from settings import *

class Bullet:
    SIZE = 5

    def __init__(self, x, y, vel_x, vel_y, is_player_bullet):
        self.x  = float(x)
        self.y  = float(y)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.is_player_bullet = is_player_bullet
        self.is_active = True
        self.age = 0.0
        self.MAX_AGE = 4.0
        # Trail: list of (x, y) positions
        self._trail = []
        self._trail_timer = 0.0

    @property
    def rect(self):
        return pygame.Rect(
            self.x - self.SIZE // 2,
            self.y - self.SIZE // 2,
            self.SIZE, self.SIZE
        )

    def update(self, dt, tile_rects):
        if not self.is_active:
            return

        # Record trail point
        self._trail_timer += dt
        if self._trail_timer > 0.018:
            self._trail_timer = 0.0
            self._trail.append((self.x, self.y))
            if len(self._trail) > 10:
                self._trail.pop(0)

        self.x   += self.vel_x * dt
        self.y   += self.vel_y * dt
        self.age += dt

        if self.age > self.MAX_AGE:
            self.destroy()
            return

        for tr in tile_rects:
            if self.rect.colliderect(tr):
                self.destroy()
                return

    def check_intercept(self, other):
        if not self.is_active or not other.is_active:
            return False
        if self.is_player_bullet == other.is_player_bullet:
            return False
        if math.hypot(self.x - other.x, self.y - other.y) <= BULLET_INTERCEPT_DIST:
            self.destroy()
            other.destroy()
            return True
        return False

    def destroy(self):
        self.is_active = False

    def draw(self, surface, camera):
        if not self.is_active:
            return
        sx, sy = camera.apply_point(self.x, self.y)

        core_col  = C_BULLET_P  if self.is_player_bullet else C_BULLET_E
        trail_col = C_BULLET_P2 if self.is_player_bullet else C_BULLET_E2

        # Trail — solid fading circles (no SRCALPHA)
        for i, (tx, ty) in enumerate(self._trail):
            stx, sty = camera.apply_point(tx, ty)
            fade = i / max(len(self._trail), 1)
            r    = max(1, int(self.SIZE * 0.4 * fade))
            c    = tuple(int(v * fade * 0.7) for v in trail_col)
            pygame.draw.circle(surface, c, (int(stx), int(sty)), r)

        # Outer glow — larger dim circle
        pygame.draw.circle(surface, tuple(v//5 for v in core_col),
                           (int(sx), int(sy)), self.SIZE + 5)
        # Mid glow
        pygame.draw.circle(surface, tuple(v//2 for v in core_col),
                           (int(sx), int(sy)), self.SIZE + 2)
        # Core
        pygame.draw.circle(surface, core_col, (int(sx), int(sy)), self.SIZE//2 + 1)
        # Bright centre
        pygame.draw.circle(surface, C_WHITE,  (int(sx), int(sy)), max(1, self.SIZE//4))
