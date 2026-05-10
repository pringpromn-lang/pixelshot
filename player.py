"""player.py — Sci-fi mech suit player"""
import pygame, math, random
from settings import *

class Player:
    W, H = 20, 28
    COYOTE_TIME      = 0.10
    JUMP_BUFFER_TIME = 0.12

    def __init__(self, x, y):
        self.x   = float(x)
        self.y   = float(y)
        self.vel_x = 0.0
        self.vel_y = 0.0

        self.is_alive      = True
        self.on_ground     = False
        self.facing        = 1
        self.ammo          = 999

        self._coyote_timer  = 0.0
        self._jump_buffer   = 0.0

        self.dash_cooldown  = 0.0
        self.dash_timer     = 0.0
        self.dash_dir       = 1
        self.is_dashing     = False
        self.iframe_timer   = 0.0

        self.slow_charges   = SLOW_CHARGES
        self.slow_active    = False
        self.slow_timer     = 0.0

        self._anim_tick     = 0.0
        self._anim_frame    = 0
        self._death_flash   = 0.0
        self._thruster_particles = []
        self._muzzle_flash  = 0.0

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.W, self.H)

    # ── Input ─────────────────────────────────────────────────────────────────
    def handle_input(self, events, keys, bullets, slow_active):
        if not self.is_alive:
            return
        move = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move = -1; self.facing = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move = 1;  self.facing = 1
        if not self.is_dashing:
            self.vel_x = move * PLAYER_SPEED

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT and self.dash_cooldown <= 0:
                    self._start_dash(move if move != 0 else self.facing)
                if event.key in (pygame.K_k, pygame.K_x):
                    self._toggle_slow()

    def request_jump(self):
        self._jump_buffer = self.JUMP_BUFFER_TIME

    def _try_jump(self):
        can_jump = self.on_ground or self._coyote_timer > 0
        if self._jump_buffer > 0 and can_jump:
            self.vel_y         = JUMP_VEL
            self._jump_buffer  = 0.0
            self._coyote_timer = 0.0

    def shoot_toward(self, target_x, target_y, bullets):
        from bullet import Bullet
        cx = self.x + self.W // 2
        cy = self.y + self.H // 2
        dx = target_x - cx
        dy = target_y - cy
        dist = math.hypot(dx, dy) or 1
        vx = dx / dist * BULLET_SPEED_P
        vy = dy / dist * BULLET_SPEED_P
        bullets.append(Bullet(cx, cy, vx, vy, is_player_bullet=True))
        self._muzzle_flash = 0.08

    def _start_dash(self, direction):
        self.is_dashing    = True
        self.dash_timer    = DASH_DURATION
        self.dash_cooldown = DASH_COOLDOWN
        self.dash_dir      = direction
        self.vel_x         = direction * DASH_SPEED
        self.vel_y         = 0
        self.iframe_timer  = DASH_IFRAME

    def _toggle_slow(self):
        if self.slow_active:
            self.slow_active = False
        elif self.slow_charges > 0:
            self.slow_active  = True
            self.slow_timer   = SLOW_DURATION
            self.slow_charges -= 1

    # ── Physics ───────────────────────────────────────────────────────────────
    def update(self, dt, tile_rects):
        if not self.is_alive:
            self._death_flash = max(0, self._death_flash - dt)
            return

        self.dash_cooldown  = max(0, self.dash_cooldown - dt)
        self.iframe_timer   = max(0, self.iframe_timer  - dt)
        self._jump_buffer   = max(0, self._jump_buffer  - dt)
        self._muzzle_flash  = max(0, self._muzzle_flash - dt)

        if self.on_ground:
            self._coyote_timer = self.COYOTE_TIME
        else:
            self._coyote_timer = max(0, self._coyote_timer - dt)

        self._try_jump()

        if self.is_dashing:
            self.dash_timer -= dt
            self.vel_x = self.dash_dir * DASH_SPEED
            if self.dash_timer <= 0:
                self.is_dashing = False
                self.vel_x = 0

        if self.slow_active:
            self.slow_timer -= dt / SLOW_SCALE
            if self.slow_timer <= 0:
                self.slow_active = False

        if not self.on_ground:
            self.vel_y += GRAVITY * dt

        self.x += self.vel_x * dt
        self._resolve_x(tile_rects)
        self.y += self.vel_y * dt
        self.on_ground = False
        self._resolve_y(tile_rects)

        self._anim_tick += dt * 10
        self._anim_frame = int(self._anim_tick) % 4

        # Thruster particles
        if self.is_dashing or (not self.on_ground and self.vel_y < 0):
            for _ in range(2):
                self._thruster_particles.append({
                    "x": self.x + self.W/2 + random.uniform(-4, 4),
                    "y": self.y + self.H - 4,
                    "vx": random.uniform(-20, 20),
                    "vy": random.uniform(40, 120),
                    "life": random.uniform(0.10, 0.22),
                    "size": random.randint(2, 4),
                })
        for p in self._thruster_particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
        self._thruster_particles = [p for p in self._thruster_particles if p["life"] > 0]

    def _resolve_x(self, tile_rects):
        r = self.rect
        for tr in tile_rects:
            if r.colliderect(tr):
                if self.vel_x > 0: self.x = tr.left - self.W
                elif self.vel_x < 0: self.x = tr.right
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

    def take_damage(self):
        if self.iframe_timer > 0 or not self.is_alive:
            return False
        self.is_alive     = False
        self._death_flash = 0.5
        return True

    # ── Draw — NO SRCALPHA surfaces, all direct draws ─────────────────────────
    def draw(self, surface, camera):
        sx, sy = camera.apply_point(self.x, self.y)
        bx, by = int(sx), int(sy)

        # Death flash — simple circle, return early
        if self._death_flash > 0:
            pygame.draw.circle(surface, C_PLAYER,
                               (bx + self.W//2, by + self.H//2),
                               int(22 * (self._death_flash / 0.5)) + 4)
            return

        # Thruster particles — solid circles, no alpha
        for p in self._thruster_particles:
            px, py = camera.apply_point(p["x"], p["y"])
            fade   = max(0, min(1, p["life"] / 0.22))
            col    = C_PLAYER if self.is_dashing else C_ACCENT2
            r      = max(1, int(p["size"] * fade))
            c      = tuple(int(v * fade) for v in col)
            pygame.draw.circle(surface, c, (int(px), int(py)), r)

        # Dash afterimage — dim solid rects
        if self.is_dashing:
            pygame.draw.rect(surface, C_PLAYER_DIM,
                             (bx - self.dash_dir*14, by+4, self.W, self.H-14),
                             border_radius=3)
            pygame.draw.rect(surface, C_PLAYER_DIM,
                             (bx - self.dash_dir*26, by+8, self.W, self.H-20),
                             border_radius=3)

        # ── Legs ─────────────────────────────────────────────────────────────
        leg_y = by + self.H - 8
        lf    = self._anim_frame
        if abs(self.vel_x) > 10 and self.on_ground:
            l1y = leg_y + (3 if lf < 2 else 0)
            l2y = leg_y + (3 if lf >= 2 else 0)
        else:
            l1y = l2y = leg_y
        pygame.draw.rect(surface, C_PLAYER2,   (bx+2,  l1y, 6, 10), border_radius=2)
        pygame.draw.rect(surface, C_PLAYER_DIM,(bx+2,  l1y, 6, 4))
        pygame.draw.rect(surface, C_PLAYER2,   (bx+12, l2y, 6, 10), border_radius=2)
        pygame.draw.rect(surface, C_PLAYER_DIM,(bx+12, l2y, 6, 4))
        noz = C_PLAYER if (self.is_dashing or not self.on_ground) else C_PLAYER_DIM
        pygame.draw.rect(surface, noz, (bx+3,  l1y+8, 4, 3), border_radius=1)
        pygame.draw.rect(surface, noz, (bx+13, l2y+8, 4, 3), border_radius=1)

        # ── Torso ─────────────────────────────────────────────────────────────
        pygame.draw.rect(surface, (20,40,70),  (bx+1, by+8, self.W-2, 14), border_radius=3)
        pygame.draw.rect(surface, (30,60,100), (bx+1, by+8, self.W-2, 14), 1, border_radius=3)
        pygame.draw.rect(surface, C_PLAYER_DIM,(bx+4, by+10, self.W-10, 8), border_radius=2)
        dot_col = C_PLAYER if not self.slow_active else C_ACCENT2
        pygame.draw.circle(surface, dot_col, (bx+self.W//2, by+15), 3)

        # Shoulder pads
        pygame.draw.rect(surface, C_PLAYER2, (bx-1, by+8, 5, 6), border_radius=2)
        pygame.draw.rect(surface, C_PLAYER2, (bx+self.W-4, by+8, 5, 6), border_radius=2)

        # ── Helmet ────────────────────────────────────────────────────────────
        pygame.draw.rect(surface, (15,35,60), (bx, by, self.W, 14), border_radius=5)
        pygame.draw.rect(surface, (25,55,90), (bx, by, self.W, 14), 1, border_radius=5)

        # Visor — solid neon bar
        visor_col = C_PLAYER if not self.slow_active else C_ACCENT2
        pygame.draw.rect(surface, visor_col, (bx+2, by+4, self.W-4, 5), border_radius=2)
        eye_x = bx + (self.W-5) if self.facing == 1 else bx + 3
        pygame.draw.circle(surface, C_WHITE, (eye_x, by+6), 2)

        # Antenna
        pygame.draw.line(surface, C_PLAYER2, (bx+self.W//2, by), (bx+self.W//2, by-5), 1)
        pygame.draw.circle(surface, visor_col, (bx+self.W//2, by-6), 2)

        # ── Gun arm ───────────────────────────────────────────────────────────
        gun_x = bx + (self.W-1) if self.facing == 1 else bx - 7
        pygame.draw.rect(surface, C_PLAYER2, (gun_x, by+15, 8, 5), border_radius=2)

        # Muzzle flash — solid circles only
        if self._muzzle_flash > 0:
            muz_x = gun_x + (9 if self.facing == 1 else -2)
            pygame.draw.circle(surface, C_BULLET_P, (muz_x, by+17), 6)
            pygame.draw.circle(surface, C_WHITE,    (muz_x, by+17), 3)

        # ── Outline ───────────────────────────────────────────────────────────
        pygame.draw.rect(surface, C_PLAYER2, (bx, by, self.W, self.H-6), 1, border_radius=4)

        # ── Slow-time ring — solid circle outlines only ───────────────────────
        if self.slow_active:
            t   = pygame.time.get_ticks() / 1000.0
            r   = 30 + int(math.sin(t * 4) * 3)
            cx2 = bx + self.W // 2
            cy2 = by + self.H // 2
            pygame.draw.circle(surface, C_ACCENT2, (cx2, cy2), r, 2)
            pygame.draw.circle(surface, C_ACCENT2, (cx2, cy2), r+5, 1)
