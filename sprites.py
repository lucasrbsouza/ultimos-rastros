import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        # Cria um quadrado básico para representar o chão
        self.image = pygame.Surface((size, size))
        self.image.fill((100, 80, 50))
        
        self.rect = self.image.get_rect(topleft=pos)