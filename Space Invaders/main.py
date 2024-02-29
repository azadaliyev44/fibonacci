import sys
import random
import pygame
import math


pygame.init()
pygame.font.init()
font = pygame.font.SysFont("Courier New", 20)
clock = pygame.time.Clock()
running = True
player = pygame.transform.scale(
    pygame.image.load("assets/images/space_ship.png"), (80, 80)
)
heart_image = pygame.transform.scale(
    pygame.image.load("assets/images/hp.png"), (20, 20)
)
level_completed = False
boss_spawned = False


WINDOW_WIDTH = 500
WINDOW_HEIGHT = 750
CONSTANT_PLAYER_Y = 620
SPEED = 15
FPS = 60
player_position = 210
score = 0
level = 1
background_color = (0, 0, 0)
player_health = 3
shoot_timer = 0

# Sounds
shoot_sound = pygame.mixer.Sound("assets/sounds/shoot.wav")
enemy_death_sound = pygame.mixer.Sound("assets/sounds/enemy_dead.wav")
boss_death_sound = pygame.mixer.Sound("assets/sounds/boss_dead.wav")
game_over_sound = pygame.mixer.Sound("assets/sounds/game_over.wav")
boss_spawn_sound = pygame.mixer.Sound("assets/sounds/boss_spawned.wav")
hp_loss_sound = pygame.mixer.Sound("assets/sounds/hp_loss.wav")


# projectile details
projectile_speed = 2000
projectile_frequency = 0.1
projectile_image = pygame.transform.scale(
    pygame.image.load("assets/images/projectile.png"), (7, 15)
)
projectiles = []

# enemy details
enemy_drone = pygame.transform.scale(
    pygame.image.load("assets/images/enemy_drone.png"), (80, 40)
)
enemy_space_ship = pygame.transform.scale(
    pygame.image.load("assets/images/enemy_space_ship.png"), (80, 80)
)
enemy_ufo = pygame.transform.scale(
    pygame.image.load("assets/images/enemy_ufo.png"), (80, 60)
)
enemy_boss = pygame.transform.scale(
    pygame.image.load("assets/images/enemy_boss.png"), (160, 160)
)
enemy_spawn_cooldown = 0.5
enemy_spawn_timer = enemy_spawn_cooldown
enemies = []
enemy_dict = { 
    enemy_drone: {"speed": 200, "health": 2},
    enemy_ufo: {"speed": 100, "health": 4},
    enemy_space_ship: {"speed": 50, "health": 6},
    enemy_boss: {"speed": 50, "health": 15},
}

window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Invaders")

while running:
    delta_time = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ##Render
    window.blit(player, (player_position, CONSTANT_PLAYER_Y))
    # Enemy
    if not boss_spawned:
        enemy_spawn_timer -= delta_time
        if enemy_spawn_timer <= 0:
            enemy_image = random.choice((enemy_space_ship, enemy_drone, enemy_ufo))
            enemy_x = random.randint(0, WINDOW_WIDTH - enemy_image.get_width())
            enemy_y = 0
            enemy = {
                "image": enemy_image,
                "x": enemy_x,
                "y": enemy_y,
                "speed": enemy_dict[enemy_image]["speed"] * math.sqrt(level),
                "health": enemy_dict[enemy_image]["health"] * 0.5 * level + 0.5,
            }
            enemies.append(enemy)
            enemy_spawn_timer = enemy_spawn_cooldown

    if score == round(10 * 2.5**level) and not level_completed:
        # Boss spawns
        enemy = {
            "image": enemy_boss,
            "x": 170,
            "y": 0,
            "speed": enemy_dict[enemy_boss]["speed"] * math.sqrt(level),
            "health": enemy_dict[enemy_boss]["health"] * 0.5 * level + 0.5,
        }
        enemies.append(enemy)
        boss_spawn_sound.play()
        boss_spawned = True
        level_completed = True
        background_color = (128, 0, 0)

    # Hit logic and score calculation
    for projectile in projectiles:
        projectile_rect = projectile_image.get_rect(
            topleft=(projectile["x"], projectile["y"])
        )
        for enemy in enemies:
            enemy_rect = enemy["image"].get_rect(topleft=(enemy["x"], enemy["y"]))
            if projectile_rect.colliderect(enemy_rect):
                enemy["health"] -= 1
                if enemy["image"] != enemy_boss:
                    score += 1
                if enemy["health"] <= 0 and enemy["image"] == enemy_boss:
                    boss_death_sound.play()
                    boss_spawned = False
                    level_completed = False
                    background_color = (0, 0, 0)
                    level += 1
                if enemy["health"] <= 0:
                    enemies.remove(enemy)
                projectiles.remove(projectile)
                break

    # Health of Player
    for enemy in enemies:
        if enemy["y"] + enemy["image"].get_height() >= 750 and enemy["image"] == enemy_boss:
            player_health = 0
        if enemy["y"] + enemy["image"].get_height() >= 750:
            hp_loss_sound.play()
            player_health -= 1
            enemies.remove(enemy)
            if player_health <= 0:
                running = False
                break
        player_rect = player.get_rect(topleft=(player_position, CONSTANT_PLAYER_Y))
        enemy_rect = enemy["image"].get_rect(topleft=(enemy["x"], enemy["y"]))
        if player_rect.colliderect(enemy_rect):
            hp_loss_sound.play()
            player_health = 0
            if player_health <= 0:
                running = False
                break

    # Score
    score_text = font.render("Score: " + str(score), True, (255, 255, 255))
    score_rect = score_text.get_rect(bottomleft=(10, WINDOW_HEIGHT - 10))
    window.blit(score_text, score_rect)
    # Level
    level_text = font.render("Level: " + str(level), True, (255, 255, 255))
    text_rect = level_text.get_rect(bottomright=(WINDOW_WIDTH - 10, WINDOW_HEIGHT - 10))
    window.blit(level_text, text_rect)
    # HP
    total_width = player_health * 30
    start_x = (WINDOW_WIDTH - total_width) // 2
    for i in range(player_health):
        window.blit(heart_image, (start_x + i * 30, WINDOW_HEIGHT - 30))

    for enemy in enemies:
        enemy["y"] += enemy["speed"] * delta_time

    for enemy in enemies:
        window.blit(enemy["image"], (enemy["x"], enemy["y"]))

    # Win screen
    if level == 4:
        window.fill((0, 0, 0))
        player_rect = player.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        window.blit(player, player_rect)
        ending_font = pygame.font.SysFont("Courier New", 36)
        win_text = ending_font.render("YOU WIN", True, (0, 255, 0))
        win_rect = win_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
        )
        window.blit(win_text, win_rect)
        pygame.display.update()
        pygame.time.delay(2000)
        running = False

    # Game over screen
    if player_health <= 0:
        game_over_sound.play()
        window.fill((0, 0, 0))
        ending_font = pygame.font.SysFont("Courier New", 36)
        game_over_text = ending_font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        )
        window.blit(game_over_text, game_over_rect)
        pygame.display.update()
        pygame.time.delay(2000)
        running = False

    # Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        if player_position > 0:
            player_position -= SPEED
    if keys[pygame.K_d]:
        if player_position < WINDOW_WIDTH - 80:
            player_position += SPEED

    # Shooting
    shoot_timer += delta_time
    if shoot_timer >= projectile_frequency / math.sqrt(level):
        projectile = {
            "x": player_position
            + player.get_width() // 2
            - projectile_image.get_width() // 2,
            "y": 620,
            "speed": projectile_speed,
        }
        projectiles.append(projectile)
        shoot_sound.play()
        shoot_timer = 0

    for projectile in projectiles:
        projectile["y"] -= projectile["speed"] * delta_time

    for projectile in projectiles:
        window.blit(projectile_image, (projectile["x"], projectile["y"]))

    pygame.display.update()
    window.fill(background_color)
    clock.tick(FPS)

pygame.QUIT()
sys.exit()
