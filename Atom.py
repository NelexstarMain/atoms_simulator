import pygame
import math
import random
import numpy as np

class Atom:
    def __init__(self,
                 x: int,
                 y: int,
                 mass: int,
                 energy: int,
                 vector: pygame.Vector2
            ) -> None:
        
        self.x: float = x
        self.y: float = y 
        self.radius = 5
        self.mass: int = mass
        self.energy: int = energy
        self.vector: pygame.Vector2 = vector
        self.color: tuple[int, int, int] = (255, 0, 0)
        
    def move(self) -> None:
        if self.vector.length() > 0:
            self.vector = self.vector.normalize()
            min_speed = 1
            max_speed = 5
            speed = min_speed + (max_speed - min_speed) * (self.energy / 100)
            
            # Apply the speed to the normalized vector
            self.x += self.vector.x * speed
            self.y += self.vector.y * speed
        
    def update(self) -> None:
        # Zakładamy, że maksymalna energia to 100, a minimalna to 0
        max_energy = 100
        min_energy = 0
        
        # Ograniczamy energię do zakresu [0, 100]
        clamped_energy = max(min(self.energy, max_energy), min_energy)
        
        # Obliczamy współczynnik interpolacji
        t = clamped_energy / max_energy
        
        # Interpolujemy między niebieskim (0, 0, 255) a czerwonym (255, 0, 0)
        red = int(255 * t)
        blue = int(255 * (1 - t))
        
        self.color = (red, 0, blue)
        self.move()
        
    def collider_with_wall(self, energy) -> None:
        if self.x < self.radius or self.x > 800 - self.radius:
            self.vector.x *= -1
            self.energy = np.mean([self.energy, energy])
        if self.y < self.radius or self.y > 600 - self.radius:
            self.vector.y *= -1
            self.energy = np.mean([self.energy, energy])
    
    def draw(self, screen) -> None:
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
    def handle_collision(self, others: list):
        for other in others:
            dx = other.x - self.x
            dy = other.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < (self.radius + other.radius):
                # Normalizacja wektora kolizji
                nx = dx / distance if distance > 0 else 0
                ny = dy / distance if distance > 0 else 0
                
                # Głębokość penetracji
                overlap = (self.radius + other.radius) - distance
                
                # Odsunięcie cząsteczek
                self.x -= nx * overlap/2
                self.y -= ny * overlap/2
                other.x += nx * overlap/2
                other.y += ny * overlap/2
                
                self.energy = np.mean([self.energy, other.energy])


            
            
        
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

atoms = [Atom(random.randint(0, 800), random.randint(0, 600), 1, 1, pygame.Vector2(random.randint(-3, 3), random.randint(-3, 3))) for _ in range(200)]

running = True
while running:
    screen.fill((0, 0, 0))
    for atom in atoms:
        atom.update()
        atom.collider_with_wall(100)
        atom.handle_collision(atoms)
        
        atom.draw(screen)
        
    pygame.display.flip()
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()