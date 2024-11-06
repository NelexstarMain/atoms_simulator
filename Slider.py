import pygame
import pygame.font as pf

class Slider:
    """
    A class representing an interactive slider in a graphical interface.

    The slider allows visual control of a numerical value within a specified range
    by dragging a control element with the mouse.

    Attributes:
        x (int): X position of the slider on screen
        y (int): Y position of the slider on screen
        width (int): Width of the slider in pixels
        height (int): Height of the slider in pixels
        min_val (float): Minimum value of the slider
        max_val (float): Maximum value of the slider
        value (float): Current value of the slider
        text (str): Text describing the slider
        color (tuple[int, int, int]): Slider color in RGB format
        active (bool): Flag indicating if slider is active (being dragged)
    """

    def __init__(
                self,
                width,
                height,
                min_val,
                max_val,
                initial_val,
                text,
                color: tuple[int, int, int] = (200, 200, 200),
            ) -> None:
        
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.text = text
        self.color = color
        self.active = False

    def set(self, sliders: list, x_offset: int, y_offset: int) -> None:
        number_in_list = sliders.index(self)
        self.x = x_offset
        self.y = y_offset + (self.height + 40) * number_in_list

    def handle_event(self, event):
        # Dostosuj pozycję myszy względem panelu kontrolnego
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
            # Odejmij szerokość ekranu symulacji, aby uzyskać właściwą pozycję na panelu kontrolnym
            adjusted_x = event.pos[0]
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.x <= adjusted_x <= self.x + self.width and \
                self.y - 10 <= event.pos[1] <= self.y + self.height + 10:
                    self.active = True
            
            elif event.type == pygame.MOUSEMOTION and self.active:
                self.slider_pos = max(self.x, min(adjusted_x, self.x + self.width))
                self.value = self.min_val + (self.slider_pos - self.x) / self.width * (self.max_val - self.min_val)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.active = False

    def draw(self, screen) -> None:
        # Rysowanie tła suwaka
        rect_1 = pygame.Rect(self.x, self.y, self.width, self.height)
        rect_2 = pygame.Rect(self.x, self.y, self.width, self.height * 0.4)
        
        rect_2.center = rect_1.center
        
        pygame.draw.rect(screen, self.color, rect_2, 3)
        
        # Rysowanie tekstu
        font = pf.SysFont('Arial', 15, bold=True)
        font_1 = pf.SysFont('Arial', 13, bold=True)
        
        text_surface = font.render(f"{self.value:.1f}", True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(rect_1.centerx, rect_1.centery + 15))
        
        if self.active:
        
            title = font_1.render(f"{self.text}", False, (0, 0, 0))
            title_rect = title.get_rect(left=self.x, top=self.y - 10)
            screen.blit(title, title_rect)
        
        screen.blit(text_surface, text_rect)
        
        
        # Rysowanie kółka suwaka
        slider_x = self.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.width
        pygame.draw.circle(screen, (0, 0, 0), (int(slider_x), self.y + self.height // 2), 8, 2)

