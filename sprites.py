import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill((100, 80, 50)) 
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        """Move o bloco no eixo X para simular o movimento da câmera."""
        self.rect.x += x_shift