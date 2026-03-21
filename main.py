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
            
            # Lógica de transição no Menu
            if self.current_state == "MENU":
                action = self.main_menu.handle_event(event)
                if action == "PLAY":
                    self.current_state = "GAMEPLAY"
                elif action == "CREDITS":
                    print("Tela de Créditos ainda será implementada!")
                elif action == "QUIT":
                    self.is_running = False
                    
            # Lógica de transição na Gameplay
            elif self.current_state == "GAMEPLAY":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.current_state = "MENU"

    def update(self):
        if self.current_state == "MENU":
            self.main_menu.update()
        elif self.current_state == "GAMEPLAY":
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