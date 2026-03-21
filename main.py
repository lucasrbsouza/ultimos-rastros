import pygame
import sys
from settings import *

class Game:
    def __init__(self):
        # Inicializa os módulos do Pygame
        pygame.init()
        
        # Configura a janela
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Últimos Rastros")
        
        # Relógio para controlar os Frames Por Segundo (FPS)
        self.clock = pygame.time.Clock()
        
        # Variável de controle do loop principal
        self.is_running = True

    def run(self):
        """O Loop Macro do jogo."""
        while self.is_running:
            self.handle_events()
            self.update()
            self.draw()
            
            # Mantém o jogo rodando na velocidade certa
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

    def handle_events(self):
        """Lida com as entradas do usuário (teclado, mouse, fechar janela)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

    def update(self):
        """Atualiza a lógica do jogo (movimento, colisões, status)."""
        # Por enquanto não temos lógica para atualizar
        pass

    def draw(self):
        """Renderiza os elementos na tela."""
        # Limpa a tela com a cor de fundo
        self.screen.fill(COLOR_BACKGROUND)
        
        # Atualiza o display com o que foi desenhado
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()