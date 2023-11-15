import pygame
import sys
import time
import random
import math  # Required for math operations

# Constants
WIDTH, HEIGHT = 800, 600
MAX_TRIES_PER_BALL = 3
MAX_FLOOR_HITS = 3
GRAVITY = 0.25
REDUCED_SPEED = 0.8
TEXT_DISPLAY_DURATION = 3.0  # Duration for text display in seconds
BALL_SLOW = 20

# Colors
BLACK = (0, 0, 0)
GRAY = (210, 210, 220)
WHITE = (255, 255, 255)
DARK_ORANGE = (245, 145, 0)
ORANGE = (255, 165, 0)
LIGHT_ORANGE = (255, 180, 0)
RED = (255, 0, 75)
GREEN = (25, 255, 0)
BLUE = (100, 100, 200)

# Initialize Pygame
pygame.init()

# Initialize display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Basketball Shooting Game")

# Set the frame rate
clock = pygame.time.Clock()
FPS = 50

# set fonts
DEFAULT_FONT = pygame.font.Font(None, 36)
BIG_FONT = pygame.font.Font(None, 40)

# Set the boundaries for the grid
VANISHING_POINT = (WIDTH // 2, HEIGHT - HEIGHT // 3)
GRID_LEFT = -WIDTH // 2
GRID_RIGHT = WIDTH + WIDTH // 2
GRID_TOP = VANISHING_POINT[1] + 45
GRID_BOTTOM = HEIGHT

class Ball:
    def __init__(self):
        self.position_changed = False
        self.reset_all()

    def draw(self):
        pygame.draw.circle(screen, DARK_ORANGE, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, ORANGE, (self.x, self.y - self.radius // 10), self.radius // 1.1)
        pygame.draw.circle(screen, LIGHT_ORANGE, (self.x, self.y - self.radius // 2.5), self.radius // 2.5)

    def reset_all(self):
        self.radius = 20
        self.x, self.y = WIDTH // 2, HEIGHT - 2 * self.radius
        self.min_y = self.y
        self.speed_x, self.speed_y = 0, 0
        self.shooting = False
        self.floor_hits = 0

    def check_hoop_collision(self, hoop):
        if self.x < hoop.x:
            self.check_collision(hoop, hoop.l_side)
        else:
            self.check_collision(hoop, hoop.r_side)

    def check_collision(self, hoop, hoop_side):
        # Calculate the distance between the ball and the center of the hoop
        distance = math.sqrt((self.x - hoop_side) ** 2 + (self.y - hoop.y) ** 2)

        # Check if the ball collides with the circular points at the edges of the hoop
        if distance < hoop.radius + self.radius:
            if not self.position_changed:
                self.position_changed = True

                # Calculate the collision normal
                collision_normal_x = (self.x - hoop_side) / distance
                collision_normal_y = (self.y - hoop.y) / distance

                # Calculate the relative velocity along the collision normal
                relative_velocity_along_normal = self.speed_x * collision_normal_x + self.speed_y * collision_normal_y

                # Calculate the impulse for an elastic collision
                impulse = 2 * relative_velocity_along_normal

                # Update the ball's velocity
                self.speed_x = self.speed_x - impulse * collision_normal_x
                self.speed_y = self.speed_y - impulse * collision_normal_y

                # reduced the speed
                self.speed_x *= REDUCED_SPEED
                self.speed_y *= REDUCED_SPEED
        else:
            self.position_changed = False



class Hoop:
    def __init__(self):
        self.width = 60
        self.radius = 3
        self.x, self.y = WIDTH // 2, (HEIGHT // 4) - self.radius
        self.l_side = self.x - self.width // 2 + self.radius
        self.r_side = self.x + self.width // 2 - self.radius
        self.sides_y = self.y - self.radius
        self.backboard_height = self.width
        self.backboard_width = self.width // 0.7
        self.stand_width = self.backboard_width // 6
        self.stand_height = GRID_TOP - self.y + 15

    def draw_stand(self):
        pygame.draw.rect(screen, BLUE, (self.x - self.stand_width // 2, self.y + self.radius // 2, self.stand_width, self.stand_height))
        pygame.draw.rect(screen, BLACK, (self.x - self.stand_width // 2, self.y + self.radius // 2, self.stand_width, self.stand_height), width=2)

    def draw_backboard(self):
        pygame.draw.rect(screen, GRAY, (self.x - self.backboard_width // 2, self.y - self.radius // 2 - self.backboard_height, self.backboard_width, self.backboard_height))
        pygame.draw.rect(screen, BLACK, (self.x - self.backboard_width // 2, self.y - self.radius // 2 - self.backboard_height, self.backboard_width, self.backboard_height), width=2)
        pygame.draw.rect(screen, BLACK, (self.x - self.backboard_width // 6, self.y - self.radius // 2 - self.backboard_height // 3, self.backboard_width // 3, self.backboard_height // 3), width=2)
        

    def draw(self):
        pygame.draw.rect(screen, DARK_ORANGE, (self.x - self.width // 2, self.y - self.radius, self.width, self.radius * 2), border_radius=self.radius)
        pygame.draw.rect(screen, ORANGE, (self.x - self.width // 2, self.y - self.radius, self.width, self.radius // 0.6), border_radius=self.radius)
        pygame.draw.rect(screen, LIGHT_ORANGE, (self.x - self.width // 2 + self.radius // 2, self.y - self.radius + 2, self.width - self.radius, self.radius // 2), border_radius=self.radius)
        # pygame.draw.circle(screen, RED, (self.l_side, self.y), self.radius)
        # pygame.draw.circle(screen, RED, (self.r_side, self.y), self.radius)

    def change_position(self):
        self.x = random.randint(0 + self.width // 2 + self.backboard_height, WIDTH - self.width // 2)
        self.y = random.randint(60, HEIGHT // 1.2)
        self.l_side = self.x - self.width // 2 + self.radius
        self.r_side = self.x + self.width // 2 - self.radius
        self.sides_y = self.y - self.radius
        self.stand_height = GRID_TOP - self.y + 15


class Message:
    def __init__(self, text, text_color):
        self.color = text_color
        self.temp_color = self.color
        self.text = text
        self.x , self.y = (WIDTH // 2 - len(self.text) * 7, 50)
        self.reset_anim()

    def reset_anim(self):
        self.anim_ctr = 0
        self.font = DEFAULT_FONT

    def animate(self):
        self.anim_ctr += 1
        if not self.anim_ctr % (FPS // 4):
            if self.font == DEFAULT_FONT:
                self.font = BIG_FONT
                self.x -= len(self.text)
                self.temp_color = self.color
            else:
                self.font = DEFAULT_FONT
                self.x += len(self.text)
                self.temp_color = ORANGE
        self.draw()

    def draw(self):
        text_surface = self.font.render(self.text, True, self.temp_color)
        screen.blit(text_surface, (self.x, self.y))


def is_player_win(ball, hoop):
    return (abs(ball.y - hoop.y) < hoop.radius
        and abs(ball.x - hoop.x) < (hoop.width // 2) - hoop.radius)

def main():
    score = 0
    ball = Ball()
    hoop = Hoop()
    success_msg = Message("You made it through the hoop!", GREEN)
    miss_msg = Message("You missed the hoop.", RED)
    results = None
    end_of_turn = 0
    floor_height = HEIGHT

    while True:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not ball.shooting:
                    ball.x, ball.y = WIDTH // 2, HEIGHT - 2 * ball.radius
                    ball.speed_x = (event.pos[0] - ball.x) / BALL_SLOW
                    ball.speed_y = (event.pos[1] - ball.y) / BALL_SLOW
                    ball.shooting = True
                else:
                    results = miss_msg
                    end_of_turn -= TEXT_DISPLAY_DURATION

        if ball.shooting:
            # if ball.y > floor_height:
            #     ball.speed_y -= (ball.y - floor_height) // 8
            if floor_height > GRID_TOP + 15:
                ball.radius *= 0.995
                floor_height *= 0.995
            ball.x += ball.speed_x
            ball.y += ball.speed_y
            ball.speed_y += GRAVITY  # Apply gravity

        # Draw grid on the floor
        for i in range(GRID_LEFT, GRID_RIGHT, 20):
            pygame.draw.line(screen, GRAY, (i, GRID_BOTTOM), VANISHING_POINT, 1)
        for i in range(GRID_TOP, GRID_BOTTOM, 15):
            pygame.draw.line(screen, GRAY, (GRID_LEFT, i), (GRID_RIGHT, i), 1)
            
        hoop.draw_stand()
        hoop.draw_backboard()
        if ball.y > ball.min_y:
            ball.draw()
            hoop.draw()
        else:
            hoop.draw()
            ball.draw()

        if ball.shooting:
            # Check if the ball hits the sides of the screen (but not the top)
            if ((ball.x <= ball.radius and ball.speed_x < 0)
                or (ball.x >= WIDTH - ball.radius and ball.speed_x > 0)
                ) and ball.y < HEIGHT - ball.radius:
                ball.speed_x *= -REDUCED_SPEED  # Bounce back with reduced speed

            # check if the trow is too low
            if ball.y < ball.min_y:
                ball.min_y = ball.y
            elif not end_of_turn:
                if ball.min_y + ball.radius > hoop.y - hoop.radius:
                    end_of_turn = time.time()
                    results = miss_msg

            # check if the ball is near the hoop (on the way down only)
            if ball.speed_y > 0 and not end_of_turn and abs(hoop.y - ball.y) < ball.radius + hoop.radius + 10:
                # Check if the ball collides with the edges of the hoop and reflect its direction
                ball.check_hoop_collision(hoop)

                # Check if the ball goes through the hoop
                if is_player_win(ball, hoop):
                    end_of_turn = time.time()
                    results = success_msg

            # Check if the ball hits the floor
            if ball.y + ball.radius > floor_height - ball.radius and ball.speed_y > 0:
                ball.min_y = ball.y # reset this value
                ball.speed_y *= -REDUCED_SPEED  # Bounce back with reduced speed

            if end_of_turn:
                if time.time() - end_of_turn < TEXT_DISPLAY_DURATION:
                    if results == success_msg:
                        results.animate()
                    else:
                        results.draw()
                else:
                    floor_height = HEIGHT
                    results.reset_anim()
                    ball.reset_all()
                    end_of_turn = 0
                    if results == success_msg:
                        hoop.change_position()
                        score += 1

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()