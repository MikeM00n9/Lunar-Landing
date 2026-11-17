import pygame
import math
import sys
import random


pygame.init()

# Screen dimensions
screenWidth = 800
screenHeight = 600

# Colors
blue = (135,206,235)
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
orange = (255, 165, 0)
yellow = (255, 255, 0)
lightGray = (200, 200, 200)

# Game settings
gravity = 0.005
thrust = -0.01
rotation = 5
landerWidth = 20
landerHeight = 40
landingSpeed = 1.0

# Create the screen
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Lunar Lander")

# Font
font = pygame.font.Font(None, 36)


class Lander:
    def __init__(self):
        self.image = pygame.Surface((landerWidth, landerHeight), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, white, [(10, 0), (0, 40), (20, 40)])
        self.rect = self.image.get_rect(center=(screenWidth // 2, 100))
        self.x = screenWidth // 30
        self.y = 100
        self.vx = 0
        self.vy = 0
        self.angle = 0
        self.thrusting = False

    def apply_gravity(self):
        self.vy += gravity

    def apply_thrust(self):
        rad_angle = math.radians(self.angle)
        thrust_x = math.sin(rad_angle) * thrust
        thrust_y = math.cos(rad_angle) * thrust
        self.vx += thrust_x
        self.vy += thrust_y

    def rotate(self, direction):
        self.angle += direction * rotation
        self.angle = self.angle % 360

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)

    def draw(self, surface):
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, rotated_rect.topleft)

    def reset(self):
        self.x = screenWidth // 2
        self.y = 100
        self.vx = 0
        self.vy = 0
        self.angle = 0


class Cloud:
    def __init__(self):
        self.x = random.randint(0, screenWidth)
        self.y = random.randint(50, screenHeight // 2)
        self.speed = random.uniform(0.5, 1.5)
        self.size = random.randint(20, 50)
        self.circles = self.generate_circles()

    def generate_circles(self):

        circles = []
        base_size = self.size
        num_circles = random.randint(3, 6)

        for _ in range(num_circles):
            offset_x = random.randint(-base_size // 2, base_size // 2)
            offset_y = random.randint(-base_size // 3, base_size // 3)
            circle_size = random.randint(base_size // 2, base_size)
            circles.append((offset_x, offset_y, circle_size))

        return circles

    def move(self):
        self.x -= self.speed
        if self.x < -self.size * 2:
            self.x = screenWidth + self.size * 2
            self.y = random.randint(50, screenHeight // 2)

    def draw(self, surface):
        for offset_x, offset_y, size in self.circles:
            pygame.draw.circle(surface, lightGray, (int(self.x + offset_x), int(self.y + offset_y)), size)
# Explosion class
class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.max_radius = 100
        self.expanding = True

    def draw(self, surface):
        if self.radius < self.max_radius:
            pygame.draw.circle(surface, orange, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, red, (int(self.x), int(self.y)), self.radius - 10)
            pygame.draw.circle(surface, yellow, (int(self.x), int(self.y)), self.radius - 20)
            self.radius += 5
        else:
            self.expanding = False

def draw_text(text, x, y, color= white):
    rendered_text = font.render(text, True, color)
    screen.blit(rendered_text, (x, y))

def main_menu():
    menuRunning = True
    while menuRunning:
        screen.fill(blue)
        draw_text("LUNAR LANDER", screenWidth // 2 - 100, screenHeight // 2 - 100)
        draw_text("1. Start Game", screenWidth // 2 - 80, screenHeight // 2)
        draw_text("2. Exit", screenWidth // 2 - 80, screenHeight // 2 + 80)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    menuRunning = False

                if event.key == pygame.K_2:
                    pygame.quit()
                    sys.exit()

        pygame.display.update()



def game_loop():
    lander = Lander()
    platform_x = screenWidth // 50
    platform_y = screenHeight - 50
    platform_width = 100
    platform_height = 10

    # Generates clouds
    clouds = [Cloud() for _ in range(5)]

    explosion = None
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            lander.thrusting = True
            lander.apply_thrust()
        else:
            lander.thrusting = False

        if keys[pygame.K_LEFT]:
            lander.rotate(-1)
        if keys[pygame.K_RIGHT]:
            lander.rotate(1)

        lander.apply_gravity()
        lander.move()

        # Checking landing or collision
        if (platform_x < lander.x < platform_x + platform_width and
            platform_y < lander.y + landerHeight // 2 < platform_y + platform_height):
            if abs(lander.vy) <= landingSpeed and -10 < lander.angle < 10:
                draw_text("You Win!", screenWidth // 2 - 150, screenHeight // 2, green)
                pygame.display.update()
                pygame.time.delay(2000)
                running = False
            else:
                print("Crash! Game Over.")
                explosion = Explosion(lander.x, lander.y)
                lander.reset()

        if lander.x < 0 or lander.x > screenWidth or lander.y < 0 or lander.y > screenHeight:
            lander.reset()


        screen.fill(black)

        # clouds
        for cloud in clouds:
            cloud.move()
            cloud.draw(screen)

        # platform
        pygame.draw.rect(screen, yellow, (platform_x, platform_y, platform_width, platform_height))

        # Draw lander or explosion
        if explosion and explosion.expanding:
            explosion.draw(screen)
        else:
            explosion = None
            lander.draw(screen)

        # Update the display
        pygame.display.update()
        # framerate
        clock.tick(120)

    pygame.quit()


main_menu()
game_loop()
