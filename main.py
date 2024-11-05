import pygame
import random
import math

WIDTH = 800
HEIGHT = 600

PARTICLE_TYPES = {
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
}

INTERACTION_MATRIX = {
    "RED": {
        "GREEN": -2,
        "BLUE": 2,
        "RED": -4,
    },
    "GREEN": {
        "RED": -10,
        "BLUE": 5,
        "GREEN": 4,
    },
    "BLUE": {
        "RED": 2,
        "GREEN": -4,
        "BLUE": -4,
    }
}

class Atom:
    def __init__(self) -> None:
        self.radius = 5
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(self.radius, HEIGHT - self.radius)
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.type = random.choice(list(PARTICLE_TYPES.keys()))
        self.color = PARTICLE_TYPES[self.type]
        
    def calculate_force(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 1: 
            distance = 1
        
        force = INTERACTION_MATRIX[self.type][other.type]
        
        
        force_x = (force * dx) / (distance ** 2)
        force_y = (force * dy) / (distance ** 2)
        
        return force_x, force_y
    
    def update(self, particles):
        fx = 0
        fy = 0
        
        for other in particles:
            if other != self:
                force_x, force_y = self.calculate_force(other)
                fx += force_x
                fy += force_y
        
        self.vx += fx * 0.1
        self.vy += fy * 0.1
        
        speed = math.sqrt(self.vx*self.vx + self.vy*self.vy)
        max_speed = 5
        if speed > max_speed:
            
            self.vx = (self.vx/speed) * 5
            self.vy = (self.vy/speed) * 5
        
        self.x += self.vx
        self.y += self.vy
        
        if self.x < self.radius:
            self.x = self.radius
            self.vx *= -0.8
        elif self.x > WIDTH - self.radius:
            self.x = WIDTH - self.radius
            self.vx *= -0.8
            
        if self.y < self.radius:
            self.y = self.radius
            self.vy *= -0.8
        elif self.y > HEIGHT - self.radius:
            self.y = HEIGHT - self.radius
            self.vy *= -0.8
            
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
atoms = [Atom() for _ in range(100)]

screen = pygame.display.set_mode((WIDTH, HEIGHT))

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill((0, 0, 0))
    
    for atom in atoms:
        atom.update(atoms)
        atom.draw(screen)
    
    pygame.display.update()
    
