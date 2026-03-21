# menu.py
import pygame
from settings import *
from ui import Button

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 72)
        self.font_button = pygame.font.Font(None, 36)

        # Dimensões e posicionamento dos botões
        btn_width = 200
        btn_height = 50
        center_x = (SCREEN_WIDTH // 2) - (btn_width // 2)

        self.btn_play = Button(center_x, 250, btn_width, btn_height, "Jogar", self.font_button)
        self.btn_credits = Button(center_x, 320, btn_width, btn_height, "Créditos", self.font_button)
        self.btn_quit = Button(center_x, 390, btn_width, btn_height, "Sair", self.font_button)

    def update(self):
        """Atualiza o estado de hover dos botões baseado na posição do mouse."""
        mouse_pos = pygame.mouse.get_pos()
        self.btn_play.update(mouse_pos)
        self.btn_credits.update(mouse_pos)
        self.btn_quit.update(mouse_pos)

    def handle_event(self, event):
        """Processa os cliques e retorna a ação correspondente."""
        if self.btn_play.is_clicked(event):
            return "PLAY"
        if self.btn_credits.is_clicked(event):
            return "CREDITS"
        if self.btn_quit.is_clicked(event):
            return "QUIT"
        return None

    def draw(self):
        self.screen.fill(COLOR_BACKGROUND)
        
        # Desenha o Título
        title_text = self.font_title.render("Últimos Rastros", True, COLOR_TEXT)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)

        # Desenha os botões
        self.btn_play.draw(self.screen)
        self.btn_credits.draw(self.screen)
        self.btn_quit.draw(self.screen)