"""camera.py — Smooth-follow camera with screenshake"""
import pygame, random
from settings import SCREEN_W, SCREEN_H

class Camera:
    def __init__(self, level_w, level_h):
        self.offset_x = 0
        self.offset_y = 0
        self.level_w  = level_w
        self.level_h  = level_h
        self._shake_intensity = 0
        self._shake_timer     = 0
        self._sx = 0
        self._sy = 0

    def shake(self, intensity=6, duration=0.18):
        self._shake_intensity = intensity
        self._shake_timer     = duration

    def update(self, target_rect, dt):
        target_x = target_rect.centerx - SCREEN_W // 2
        target_y = target_rect.centery - SCREEN_H // 2
        self.offset_x += (target_x - self.offset_x) * min(dt * 10, 1)
        self.offset_y += (target_y - self.offset_y) * min(dt * 10, 1)

        self.offset_x = max(0, min(self.offset_x, self.level_w  - SCREEN_W))
        self.offset_y = max(0, min(self.offset_y, self.level_h  - SCREEN_H))

        self._sx, self._sy = 0, 0
        if self._shake_timer > 0:
            self._shake_timer -= dt
            self._sx = random.uniform(-self._shake_intensity, self._shake_intensity)
            self._sy = random.uniform(-self._shake_intensity, self._shake_intensity)
            self._shake_intensity *= 0.85

    def apply(self, rect):
        return pygame.Rect(
            rect.x - self.offset_x + self._sx,
            rect.y - self.offset_y + self._sy,
            rect.w, rect.h
        )

    def apply_point(self, x, y):
        return (x - self.offset_x + self._sx,
                y - self.offset_y + self._sy)