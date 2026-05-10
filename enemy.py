"""enemy.py — Sci-fi drone enemy, zero SRCALPHA surfaces"""
import pygame, math, random
from settings import *
from bullet import Bullet

class GuardEnemy:
    W, H = 24, 28
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
        self._anim_tick   = 0.0
        self._hover_bob   = random.uniform(0, math.pi * 2)
        self._scan_angle  = 0.0
        self._muzzle_flash= 0.0

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.W, self.H)

    @property
    def is_alive(self):
        return self.state != "dead"

    def change_state(self, s): self.state = s

    def _dist(self, px, py):
        return math.hypot(self.x - px, self.y - py)

    def detect_player(self, px, py):
        return self._dist(px, py) < GUARD_DETECT_R

    def update(self, dt, tile_rects, player, bullets):
        if self.state == "dead":
            self.dead_timer -= dt
            return

        self._hover_bob  += dt * 3.0
        self._anim_tick  += dt * 5
        self._muzzle_flash = max(0, self._muzzle_flash - dt)

        px = player.x + player.W / 2
        py = player.y + player.H / 2
        dist = self._dist(px, py)

        if self.state == "patrol":
            if self.detect_player(px, py) and player.is_alive:
                self.change_state("alert")
                self.alert_timer = 0.6
        elif self.state == "alert":
            self.alert_timer -= dt
            self._scan_angle  += dt * 4
            if self.alert_timer <= 0:
                self.change_state("attack")
                self.shoot_timer = 0.3
        elif self.state == "attack":
            if not player.is_alive or dist > GUARD_DETECT_R * 1.5:
                self.change_state("patrol")

        if self.state == "patrol":
            self._do_patrol(dt, tile_rects)
            self._scan_angle += dt * 1.5
        elif self.state == "alert":
            self.vel_x = 0
            self.facing = 1 if px > self.x else -1
        elif self.state == "attack":
            dx = (px - self.W/2) - self.x
            if abs(dx) > 80:
                self.vel_x = math.copysign(GUARD_SPEED * 0.65, dx)
                self.facing = 1 if dx > 0 else -1
            else:
                self.vel_x = 0
                self.facing = 1 if px > self.x else -1
            self.shoot_timer -= dt
            if self.shoot_timer <= 0:
                self.shoot_timer = GUARD_FIRE_RATE
                self._shoot(px, py, bullets)

        self.vel_y += GRAVITY * dt
        self.x += self.vel_x * dt
        self._resolve_x(tile_rects)
        self.y += self.vel_y * dt
        self.on_ground = False
        self._resolve_y(tile_rects)

    def _do_patrol(self, dt, tile_rects):
        self.patrol_timer -= dt
        if self.patrol_timer <= 0:
            self.patrol_dir   = random.choice([-1, 1])
            self.patrol_timer = random.uniform(1.2, 2.8)
        self.vel_x = self.patrol_dir * GUARD_SPEED * 0.5
        self.facing = self.patrol_dir

    def _shoot(self, tx, ty, bullets):
        cx = self.x + self.W/2
        cy = self.y + self.H/2
        dx, dy = tx-cx, ty-cy
        dist = math.hypot(dx, dy) or 1
        noise = math.radians(random.uniform(-5, 5))
        cn, sn = math.cos(noise), math.sin(noise)
        vx = (dx/dist*cn - dy/dist*sn) * BULLET_SPEED_E
        vy = (dx/dist*sn + dy/dist*cn) * BULLET_SPEED_E
        bullets.append(Bullet(cx, cy, vx, vy, is_player_bullet=False))
        self._muzzle_flash = 0.1

    def take_damage(self):
        if self.state == "dead": return
        self.change_state("dead")
        self.dead_timer = 0.5

    def _resolve_x(self, tile_rects):
        r = self.rect
        for tr in tile_rects:
            if r.colliderect(tr):
                if self.vel_x > 0:   self.x = tr.left - self.W; self.patrol_dir = -1
                elif self.vel_x < 0: self.x = tr.right;          self.patrol_dir =  1
                self.vel_x = 0; r = self.rect

    def _resolve_y(self, tile_rects):
        r = self.rect
        for tr in tile_rects:
            if r.colliderect(tr):
                if self.vel_y > 0:   self.y = tr.top - self.H; self.on_ground = True
                elif self.vel_y < 0: self.y = tr.bottom
                self.vel_y = 0; r = self.rect

    # ── Draw — NO SRCALPHA surfaces ───────────────────────────────────────────
    def draw(self, surface, camera):
        sx, sy = camera.apply_point(self.x, self.y)
        bx, by = int(sx), int(sy)
        t = pygame.time.get_ticks() / 1000.0

        # ── Dead: expanding ring ──────────────────────────────────────────────
        if self.state == "dead":
            if self.dead_timer > 0:
                r = int((1 - self.dead_timer/0.5) * 24) + 4
                pygame.draw.circle(surface, C_ENEMY,  (bx+self.W//2, by+self.H//2), r, 3)
                pygame.draw.circle(surface, C_ENEMY2, (bx+self.W//2, by+self.H//2), max(1,r-4), 2)
            return

        # ── Scan laser — direct line on surface ───────────────────────────────
        if self.state in ("alert", "attack"):
            la  = self._scan_angle if self.state == "alert" else math.atan2(
                (camera.offset_y + surface.get_height()//2) - (by + self.H//2),
                (camera.offset_x + surface.get_width()//2)  - (bx + self.W//2))
            lx2 = bx + self.W//2 + int(math.cos(la) * 100)
            ly2 = by + self.H//2 + int(math.sin(la) * 100)
            pygame.draw.line(surface, C_ENEMY2 if self.state=="alert" else C_ENEMY_DIM,
                             (bx+self.W//2, by+self.H//2), (lx2, ly2), 1)

        # ── Patrol detection ring — thin circle ───────────────────────────────
        if self.state == "patrol":
            pulse = int(abs(math.sin(t*1.5)) * 15) + 3
            pygame.draw.circle(surface, C_ENEMY_DIM,
                               (bx+self.W//2, by+self.H//2),
                               GUARD_DETECT_R, 1)

        # ── Landing struts ────────────────────────────────────────────────────
        leg_y = by + self.H - 6
        for lx_off in [4, self.W-10]:
            pygame.draw.rect(surface, C_ENEMY2, (bx+lx_off, leg_y, 4, 8), border_radius=1)
            pygame.draw.rect(surface, C_ENEMY,  (bx+lx_off-2, leg_y+7, 8, 2), border_radius=1)

        # ── Hull ──────────────────────────────────────────────────────────────
        pygame.draw.rect(surface, (50,12,18), (bx, by+6, self.W, self.H-12), border_radius=4)
        pygame.draw.rect(surface, (80,20,28), (bx, by+6, self.W, self.H-12), 1, border_radius=4)
        # Panel lines
        pygame.draw.line(surface, (60,15,22), (bx+3,  by+10), (bx+3,  by+self.H-10), 1)
        pygame.draw.line(surface, (60,15,22), (bx+self.W-4, by+10), (bx+self.W-4, by+self.H-10), 1)

        # ── Sensor dome ───────────────────────────────────────────────────────
        pygame.draw.ellipse(surface, (40,10,15), (bx+2, by, self.W-4, 10))
        pygame.draw.ellipse(surface, (70,18,26), (bx+2, by, self.W-4, 10), 1)

        # ── Scanner eye — pulsing solid circle ────────────────────────────────
        pulse = int(abs(math.sin(t*3)) * 60)
        eye_col = (255, max(0, 50-pulse), max(0, 50-pulse))
        eye_x   = bx + (self.W-6) if self.facing == 1 else bx + 3
        pygame.draw.circle(surface, eye_col, (eye_x, by+5), 4)
        pygame.draw.circle(surface, C_WHITE,  (eye_x, by+5), 1)

        # Alert flash: draw red outline on hull
        if self.state == "alert" and int(t*10) % 2 == 0:
            pygame.draw.rect(surface, C_ENEMY, (bx, by+6, self.W, self.H-12), 2, border_radius=4)

        # ── Weapon mount ──────────────────────────────────────────────────────
        gun_x = bx + (self.W-2) if self.facing == 1 else bx - 6
        pygame.draw.rect(surface, (80,20,28), (gun_x, by+10, 8, 5), border_radius=2)

        # Muzzle flash
        if self._muzzle_flash > 0:
            muz_x = gun_x + (9 if self.facing == 1 else -2)
            pygame.draw.circle(surface, C_BULLET_E, (muz_x, by+12), 5)
            pygame.draw.circle(surface, C_WHITE,    (muz_x, by+12), 2)

        # ── Status strip ──────────────────────────────────────────────────────
        strip = {"patrol": C_ENEMY2, "alert": C_BULLET_E, "attack": C_ENEMY}[self.state]
        pygame.draw.rect(surface, strip, (bx+4, by+self.H-14, self.W-8, 3), border_radius=1)
