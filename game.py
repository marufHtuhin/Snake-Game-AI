import json
import os
import pygame

from settings import *
from snake import Snake, DIRECTIONS
from food import Food
from ai.ai_controller import AIController

class SnakeGame:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial,dejavusans", 20)
        self.small = pygame.font.SysFont("arial,dejavusans", 15)
        self.medium = pygame.font.SysFont("arial,dejavusans", 27, bold=True)
        self.large = pygame.font.SysFont("arial,dejavusans", 48, bold=True)
        self.highscore_file = os.path.join("data", "highscore.json")
        try:
            os.makedirs("data", exist_ok=True)
        except OSError:
            pass
        self.highscore = self.load_highscore()
        self.state = "menu"
        self.mode = "player"
        self.reset()

    def load_highscore(self):
        try:
            with open(self.highscore_file, "r", encoding="utf-8") as f:
                return int(json.load(f).get("highscore", 0))
        except (OSError, ValueError, json.JSONDecodeError):
            return 0

    def save_highscore(self):
        if self.score > self.highscore:
            self.highscore = self.score
            try:
                with open(self.highscore_file, "w", encoding="utf-8") as f:
                    json.dump({"highscore": self.highscore}, f)
            except OSError:
                pass

    def reset(self):
        self.snake = Snake(BOARD_COLS, BOARD_ROWS)
        self.food = Food(BOARD_COLS, BOARD_ROWS)
        self.food.respawn(self.snake.body)
        self.ai = AIController(BOARD_COLS, BOARD_ROWS)
        self.score = 0
        self.paused = False
        self.move_timer = 0.0
        self.move_delay = 0.115

    def start(self, mode):
        self.reset()
        self.mode = mode
        self.state = "playing"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.state == "playing":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                        self.move_delay = max(0.03, self.move_delay - 0.015)
                    elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        self.move_delay = min(0.3, self.move_delay + 0.015)
                    elif self.mode == "player":
                        keys = {
                            pygame.K_UP: "UP",
                            pygame.K_DOWN: "DOWN",
                            pygame.K_LEFT: "LEFT",
                            pygame.K_RIGHT: "RIGHT",
                        }
                        if event.key in keys:
                            self.snake.set_direction(keys[event.key])
                elif self.state in ("gameover", "win"):
                    if event.key == pygame.K_RETURN:
                        self.start(self.mode)
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                elif self.state == "menu" and event.key == pygame.K_ESCAPE:
                    return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if self.state == "menu":
                    if self.player_button.collidepoint(pos):
                        self.start("player")
                    elif self.ai_button.collidepoint(pos):
                        self.start("ai")
                    elif self.help_button.collidepoint(pos):
                        self.state = "help"
                    elif self.quit_button.collidepoint(pos):
                        return False
                elif self.state == "help":
                    if self.back_button.collidepoint(pos):
                        self.state = "menu"
                elif self.state in ("gameover", "win"):
                    if self.again_button.collidepoint(pos):
                        self.start(self.mode)
                    elif self.menu_button.collidepoint(pos):
                        self.state = "menu"
                elif self.state == "playing":
                    if self.pause_button.collidepoint(pos):
                        self.paused = not self.paused
                    elif self.menu_small_button.collidepoint(pos):
                        self.state = "menu"
        return True

    def update(self, dt):
        if self.state != "playing" or self.paused:
            return
        self.move_timer += dt
        if self.move_timer < self.move_delay:
            return
        self.move_timer = 0

        direction = None
        if self.mode == "ai":
            direction = self.ai.choose_direction(self.snake, self.food.position)

        # Determine next cell before moving.
        if direction:
            self.snake.set_direction(direction)
        next_head = self.snake.next_head()
        eating = next_head == self.food.position

        # The tail vacates its cell unless the snake eats food this turn.
        collision_body = list(self.snake.body) if eating else list(self.snake.body)[:-1]
        hit_wall = not (0 <= next_head[0] < BOARD_COLS and 0 <= next_head[1] < BOARD_ROWS)
        hit_self = next_head in collision_body

        if hit_wall or hit_self:
            self.state = "gameover"
            self.save_highscore()
            return

        if eating:
            self.snake.grow()
        self.snake.move()
        if eating:
            self.score += 10
            self.food.respawn(self.snake.body)
            if self.food.position is None:
                self.state = "win"
                self.save_highscore()

    def draw_text(self, text, font, color, center):
        surface = font.render(text, True, color)
        self.screen.blit(surface, surface.get_rect(center=center))

    def draw_button(self, rect, text, color=None):
        mouse = rect.collidepoint(pygame.mouse.get_pos())
        fill = COLORS["panel2"] if mouse else COLORS["panel"]
        pygame.draw.rect(self.screen, fill, rect, border_radius=13)
        pygame.draw.rect(self.screen, color or COLORS["green"], rect, 2, border_radius=13)
        self.draw_text(text, self.font, COLORS["white"], rect.center)

    def draw_menu(self):
        self.screen.fill(COLORS["bg"])
        self.draw_text("SNAKE GAME", self.large, COLORS["white"], (500, 155))
        self.draw_text("AI EDITION", self.medium, COLORS["green"], (500, 207))
        self.draw_text("Think smart. Move fast. Survive longer.", self.font, COLORS["muted"], (500, 260))
        self.draw_text("Choose your game mode", self.font, COLORS["white"], (500, 315))
        self.player_button = pygame.Rect(350, 350, 300, 55)
        self.ai_button = pygame.Rect(350, 420, 300, 55)
        self.help_button = pygame.Rect(350, 490, 145, 50)
        self.quit_button = pygame.Rect(505, 490, 145, 50)
        self.draw_button(self.player_button, "PLAY WITH PLAYER")
        self.draw_button(self.ai_button, "PLAY WITH AI")
        self.draw_button(self.help_button, "HOW TO PLAY", COLORS["blue"])
        self.draw_button(self.quit_button, "EXIT", COLORS["red"])
        self.draw_text("Built with Python, Pygame and A* Search", self.small, COLORS["muted"], (500, 600))

    def draw_help(self):
        self.screen.fill(COLORS["bg"])
        self.draw_text("HOW TO PLAY", self.large, COLORS["green"], (500, 175))
        lines = [
            "PLAYER MODE: Use arrow keys to control the snake.",
            "AI MODE: A* searches for food; safety checks avoid traps.",
            "Eat food to gain 10 points and grow longer.",
            "Avoid the walls and your own body.",
            "SPACE: Pause   ESC: Menu   + / - : Speed",
        ]
        for i, line in enumerate(lines):
            self.draw_text(line, self.font, COLORS["white"], (500, 270 + i * 48))
        self.back_button = pygame.Rect(400, 540, 200, 55)
        self.draw_button(self.back_button, "BACK TO MENU")

    def draw_game(self):
        self.screen.fill(COLORS["bg"])
        self.draw_text("SNAKE GAME AI", self.medium, COLORS["white"], (220, 42))
        mode_text = "AI AUTOPILOT" if self.mode == "ai" else "PLAYER MODE"
        self.draw_text(mode_text, self.font, COLORS["green"], (500, 42))
        self.draw_text(f"SCORE  {self.score}", self.font, COLORS["white"], (760, 35))
        self.draw_text(f"BEST  {self.highscore}", self.small, COLORS["muted"], (760, 63))

        board = pygame.Rect(BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT)
        pygame.draw.rect(self.screen, COLORS["panel"], board, border_radius=10)
        for x in range(BOARD_COLS + 1):
            px = BOARD_X + x * CELL
            pygame.draw.line(self.screen, COLORS["grid"], (px, BOARD_Y), (px, BOARD_Y + BOARD_HEIGHT))
        for y in range(BOARD_ROWS + 1):
            py = BOARD_Y + y * CELL
            pygame.draw.line(self.screen, COLORS["grid"], (BOARD_X, py), (BOARD_X + BOARD_WIDTH, py))

        if self.mode == "ai":
            for (px_, py_) in self.ai.path:
                r = pygame.Rect(BOARD_X + px_ * CELL + 9, BOARD_Y + py_ * CELL + 9, CELL - 18, CELL - 18)
                pygame.draw.rect(self.screen, COLORS["blue"], r, border_radius=3)

        if self.food.position:
            fx, fy = self.food.position
            center = (BOARD_X + fx * CELL + CELL // 2, BOARD_Y + fy * CELL + CELL // 2)
            pygame.draw.circle(self.screen, COLORS["red"], center, CELL // 2 - 3)
            pygame.draw.circle(self.screen, COLORS["yellow"], (center[0] + 3, center[1] - 4), 3)

        for i, (x, y) in enumerate(self.snake.body):
            rect = pygame.Rect(BOARD_X + x * CELL + 2, BOARD_Y + y * CELL + 2, CELL - 4, CELL - 4)
            color = COLORS["green"] if i == 0 else COLORS["green_dark"]
            pygame.draw.rect(self.screen, color, rect, border_radius=6)
            if i == 0:
                self.draw_snake_eyes(rect)

        self.pause_button = pygame.Rect(355, 665 - 45, 135, 35)
        self.menu_small_button = pygame.Rect(510, 620, 135, 35)
        self.draw_button(self.pause_button, "RESUME" if self.paused else "PAUSE", COLORS["blue"])
        self.draw_button(self.menu_small_button, "MAIN MENU", COLORS["red"])
        status = self.ai.last_status if self.mode == "ai" else "Arrow keys to move"
        self.draw_text(status, self.small, COLORS["muted"], (500, 650))

        if self.paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            self.draw_text("PAUSED", self.large, COLORS["white"], (500, 335))
            self.draw_text("Press SPACE to continue", self.font, COLORS["green"], (500, 390))

    def draw_snake_eyes(self, rect):
        cx, cy = rect.center
        if self.snake.direction == "RIGHT":
            eyes = [(cx + 5, cy - 5), (cx + 5, cy + 5)]
        elif self.snake.direction == "LEFT":
            eyes = [(cx - 5, cy - 5), (cx - 5, cy + 5)]
        elif self.snake.direction == "UP":
            eyes = [(cx - 5, cy - 5), (cx + 5, cy - 5)]
        else:
            eyes = [(cx - 5, cy + 5), (cx + 5, cy + 5)]
        for eye in eyes:
            pygame.draw.circle(self.screen, COLORS["bg"], eye, 2)

    def draw_end(self):
        self.screen.fill(COLORS["bg"])
        title = "YOU WIN!" if self.state == "win" else "GAME OVER"
        self.draw_text(title, self.large, COLORS["green"] if self.state == "win" else COLORS["red"], (500, 230))
        self.draw_text(f"Final score: {self.score}", self.medium, COLORS["white"], (500, 310))
        self.draw_text(f"Best score: {self.highscore}", self.font, COLORS["muted"], (500, 355))
        self.again_button = pygame.Rect(350, 420, 300, 55)
        self.menu_button = pygame.Rect(350, 490, 300, 55)
        self.draw_button(self.again_button, "PLAY AGAIN")
        self.draw_button(self.menu_button, "MAIN MENU", COLORS["blue"])

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "help":
            self.draw_help()
        elif self.state == "playing":
            self.draw_game()
        elif self.state in ("gameover", "win"):
            self.draw_end()
