# main.py
import pygame
import sys
from settings import *
from menu import MainMenu

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Últimos Rastros")
        self.clock = pygame.time.Clock()
        self.is_running = True
        
        # Gerenciamento de Estados ("MENU", "GAMEPLAY", "GAMEOVER", "VICTORY")
        self.current_state = "MENU"
        
        # Instanciando os componentes visuais
        self.main_menu = MainMenu(self.screen)

    def run(self):
        while self.is_running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            
            # Lógica simples de transição de estado para teste
            if event.type == pygame.KEYDOWN:
                if self.current_state == "MENU" and event.key == pygame.K_RETURN:
                    self.current_state = "GAMEPLAY"
                elif self.current_state == "GAMEPLAY" and event.key == pygame.K_ESCAPE:
                    # Permite voltar ao menu apertando ESC
                    self.current_state = "MENU"

    def update(self):
        if self.current_state == "MENU":
            self.main_menu.update()
        elif self.current_state == "GAMEPLAY":
            # A lógica do Curupira e do cenário virá aqui
            pass

    def draw(self):
        if self.current_state == "MENU":
            self.main_menu.draw()
        elif self.current_state == "GAMEPLAY":
            # Cor diferente para provar que mudamos de estado (uma simulação da floresta)
            self.screen.fill((30, 80, 40)) 
            
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()