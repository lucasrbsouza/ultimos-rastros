import pygame
import sys
from settings import *
from menu import MainMenu, GameOverMenu, VictoryMenu, CreditsMenu
from level import Level
from save_system import delete_save, load_game, has_save

MENU_BGM_PATH = 'assets/sounds/menu_bgm.mp3'
GAME_BGM_PATH = 'assets/sounds/game_bgm.mp3'
GAMEOVER_SOUND_PATH = 'assets/sounds/gameover.mp3'
VICTORY_SOUND_PATH = 'assets/sounds/victory.mp3'

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Últimos Rastros")
        self.clock = pygame.time.Clock()
        self.is_running = True
        
        # Instanciando os componentes
        self.main_menu = MainMenu(self.screen)
        self.game_over_menu = GameOverMenu(self.screen)
        self.victory_menu = VictoryMenu(self.screen)
        self.credits_menu = CreditsMenu(self.screen)
        self.level = None

        self.current_state = None
        self.change_state("MENU")

    def change_state(self, new_state):
        old_state = self.current_state
        self.current_state = new_state

        if new_state == "MENU" and old_state == "CREDITS":
            pygame.mixer.music.unpause()
            return

        # Recria o menu principal para que has_save seja reavaliado
        if new_state == "MENU":
            self.main_menu = MainMenu(self.screen)

        # Mantém a música ao entrar nos Créditos
        if new_state == "CREDITS":
            pygame.mixer.music.unpause()
            return

        pygame.mixer.music.stop()

        try:
            if new_state == "MENU":
                pygame.mixer.music.load(MENU_BGM_PATH)
                pygame.mixer.music.play(-1)
            elif new_state == "GAMEPLAY":
                pygame.mixer.music.load(GAME_BGM_PATH)
                pygame.mixer.music.play(-1)
            elif new_state == "GAMEOVER":
                pygame.mixer.music.load(GAMEOVER_SOUND_PATH)
                pygame.mixer.music.play(0)
            elif new_state == "VICTORY":
                pygame.mixer.music.load(VICTORY_SOUND_PATH)
                pygame.mixer.music.play(0)
                
        except pygame.error:
            print(f"Aviso: Música para o estado {new_state} não encontrada na pasta assets.")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            
            if self.current_state == "MENU":
                action = self.main_menu.handle_event(event)
                if action == "CONTINUE":
                    save_data = load_game()
                    self.level = Level(self.screen, save_data)
                    self.change_state("GAMEPLAY")
                elif action == "NEW_GAME":
                    delete_save()
                    self.level = Level(self.screen)
                    self.change_state("GAMEPLAY")
                elif action == "CREDITS":
                    self.change_state("CREDITS")
                    print("Créditos: José Lucas Silva Souza")
                elif action == "QUIT":
                    self.is_running = False
                    
            elif self.current_state == "GAMEPLAY":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.change_state("MENU")
                self.level.player.sprite.handle_event(event)
            
            elif self.current_state == "GAMEOVER":
                action = self.game_over_menu.handle_event(event)
                if action == "RETRY":
                    delete_save()
                    self.level = Level(self.screen)
                    self.change_state("GAMEPLAY")
                elif action == "MENU":
                    self.change_state("MENU")
                    
            elif self.current_state == "VICTORY":
                action = self.victory_menu.handle_event(event)
                if action == "MENU":
                    self.change_state("MENU")
                elif action == "QUIT":
                    self.is_running = False
            
            elif self.current_state == "CREDITS":
                action = self.credits_menu.handle_event(event)
                if action == "MENU":
                    self.change_state("MENU")

    def update(self):
        if self.current_state == "MENU":
            self.main_menu.update()
        elif self.current_state == "GAMEOVER":
            self.game_over_menu.update()
        elif self.current_state == "VICTORY":
            self.victory_menu.update()
        elif self.current_state == "CREDITS":
            self.credits_menu.update()

    def draw(self):
        if self.current_state == "MENU":
            self.main_menu.draw()
            
        elif self.current_state == "GAMEPLAY":
            game_status = self.level.run() 
            if game_status == "GAMEOVER":
                self.change_state("GAMEOVER")
            elif game_status == "VICTORY":
                self.change_state("VICTORY")
                
        elif self.current_state == "GAMEOVER":
            self.game_over_menu.draw()
            
        elif self.current_state == "VICTORY":
            self.victory_menu.draw()
        elif self.current_state == "CREDITS":
            self.credits_menu.draw()
            
        pygame.display.flip()

    def run(self):
        while self.is_running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()