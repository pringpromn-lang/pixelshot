"""player.py — Player character"""
import pygame, math
from settings import *
from bullet import Bullet

class Player:
    W, H = 20, 32
    COYOTE_TIME      = 0.10
    JUMP_BUFFER_TIME = 0.12

    def __init__(self, x, y):
        self.x   = float(x)
        self.y   = float(y)
        self.vel_x = 0.0
        self.vel_y = 0.0

        self.is_alive      = True
        self.on_ground     = False
        self.facing        = 1          # 1 = right, -1 = left
        self.ammo          = 999        # unlimited for prototype

        # Jump feel
        self._coyote_timer  = 0.0      # grace period after walking off edge
        self._jump_buffer   = 0.0      # remember jump press for a few frames
        COYOTE_TIME         = 0.10     # seconds
        JUMP_BUFFER_TIME    = 0.12     # seconds

        # Dash
        self.dash_cooldown  = 0.0
        self.dash_timer     = 0.0
        self.dash_dir       = 1
        self.is_dashing     = False
        self.iframe_timer   = 0.0      # invincibility frames

        # Slow-time
        self.slow_charges   = SLOW_CHARGES
        self.slow_active    = False
        self.slow_timer     = 0.0

        # Animation
        self._anim_tick  = 0.0
        self._anim_frame = 0

        # Death flash
        self._death_flash = 0.0

    # ── Rect ──────────────────────────────────────────────────────────────────
    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.W, self.H)

    # ── Input ─────────────────────────────────────────────────────────────────
    def handle_input(self, events, keys, bullets, slow_active):
        if not self.is_alive:
            return

        # Horizontal movement
        move = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move = -1
            self.facing = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move = 1
            self.facing = 1

        if not self.is_dashing:
            self.vel_x = move * PLAYER_SPEED

        for event in events:
            if event.type == pygame.KEYDOWN:
                # Dash
                if event.key == pygame.K_LSHIFT and self.dash_cooldown <= 0:
                    self._start_dash(move if move != 0 else self.facing)
                # Shoot
                if event.key == pygame.K_j or event.key == pygame.K_z:
                    self._shoot(bullets)
                # Slow-time toggle
                if event.key == pygame.K_k or event.key == pygame.K_x:
                    self._toggle_slow()

    def request_jump(self):
        """Called from game.py on keydown — buffers the request."""
        self._jump_buffer = self.JUMP_BUFFER_TIME

    def _try_jump(self):
        can_jump = self.on_ground or self._coyote_timer > 0
        if self._jump_buffer > 0 and can_jump:
            self.vel_y         = JUMP_VEL
            self._jump_buffer  = 0.0
            self._coyote_timer = 0.0

    def _start_dash(self, direction):
        self.is_dashing    = True
        self.dash_timer    = DASH_DURATION
        self.dash_cooldown = DASH_COOLDOWN
        self.dash_dir      = direction
        self.vel_x         = direction * DASH_SPEED
        self.vel_y         = 0
        self.iframe_timer  = DASH_IFRAME

    def _shoot(self, bullets):
        mx, my = pygame.mouse.get_pos()
        # Convert mouse to world space (approximation; game passes camera offset)
        cx = self.x + self.W // 2
        cy = self.y + self.H // 2
        # Direction stored externally; use facing if no mouse movement
        dx = mx - (cx)  # rough — game.py will pass camera-adjusted coords
        dy = my - (cy)
        dist = math.hypot(dx, dy) or 1
        vx = dx / dist * BULLET_SPEED_P
        vy = dy / dist * BULLET_SPEED_P
        bullets.append(Bullet(cx, cy, vx, vy, is_player_bullet=True))

    def shoot_toward(self, target_x, target_y, bullets):
        """Called by Game with world-space target."""
        cx = self.x + self.W // 2
        cy = self.y + self.H // 2
        dx = target_x - cx
        dy = target_y - cy
        dist = math.hypot(dx, dy) or 1
        vx = dx / dist * BULLET_SPEED_P
        vy = dy / dist * BULLET_SPEED_P
        bullets.append(Bullet(cx, cy, vx, vy, is_player_bullet=True))

    def _toggle_slow(self):
        if self.slow_active:
            self.slow_active = False
        elif self.slow_charges > 0:
            self.slow_active  = True
            self.slow_timer   = SLOW_DURATION
            self.slow_charges -= 1

    # ── Physics / Update ──────────────────────────────────────────────────────
    def update(self, dt, tile_rects):
        if not self.is_alive:
            self._death_flash = max(0, self._death_flash - dt)
            return

        # Timers
        self.dash_cooldown   = max(0, self.dash_cooldown  - dt)
        self.iframe_timer    = max(0, self.iframe_timer   - dt)
        self._jump_buffer    = max(0, self._jump_buffer   - dt)

        # Coyote time — count down after leaving ground
        if self.on_ground:
            self._coyote_timer = self.COYOTE_TIME
        else:
            self._coyote_timer = max(0, self._coyote_timer - dt)

        # Try to consume a buffered jump
        self._try_jump()

        # Dash
        if self.is_dashing:
            self.dash_timer -= dt
            self.vel_x = self.dash_dir * DASH_SPEED
            if self.dash_timer <= 0:
                self.is_dashing = False
                self.vel_x = 0

        # Slow-time
        if self.slow_active:
            self.slow_timer -= dt / SLOW_SCALE   # dt already scaled; count real seconds
            if self.slow_timer <= 0:
                self.slow_active = False

        # Gravity
        if not self.on_ground:
            self.vel_y += GRAVITY * dt

        # Move X
        self.x += self.vel_x * dt
        self._resolve_x(tile_rects)

        # Move Y
        self.y += self.vel_y * dt
        self.on_ground = False
        self._resolve_y(tile_rects)

        # Animation tick
        self._anim_tick += dt * 8
        self._anim_frame = int(self._anim_tick) % 4

    def _resolve_x(self, tile_rects):
        r = self.rect
        for tr in tile_rects:
            if r.colliderect(tr):
                if self.vel_x > 0:
                    self.x = tr.left - self.W
                elif self.vel_x < 0:
                    self.x = tr.right
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

    # ── Damage / Death ────────────────────────────────────────────────────────
    def take_damage(self):
        if self.iframe_timer > 0 or not self.is_alive:
            return False
        self.is_alive    = False
        self._death_flash = 0.4
        return True

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surface, camera):
        sx, sy = camera.apply_point(self.x, self.y)
        r = pygame.Rect(sx, sy, self.W, self.H)

        # Body
        colour = C_FLASH if self._death_flash > 0 else C_PLAYER
        pygame.draw.rect(surface, colour, r, border_radius=4)

        # Eyes / direction indicator
        ew = 5
        ex = sx + (self.W - ew - 2) if self.facing == 1 else sx + 2
        pygame.draw.rect(surface, C_BG, (ex, sy + 6, ew, 4), border_radius=2)

        # Legs animation when moving
        if self.vel_x != 0 and self.on_ground:
            lf = self._anim_frame
            l1y = sy + self.H - 8 + (3 if lf < 2 else 0)
            l2y = sy + self.H - 8 + (3 if lf >= 2 else 0)
            pygame.draw.rect(surface, C_GRAY, (sx + 3,  l1y, 5, 8))
            pygame.draw.rect(surface, C_GRAY, (sx + 12, l2y, 5, 8))

        # Dash flash
        if self.is_dashing:
            flash = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            flash.fill((255, 255, 180, 80))
            surface.blit(flash, (sx, sy))

        # Slow-time ring
        if self.slow_active:
            cx = int(sx + self.W / 2)
            cy = int(sy + self.H / 2)
            pygame.draw.circle(surface, C_ACCENT, (cx, cy), 28, 1)
