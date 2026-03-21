import pygame
import sys
from settings import *
from menu import MainMenu
from level import Level
from menu import MainMenu, GameOverMenu, VictoryMenu

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Últimos Rastros")
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.current_state = "MENU"
        # Instanciando os componentes
        self.main_menu = MainMenu(self.screen)
        self.game_over_menu = GameOverMenu(self.screen)
        self.victory_menu = VictoryMenu(self.screen)
        self.level = Level(self.screen)
        

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
            
            if self.current_state == "MENU":
                action = self.main_menu.handle_event(event)
                if action == "PLAY":
                    self.level = Level(self.screen)
                    self.current_state = "GAMEPLAY"
                elif action == "CREDITS":
                    print("Créditos: José Lucas Silva Souza")
                elif action == "QUIT":
                    self.is_running = False
                    
            elif self.current_state == "GAMEPLAY":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.current_state = "MENU"
            
            elif self.current_state == "GAMEOVER":
                action = self.game_over_menu.handle_event(event)
                if action == "RETRY":
                    self.level = Level(self.screen) # Recria a fase do zero
                    self.current_state = "GAMEPLAY"
                elif action == "MENU":
                    self.current_state = "MENU"

            elif self.current_state == "VICTORY":
                action = self.victory_menu.handle_event(event)
                if action == "MENU":
                    self.current_state = "MENU"
                elif action == "QUIT":
                    self.is_running = False
            

    def update(self):
        if self.current_state == "MENU":
            self.main_menu.update()
        elif self.current_state == "GAMEOVER":
            self.game_over_menu.update()
        elif self.current_state == "VICTORY":
            self.victory_menu.update()

    def draw(self):
        if self.current_state == "MENU":
            self.main_menu.draw()
            
        elif self.current_state == "GAMEPLAY":
            game_status = self.level.run() 
            if game_status == "GAMEOVER":
                self.current_state = "GAMEOVER"
            elif game_status == "VICTORY":
                self.current_state = "VICTORY"
                
        elif self.current_state == "GAMEOVER":
            self.game_over_menu.draw()
        
        elif self.current_state == "VICTORY":
            self.victory_menu.draw()
            
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()