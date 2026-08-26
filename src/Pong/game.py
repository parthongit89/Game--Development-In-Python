import json
import os
import math
import random
import pygame

from audio import SoundEffects
from config import *
from entities import Ball, Flash, Paddle, PowerUp, SparkParticle, Confetti


class PongGame:
    def __init__(self):
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        self.fullscreen = True
        try:
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        except Exception:
            self.window = pygame.display.set_mode((WIDTH, HEIGHT))
            self.fullscreen = False
            
        pygame.display.set_caption("Enhanced Pong")

        self.font = pygame.font.SysFont("comicsans", 30)
        self.score_font = pygame.font.SysFont("comicsans", 50)
        self.title_font = pygame.font.SysFont("comicsans", 72, bold=True)
        self.rally_font = pygame.font.SysFont("comicsans", 28, bold=True)
        self.small_font = pygame.font.SysFont("comicsans", 22)
        
        self.sounds, self.clock = SoundEffects(), pygame.time.Clock()
        self.left, self.right, self.ball = Paddle(10, 200), Paddle(WIDTH - 30, 200), Ball()
        self.mode, self.state, self.scores = "single", "start", [0, 0]
        self.ai_difficulty = "Medium"
        self.is_paused = False
        
        self.countdown_start = self.last_powerup = 0
        self.last_countdown_sec = -1
        self.powerup, self.flashes, self.running = None, [], True
        self.sparks, self.confetti = [], [Confetti(WIDTH, HEIGHT) for _ in range(60)]
        self.rally_count = 0
        self.shake_until = 0
        
        # Match statistics
        self.match_start_time = 0
        self.match_duration_sec = 0
        self.max_match_rally = 0
        self.powerups_collected = 0

        # High Scores & Best Rally Persistence
        self.highscore_file = os.path.join(os.path.dirname(__file__), "highscores_pong.json")
        self.best_rally = 0
        self.total_wins = 0
        self.load_highscores()

    def load_highscores(self):
        try:
            if os.path.exists(self.highscore_file):
                with open(self.highscore_file, "r") as f:
                    data = json.load(f)
                    self.best_rally = data.get("best_rally", 0)
                    self.total_wins = data.get("total_wins", 0)
        except Exception:
            pass

    def save_highscores(self):
        try:
            with open(self.highscore_file, "w") as f:
                json.dump({"best_rally": self.best_rally, "total_wins": self.total_wins}, f)
        except Exception:
            pass

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            now = pygame.time.get_ticks()
            self.handle_events(now)
            self.update(now)
            self.draw(now)
        pygame.quit()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            try:
                self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            except Exception:
                self.window = pygame.display.set_mode((WIDTH, HEIGHT))
                self.fullscreen = False
        else:
            self.window = pygame.display.set_mode((WIDTH, HEIGHT))

    def handle_events(self, now):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                    continue
                if self.state == "start":
                    if event.key == pygame.K_1:
                        self.mode = "single"
                    elif event.key == pygame.K_2:
                        self.mode = "two"
                    elif event.key in (pygame.K_d, pygame.K_DIALPAD_D):
                        diffs = list(AI_DIFFICULTIES.keys())
                        idx = (diffs.index(self.ai_difficulty) + 1) % len(diffs)
                        self.ai_difficulty = diffs[idx]
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.start_match(now)
                elif self.state in ("playing", "countdown"):
                    if event.key in (pygame.K_p, pygame.K_ESCAPE):
                        self.is_paused = not self.is_paused
                    elif self.is_paused:
                        if event.key == pygame.K_r:
                            self.start_match(now)
                        elif event.key == pygame.K_m:
                            self.state = "start"
                            self.is_paused = False
                elif self.state == "game_over":
                    if event.key == pygame.K_r:
                        self.start_match(now)
                    elif event.key in (pygame.K_ESCAPE, pygame.K_m):
                        self.state = "start"


    def start_match(self, now):
        self.scores, self.powerup, self.flashes, self.sparks = [0, 0], None, [], []
        self.ball.reset()
        self.rally_count = 0
        self.max_match_rally = 0
        self.powerups_collected = 0
        self.match_start_time = now
        self.match_duration_sec = 0
        self.countdown_start = self.last_powerup = now
        self.last_countdown_sec = -1
        self.state = "countdown"
        self.is_paused = False

    def update(self, now):
        if self.is_paused:
            return

        for paddle in (self.left, self.right):
            paddle.update(now)
        self.flashes = [flash for flash in self.flashes if flash.tick()]
        self.sparks = [spark for spark in self.sparks if spark.tick()]
        
        if self.state == "game_over":
            for c in self.confetti:
                c.tick(HEIGHT)
            return

        if self.state == "countdown":
            elapsed = now - self.countdown_start
            sec = max(1, COUNTDOWN_SECONDS - elapsed // 1000)
            if sec != self.last_countdown_sec:
                self.last_countdown_sec = sec
                self.sounds.play("countdown_beep")
            if elapsed >= COUNTDOWN_SECONDS * 1000:
                self.sounds.play("countdown_go")
                self.state = "playing"
            return

        # Main gameplay update
        self.move_paddles()
        self.ball.move()
        self.handle_collisions(now)
        self.update_powerup(now)
        self.check_score(now)

    def move_paddles(self):
        keys = pygame.key.get_pressed()
        self.move_human(self.left, keys, pygame.K_w, pygame.K_s)
        if self.mode == "two":
            self.move_human(self.right, keys, pygame.K_UP, pygame.K_DOWN)
            return

        # Single Player AI Movement
        self.right.stop()
        target = self.ball.y if self.ball.x_vel > 0 else HEIGHT / 2
        diff = AI_DIFFICULTIES[self.ai_difficulty]
        speed, tol = diff["speed"], diff["tolerance"]

        if self.right.center_y < target - tol:
            self.right.move(1, speed=speed)
        elif self.right.center_y > target + tol:
            self.right.move(-1, speed=speed)

    @staticmethod
    def move_human(paddle, keys, up, down):
        paddle.stop()
        if keys[up]: paddle.move(-1)
        if keys[down]: paddle.move(1)

    def handle_collisions(self, now):
        ball = self.ball
        if ball.y + ball.radius >= HEIGHT or ball.y - ball.radius <= 0:
            ball.y = min(max(ball.y, ball.radius), HEIGHT - ball.radius)
            ball.y_vel *= -1
            self.feedback(ball.x, ball.y, GRAY, "wall")
            
        paddle = self.left if ball.x_vel < 0 else self.right
        reaches = ball.x - ball.radius <= paddle.x + paddle.width if ball.x_vel < 0 else ball.x + ball.radius >= paddle.x
        
        if paddle.y <= ball.y <= paddle.y + paddle.height and reaches:
            ball.x = paddle.x + paddle.width + ball.radius if ball.x_vel < 0 else paddle.x - ball.radius
            angle = (ball.y - paddle.center_y) / (paddle.height / 2)
            ball.y_vel = max(-ball.MAX_SPEED, min(ball.MAX_SPEED, angle * ball.speed + paddle.last_move * 2.2))
            ball.speed_up()
            ball.x_vel = ball.speed if ball.x_vel < 0 else -ball.speed
            
            self.rally_count += 1
            self.max_match_rally = max(self.max_match_rally, self.rally_count)
            
            if self.rally_count > self.best_rally:
                self.best_rally = self.rally_count
                self.save_highscores()
                
            if self.rally_count >= 5:
                self.shake_until = now + 150
                
            for _ in range(12):
                self.sparks.append(SparkParticle(ball.x, ball.y, CYAN if ball.speed < 7 else (255, 180, 50)))
            self.feedback(ball.x, ball.y, CYAN, "hit")

    def update_powerup(self, now):
        if self.powerup is None and now - self.last_powerup >= 8000:
            self.powerup, self.last_powerup = PowerUp.spawn(now), now
        if self.powerup and now >= self.powerup.expires_at:
            self.powerup, self.last_powerup = None, now
        if self.powerup and math.hypot(self.ball.x - self.powerup.x, self.ball.y - self.powerup.y) <= self.ball.radius + 14:
            self.powerups_collected += 1
            if self.powerup.kind == "grow":
                (self.right if self.ball.x_vel > 0 else self.left).grow_until = now + 6000
            else:
                self.ball.slow_down()
            self.feedback(self.powerup.x, self.powerup.y, POWERUP_COLORS[self.powerup.kind], "power", 28)
            self.powerup = None

    def check_score(self, now):
        if not (self.ball.x < 0 or self.ball.x > WIDTH): return
        self.scores[1 if self.ball.x < 0 else 0] += 1
        self.sounds.play("score")
        self.powerup, self.flashes, self.rally_count = None, [], 0
        if max(self.scores) >= WINNING_SCORE:
            self.state = "game_over"
            self.match_duration_sec = (now - self.match_start_time) // 1000
            self.sounds.play("victory")
            self.total_wins += 1
            self.save_highscores()
        else:
            self.ball.reset()
            self.countdown_start = now
            self.last_countdown_sec = -1
            self.state = "countdown"

    def feedback(self, x, y, color, sound, size=20):
        self.flashes.append(Flash(x, y, color, size))
        self.sounds.play(sound)

    def draw(self, now):
        offset_x = random.randint(-4, 4) if now < self.shake_until else 0
        offset_y = random.randint(-4, 4) if now < self.shake_until else 0
        surface = pygame.Surface((WIDTH, HEIGHT))

        if self.state == "start":
            self.draw_start(surface)
        elif self.state == "game_over":
            self.draw_winner(surface)
        else:
            countdown = None
            if self.state == "countdown":
                elapsed = now - self.countdown_start
                countdown = max(1, COUNTDOWN_SECONDS - elapsed // 1000)
            self.draw_board(surface, countdown, now)
            
            if self.is_paused:
                self.draw_pause_overlay(surface)

        win_w, win_h = self.window.get_size()
        if (win_w, win_h) == (WIDTH, HEIGHT):
            self.window.blit(surface, (offset_x, offset_y))
        else:
            scaled = pygame.transform.smoothscale(surface, (win_w, win_h))
            self.window.blit(scaled, (offset_x, offset_y))
        pygame.display.flip()

    def text(self, surface, value, y, font=None, color=WHITE):
        image = (font or self.font).render(value, True, color)
        surface.blit(image, (WIDTH // 2 - image.get_width() // 2, y))

    def draw_start(self, surface):
        surface.fill(BLACK)
        self.text(surface, "ENHANCED PONG", 70, self.title_font, color=WHITE)
        
        self.text(surface, "1: Single player vs AI     2: Two players", 195)
        selected_mode = "Single player vs AI" if self.mode == "single" else "Two players"
        self.text(surface, f"Mode: {selected_mode}", 235, color=CYAN)
        
        if self.mode == "single":
            self.text(surface, f"Press D to change AI Difficulty: [{self.ai_difficulty}]", 275, color=GOLD)
            
        self.text(surface, f"ALL-TIME BEST RALLY: {self.best_rally}   MATCH WINS: {self.total_wins}", 325, color=(255, 180, 50))
        self.text(surface, "Press SPACE or ENTER to start match", 375, color=WHITE)
        self.text(surface, "Controls: W/S (Left) | Arrows (Right) | P: Pause | F11: Fullscreen", 420, color=GRAY)


    def draw_pause_overlay(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))
        
        self.text(surface, "PAUSED", 160, self.title_font, color=GOLD)
        self.text(surface, "P or ESC : Resume Match", 250, color=WHITE)
        self.text(surface, "R : Restart Match", 295, color=CYAN)
        self.text(surface, "M : Return to Main Menu", 340, color=GRAY)

    def draw_winner(self, surface):
        surface.fill(BLACK)
        for c in self.confetti:
            pygame.draw.rect(surface, c.color, (int(c.x), int(c.y), 6, 6))
            
        if self.mode == "single":
            winner = "You win!" if self.scores[0] > self.scores[1] else "Computer wins!"
        else:
            winner = "Left Player wins!" if self.scores[0] > self.scores[1] else "Right Player wins!"
            
        self.text(surface, winner, 100, self.title_font, color=GOLD)
        self.text(surface, f"Final Score: {self.scores[0]} - {self.scores[1]}", 185, self.score_font)
        
        # Match statistics
        self.text(surface, f"Match Duration: {self.match_duration_sec} seconds", 250, self.font, color=CYAN)
        self.text(surface, f"Match Max Rally: {self.max_match_rally} hits", 290, self.font, color=WHITE)
        self.text(surface, f"Power-Ups Grabbed: {self.powerups_collected}", 330, self.font, color=(65, 220, 110))
        self.text(surface, f"All-Time Best Rally: {self.best_rally}", 370, self.font, color=GOLD)
        
        self.text(surface, "Press R to play again or ESC/M for Main Menu", 425, color=GRAY)

    def draw_board(self, surface, countdown, now):
        surface.fill(BLACK)
        
        # Score display
        for x, score in ((WIDTH // 4, self.scores[0]), (WIDTH * 3 // 4, self.scores[1])):
            image = self.score_font.render(str(score), True, WHITE)
            surface.blit(image, (x - image.get_width() // 2, 20))
            
        # Center court divider
        for y in range(10, HEIGHT, HEIGHT // 10):
            pygame.draw.rect(surface, (90, 90, 90), (WIDTH // 2 - 2, y, 4, HEIGHT // 20))
        
        # Best Rally & Active Rally HUD
        best_text = self.rally_font.render(f"BEST RALLY: {self.best_rally}", True, GOLD)
        surface.blit(best_text, (WIDTH // 2 - best_text.get_width() // 2, 10))

        if self.rally_count >= 3:
            r_text = self.rally_font.render(f"RALLY x{self.rally_count}!", True, GOLD if self.rally_count >= 6 else CYAN)
            surface.blit(r_text, (WIDTH // 2 - r_text.get_width() // 2, 100))

        # Render paddles & active buff timers
        for paddle in (self.left, self.right):
            pygame.draw.rect(surface, WHITE, (paddle.x, paddle.y, paddle.width, paddle.height), border_radius=3)
            if now < paddle.grow_until:
                remaining_ratio = max(0.0, (paddle.grow_until - now) / 6000)
                bar_width = int(paddle.width * remaining_ratio)
                pygame.draw.rect(surface, (65, 220, 110), (paddle.x, paddle.y - 8, bar_width, 4))

        # Power-up drop
        if self.powerup:
            pygame.draw.circle(surface, POWERUP_COLORS[self.powerup.kind], (self.powerup.x, self.powerup.y), 14)
            self.text(surface, "+" if self.powerup.kind == "grow" else "S", self.powerup.y - 14, color=BLACK)

        # Dynamic Rainbow Ball Trail
        ratio = min(1.0, (self.ball.speed - self.ball.BASE_SPEED) / (self.ball.MAX_SPEED - self.ball.BASE_SPEED))
        trail_color = (int(255 * ratio), int(255 * (1 - ratio)), 255)
        for index, (x, y) in enumerate(self.ball.trail):
            alpha_val = int(255 * (index / max(1, len(self.ball.trail))))
            c = (min(255, trail_color[0] + alpha_val // 2), min(255, trail_color[1] + alpha_val // 2), min(255, trail_color[2] + alpha_val // 2))
            pygame.draw.circle(surface, c, (round(x), round(y)), max(2, index // 2))
        
        # Ball & visual effects
        pygame.draw.circle(surface, WHITE, (round(self.ball.x), round(self.ball.y)), self.ball.radius)
        for flash in self.flashes:
            pygame.draw.circle(surface, flash.color, (round(flash.x), round(flash.y)), flash.size, 2)
        for spark in self.sparks:
            pygame.draw.circle(surface, spark.color, (round(spark.x), round(spark.y)), int(spark.radius))
            
        if countdown:
            self.text(surface, f"Serve in {countdown}", HEIGHT // 2 - 100, font=self.title_font, color=GOLD)
