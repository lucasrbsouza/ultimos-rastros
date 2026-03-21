import pygame
from settings import *

class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        
        # Cores para o efeito visual de hover
        self.color_normal = (50, 80, 60) 
        self.color_hover = (70, 110, 80)
        self.color_text = COLOR_TEXT
        
        self.is_hovered = False

    def update(self, mouse_pos):
        """Verifica se o mouse está sobre o botão."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        """Verifica se o botão foi clicado com o botão esquerdo do mouse."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

    def draw(self, screen):
        """Renderiza o botão na tela."""
        # Altera a cor se o mouse estiver por cima
        current_color = self.color_hover if self.is_hovered else self.color_normal
        pygame.draw.rect(screen, current_color, self.rect, border_radius=8)

        # Desenha o texto centralizado no retângulo
        text_surf = self.font.render(self.text, True, self.color_text)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)