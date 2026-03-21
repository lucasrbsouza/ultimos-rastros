import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((32, 64))
        self.image.fill((255, 50, 50)) 
        self.rect = self.image.get_rect(topleft=pos)

        # Vetor de direção (x, y)
        self.direction = pygame.math.Vector2(0, 0)
        
        # Variáveis de Física e Movimento
        self.speed = 5
        self.gravity = 0.8
        self.jump_speed = -16

    def get_input(self):
        """Captura as teclas pressionadas pelo jogador."""
        keys = pygame.key.get_pressed()

        # Movimento Horizontal (Setas ou A/D)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0

        # Pulo (Seta pra cima, W ou Espaço)
        # O pulo só acontece se a velocidade Y for 0 (ou seja, ele está no chão)
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.direction.y == 0:
            self.jump()

    def apply_gravity(self):
        """A gravidade puxa o jogador para baixo constantemente."""
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed

    def update(self):
        """Atualiza a intenção de movimento. A colisão real será feita no Level."""
        self.get_input()