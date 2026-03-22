import pygame
from settings import *
from ui import Button

BG_MENU_PATH = 'assets/backgrounds/bg_menu.png'
BG_GAMEOVER_PATH = 'assets/backgrounds/bg_gameover.png'
BG_VICTORY_PATH = 'assets/backgrounds/bg_victory.png'

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 72)
        self.font_button = pygame.font.Font(None, 36)

        btn_width = 200
        btn_height = 50
        center_x = (SCREEN_WIDTH // 2) - (btn_width // 2)

        self.btn_play = Button(center_x, 250, btn_width, btn_height, "Jogar", self.font_button)
        self.btn_credits = Button(center_x, 320, btn_width, btn_height, "Créditos", self.font_button)
        self.btn_quit = Button(center_x, 390, btn_width, btn_height, "Sair", self.font_button)

        # Carrega o background do Menu
        try:
            self.bg_image = pygame.image.load(BG_MENU_PATH).convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except FileNotFoundError:
            self.bg_image = None

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_play.update(mouse_pos)
        self.btn_credits.update(mouse_pos)
        self.btn_quit.update(mouse_pos)

    def handle_event(self, event):
        if self.btn_play.is_clicked(event):
            return "PLAY"
        if self.btn_credits.is_clicked(event):
            return "CREDITS"
        if self.btn_quit.is_clicked(event):
            return "QUIT"
        return None

    def draw(self):
        # Desenha a imagem se existir; caso contrário, usa a cor sólida
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(COLOR_BACKGROUND)
        
        title_text = self.font_title.render("Últimos Rastros", True, COLOR_TEXT)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)

        self.btn_play.draw(self.screen)
        self.btn_credits.draw(self.screen)
        self.btn_quit.draw(self.screen)


class GameOverMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 72)
        self.font_button = pygame.font.Font(None, 36)

        btn_width = 250
        btn_height = 50
        center_x = (SCREEN_WIDTH // 2) - (btn_width // 2)

        self.btn_retry = Button(center_x, 300, btn_width, btn_height, "Tentar Novamente", self.font_button)
        self.btn_menu = Button(center_x, 370, btn_width, btn_height, "Menu Principal", self.font_button)

        # Carrega o background de Game Over
        try:
            self.bg_image = pygame.image.load(BG_GAMEOVER_PATH).convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except FileNotFoundError:
            self.bg_image = None

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
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill((50, 15, 15)) 
        
        title_text = self.font_title.render("A Floresta Esqueceu...", True, (255, 100, 100))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)

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

        # Carrega o background de Vitória
        try:
            self.bg_image = pygame.image.load(BG_VICTORY_PATH).convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except FileNotFoundError:
            self.bg_image = None

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
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill((20, 50, 30)) 
        
        title_text = self.font_title.render("A Lenda Vive!", True, (150, 255, 150))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)

        self.btn_menu.draw(self.screen)
        self.btn_quit.draw(self.screen)