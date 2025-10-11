import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 0)
GREEN = (50, 255, 50)
PURPLE = (200, 50, 255)

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Survivor")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 15
        self.speed = 5
        self.shield = False
        self.shield_timer = 0
    
    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
        
        # Keep player on screen
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))
    
    def draw(self):
        if self.shield:
            pygame.draw.circle(screen, BLUE, (self.x, self.y), self.radius + 10, 2)
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.radius - 5)

class Asteroid:
    def __init__(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.x = random.randint(0, WIDTH)
            self.y = -20
        elif side == 'bottom':
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT + 20
        elif side == 'left':
            self.x = -20
            self.y = random.randint(0, HEIGHT)
        else:
            self.x = WIDTH + 20
            self.y = random.randint(0, HEIGHT)
        
        self.radius = random.randint(15, 35)
        angle = math.atan2(HEIGHT // 2 - self.y, WIDTH // 2 - self.x)
        speed = random.uniform(2, 4)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-5, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rot_speed
    
    def draw(self):
        points = []
        for i in range(8):
            angle = math.radians(self.rotation + i * 45)
            r = self.radius + random.randint(-5, 5)
            px = self.x + math.cos(angle) * r
            py = self.y + math.sin(angle) * r
            points.append((px, py))
        pygame.draw.polygon(screen, RED, points)
    
    def off_screen(self):
        return (self.x < -50 or self.x > WIDTH + 50 or 
                self.y < -50 or self.y > HEIGHT + 50)

class PowerUp:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.radius = 12
        self.type = random.choice(['shield', 'slow'])
        self.lifetime = 300
    
    def update(self):
        self.lifetime -= 1
    
    def draw(self):
        if self.type == 'shield':
            pygame.draw.circle(screen, BLUE, (self.x, self.y), self.radius)
            pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius - 4, 2)
        else:
            pygame.draw.circle(screen, GREEN, (self.x, self.y), self.radius)
            pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius - 4, 2)

def check_collision(x1, y1, r1, x2, y2, r2):
    distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return distance < r1 + r2

def main():
    player = Player()
    asteroids = []
    powerups = []
    score = 0
    game_over = False
    spawn_timer = 0
    powerup_timer = 0
    difficulty = 1
    
    running = True
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_over:
                    # Restart game
                    player = Player()
                    asteroids = []
                    powerups = []
                    score = 0
                    game_over = False
                    difficulty = 1
                    spawn_timer = 0
                    powerup_timer = 0
        
        if not game_over:
            keys = pygame.key.get_pressed()
            player.move(keys)
            
            # Update shield timer
            if player.shield:
                player.shield_timer -= 1
                if player.shield_timer <= 0:
                    player.shield = False
            
            # Spawn asteroids
            spawn_timer += 1
            spawn_rate = max(20, 60 - difficulty)
            if spawn_timer >= spawn_rate:
                asteroids.append(Asteroid())
                spawn_timer = 0
            
            # Spawn powerups
            powerup_timer += 1
            if powerup_timer >= 300 and len(powerups) < 2:
                powerups.append(PowerUp())
                powerup_timer = 0
            
            # Update asteroids
            for asteroid in asteroids[:]:
                asteroid.update()
                if asteroid.off_screen():
                    asteroids.remove(asteroid)
                    score += 1
                    difficulty = score // 10 + 1
                elif check_collision(player.x, player.y, player.radius,
                                   asteroid.x, asteroid.y, asteroid.radius):
                    if player.shield:
                        asteroids.remove(asteroid)
                        score += 5
                    else:
                        game_over = True
            
            # Update powerups
            for powerup in powerups[:]:
                powerup.update()
                if powerup.lifetime <= 0:
                    powerups.remove(powerup)
                elif check_collision(player.x, player.y, player.radius,
                                   powerup.x, powerup.y, powerup.radius):
                    if powerup.type == 'shield':
                        player.shield = True
                        player.shield_timer = 180
                    else:  # slow
                        for asteroid in asteroids:
                            asteroid.vx *= 0.5
                            asteroid.vy *= 0.5
                    powerups.remove(powerup)
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw stars
        for i in range(50):
            x = (i * 137 + score) % WIDTH
            y = (i * 197 + score // 2) % HEIGHT
            pygame.draw.circle(screen, WHITE, (x, y), 1)
        
        for asteroid in asteroids:
            asteroid.draw()
        
        for powerup in powerups:
            powerup.draw()
        
        player.draw()
        
        # Draw UI
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        level_text = small_font.render(f"Level: {difficulty}", True, PURPLE)
        screen.blit(level_text, (10, 50))
        
        if player.shield:
            shield_text = small_font.render(f"Shield: {player.shield_timer // 60}s", True, BLUE)
            screen.blit(shield_text, (10, 80))
        
        if game_over:
            game_over_text = font.render("GAME OVER!", True, RED)
            restart_text = small_font.render("Press SPACE to restart", True, WHITE)
            final_score = font.render(f"Final Score: {score}", True, YELLOW)
            
            screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 60))
            screen.blit(final_score, (WIDTH // 2 - 110, HEIGHT // 2 - 10))
            screen.blit(restart_text, (WIDTH // 2 - 130, HEIGHT // 2 + 40))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
