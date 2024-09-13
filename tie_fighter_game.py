import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
RETRO_GREEN = (0, 255, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tie Fighter")

# Load images
tie_fighter_img = pygame.image.load("tie_fighter.png").convert_alpha()
xwing_img = pygame.image.load("xwing.png").convert_alpha()
background_img = pygame.image.load("space_background.png").convert()

# Load explosion image
explosion_img_path = "explosion.png"
if os.path.exists(explosion_img_path):
    explosion_img = pygame.image.load(explosion_img_path).convert_alpha()
else:
    # Create a placeholder surface if the image is missing
    explosion_img = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.circle(explosion_img, (255, 165, 0), (25, 25), 25)

# Function to scale images while maintaining aspect ratio
def scale_image(image, new_width=None, new_height=None):
    original_width, original_height = image.get_size()
    if new_width and not new_height:
        scale_factor = new_width / original_width
    elif new_height and not new_width:
        scale_factor = new_height / original_height
    else:
        scale_factor = min(new_width / original_width, new_height / original_height)
    new_size = (int(original_width * scale_factor), int(original_height * scale_factor))
    return pygame.transform.smoothscale(image, new_size)

# Scale background image to fit the screen while maintaining aspect ratio
background_img = scale_image(background_img, new_width=SCREEN_WIDTH, new_height=SCREEN_HEIGHT)
background_rect = background_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

# Scale Tie Fighter, X-Wing, and Explosion images
tie_fighter_img = scale_image(tie_fighter_img, new_height=SCREEN_HEIGHT * 0.15)
xwing_img = scale_image(xwing_img, new_height=SCREEN_HEIGHT * 0.1)
explosion_img = scale_image(explosion_img, new_height=SCREEN_HEIGHT * 0.1)

# Game clock
clock = pygame.time.Clock()

# Font
font = pygame.font.SysFont(None, 36)

# Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = explosion_img
        self.rect = self.image.get_rect(center=center)
        self.timer = pygame.time.get_ticks()
        self.duration = 500  # milliseconds

    def update(self):
        # Remove the explosion after its duration
        if pygame.time.get_ticks() - self.timer > self.duration:
            self.kill()

# Bullet group for X-Wings
xwing_bullets = pygame.sprite.Group()

# Explosion group
explosion_group = pygame.sprite.Group()

# Tie Fighter class
class TieFighter(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = tie_fighter_img
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - self.rect.height)
        self.speed = 10
        self.shield = 50

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys_pressed[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys_pressed[pygame.K_DOWN]:
            self.rect.y += self.speed

        # Keep within screen bounds
        self.rect.clamp_ip(screen.get_rect())

# X-Wing class
class XWing(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = xwing_img
        self.rect = self.image.get_rect()
        # Spawn at random horizontal position at the top
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = -self.rect.height  # Start just above the screen
        self.speed = 3  # Adjust speed as needed
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = random.randint(1500, 3000)  # Shoot every 1.5 to 3 seconds

    def update(self, tie_fighter_x):
        # Move downwards
        self.rect.y += self.speed
        # Adjust x towards Tie Fighter
        if self.rect.centerx < tie_fighter_x:
            self.rect.x += min(self.speed, tie_fighter_x - self.rect.centerx)
        elif self.rect.centerx > tie_fighter_x:
            self.rect.x -= min(self.speed, self.rect.centerx - tie_fighter_x)

        # Shoot bullets at intervals
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.last_shot = current_time
            self.shoot_delay = random.randint(1500, 3000)
            # Shoot bullet downwards
            bullet = Bullet(
                self.rect.center,
                (0, 1),  # Direction down
                7,
                (255, 0, 0)
            )
            xwing_bullets.add(bullet)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction, speed, color):
        super().__init__()
        self.image = pygame.Surface((5, 5), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (2, 2), 2)
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed
        self.direction = direction

    def update(self):
        self.rect.x += self.direction[0]*self.speed
        self.rect.y += self.direction[1]*self.speed
        # Remove if off screen
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

# Display instructions
def display_instructions():
    instructions = [
        "Tie Fighter Game",
        "",
        "Instructions:",
        "Use arrow keys to move the Tie Fighter.",
        "Press Spacebar to shoot.",
        "Destroy X-Wings before they reach the bottom!",
        "Survive as long as you can.",
        "",
        "Press any key to start..."
    ]
    screen.fill(BLACK)
    y_offset = 100
    for line in instructions:
        text = font.render(line, True, RETRO_GREEN)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        screen.blit(text, text_rect)
        y_offset += 40
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                waiting = False
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

# Main game function
def main():
    # Game variables
    tie_fighter = TieFighter()
    tie_group = pygame.sprite.Group(tie_fighter)
    xwing_group = pygame.sprite.Group()
    tie_bullets = pygame.sprite.Group()
    xwing_spawn_timer = 0
    game_over = False
    start_time = pygame.time.get_ticks()
    score = 0  # Initialize score
    display_instructions()

    while True:
        clock.tick(60)
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) // 1000  # In seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_SPACE:
                    # Shoot bullet upwards
                    bullet = Bullet(
                        tie_fighter.rect.center,
                        (0, -1),
                        15,
                        RETRO_GREEN
                    )
                    tie_bullets.add(bullet)

        if not game_over:
            keys_pressed = pygame.key.get_pressed()
            tie_fighter.update(keys_pressed)

            # Spawn X-Wings every 2 to 3 seconds
            if current_time - xwing_spawn_timer > random.randint(2000, 3000):
                xwing = XWing()
                xwing_group.add(xwing)
                xwing_spawn_timer = current_time

            xwing_group.update(tie_fighter.rect.centerx)
            tie_bullets.update()
            xwing_bullets.update()
            explosion_group.update()

            # Check collisions between Tie Fighter bullets and X-Wings
            for bullet in tie_bullets:
                hit_xwings = pygame.sprite.spritecollide(bullet, xwing_group, True)
                if hit_xwings:
                    for xwing in hit_xwings:
                        # Create explosion
                        explosion = Explosion(xwing.rect.center)
                        explosion_group.add(explosion)
                        score += 10  # Increase score
                    bullet.kill()

            # Check collisions between Tie Fighter and X-Wing bullets
            colliding_bullets = pygame.sprite.spritecollide(tie_fighter, xwing_bullets, True)
            if colliding_bullets:
                tie_fighter.shield -= 1  # Decrease shield by 1 per collision event
                print(f"Hit by bullet! Shield decreased to {tie_fighter.shield}")
                if tie_fighter.shield <= 0:
                    game_over = True
                    game_over_time = pygame.time.get_ticks()

            # Check collisions between Tie Fighter and X-Wings
            colliding_xwings = pygame.sprite.spritecollide(tie_fighter, xwing_group, True)
            if colliding_xwings:
                tie_fighter.shield -= 1  # Decrease shield by 1 per collision event
                print(f"Collided with X-Wing! Shield decreased to {tie_fighter.shield}")
                if tie_fighter.shield <= 0:
                    game_over = True
                    game_over_time = pygame.time.get_ticks()

            # Check if X-Wings reach the bottom
            for xwing in xwing_group:
                if xwing.rect.top > SCREEN_HEIGHT:
                    tie_fighter.shield -= 1  # Deduct shield point
                    print(f"X-Wing passed! Shield decreased to {tie_fighter.shield}")
                    xwing.kill()  # Remove X-Wing to prevent continuous decrement
                    if tie_fighter.shield <= 0:
                        game_over = True
                        game_over_time = pygame.time.get_ticks()

        # Draw everything
        screen.fill(BLACK)
        screen.blit(background_img, background_rect)
        tie_group.draw(screen)
        xwing_group.draw(screen)
        tie_bullets.draw(screen)
        xwing_bullets.draw(screen)
        explosion_group.draw(screen)

        # Draw shield
        shield_text = font.render(f"Shield: {tie_fighter.shield}", True, RETRO_GREEN)
        screen.blit(shield_text, (10, 10))

        # Draw timer
        timer_text = font.render(f"Time: {elapsed_time}", True, RETRO_GREEN)
        screen.blit(timer_text, (SCREEN_WIDTH - 150, 10))

        # Draw score
        score_text = font.render(f"Score: {score}", True, RETRO_GREEN)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 50))

        # Draw game title
        title_text = font.render("Zain's Game", True, RETRO_GREEN)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 10))

        if game_over:
            # Display game over message
            game_over_text = font.render("Game Over!", True, RETRO_GREEN)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(game_over_text, text_rect)
            pygame.display.flip()
            pygame.time.delay(3000)
            # Restart game
            main()

        pygame.display.flip()

if __name__ == "__main__":
    main()
