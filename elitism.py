import pygame
from pygame.locals import Rect
import random

pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Genetic Algorithm")

clock = pygame.time.Clock()

# Set up the moves and lifespan of a generation
DIRECTIONS = ["up", "down", "left", "right"]
LIFESPAN = 400
ELITE_COUNT = 5

class Win():
    def __init__(self):
        self.body = Rect(0, 0, 20, 20)
        self.position = [600, HEIGHT // 2]
    
    def draw(self):
        pygame.draw.rect(screen, (0, 255, 0), self.body.move(self.position[0], self.position[1]))
    
class Obstacle():
    def __init__(self, x, y, width, height):
        self.body = Rect(0, 0, width, height)
        self.position = [x, y]
    
    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0), self.body.move(self.position[0], self.position[1]))

OBSTACLES = []
OBSTACLES.append(Obstacle(400, 200, 20, 200))

class Agent():
    def __init__(self):
        self.body = Rect(0, 0, 20, 20)
        self.position = [200, HEIGHT // 2]
        self.step = 0
        self.finished = False
        self.fitness = 0
        self.elite = False
        self.dna = [random.choice(DIRECTIONS) for _ in range(LIFESPAN)]

    def calculate_fitness(self, win):
        dx = self.position[0] - win.position[0]
        dy = self.position[1] - win.position[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5
        self.fitness = 1 / (distance + 1) 

    def update(self):
        if not self.finished and self.step < LIFESPAN:
            self.move(self.dna[self.step])
            self.step += 1

            if self.body.move(self.position[0], self.position[1]).colliderect(win.body.move(win.position[0], win.position[1])):
                print("an agent reached the win!")
                self.finished = True
                self.fitness *= 10

    def draw(self, colour, alpha):
        rect = self.body.move(self.position[0], self.position[1])

        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        surface.fill((*colour, alpha))

        screen.blit(surface, rect.topleft)
    
    def move(self, direction):
        if not self.collides_with_obstacle():
            if direction == "up":
                self.position[1] -= 5
            elif direction == "down":
                self.position[1] += 5
            elif direction == "left":
                self.position[0] -= 5
            elif direction == "right":
                self.position[0] += 5
    
    def collides_with_obstacle(self):
        for obstacle in OBSTACLES:
            if self.body.move(self.position[0], self.position[1]).colliderect(obstacle.body.move(obstacle.position[0], obstacle.position[1])):
                return True
        return False

class Population():
    def __init__(self, size):
        self.agents = [Agent() for _ in range(size)]
        self.generation = 1
    
    def update(self):
        for agent in self.agents:
            agent.update()
    
    def draw(self):
        for agent in self.agents:
            if not agent.elite:
                agent.draw((100, 100, 100), 60)
            else:
                agent.draw((255, 0, 0), 255)
    
    def evaluate(self, win):
        total_fitness = 0
        for agent in self.agents:
            agent.calculate_fitness(win)
            total_fitness += agent.fitness
        
        for agent in self.agents:
            agent.fitness /= total_fitness

        # Sort into highest fitness first (agent[0] is the best)
        self.agents.sort(key=lambda a: a.fitness, reverse=True)
    
    def select_parent(self):
        r = random.random()
        cumulative = 0
        for agent in self.agents:
            cumulative += agent.fitness
            if r < cumulative:
                return agent
    
    def generate_next(self):
        new_agents = []

        # Keep the best agents
        for i in range(ELITE_COUNT):
            elite = Agent()
            elite.elite = True
            elite.dna = self.agents[i].dna[:] # copy it's dna
            new_agents.append(elite)
        
        # Fill the rest with children of the best agents
        while len(new_agents) < len(self.agents):
            parent1 = self.select_parent()
            parent2 = self.select_parent()

            child = Agent()
            midpoint = random.randint(0, LIFESPAN)

            for i in range(LIFESPAN):
                if i < midpoint:
                    child.dna[i] = parent1.dna[i]
                else:
                    child.dna[i] = parent2.dna[i]

                if random.random() < 0.01:
                    child.dna[i] = random.choice(DIRECTIONS)
        
            new_agents.append(child)
        
        self.agents = new_agents
        self.generation += 1

win = Win()
population = Population(100)
frame_count = 0

speed = 1

# Main game loop
running = True
while running:
    clock.tick(60 * speed)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                speed *= 100
            if event.key == pygame.K_DOWN:
                speed /= 100

    # Fill the background
    screen.fill((255, 255, 255))

    # Draw the agent
    population.update()
    population.draw()

    frame_count += 1

    if frame_count >= LIFESPAN:
        population.evaluate(win)
        population.generate_next()
        frame_count = 0
        print(f"Generation: {population.generation}")

    # Draw the win
    win.draw()
    for obstacle in OBSTACLES:
        obstacle.draw()

    # Update the display
    pygame.display.flip()

pygame.quit()