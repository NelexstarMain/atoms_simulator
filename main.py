import pygame
import random
import math

# Inicjalizacja Pygame
pygame.init()

# Ustawienia okna
WIDTH = 1024
HEIGHT = 600
CONTROL_PANEL_WIDTH = 300
MAIN_SCREEN_WIDTH = WIDTH - CONTROL_PANEL_WIDTH

screen = pygame.display.set_mode((WIDTH, HEIGHT))
simulation_surface = pygame.Surface((MAIN_SCREEN_WIDTH, HEIGHT))
control_surface = pygame.Surface((CONTROL_PANEL_WIDTH, HEIGHT))

trail_surface = pygame.Surface((WIDTH, HEIGHT))
trail_surface.set_colorkey((0, 0, 0))
trail_surface.set_alpha(20)  

# Definicje typów cząsteczek
PARTICLE_TYPES = {
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 0, 255),
    'YELLOW': (255, 255, 0)

}

# Macierz oddziaływań między typami
INTERACTION_MATRIX = {
    'RED': {'RED': -10, 'GREEN': 40, 'BLUE': -20, 'YELLOW': 60, 'CURSOR': -100},
    'GREEN': {'RED': 40, 'GREEN': -10, 'BLUE': 40, 'YELLOW': 60, 'CURSOR': -100},
    'BLUE': {'BLUE': -10, 'RED': -20, 'GREEN': 40, 'YELLOW': 60, 'CURSOR': -100},
    'YELLOW': {'BLUE': -40, 'RED': -40, 'GREEN': -40, 'YELLOW': -100, 'CURSOR': -100},
    'CURSOR': {'BLUE': -50, 'GREEN': -50, 'RED': -50, 'YELLOW': -50, 'CURSOR': 0}
}


class Particle:
    def __init__(self):
        self.radius = 5
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(self.radius, HEIGHT - self.radius)
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.type = random.choice(list(PARTICLE_TYPES.keys()))
        self.color = PARTICLE_TYPES[self.type]
        self.mass = 1

        
    def calculate_force(self, other):
        # Obliczanie odległości między cząsteczkami
        dx = other.x - self.x
        dy = other.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 1:
            distance = 1
            
        # Siła oddziaływania zależna od typu cząsteczek
        force = INTERACTION_MATRIX[self.type][other.type]
        
        # Obliczanie składowych siły
        force_x = (force * dx) / (distance * distance)
        force_y = (force * dy) / (distance * distance)
        
        return force_x, force_y, distance

    def handle_collision(self, other):
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
            
            # Obliczanie prędkości względnej
            relative_vx = self.vx - other.vx
            relative_vy = self.vy - other.vy
            
            # Prędkość względna wzdłuż normalnej
            velocity_along_normal = relative_vx * nx + relative_vy * ny
            
            if velocity_along_normal > 0:
                return
            
            restitution = 0.8
            
            # Obliczanie impulsu
            j = -(1 + restitution) * velocity_along_normal
            j /= 1/self.mass + 1/other.mass
            
            # Aplikowanie impulsu
            impulse_x = j * nx
            impulse_y = j * ny
            
            self.vx -= impulse_x / self.mass
            self.vy -= impulse_y / self.mass
            other.vx += impulse_x / other.mass
            other.vy += impulse_y / other.mass

    def update(self, particles):
        fx = fy = 0
        
        for other in particles:
            if other != self:
                force_x, force_y, distance = self.calculate_force(other)
                fx += force_x
                fy += force_y
                self.handle_collision(other)
        
        # Aktualizacja prędkości
        self.vx += fx * 0.1
        self.vy += fy * 0.1
        
        # Ograniczenie prędkości
        speed = math.sqrt(self.vx*self.vx + self.vy*self.vy)
        if speed > 10:
            self.vx = (self.vx/speed) * 5
            self.vy = (self.vy/speed) * 5
        
        # Aktualizacja pozycji
        self.x += self.vx
        self.y += self.vy
        
        # Odbicie od ścian
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
        # Rysowanie poświaty
        for glow_radius in range(self.radius + 2, self.radius, -2):
            alpha = max(0, min(255, int(150 * (1 - (glow_radius - self.radius) / 12))))
            glow_surface = pygame.Surface((glow_radius * 2 + 2, glow_radius * 2 + 2), pygame.SRCALPHA)
            color_with_alpha = (*[min(255, c + 100) for c in self.color], alpha)
            pygame.draw.circle(glow_surface, color_with_alpha, 
                            (glow_radius + 1, glow_radius + 1), glow_radius)
            screen.blit(glow_surface, (int(self.x - glow_radius - 1), 
                                    int(self.y - glow_radius - 1)))
        
        # Rysowanie śladu
        trail_color = tuple(min(255, c + 100) for c in self.color)
        pygame.draw.circle(trail_surface, trail_color, 
                        (int(self.x), int(self.y)), self.radius)
        
        # Rysowanie głównej cząsteczki
        pygame.draw.circle(screen, self.color, 
                        (int(self.x), int(self.y)), self.radius)


            
        
        
        
class Cursor(Particle):
    def __init__(self):
        self.radius = 50
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(self.radius, HEIGHT - self.radius)
        self.type = "CURSOR"
        self.color = (0, 0, 0)
        self.vx = 10
        self.vy = 10
        self.mass = 40
        
        
        
        
        
class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.text = text
        self.active = False
        self.slider_pos = self.x + (self.value - min_val) / (max_val - min_val) * self.width

    def draw(self, screen):
        # Rysuj tło suwaka
        pygame.draw.rect(screen, (100, 100, 100), (self.x, self.y, self.width, self.height))
        # Rysuj suwak
        pygame.draw.circle(screen, (200, 200, 200), (int(self.slider_pos), self.y + self.height//2), 10)
        # Rysuj tekst i wartość
        font = pygame.font.Font(None, 24)
        text_surface = font.render(f"{self.text}: {self.value:.1f}", True, (255, 255, 255))
        screen.blit(text_surface, (self.x, self.y - 20))

    def handle_event(self, event):
        # Dostosuj pozycję myszy względem panelu kontrolnego
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
            # Odejmij szerokość ekranu symulacji, aby uzyskać właściwą pozycję na panelu kontrolnym
            adjusted_x = event.pos[0] - MAIN_SCREEN_WIDTH
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.x <= adjusted_x <= self.x + self.width and \
                self.y - 10 <= event.pos[1] <= self.y + self.height + 10:
                    self.active = True
            
            elif event.type == pygame.MOUSEMOTION and self.active:
                self.slider_pos = max(self.x, min(adjusted_x, self.x + self.width))
                self.value = self.min_val + (self.slider_pos - self.x) / self.width * (self.max_val - self.min_val)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.active = False
# Dodaj suwaki na początku programu, po inicjalizacji pygame:
sliders = [
    # Interakcje RED
    Slider(20, 20, 260, 10, -100, 100, INTERACTION_MATRIX['RED']['RED'], "RED-RED"),
    Slider(20, 50, 260, 10, -100, 100, INTERACTION_MATRIX['RED']['GREEN'], "RED-GREEN"),
    Slider(20, 80, 260, 10, -100, 100, INTERACTION_MATRIX['RED']['BLUE'], "RED-BLUE"),
    Slider(20, 110, 260, 10, -100, 100, INTERACTION_MATRIX['RED']['YELLOW'], "RED-YELLOW"),
    
    # Interakcje GREEN
    Slider(20, 160, 260, 10, -100, 100, INTERACTION_MATRIX['GREEN']['GREEN'], "GREEN-GREEN"),
    Slider(20, 190, 260, 10, -100, 100, INTERACTION_MATRIX['GREEN']['BLUE'], "GREEN-BLUE"),
    Slider(20, 220, 260, 10, -100, 100, INTERACTION_MATRIX['GREEN']['YELLOW'], "GREEN-YELLOW"),
    
    # Interakcje BLUE
    Slider(20, 270, 260, 10, -100, 100, INTERACTION_MATRIX['BLUE']['BLUE'], "BLUE-BLUE"),
    Slider(20, 300, 260, 10, -100, 100, INTERACTION_MATRIX['BLUE']['YELLOW'], "BLUE-YELLOW"),
    
    # Interakcje YELLOW
    Slider(20, 350, 260, 10, -100, 100, INTERACTION_MATRIX['YELLOW']['YELLOW'], "YELLOW-YELLOW"),
    
    # Parametry fizyczne
    Slider(20, 400, 260, 10, 0.1, 5.0, 1.0, "Prędkość"),
    Slider(20, 430, 260, 10, 1, 20, 5, "Promień"),
    Slider(20, 460, 260, 10, 0.1, 2.0, 0.8, "Elastyczność"),
    Slider(20, 490, 260, 10, 1, 100, 20, "Siła oddziaływań"),
    Slider(20, 520, 260, 10, 0, 100, 20, "Przezroczystość śladów")
]


particles = [Particle() for _ in range(200)]
particles.append(Cursor())

# Główna pętla
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for slider in sliders:
            slider.handle_event(event)

    # Aktualizacja wartości
    INTERACTION_MATRIX['RED']['RED'] = sliders[0].value
    INTERACTION_MATRIX['RED']['GREEN'] = sliders[1].value
    INTERACTION_MATRIX['RED']['BLUE'] = sliders[2].value
    INTERACTION_MATRIX['RED']['YELLOW'] = sliders[3].value
    
    INTERACTION_MATRIX['GREEN']['GREEN'] = sliders[4].value
    INTERACTION_MATRIX['GREEN']['BLUE'] = sliders[5].value
    INTERACTION_MATRIX['GREEN']['YELLOW'] = sliders[6].value
    
    INTERACTION_MATRIX['BLUE']['BLUE'] = sliders[7].value
    INTERACTION_MATRIX['BLUE']['YELLOW'] = sliders[8].value
    
    INTERACTION_MATRIX['YELLOW']['YELLOW'] = sliders[9].value
    
    speed_multiplier = sliders[10].value
    particle_radius = int(sliders[11].value)
    restitution = sliders[12].value
    force_multiplier = sliders[13].value
    trail_alpha = int(sliders[14].value)
    
    # Aktualizacja przezroczystości śladów
    trail_surface.set_alpha(trail_alpha)

    # Czyszczenie powierzchni
    simulation_surface.fill((0, 0, 0))
    control_surface.fill((40, 40, 40))  # Ciemniejsze tło dla panelu kontrolnego
    
    # Przyciemnianie śladów
    dark_surface = pygame.Surface((MAIN_SCREEN_WIDTH, HEIGHT))
    dark_surface.fill((0, 0, 0))
    dark_surface.set_alpha(10)
    trail_surface.blit(dark_surface, (0, 0))
    
    # Rysowanie śladów
    simulation_surface.blit(trail_surface, (0, 0))
    
    # Aktualizacja i rysowanie cząsteczek
    for particle in particles:
        if particle.type == "CURSOR":
            particle.x, particle.y = pygame.mouse.get_pos()
            if particle.x > MAIN_SCREEN_WIDTH:
                particle.x = MAIN_SCREEN_WIDTH
        else:
            particle.update(particles)
            particle.radius = particle_radius
            particle.draw(simulation_surface)
    
    # Rysowanie suwaków na panelu kontrolnym
    for slider in sliders:
        slider.draw(control_surface)
    
    # Łączenie powierzchni
    screen.blit(simulation_surface, (0, 0))
    screen.blit(control_surface, (MAIN_SCREEN_WIDTH, 0))
    
    pygame.display.flip()
    clock.tick(60)