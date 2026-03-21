import pygame
from settings import *

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 72)
        self.font_text = pygame.font.Font(None, 36)

    def update(self):
        pass

    def draw(self):
        self.screen.fill(COLOR_BACKGROUND)
        
        # Renderiza o Título
        title_text = self.font_title.render("Últimos Rastros", True, COLOR_TEXT)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)
        
        # Renderiza uma instrução temporária
        instruction_text = self.font_text.render("Pressione ENTER para Jogar", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(instruction_text, instruction_rect)