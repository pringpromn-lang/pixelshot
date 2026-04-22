"""bullet.py — Projectile with bullet-block intercept logic"""
import pygame, math
from settings import *

class Bullet:
    SIZE = 6

    def __init__(self, x, y, vel_x, vel_y, is_player_bullet):
        self.x  = float(x)
        self.y  = float(y)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.is_player_bullet = is_player_bullet
        self.is_active = True
        self.age = 0.0          # seconds alive
        self.MAX_AGE = 4.0

    # ── Rect for collision ────────────────────────────────────────────────────
    @property
    def rect(self):
        return pygame.Rect(
            self.x - self.SIZE // 2,
            self.y - self.SIZE // 2,
            self.SIZE, self.SIZE
        )

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt, tile_rects):
        if not self.is_active:
            return
        self.x   += self.vel_x * dt
        self.y   += self.vel_y * dt
        self.age += dt

        if self.age > self.MAX_AGE:
            self.destroy()
            return

        # Tile collision
        for tr in tile_rects:
            if self.rect.colliderect(tr):
                self.destroy()
                return

    # ── Bullet-block intercept ────────────────────────────────────────────────
    def check_intercept(self, other):
        """
        Returns True if this player bullet intercepts an enemy bullet.
        Destroys both on success.
        """
        if not self.is_active or not other.is_active:
            return False
        if self.is_player_bullet == other.is_player_bullet:
            return False
        dx = self.x - other.x
        dy = self.y - other.y
        if math.hypot(dx, dy) <= BULLET_INTERCEPT_DIST:
            self.destroy()
            other.destroy()
            return True
        return False

    def destroy(self):
        self.is_active = False

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surface, camera):
        if not self.is_active:
            return
        sx, sy = camera.apply_point(self.x, self.y)
        colour  = C_BULLET_P if self.is_player_bullet else C_BULLET_E
        # Glow effect: draw a slightly larger dim circle first
        glow_r = self.SIZE + 3
        glow_surf = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
        gc = (*colour, 60)
        pygame.draw.circle(glow_surf, gc, (glow_r, glow_r), glow_r)
        surface.blit(glow_surf, (sx - glow_r, sy - glow_r))
        pygame.draw.circle(surface, colour, (int(sx), int(sy)), self.SIZE // 2 + 1)
