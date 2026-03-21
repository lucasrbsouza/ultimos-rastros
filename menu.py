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

class GameOverMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 72)
        self.font_button = pygame.font.Font(None, 36)

        # Configuração dos botões
        btn_width = 250
        btn_height = 50
        center_x = (SCREEN_WIDTH // 2) - (btn_width // 2)

        # O botão exigido pelo GDD
        self.btn_retry = Button(center_x, 300, btn_width, btn_height, "Tentar Novamente", self.font_button)
        self.btn_menu = Button(center_x, 370, btn_width, btn_height, "Menu Principal", self.font_button)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_retry.update(mouse_pos)
        self.btn_menu.update(mouse_pos)

    def handle_event(self, event):
        if self.btn_retry.is_clicked(event):
            return "RETRY"
        if self.btn_menu.is_clicked(event):
            return "MENU"
        return None

    def draw(self):
        # Fundo avermelhado escuro para indicar derrota
        self.screen.fill((50, 15, 15)) 
        
        # Título
        title_text = self.font_title.render("A Floresta Esqueceu...", True, (255, 100, 100))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)

        # Botões
        self.btn_retry.draw(self.screen)
        self.btn_menu.draw(self.screen)

class VictoryMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 72)
        self.font_button = pygame.font.Font(None, 36)

        btn_width = 250
        btn_height = 50
        center_x = (SCREEN_WIDTH // 2) - (btn_width // 2)

        self.btn_menu = Button(center_x, 300, btn_width, btn_height, "Menu Principal", self.font_button)
        self.btn_quit = Button(center_x, 370, btn_width, btn_height, "Sair do Jogo", self.font_button)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_menu.update(mouse_pos)
        self.btn_quit.update(mouse_pos)

    def handle_event(self, event):
        if self.btn_menu.is_clicked(event):
            return "MENU"
        if self.btn_quit.is_clicked(event):
            return "QUIT"
        return None

    def draw(self):
        self.screen.fill((20, 50, 30)) 
        
        # Título
        title_text = self.font_title.render("A Lenda Vive!", True, (150, 255, 150))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)

        # Botões
        self.btn_menu.draw(self.screen)
        self.btn_quit.draw(self.screen)