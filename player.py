import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        
        self.import_character_assets()
        self.frame_index = 0
        self.animation_speed = 0.15
        
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        # Define a imagem inicial (parado)
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        # 2. Variáveis de Movimento
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 5
        self.gravity = 0.8
        self.jump_speed = -16

        # 3. Status e Direção (NOVO)
        self.status = 'idle'
        self.facing_right = True

        # 4. Status do Jogador
        self.max_health = 5
        self.current_health = 5
        self.memories = 0
        self.is_invincible = False
        self.invincibility_duration = 1000 
        self.hurt_time = 0

        try:
            self.jump_sound = pygame.mixer.Sound('assets/jump.mp3')
            self.jump_sound.set_volume(0.3) # Abaixamos o volume para não estourar o ouvido
            
            self.damage_sound = pygame.mixer.Sound('assets/damage.mp3')
            self.damage_sound.set_volume(0.5)
        except FileNotFoundError:
            # Se o arquivo não existir, o jogo continua rodando sem som
            self.jump_sound = None
            self.damage_sound = None

    def import_character_assets(self):
        """Carrega a imagem e cria variações para simular animação (Squash & Stretch)."""
        self.animations = {'idle': [], 'run': [], 'jump': []}
        
        try:
            img = pygame.image.load('assets/player.png').convert_alpha()
            base_image = pygame.transform.scale(img, (32, 64))
            
            # Animação Parado (Idle)
            self.animations['idle'].append(base_image)
            
            # Animação Correndo (Intercala a imagem normal com uma levemente achatada)
            run_frame = pygame.transform.scale(img, (34, 60)) 
            self.animations['run'].append(base_image)
            self.animations['run'].append(run_frame)
            
            # Animação Pulando (Imagem levemente esticada)
            jump_frame = pygame.transform.scale(img, (28, 68))
            self.animations['jump'].append(jump_frame)

        except FileNotFoundError:
            # Fallback: Mantém os blocos vermelhos se faltar imagem
            fallback = pygame.Surface((32, 64))
            fallback.fill((255, 50, 50))
            self.animations['idle'].append(fallback)
            self.animations['run'].append(fallback)
            self.animations['jump'].append(fallback)

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.facing_right = True # Curupira olha para a direita
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            self.facing_right = False # Curupira olha para a esquerda
        else:
            self.direction.x = 0

        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.direction.y == 0:
            self.jump()

    def get_status(self):
        """Define o estado atual do personagem baseado no movimento."""
        if self.direction.y != 0:
            self.status = 'jump' # Se estiver subindo ou caindo, está pulando
        elif self.direction.x != 0:
            self.status = 'run'  # Se está no chão e se movendo, está correndo
        else:
            self.status = 'idle' # Se não é nenhum dos dois, está parado

    def animate(self):
        """Roda a animação correta e vira a imagem se necessário."""
        animation = self.animations[self.status]
        
        # Aumenta o índice para trocar de quadro
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
            
        # Pega a imagem atual da lista
        image = animation[int(self.frame_index)]
        
        # O pulo do gato: pygame.transform.flip vira a imagem horizontalmente!
        if self.facing_right:
            self.image = image
        else:
            self.image = pygame.transform.flip(image, True, False) # True no X, False no Y

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed
        if self.jump_sound: # Só toca se o som foi carregado com sucesso
            self.jump_sound.play()

    def take_damage(self, amount):
        if not self.is_invincible:
            self.current_health -= amount
            self.is_invincible = True
            self.hurt_time = pygame.time.get_ticks()
            
            if self.damage_sound: # Toca o som de dor
                self.damage_sound.play()

    def invincibility_timer(self):
        if self.is_invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time >= self.invincibility_duration:
                self.is_invincible = False

    def update(self):
        self.get_input()
        self.get_status()
        self.animate() 
        self.invincibility_timer()