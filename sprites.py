import pygame

TILE_IMAGE_PATH = 'assets/tile.svg'
MEMORY_IMAGE_PATH = 'assets/memory.png'
ENEMY_IMAGE_PATH = 'assets/enemy.svg'
GOAL_IMAGE_PATH = 'assets/goal.png'

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        # Carrega a imagem e converte para um formato otimizado do Pygame (com transparência)
        try:
            self.image = pygame.image.load(TILE_IMAGE_PATH).convert_alpha()
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
            self.image = pygame.image.load(MEMORY_IMAGE_PATH).convert_alpha()
            self.image = pygame.transform.scale(self.image, (size // 2, size // 2))
        except FileNotFoundError:
            self.image = pygame.Surface((size // 2, size // 2))
            self.image.fill((255, 220, 50))
            
        center_x = pos[0] + (size // 2)
        center_y = pos[1] + (size // 2)
        self.rect = self.image.get_rect(center=(center_x, center_y))

    def update(self, x_shift):
        self.rect.x += x_shift

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        
        try:
            self.image = pygame.image.load(ENEMY_IMAGE_PATH).convert_alpha()
            self.image = pygame.transform.scale(self.image, (size, size))
        except FileNotFoundError:
            self.image = pygame.Surface((size, size))
            self.image.fill((200, 50, 50)) 
        self.rect = self.image.get_rect(topleft=pos)

        # Variáveis de Patrulha (Inteligência Artificial básica)
        self.speed = 2
        self.direction = -1 # 1 para a direita, -1 para a esquerda
        self.patrol_distance = 0
        self.max_patrol = 60 # Quantidade de pixels que ele anda antes de virar

    def update(self, x_shift):
        """Move o inimigo com a câmera E faz ele patrulhar."""
        # 1. Movimento da câmera
        self.rect.x += x_shift
        
        # 2. Movimento autônomo (Patrulha)
        self.rect.x += self.speed * self.direction
        self.patrol_distance += self.speed
        
        
        if self.patrol_distance >= self.max_patrol:
            self.direction *= -1 # Inverte a direção
            self.patrol_distance = -self.max_patrol # Reinicia a contagem para voltar
            
            
            self.image = pygame.transform.flip(self.image, True, False)

class Goal(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        try:
            self.image = pygame.image.load(GOAL_IMAGE_PATH).convert_alpha()
            self.image = pygame.transform.scale(self.image, (size, size * 2))
        except FileNotFoundError:
            self.image = pygame.Surface((size, size * 2))
            self.image.fill((100, 255, 100))
            
        self.rect = self.image.get_rect(topleft=(pos[0], pos[1] - size))

    def update(self, x_shift):
        self.rect.x += x_shift