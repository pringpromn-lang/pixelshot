"""game.py — Main game loop and state manager"""
import pygame, sys
from settings import *
from level         import Level
from player        import Player
from camera        import Camera
from bullet        import Bullet
from game_stats    import GameStats
from ui_manager    import UIManager
from input_handler import InputHandler
from stats_screen  import StatsScreen

class Game:
    # States
    START      = "start"
    STATS      = "stats"
    PLAYING    = "playing"
    DEAD       = "dead"
    NEXT_LEVEL = "next_level"
    WIN        = "win"

    def __init__(self, screen):
        self.screen      = screen
        self.ui          = UIManager(screen)
        self.stats_screen= StatsScreen(screen)
        self.state       = self.START
        self.level_num   = 1
        self._init_session(self.level_num)

    # ── Session init ─────────────────────────────────────────────────────────
    def _init_session(self, level_num=1):
        self.level_num   = level_num
        self.level       = Level(level_num)
        self.player      = Player(*self.level.spawn_pos)
        self.camera      = Camera(self.level.width, self.level.height)
        self.bullets : list[Bullet] = []
        self.stats       = GameStats()
        self.input       = InputHandler()
        self.score       = 0
        self._respawn_timer = 0.0
        self._win_summary   = None
        self._block_flashes : list[tuple] = []
        self._particles     : list[dict]  = []

    # ── Main loop ─────────────────────────────────────────────────────────────
    def run(self, clock):
        while True:
            raw_dt = clock.tick(FPS) / 1000.0
            raw_dt = min(raw_dt, 0.05)

            slow = (self.player.slow_active
                    if self.state == self.PLAYING else False)
            dt = raw_dt * (SLOW_SCALE if slow else 1.0)

            if not self.input.poll():
                self._quit()

            self._handle_global_keys()

            if   self.state == self.START:      self._update_start(dt, raw_dt)
            elif self.state == self.STATS:      self._update_stats()
            elif self.state == self.PLAYING:    self._update_playing(dt, raw_dt)
            elif self.state == self.DEAD:       self._update_dead(raw_dt)
            elif self.state == self.NEXT_LEVEL: self._update_next_level(raw_dt)
            elif self.state == self.WIN:        self._update_win()

            self._draw()
            pygame.display.flip()

    # ── Global keys ──────────────────────────────────────────────────────────
    def _handle_global_keys(self):
        if self.input.is_pressed(pygame.K_ESCAPE):
            if self.state in (self.PLAYING, self.DEAD, self.WIN, self.NEXT_LEVEL):
                self._quit()
            # ESC from STATS → back to START (handled in _draw)
        if self.input.is_pressed(pygame.K_r) and self.state in (self.DEAD, self.WIN):
            self._init_session(1)
            self.level_num = 1
            self.state = self.PLAYING

    def _quit(self):
        if self.state == self.PLAYING:
            self.stats.export_csv()
        pygame.quit()
        sys.exit()

    # ── START ────────────────────────────────────────────────────────────────
    def _update_start(self, dt, raw_dt):
        # button logic handled inside _draw via ui.draw_start_screen
        pass

    # ── STATS ────────────────────────────────────────────────────────────────
    def _update_stats(self):
        # button logic handled inside _draw via ui.draw_stats_screen
        pass

    # ── PLAYING ──────────────────────────────────────────────────────────────
    def _update_playing(self, dt, raw_dt):
        keys   = self.input.curr_state
        events = self.input.events  # contains both KEYDOWN and MOUSEBUTTONDOWN

        for event in events:
            # Mouse shoot
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                wx = mx + self.camera.offset_x
                wy = my + self.camera.offset_y
                self.player.shoot_toward(wx, wy, self.bullets)
                self.stats.record_shot()

            if event.type == pygame.KEYDOWN:
                # Keyboard shoot
                if event.key in (pygame.K_j, pygame.K_z):
                    mx, my = pygame.mouse.get_pos()
                    wx = mx + self.camera.offset_x
                    wy = my + self.camera.offset_y
                    self.player.shoot_toward(wx, wy, self.bullets)
                    self.stats.record_shot()
                # Dash stat
                if event.key == pygame.K_LSHIFT and self.player.dash_cooldown <= 0:
                    self.stats.record_dash()
                # Slow stat
                if event.key in (pygame.K_k, pygame.K_x) and self.player.slow_charges > 0:
                    self.stats.record_slow()

        # ── Jump — buffered so it is never missed ─────────────────────────────
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_w, pygame.K_UP, pygame.K_SPACE):
                    self.player.request_jump()

        # ── Player input ──────────────────────────────────────────────────────
        self.player.handle_input(events, keys, self.bullets, self.player.slow_active)
        self.player.update(dt, self.level.solid_rects)
        self.stats.record_position(self.player.x, self.player.y)

        # ── Camera ────────────────────────────────────────────────────────────
        self.camera.update(self.player.rect, raw_dt)

        # ── Enemies ───────────────────────────────────────────────────────────
        for enemy in self.level.enemies:
            if enemy.is_alive:
                enemy.update(dt, self.level.solid_rects, self.player, self.bullets)

        # ── Bullets ───────────────────────────────────────────────────────────
        self._update_bullets(dt)

        # ── Score update ──────────────────────────────────────────────────────
        summary = self.stats.get_summary()
        self.score = summary["score"]

        # ── Win / next level condition ─────────────────────────────────────────
        if self.level.check_completion(self.player.rect) and self.player.is_alive:
            self._win_summary = self.stats.export_csv()
            self.stats_screen.invalidate()
            if self.level.is_last_level:
                self.state = self.WIN
            else:
                self._next_level_timer = 1.5
                self.state = self.NEXT_LEVEL

        # ── Particles ─────────────────────────────────────────────────────────
        self._update_particles(dt)
        self.ui.update(dt)

        # ── Block flash cleanup ───────────────────────────────────────────────
        self._block_flashes = [(x, y, t - dt) for x, y, t in self._block_flashes if t - dt > 0]

    def _update_bullets(self, dt):
        # Move all bullets
        for b in self.bullets:
            b.update(dt, self.level.solid_rects)

        # Bullet-block: player bullets vs enemy bullets
        p_bullets = [b for b in self.bullets if b.is_player_bullet and b.is_active]
        e_bullets  = [b for b in self.bullets if not b.is_player_bullet and b.is_active]

        for pb in p_bullets:
            for eb in e_bullets:
                if pb.check_intercept(eb):
                    self.stats.record_block()
                    self.score += SCORE_BLOCK
                    self.ui.add_combo()
                    self._block_flashes.append((pb.x, pb.y, 0.6))
                    self._spawn_particles(pb.x, pb.y, C_ACCENT, count=8)

        # Player bullets vs enemies
        for b in p_bullets:
            if not b.is_active:
                continue
            for enemy in self.level.enemies:
                if enemy.is_alive and b.rect.colliderect(enemy.rect):
                    enemy.take_damage()
                    b.destroy()
                    self.stats.record_kill()
                    self.ui.add_combo()
                    self.camera.shake(5, 0.15)
                    self._spawn_particles(enemy.x + enemy.W//2,
                                          enemy.y + enemy.H//2, C_RED, count=10)
                    break

        # Enemy bullets vs player
        for b in e_bullets:
            if not b.is_active:
                continue
            if self.player.is_alive and b.rect.colliderect(self.player.rect):
                if self.player.take_damage():
                    b.destroy()
                    self.stats.record_death()
                    self.camera.shake(10, 0.3)
                    self._spawn_particles(
                        self.player.x + self.player.W // 2,
                        self.player.y + self.player.H // 2,
                        C_PLAYER, count=12)
                    self._respawn_timer = 2.0
                    self.state = self.DEAD

        # Prune dead bullets
        self.bullets = [b for b in self.bullets if b.is_active]

    # ── DEAD ─────────────────────────────────────────────────────────────────
    def _update_dead(self, raw_dt):
        self._respawn_timer -= raw_dt
        self._update_particles(raw_dt)
        if self._respawn_timer <= 0:
            self.level = Level(self.level_num)
            self.player = Player(*self.level.spawn_pos)
            self.camera = Camera(self.level.width, self.level.height)
            self.bullets.clear()
            self.state = self.PLAYING

    # ── NEXT LEVEL ───────────────────────────────────────────────────────────
    def _update_next_level(self, raw_dt):
        self._next_level_timer -= raw_dt
        if self._next_level_timer <= 0:
            self.level_num += 1
            self._init_session(self.level_num)
            self.state = self.PLAYING

    # ── WIN ──────────────────────────────────────────────────────────────────
    def _update_win(self):
        pass  # wait for R / ESC

    # ── Particles ─────────────────────────────────────────────────────────────
    def _spawn_particles(self, x, y, colour, count=6):
        import random, math
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(60, 220)
            self._particles.append({
                "x": x, "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.uniform(0.3, 0.7),
                "colour": colour,
                "size": random.randint(2, 5)
            })

    def _update_particles(self, dt):
        for p in self._particles:
            p["x"]   += p["vx"] * dt
            p["y"]   += p["vy"] * dt
            p["vy"]  += 400 * dt   # gravity
            p["life"] -= dt
        self._particles = [p for p in self._particles if p["life"] > 0]

    # ── Draw ─────────────────────────────────────────────────────────────────
    def _draw(self):
        mouse_pos = pygame.mouse.get_pos()
        events    = self.input.events

        if self.state == self.START:
            action = self.ui.draw_start_screen(mouse_pos, events)
            if action == "play":
                self._init_session(1)
                self.level_num = 1
                self.state = self.PLAYING
            elif action == "stats":
                self.state = self.STATS
            # Also allow ENTER key
            if self.input.is_pressed(pygame.K_RETURN):
                self._init_session(1)
                self.level_num = 1
                self.state = self.PLAYING
            return

        if self.state == self.STATS:
            action = self.stats_screen.draw(mouse_pos, events)
            if action == "back":
                self.state = self.START
            return

        # Level + entities
        self.level.draw(self.screen, self.camera)
        for b in self.bullets:
            b.draw(self.screen, self.camera)
        for enemy in self.level.enemies:
            enemy.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)

        # Particles
        for p in self._particles:
            sx, sy = self.camera.apply_point(p["x"], p["y"])
            alpha  = int(max(0, p["life"] / 0.7 * 200))
            size   = p["size"]
            surf   = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            c      = (*p["colour"], alpha)
            pygame.draw.circle(surf, c, (size, size), size)
            self.screen.blit(surf, (sx - size, sy - size))

        # Block flashes
        for x, y, t in self._block_flashes:
            sx, sy = self.camera.apply_point(x, y)
            self.ui.show_block_flash(int(sx), int(sy))

        if self.state == self.PLAYING or self.state == self.DEAD:
            summary = self.stats.get_summary()
            self.ui.draw_hud(
                score         = summary["score"],
                slow_charges  = self.player.slow_charges,
                slow_active   = self.player.slow_active,
                slow_timer    = self.player.slow_timer,
                dash_cooldown = self.player.dash_cooldown,
                kills         = summary["kill_count"],
                bullet_blocks = summary["bullet_blocks"],
                deaths        = summary["deaths"],
            )

        if self.state == self.DEAD:
            self.ui.draw_death_screen(self._respawn_timer)

        if self.state == self.NEXT_LEVEL:
            self.ui.draw_next_level_screen(self.level_num, self._win_summary)

        if self.state == self.WIN:
            self.ui.show_rank_screen(self._win_summary)
