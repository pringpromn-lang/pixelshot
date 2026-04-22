"""enemy.py — GuardEnemy with simple FSM: Idle → Alert → Chase → Attack"""
import pygame, math, random
from settings import *
from bullet import Bullet

class GuardEnemy:
    W, H = 22, 32
    STATES = ("idle", "patrol", "alert", "attack", "dead")

    def __init__(self, x, y):
        self.x     = float(x)
        self.y     = float(y)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.facing    = -1

        self.state        = "patrol"
        self.patrol_dir   = 1
        self.patrol_timer = 0.0
        self.alert_timer  = 0.0
        self.shoot_timer  = 0.0
        self.dead_timer   = 0.0

        self._anim_tick  = 0.0
        self._anim_frame = 0

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.W, self.H)

    @property
    def is_alive(self):
        return self.state != "dead"

    # ── FSM ───────────────────────────────────────────────────────────────────
    def change_state(self, new_state):
        self.state = new_state

    def _dist_to_player(self, px, py):
        return math.hypot(self.x - px, self.y - py)

    def detect_player(self, px, py):
        return self._dist_to_player(px, py) < GUARD_DETECT_R

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt, tile_rects, player, bullets):
        if self.state == "dead":
            self.dead_timer -= dt
            return

        px = player.x + player.W / 2
        py = player.y + player.H / 2
        dist = self._dist_to_player(px, py)

        # ── State transitions ─────────────────────────────────────────────────
        if self.state == "patrol":
            if self.detect_player(px, py) and player.is_alive:
                self.change_state("alert")
                self.alert_timer = 0.5

        elif self.state == "alert":
            self.alert_timer -= dt
            if self.alert_timer <= 0:
                self.change_state("attack")

        elif self.state == "attack":
            if not player.is_alive or dist > GUARD_DETECT_R * 1.4:
                self.change_state("patrol")

        # ── State behaviour ───────────────────────────────────────────────────
        if self.state == "patrol":
            self._do_patrol(dt, tile_rects)

        elif self.state == "alert":
            self.vel_x = 0   # stop and flash
            self.facing = 1 if px > self.x else -1

        elif self.state == "attack":
            # Strafe toward player slowly
            target_x = px - self.W / 2
            dx = target_x - self.x
            if abs(dx) > 60:
                self.vel_x = math.copysign(GUARD_SPEED * 0.7, dx)
                self.facing = 1 if dx > 0 else -1
            else:
                self.vel_x = 0
                self.facing = 1 if px > self.x else -1

            # Shoot
            self.shoot_timer -= dt
            if self.shoot_timer <= 0:
                self.shoot_timer = GUARD_FIRE_RATE
                self._shoot(px, py, bullets)

        # ── Physics ───────────────────────────────────────────────────────────
        self.vel_y += GRAVITY * dt
        self.x += self.vel_x * dt
        self._resolve_x(tile_rects)
        self.y += self.vel_y * dt
        self.on_ground = False
        self._resolve_y(tile_rects)

        # Animation
        self._anim_tick += dt * 6
        self._anim_frame = int(self._anim_tick) % 4

    def _do_patrol(self, dt, tile_rects):
        self.patrol_timer -= dt
        if self.patrol_timer <= 0:
            self.patrol_dir   = random.choice([-1, 1])
            self.patrol_timer = random.uniform(1.2, 2.8)
        self.vel_x = self.patrol_dir * GUARD_SPEED * 0.5
        self.facing = self.patrol_dir

    def _shoot(self, tx, ty, bullets):
        cx = self.x + self.W / 2
        cy = self.y + self.H / 2
        dx = tx - cx
        dy = ty - cy
        dist = math.hypot(dx, dy) or 1
        # Add slight inaccuracy
        angle_noise = math.radians(random.uniform(-6, 6))
        cos_n, sin_n = math.cos(angle_noise), math.sin(angle_noise)
        vx = (dx/dist*cos_n - dy/dist*sin_n) * BULLET_SPEED_E
        vy = (dx/dist*sin_n + dy/dist*cos_n) * BULLET_SPEED_E
        bullets.append(Bullet(cx, cy, vx, vy, is_player_bullet=False))

    def take_damage(self):
        if self.state == "dead":
            return
        self.change_state("dead")
        self.dead_timer = 0.4

    def _resolve_x(self, tile_rects):
        r = self.rect
        for tr in tile_rects:
            if r.colliderect(tr):
                if self.vel_x > 0:
                    self.x = tr.left - self.W
                    self.patrol_dir = -1
                elif self.vel_x < 0:
                    self.x = tr.right
                    self.patrol_dir = 1
                self.vel_x = 0
                r = self.rect

    def _resolve_y(self, tile_rects):
        r = self.rect
        for tr in tile_rects:
            if r.colliderect(tr):
                if self.vel_y > 0:
                    self.y = tr.top - self.H
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.y = tr.bottom
                self.vel_y = 0
                r = self.rect

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surface, camera):
        sx, sy = camera.apply_point(self.x, self.y)
        r = pygame.Rect(sx, sy, self.W, self.H)

        if self.state == "dead":
            pygame.draw.rect(surface, C_GRAY, r, border_radius=3)
            return

        # Body
        col = C_ENEMY
        if self.state == "alert":
            # Flash red/white
            col = C_FLASH if int(pygame.time.get_ticks() / 80) % 2 == 0 else C_ENEMY
        pygame.draw.rect(surface, col, r, border_radius=3)

        # Visor
        vw = 8
        vx = sx + (self.W - vw - 2) if self.facing == 1 else sx + 2
        pygame.draw.rect(surface, (60, 20, 20), (vx, sy + 6, vw, 5), border_radius=2)

        # Detection arc (faint)
        if self.state == "patrol":
            detect_surf = pygame.Surface((GUARD_DETECT_R*2, GUARD_DETECT_R*2), pygame.SRCALPHA)
            pygame.draw.circle(detect_surf, (255, 80, 80, 18),
                               (GUARD_DETECT_R, GUARD_DETECT_R), GUARD_DETECT_R)
            surface.blit(detect_surf, (sx + self.W//2 - GUARD_DETECT_R,
                                       sy + self.H//2 - GUARD_DETECT_R))

        # Legs
        if self.vel_x != 0 and self.on_ground:
            lf = self._anim_frame
            l1y = sy + self.H - 8 + (3 if lf < 2 else 0)
            l2y = sy + self.H - 8 + (3 if lf >= 2 else 0)
            pygame.draw.rect(surface, (150, 50, 50), (sx + 3,  l1y, 5, 8))
            pygame.draw.rect(surface, (150, 50, 50), (sx + 12, l2y, 5, 8))

        # State label (small)
        font = pygame.font.SysFont("monospace", 9)
        lbl  = font.render(self.state.upper(), True, C_GRAY)
        surface.blit(lbl, (sx, sy - 12))
