import pygame
import pygame.gfxdraw 
import  pygame.font as pf

import math
import random
import numpy as np
from Slider import Slider

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
        self.colided_with: list = []
        
    def move(self, gravity_value) -> None:
        if self.vector.length() > 0:
            self.vector = self.vector.normalize()
            min_speed = 1
            max_speed = 5
            speed = min_speed + (max_speed - min_speed) * (self.energy / 100)
            
            # Dodanie grawitacji zależnej od energii
            gravity = gravity_value * (1 - self.energy/100)  # Im mniejsza energia, tym większa grawitacja
            self.vector.y += gravity
            
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

        
    def collider_with_wall(self, energy) -> None:
        # Lewa ściana
        if self.x < self.radius:
            self.x = self.radius  # Wymuszamy prawidłową pozycję
            self.vector.x *= -1
            self.energy = np.mean([self.energy, energy])
        
        # Prawa ściana    
        elif self.x > 800 - self.radius:
            self.x = 800 - self.radius  # Wymuszamy prawidłową pozycję
            self.vector.x *= -1
            self.energy = np.mean([self.energy, energy])
        
        # Górna ściana
        if self.y < self.radius:
            self.y = self.radius  # Wymuszamy prawidłową pozycję
            self.vector.y *= -1
            self.energy = np.mean([self.energy, energy])
        
        # Dolna ściana
        elif self.y > 600 - self.radius:
            self.y = 600 - self.radius  # Wymuszamy prawidłową pozycję
            self.vector.y *= -1
            self.energy = np.mean([self.energy, energy])
    
    def draw_rect(self, screen) -> None:
        # Rysowanie głównego koła z wypełnieniem
        pygame.gfxdraw.filled_circle(screen, 
                                    int(self.x), 
                                    int(self.y), 
                                    self.radius, 
                                    (0, 0, 0))
        
        # Dodanie wygładzonej krawędzi
        pygame.gfxdraw.aacircle(screen, 
                            int(self.x), 
                            int(self.y), 
                            self.radius, 
                            self.color)

        
    def draw_line(self, screen) -> None:
        for other in self.colided_with:
            # Obliczamy punkty dla linii
            start_pos = (self.x, self.y)
            end_pos = (other.x, other.y)
            
            # Obliczamy długość linii
            length = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
            
            # Liczba segmentów gradientu (możesz dostosować)
            segments = 20
            
            for i in range(segments):
                # Obliczamy pozycje początku i końca segmentu
                start_segment = (
                    start_pos[0] + (end_pos[0] - start_pos[0]) * i / segments,
                    start_pos[1] + (end_pos[1] - start_pos[1]) * i / segments
                )
                end_segment = (
                    start_pos[0] + (end_pos[0] - start_pos[0]) * (i + 1) / segments,
                    start_pos[1] + (end_pos[1] - start_pos[1]) * (i + 1) / segments
                )
                
                # Interpolacja kolorów
                t = i / segments
                color = (
                    int(self.color[0] + (other.color[0] - self.color[0]) * t),
                    int(self.color[1] + (other.color[1] - self.color[1]) * t),
                    int(self.color[2] + (other.color[2] - self.color[2]) * t)
                )
                
                # Rysowanie segmentu
                pygame.draw.line(screen, color, start_segment, end_segment, 2)
        
    def handle_collision(self, others: list):
        self.colided_with = []
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
                
                # Clamp velocity components to prevent overflow
                MAX_VELOCITY = 1000  # Adjust this value as needed
                vx_diff = min(max(other.vector.x - self.vector.x, -MAX_VELOCITY), MAX_VELOCITY)
                vy_diff = min(max(other.vector.y - self.vector.y, -MAX_VELOCITY), MAX_VELOCITY)
                
                relative_velocity = math.sqrt(vx_diff**2 + vy_diff**2)
                impulse = (2 * relative_velocity) / (self.mass + other.mass)
                
                # Clamp impulse to prevent excessive forces
                MAX_IMPULSE = 100  # Adjust this value as needed
                impulse = min(impulse, MAX_IMPULSE)
                
                other.vector.x += (nx * impulse * self.mass)
                other.vector.y += (ny * impulse * self.mass)
                self.vector.x -= (nx * impulse * other.mass)
                self.vector.y -= (ny * impulse * other.mass)
                
                self.energy = np.mean([self.energy, other.energy])
                
            elif self.radius <= 10:
                if distance < self.radius * 4:
                    self.colided_with.append(other)
            elif self.radius > 10:
                if distance < self.radius * 3:
                    self.colided_with.append(other)
    
def calculate_average_energy(atoms: list) -> float:
    # Zbieramy energie wszystkich atomów do listy
    energies = [atom.energy for atom in atoms]
    
    # Używamy numpy do obliczenia średniej
    average_energy = np.mean(energies)
    return average_energy

            
        
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

atoms = [Atom(random.randint(0, 800), random.randint(0, 600), 1, 1, pygame.Vector2(random.randint(1, 3), random.randint(1, 3))) for _ in range(200)]
sliders = [
    Slider(200, 50, 1, 100, 20, "temp", (40, 20, 80)),
    Slider(200, 50, 0, 1, 0.2, "gravity", (40, 20, 80)),
    Slider(200, 50, 5, 15, 10, "size", (40, 20, 80))
]   
font = pygame.font.SysFont('Arial', 20)
for slider in sliders:
        slider.set(sliders, 10, 5)
        
running = True
while running:
    average_energy = calculate_average_energy(atoms)

    # print average energy on screen
    
    screen.fill((0, 0, 0))
    text_surface = font.render(f"{average_energy:.2f}", True, (255, 255, 255))
    screen.blit(text_surface, (700, 10))
    

    for atom in atoms:
        atom.update()
        atom.radius = math.floor(sliders[2].value)
        
        atom.move(sliders[1].value)
        atom.collider_with_wall(sliders[0].value)
        atom.handle_collision(atoms)
        
        atom.draw_line(screen)
        
    for atom in atoms:
        atom.draw_rect(screen)

  
    for slider in sliders:
        slider.draw(screen)
        slider
    pygame.display.flip()
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for slider in sliders:
            slider.handle_event(event)
pygame.quit()