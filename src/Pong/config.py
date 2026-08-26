"""Central configuration for Pong."""

WIDTH, HEIGHT, FPS = 700, 500, 60
WINNING_SCORE, COUNTDOWN_SECONDS = 5, 3
PADDLE_WIDTH, PADDLE_HEIGHT, BALL_RADIUS = 20, 100, 7
WHITE, BLACK, GRAY, CYAN = (255, 255, 255), (0, 0, 0), (170, 170, 170), (80, 220, 255)
GOLD, ORANGE, PURPLE = (255, 215, 0), (255, 140, 0), (155, 100, 255)
POWERUP_COLORS = {"grow": (65, 220, 110), "slow": PURPLE}

AI_DIFFICULTIES = {
    "Easy": {"speed": 3, "tolerance": 16},
    "Medium": {"speed": 4, "tolerance": 8},
    "Hard": {"speed": 5.5, "tolerance": 2},
}

