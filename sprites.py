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

class Memory(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        # Um quadrado menor e amarelo para representar a memória
        self.image = pygame.Surface((size // 2, size // 2))
        self.image.fill((255, 220, 50)) 
        
        # Centraliza o item no meio do bloco
        center_x = pos[0] + (size // 2)
        center_y = pos[1] + (size // 2)
        self.rect = self.image.get_rect(center=(center_x, center_y))

    def update(self, x_shift):
        """Move o item junto com a câmera do cenário."""
        self.rect.x += x_shift

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        # Um bloco roxo para sinalizar perigo
        self.image = pygame.Surface((size, size))
        self.image.fill((150, 0, 150)) 
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        """Move o obstáculo junto com a câmera."""
        self.rect.x += x_shift