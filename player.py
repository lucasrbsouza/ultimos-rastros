import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((32, 64))
        self.image.fill((255, 50, 50)) 
        self.rect = self.image.get_rect(topleft=pos)

        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 5
        self.gravity = 0.8
        self.jump_speed = -16

        # Status do Jogador
        self.max_health = 5
        self.current_health = 5
        self.memories = 0
        
        self.is_invincible = False
        self.invincibility_duration = 1000
        self.hurt_time = 0

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0

        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.direction.y == 0:
            self.jump()

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed

    def take_damage(self, amount):
        """Reduz a vida se o jogador não estiver invencível."""
        if not self.is_invincible:
            self.current_health -= amount
            self.is_invincible = True
            self.hurt_time = pygame.time.get_ticks() # Registra o momento do dano

    def invincibility_timer(self):
        """Verifica se o tempo de invencibilidade já acabou."""
        if self.is_invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time >= self.invincibility_duration:
                self.is_invincible = False

    def update(self):
        self.get_input()
        self.invincibility_timer() # Checa o tempo de invencibilidade todo frame