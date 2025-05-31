import pygame
import sys
import random

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 600, 400
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Capture the Flag")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Player
player_size = 30
player_pos = [50, 50]
player_speed = 5
default_speed = player_speed

# Flag
flag_size = 20
flag_pos = [random.randint(100, WIDTH-flag_size), random.randint(100, HEIGHT-flag_size)]

def generate_obstacles(num_obstacles=4):
    obstacles = []
    for _ in range(num_obstacles):
        width = random.randint(60, 150)
        height = random.randint(15, 40)
        x = random.randint(0, WIDTH - width)
        y = random.randint(0, HEIGHT - height)
        # Avoid spawning obstacles too close to the player start
        if abs(x - 50) < 60 and abs(y - 50) < 60:
            x = 200
            y = 100
        obstacles.append(pygame.Rect(x, y, width, height))
    return obstacles

# Obstacles
obstacles = generate_obstacles()

# Enemies
enemy_size = 30
num_enemies = 3
enemies = [
    {"pos": [random.randint(0, WIDTH-enemy_size), random.randint(0, HEIGHT-enemy_size)],
     "speed": [random.choice([-2, 2]), random.choice([-2, 2])]}
    for _ in range(num_enemies)
]

# Power-up
power_up_size = 20
power_up_pos = [random.randint(0, WIDTH-power_up_size), random.randint(0, HEIGHT-power_up_size)]
power_up_active = False
power_up_timer = 0
POWER_UP_DURATION = 5000  # 5 seconds in milliseconds

# Score
score = 0
high_score = 0

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

def draw_window():
    WIN.fill(WHITE)
    pygame.draw.rect(WIN, BLUE, (*player_pos, player_size, player_size))
    pygame.draw.rect(WIN, RED, (*flag_pos, flag_size, flag_size))
    for obs in obstacles:
        pygame.draw.rect(WIN, BLACK, obs)
    for enemy in enemies:
        pygame.draw.rect(WIN, (128, 0, 128), (*enemy["pos"], enemy_size, enemy_size))
    if not power_up_active:
        pygame.draw.rect(WIN, YELLOW, (*power_up_pos, power_up_size, power_up_size))
    
    # Display score and high score
    score_text = font.render(f"Score: {score}", True, BLACK)
    high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
    WIN.blit(score_text, (10, 10))
    WIN.blit(high_score_text, (10, 50))
    
    pygame.display.update()

def check_collision(rect1, rect2):
    return pygame.Rect(rect1).colliderect(pygame.Rect(rect2))

def move_enemies():
    for enemy in enemies:
        enemy["pos"][0] += enemy["speed"][0]
        enemy["pos"][1] += enemy["speed"][1]

        # Bounce off walls
        if enemy["pos"][0] <= 0 or enemy["pos"][0] >= WIDTH - enemy_size:
            enemy["speed"][0] *= -1
        if enemy["pos"][1] <= 0 or enemy["pos"][1] >= HEIGHT - enemy_size:
            enemy["speed"][1] *= -1

def reset_game():
    global player_pos, flag_pos, power_up_pos, power_up_active, power_up_timer, score, obstacles
    player_pos = [50, 50]
    flag_pos = [random.randint(100, WIDTH-flag_size), random.randint(100, HEIGHT-flag_size)]
    power_up_pos = [random.randint(0, WIDTH-power_up_size), random.randint(0, HEIGHT-power_up_size)]
    power_up_active = False
    power_up_timer = 0
    score = 0
    obstacles = generate_obstacles()

def main():
    global player_speed, power_up_active, power_up_timer, score, high_score, flag_pos, power_up_pos
    run = True
    while run:
        clock.tick(60)  # Increased FPS for smoother gameplay
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reset game with R key
                    reset_game()

        keys = pygame.key.get_pressed()
        move = [0, 0]
        if keys[pygame.K_LEFT]:
            move[0] -= player_speed
        if keys[pygame.K_RIGHT]:
            move[0] += player_speed
        if keys[pygame.K_UP]:
            move[1] -= player_speed
        if keys[pygame.K_DOWN]:
            move[1] += player_speed

        # Move player and check for obstacle collision
        new_pos = [player_pos[0] + move[0], player_pos[1] + move[1]]
        player_rect = pygame.Rect(*new_pos, player_size, player_size)
        if not any(player_rect.colliderect(obs) for obs in obstacles):
            if 0 <= new_pos[0] <= WIDTH - player_size and 0 <= new_pos[1] <= HEIGHT - player_size:
                player_pos[:] = new_pos

        # Move enemies
        move_enemies()

        # Check for flag capture
        if check_collision((*player_pos, player_size, player_size), (*flag_pos, flag_size, flag_size)):
            score += 1
            if score > high_score:
                high_score = score
            flag_pos = [random.randint(100, WIDTH-flag_size), random.randint(100, HEIGHT-flag_size)]

        # Check for enemy collision
        for enemy in enemies:
            if check_collision((*player_pos, player_size, player_size), (*enemy["pos"], enemy_size, enemy_size)):
                WIN.fill(RED)
                text = font.render("Game Over! Press R to restart", True, WHITE)
                WIN.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
                pygame.display.update()
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            run = False
                            waiting = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_r:
                                reset_game()
                                waiting = False
                            elif event.key == pygame.K_q:
                                run = False
                                waiting = False

        # Check for power-up collision
        if not power_up_active and check_collision((*player_pos, player_size, player_size), (*power_up_pos, power_up_size, power_up_size)):
            power_up_active = True
            player_speed = 8
            power_up_timer = pygame.time.get_ticks()

        # Reset power-up effect after duration
        if power_up_active and pygame.time.get_ticks() - power_up_timer > POWER_UP_DURATION:
            power_up_active = False
            player_speed = default_speed
            power_up_pos = [random.randint(0, WIDTH-power_up_size), random.randint(0, HEIGHT-power_up_size)]

        draw_window()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 