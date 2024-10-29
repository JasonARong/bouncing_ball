import pygame
import math
import random
import numpy as np
from birthData import BirthData

# Initialize Pygame
pygame.init()

# Define colors (RGB)
WHITE = (240, 240, 240)
GREY = (210, 210, 210)
BLACK = (0, 0, 0)
RED = (240, 84, 84)
BLUE = (0, 89, 213)
GREEN = (0, 255, 0)
ball_colors = [RED, GREEN, BLUE]

# Screen dimensions
screen_width = 550
screen_height = 750
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Bouncing Ball Data Visualization")

# Set up font
font = pygame.font.Font(None, 36) 
small_font = pygame.font.Font(None, 24) 

# Circle properties
circle_radius = 200
circle_center = np.array([screen_width // 2, screen_height // 2], dtype=float)

# Ball properties
ball_radius = 6
GRAVITY = np.array([0, 0])  # Gravity vector (no gravity in this case)

# Initialize birth_data object
birth_data = BirthData("us_birth_population_1924_2023.csv")
future = birth_data.load_data()

# Helper function: Generate random velocity for ball
def create_random_velocity():
    """Create a random velocity with direction either -2 or 2."""
    return np.array([random.choice([-3, 3]), random.choice([-3, 3])], dtype=float)

# Helper function: Generate random position within the circle
def create_random_position():
    """Generate a random position within the circle boundary."""
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(0, circle_radius - ball_radius)
    x = circle_center[0] + distance * math.cos(angle)
    y = circle_center[1] + distance * math.sin(angle)
    return np.array([x, y], dtype=float)

# Helper function: Calculate distance between two points
def distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# Helper function: Check if a point is inside the circle
def is_point_in_circle(point, circle_center, circle_radius):
    """Check if a given point lies inside the circle."""
    return distance(point, circle_center) <= circle_radius - ball_radius

def create_balls(balls, ball_num, gender):
    for i in range(ball_num):
        ball_color = BLUE if gender=='male' else RED
        balls.append({
            'ballObj': Ball(create_random_position(), create_random_velocity(), ball_radius, ball_color), 
            'gender': gender
        })

def delete_balls(balls, ball_num, gender):
    deleted_balls = 0
    for i in range(len(balls)):
        # print('i:' + str(i))
        if deleted_balls >= ball_num:
            break
        if balls[i]['gender'] == gender:
            balls.remove(balls[i])
            deleted_balls += 1


class Ball:
    """Ball class representing a bouncing ball."""
    def __init__(self, pos, vel, radius, color):
        self.pos = pos  # Ball position
        self.vel = vel  # Ball velocity
        self.radius = radius  # Ball radius
        self.color = color  # Ball color
    
    def next_frame(self):
        """Update ball position and velocity for the next frame."""
        self.pos += self.vel
        self.vel += GRAVITY

class Circle:
    """Circle class representing the boundary for balls."""
    def __init__(self, center, radius):
        self.center = center  # Circle center
        self.radius = radius  # Circle radius

    def check_collision(self, ball):
        """Handle collision of the ball with the circle boundary."""
        dist = distance(ball.pos + ball.vel, self.center)
        if dist > (self.radius - ball.radius):  # Collision with boundary
            # Adjust velocity based on collision normal
            normal = (ball.pos - self.center) / dist
            dot_product = np.dot(ball.vel, normal)
            ball.vel -= 2 * dot_product * normal

            # Correct the ball's position to prevent it from going outside the circle
            dist_to_correct = dist + ball.radius - self.radius
            ball.pos -= dist_to_correct * normal

def collision_handler(ball, balls):
    """Handle ball-ball collisions."""
    for other_ball_dic in balls:
        other_ball = other_ball_dic['ballObj']
        if ball is not other_ball:
            dist = distance(ball.pos, other_ball.pos)
            if dist < (ball.radius + other_ball.radius):  # Collision detected
                dv = ball.vel - other_ball.vel  # Velocity difference
                normal = (ball.pos - other_ball.pos) / dist  # Normal vector
                dot_product = np.dot(dv, normal)

                # Update velocities based on elastic collision
                ball.vel -= dot_product * normal
                other_ball.vel += dot_product * normal

                # Correct positions to avoid overlapping
                overlap = (ball.radius + other_ball.radius - dist)
                proportion = ball.radius / (ball.radius + other_ball.radius)
                ball.pos += normal * overlap * proportion
                other_ball.pos -= normal * overlap * (1 - proportion)

# Game loop setup
running = True
clock = pygame.time.Clock()
circle = Circle(circle_center, circle_radius)

# Get initial data from csv and set up ball number 
future.result()
inital_data = birth_data.get_curr_balls()
year = int(inital_data[0])
male_balls = inital_data[2]
female_balls = inital_data[3]
balls = []
create_balls(balls, male_balls, 'male')
create_balls(balls, female_balls, 'female')

inital_birth_data = birth_data.read_current_entry()
male_births = inital_birth_data[2]
female_births = inital_birth_data[3]

def handle_year_change(next):
    global male_balls
    global female_balls
    global male_births
    global female_births

    if next == True:
        birth_data.next_year()
    elif next == False:
        birth_data.previous_year()

    current_data = birth_data.get_curr_balls()
    curr_male_balls = current_data[2]
    curr_female_balls = current_data[3]
    male_balls_diff = curr_male_balls - male_balls
    female_balls_diff = curr_female_balls - female_balls

    current_birth_data = birth_data.read_current_entry()
    curr_male_births = current_birth_data[2]
    curr_female_births = current_birth_data[3]

    if male_balls_diff > 0:
        create_balls(balls, male_balls_diff, 'male')
    elif male_balls_diff < 0:
        print('delete male balls' + str(male_balls_diff))
        delete_balls(balls, abs(male_balls_diff), 'male')
        
    if female_balls_diff > 0:
        create_balls(balls, female_balls_diff, 'female')
    elif female_balls_diff < 0:
        print('delete female balls'  + str(female_balls_diff))
        delete_balls(balls, abs(female_balls_diff), 'female')
    
    male_balls = curr_male_balls
    female_balls = curr_female_balls
    male_births = curr_male_births
    female_births = curr_female_births

    # print('current male: ' + str(male_balls))
    # print('current female: ' + str(female_balls))
    # print('total ball count: ' + str(len(balls)))


# Main game loop
while running:
    screen.fill(BLACK)  # Clear the screen
    pygame.draw.circle(screen, WHITE, circle_center, circle_radius, width=1)  # Draw circle boundary

    # Create all the in-game Text
    year_text = font.render(str(year), True, WHITE)
    year_text_rect = year_text.get_rect()
    year_text_rect.topright = (screen_width - 10, 10)  
    screen.blit(year_text, year_text_rect)

    title_text = font.render('US Number of Births Per Year', True, WHITE)
    title_text_rect = title_text.get_rect()
    title_text_rect.topleft = (10, 10)  
    screen.blit(title_text, title_text_rect)

    male_text = small_font.render('Male Birth: ' + str(male_births), True, GREY)
    male_text_rect = male_text.get_rect()
    male_text_rect.topleft = (10, 84)  
    screen.blit(male_text, male_text_rect)
    
    female_text = small_font.render('Female Birth: ' + str(female_births), True, GREY)
    female_text_rect = female_text.get_rect()
    female_text_rect.topleft = (10, 60)  
    screen.blit(female_text, female_text_rect)

    instruction_text = small_font.render('Press LEFT or RIGHT Arrow Key to Change Year', True, WHITE)
    instruction_text_rect = instruction_text.get_rect()
    instruction_text_rect.bottomleft = (10, screen_height - 10)  
    screen.blit(instruction_text, instruction_text_rect)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # Exit the loop
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                handle_year_change(True)
                if(year < 2023):
                    year += 1
                    
            elif event.key == pygame.K_LEFT:
                handle_year_change(False)
                if(year > 1924):
                    year -= 1
            

    # Update and draw each ball
    for ball_dic in balls:
        ball = ball_dic['ballObj']
        pygame.draw.circle(screen, ball.color, (int(ball.pos[0]), int(ball.pos[1])), ball.radius, width=0)
    
    # Check for collisions with the circle boundary and between balls
    for ball_dic in balls:
        ball = ball_dic['ballObj']
        circle.check_collision(ball)
    for ball_dic in balls:
        ball = ball_dic['ballObj']
        collision_handler(ball, balls)
    for ball_dic in balls:
        ball = ball_dic['ballObj']
        ball.next_frame()

    pygame.display.flip()  # Update display
    clock.tick(60)  # Maintain 60 FPS

pygame.quit()
