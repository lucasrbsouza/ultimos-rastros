import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        # Carrega a imagem e converte para um formato otimizado do Pygame (com transparência)
        try:
            self.image = pygame.image.load('assets/tile.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (size, size))
        except FileNotFoundError:
            # Fallback (plano B) caso a imagem falte: desenha o quadrado antigo
            self.image = pygame.Surface((size, size))
            self.image.fill((100, 80, 50))
            
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift

class Memory(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        try:
            self.image = pygame.image.load('assets/memory.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (size // 2, size // 2))
        except FileNotFoundError:
            self.image = pygame.Surface((size // 2, size // 2))
            self.image.fill((255, 220, 50))
            
        center_x = pos[0] + (size // 2)
        center_y = pos[1] + (size // 2)
        self.rect = self.image.get_rect(center=(center_x, center_y))

    def update(self, x_shift):
        self.rect.x += x_shift

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        try:
            self.image = pygame.image.load('assets/obstacle.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (size, size))
        except FileNotFoundError:
            self.image = pygame.Surface((size, size))
            self.image.fill((150, 0, 150))
            
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift

class Goal(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        try:
            self.image = pygame.image.load('assets/goal.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (size, size * 2))
        except FileNotFoundError:
            self.image = pygame.Surface((size, size * 2))
            self.image.fill((100, 255, 100))
            
        self.rect = self.image.get_rect(topleft=(pos[0], pos[1] - size))

    def update(self, x_shift):
        self.rect.x += x_shift