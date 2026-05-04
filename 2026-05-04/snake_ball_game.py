import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Ball Game')
clock = pygame.time.Clock()

# Font for score (defined globally so it can be used in draw_score)
font = pygame.font.SysFont(None, 30)

# Snake creation
def create_snake():
    # Start with 3 segments in the middle
    start_x = GRID_WIDTH // 2
    start_y = GRID_HEIGHT // 2
    return [
        (start_x, start_y),
        (start_x - 1, start_y),
        (start_x - 2, start_y)
    ]

snake = create_snake()
snake_direction = (1, 0)  # Moving right initially

# Food (ball) creation
def spawn_food():
    while True:
        food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if food not in snake:
            return food

food = spawn_food()

# Score tracking
score = 0

# Drawing helpers
def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (WIDTH, y))

def draw_snake(snake_body):
    for segment in snake_body:
        x, y = segment[0] * GRID_SIZE, segment[1] * GRID_SIZE
        pygame.draw.rect(screen, GREEN, (x, y, GRID_SIZE, GRID_SIZE))

def draw_food(food_pos):
    x, y = food_pos[0] * GRID_SIZE, food_pos[1] * GRID_SIZE
    pygame.draw.rect(screen, RED, (x, y, GRID_SIZE, GRID_SIZE))

def draw_score(score):
    text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(text, (10, 10))

# Game over handling
def game_over():
    global score
    screen.fill(BLACK)
    game_over_text = font.render('Game Over', True, RED)
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 30))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 10))
    pygame.display.flip()
    pygame.time.wait(2000)
    pygame.quit()
    sys.exit()

# Main game loop
def main():
    global snake, snake_direction, food, score
    score = 0
    snake = create_snake()
    snake_direction = (1, 0)
    food = spawn_food()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake_direction != (0, 1):
                    snake_direction = (0, -1)
                elif event.key == pygame.K_DOWN and snake_direction != (0, -1):
                    snake_direction = (0, 1)
                elif event.key == pygame.K_LEFT and snake_direction != (1, 0):
                    snake_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and snake_direction != (-1, 0):
                    snake_direction = (1, 0)

        # Move snake
        head_x, head_y = snake[0]
        dx, dy = snake_direction
        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)
        snake.insert(0, new_head)

        # Check if food eaten
        if new_head == food:
            score += 1
            food = spawn_food()
        else:
            snake.pop()  # Remove tail

        # Self-collision detection
        if new_head in snake[1:]:
            game_over()

        # Draw everything
        screen.fill(BLACK)
        draw_grid()
        draw_snake(snake)
        draw_food(food)
        draw_score(score)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()