import pygame

PLAYER_IDLE_PATH = 'assets/player_spritesheet/Idle.png'
PLAYER_WALK_PATH = 'assets/player_spritesheet/Walk.png'
PLAYER_RUN_PATH = 'assets/player_spritesheet/Run.png'
PLAYER_JUMP_PATH = 'assets/player_spritesheet/Jump.png'
JUMP_SOUND_PATH = 'assets/sounds/jump.mp3'
DAMAGE_SOUND_PATH = 'assets/sounds/damage.mp3'

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
            self.jump_sound = pygame.mixer.Sound(JUMP_SOUND_PATH)
            self.jump_sound.set_volume(0.3) # Abaixamos o volume para não estourar o ouvido
            
            self.damage_sound = pygame.mixer.Sound(DAMAGE_SOUND_PATH)
            self.damage_sound.set_volume(0.5)
        except FileNotFoundError:
            # Se o arquivo não existir, o jogo continua rodando sem som
            self.jump_sound = None
            self.damage_sound = None

    def get_frame(self, sheet, frame_x, frame_y, width, height, scale):
        """Extrai um único quadro (frame) do spritesheet."""
        # Cria uma superfície vazia transparente do tamanho exato do quadro
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # 'Carimba' o pedaço específico do spritesheet nessa superfície vazia
        # O tuplo (frame_x, frame_y, width, height) é o retângulo de corte
        image.blit(sheet, (0, 0), (frame_x, frame_y, width, height))
        
        # Redimensiona a imagem para o jogo (caso o pixel art seja muito pequeno)
        image = pygame.transform.scale(image, (width * scale, height * scale))
        
        return image

    def import_character_assets(self):
        """Carrega o spritesheet e recorta as animações automaticamente."""
        self.animations = {'idle': [], 'run': [], 'jump': []}
        
        try:
            # Carregue as imagens dos spritesheets
            player_idle = pygame.image.load(PLAYER_IDLE_PATH).convert_alpha()
            player_run = pygame.image.load(PLAYER_RUN_PATH).convert_alpha()
            player_jump = pygame.image.load(PLAYER_JUMP_PATH).convert_alpha()

            # --- Dimensões do spritesheet ---
            # Largura total: 1024 px, altura: 128 px, 8 quadros
            frame_width = 1024 // 8   # = 128
            frame_height = 128        # = 128
            scale = 0.80                # fator de escala (ajuste se necessário)

            # Recortando a animação de Idle (Parado)
            # Todos os quadros estão na linha Y = 0
            for i in range(5):
                frame = self.get_frame(player_idle, i * frame_width, 0, frame_width, frame_height, scale)
                self.animations['idle'].append(frame)

            # Recortando a animação de Walk (Andar)
            for i in range(8):
                frame = self.get_frame(player_run, i * frame_width, 0, frame_width, frame_height, scale)
                self.animations['run'].append(frame)

            # Recortando a animação de Jump (Pular)
            # Se o spritesheet de pulo tiver menos quadros, ajuste o range
            # Exemplo: se tiver apenas 2 quadros, use range(2)
            # Caso tenha 8 quadros, use range(8)
            for i in range(7):  # ou range(2) se for o caso
                frame = self.get_frame(player_jump, i * frame_width, 0, frame_width, frame_height, scale)
                self.animations['jump'].append(frame)


        except FileNotFoundError:
            # Fallback de segurança (mantém o quadrado vermelho se algo der errado)
            fallback = pygame.Surface((32, 64))
            fallback.fill((255, 50, 50))
            self.animations['idle'].append(fallback)
            self.animations['run'].append(fallback)
            self.animations['jump'].append(fallback)

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            self.facing_right = False
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
        
        if self.facing_right:
            self.image = image
        else:
            self.image = pygame.transform.flip(image, True, False) # True no X, False no Y

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed
        if self.jump_sound:
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