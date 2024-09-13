import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions and frame rate
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Squirrel Finder')

clock = pygame.time.Clock()

# Load images
try:
    koala_image = pygame.image.load('koala.png')
except:
    koala_image = pygame.Surface((40, 40))
    koala_image.fill((255, 255, 255))

koala_image = pygame.transform.scale(koala_image, (40, 40))

try:
    strawberry_image = pygame.image.load('strawberry.png')
except:
    strawberry_image = pygame.Surface((40, 40))
    strawberry_image.fill((255, 0, 0))

strawberry_image = pygame.transform.scale(strawberry_image, (40, 40))

try:
    squirrel_image = pygame.image.load('squirrel.png')
except:
    squirrel_image = pygame.Surface((40, 40))
    squirrel_image.fill((160, 82, 45))

squirrel_image = pygame.transform.scale(squirrel_image, (40, 40))

# Define colors
DARK_BACKGROUND = (20, 20, 20)
RETRO_COLOR = (0, 255, 0)

# Define font
font = pygame.font.SysFont('Arial', 24)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = koala_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.speed = 8

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys_pressed[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys_pressed[pygame.K_DOWN]:
            self.rect.y += self.speed

        # Keep the player within the screen boundaries
        self.rect.clamp_ip(screen.get_rect())

# Strawberry class
class Strawberry(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = strawberry_image
        self.rect = self.image.get_rect(
            x=random.randint(0, SCREEN_WIDTH - 40),
            y=random.randint(0, SCREEN_HEIGHT - 40)
        )
        self.vx = random.choice([-5, 5])
        self.vy = random.choice([-5, 5])

    def update(self, *args):
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Bounce off walls
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.vx *= -1
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.vy *= -1

# Squirrel class
class Squirrel(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = squirrel_image
        self.rect = self.image.get_rect(
            x=random.randint(0, SCREEN_WIDTH - 40),
            y=random.randint(0, SCREEN_HEIGHT - 40)
        )
        self.vx = random.choice([-7, 7])
        self.vy = random.choice([-7, 7])

    def update(self, *args):
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Bounce off walls
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.vx *= -1
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.vy *= -1

def show_instructions():
    instructions = [
        "Squirrel Finder",
        "You are the koala. Use the arrow keys to move.",
        "Avoid the strawberries!",
        "After 3 seconds, a squirrel will appear.",
        "Find and touch the squirrel to win.",
        "Press any key to start."
    ]

    screen.fill(DARK_BACKGROUND)
    y_offset = SCREEN_HEIGHT // 2 - len(instructions) * 20
    for line in instructions:
        text = font.render(line, True, RETRO_COLOR)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        screen.blit(text, rect)
        y_offset += 40

    pygame.display.flip()
    wait_for_key()

def wait_for_key():
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def main():
    while True:
        # Show instructions
        show_instructions()

        # Initialize game variables
        player = Player()
        all_sprites = pygame.sprite.Group()
        all_sprites.add(player)
        strawberries = pygame.sprite.Group()
        squirrel_group = pygame.sprite.Group()

        strawberry_spawn_timer = 0
        squirrel_spawned = False
        game_time = 0

        running = True
        while running:
            dt = clock.tick(FPS)
            game_time += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys_pressed = pygame.key.get_pressed()

            # Update sprites (pass keys_pressed to handle player movement)
            all_sprites.update(keys_pressed)

            # Spawn strawberry every second
            strawberry_spawn_timer += dt
            if strawberry_spawn_timer >= 1000:
                strawberry = Strawberry()
                strawberries.add(strawberry)
                all_sprites.add(strawberry)
                strawberry_spawn_timer = 0

            # Spawn squirrel after 3 seconds
            if not squirrel_spawned and game_time >= 3000:
                squirrel = Squirrel()
                squirrel_group.add(squirrel)
                all_sprites.add(squirrel)
                squirrel_spawned = True

            # Check collisions
            if pygame.sprite.spritecollideany(player, strawberries):
                # Player dies
                running = False
                game_over_text = "You were hit by a strawberry! You lose."
            if squirrel_spawned and pygame.sprite.spritecollideany(player, squirrel_group):
                # Player wins
                running = False
                game_over_text = "You found the squirrel! You win."

            # Draw everything
            screen.fill(DARK_BACKGROUND)
            all_sprites.draw(screen)

            # Draw "openai"
            openai_text = font.render("openai", True, RETRO_COLOR)
            screen.blit(openai_text, (10, 10))

            # Draw timer
            timer_seconds = game_time // 1000
            timer_text = font.render(f"Time: {timer_seconds}", True, RETRO_COLOR)
            screen.blit(timer_text, (SCREEN_WIDTH - 150, 10))

            pygame.display.flip()

        # Game over screen
        screen.fill(DARK_BACKGROUND)
        text = font.render(game_over_text, True, RETRO_COLOR)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, rect)
        pygame.display.flip()
        pygame.time.wait(2000)

if __name__ == "__main__":
    main()
