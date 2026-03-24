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
        
        # 1. Configuração Visual e Hitbox
        self.image = self.animations['idle'][self.frame_index]
        full_image_rect = self.image.get_rect(topleft=pos)

        # Hitbox Físico: 40px de largura e 80px de altura
        # Se a colisão continuar estranha, ajuste apenas estes dois números!
        self.rect = pygame.Rect(full_image_rect.x, full_image_rect.y, 40, 80)
        self.rect.midbottom = full_image_rect.midbottom

        # 2. Variáveis de Movimento
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 5
        self.gravity = 0.8
        self.jump_speed = -16

        # 3. Status e Direção
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
            self.jump_sound.set_volume(0.3) 
            
            self.damage_sound = pygame.mixer.Sound(DAMAGE_SOUND_PATH)
            self.damage_sound.set_volume(0.5)
        except FileNotFoundError:
            self.jump_sound = None
            self.damage_sound = None

    def get_frame(self, sheet, frame_x, frame_y, width, height, scale):
        """Extrai um único quadro (frame) do spritesheet."""
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(sheet, (0, 0), (frame_x, frame_y, width, height))
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        return image

    def import_character_assets(self):
        """Carrega e fatia os spritesheets de forma dinâmica (Clean Code)."""
        self.animations = {'idle': [], 'run': [], 'jump': []}
        scale = 0.80 

        try:
            player_idle = pygame.image.load(PLAYER_IDLE_PATH).convert_alpha()
            player_run = pygame.image.load(PLAYER_RUN_PATH).convert_alpha()
            player_jump = pygame.image.load(PLAYER_JUMP_PATH).convert_alpha()

            # --- ATENÇÃO AQUI ---
            # Verifique nas suas imagens quantos desenhos tem em cada uma e coloque abaixo:
            frames_idle = 5   # Exemplo: Se Idle.png tiver 6 desenhos, mude para 6
            frames_run = 8    
            frames_jump = 7   

            # --- IDLE ---
            frame_width = player_idle.get_width() // frames_idle
            frame_height = player_idle.get_height()
            for i in range(frames_idle):
                frame = self.get_frame(player_idle, i * frame_width, 0, frame_width, frame_height, scale)
                self.animations['idle'].append(frame)

            # --- RUN ---
            frame_width = player_run.get_width() // frames_run
            frame_height = player_run.get_height()
            for i in range(frames_run):
                frame = self.get_frame(player_run, i * frame_width, 0, frame_width, frame_height, scale)
                self.animations['run'].append(frame)

            # --- JUMP ---
            frame_width = player_jump.get_width() // frames_jump
            frame_height = player_jump.get_height()
            for i in range(frames_jump):
                frame = self.get_frame(player_jump, i * frame_width, 0, frame_width, frame_height, scale)
                self.animations['jump'].append(frame)

        except FileNotFoundError as e:
            print(f"Erro ao carregar imagem: {e}")
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
        if self.direction.y != 0:
            self.status = 'jump' 
        elif self.direction.x != 0:
            self.status = 'run'  
        else:
            self.status = 'idle' 

    def animate(self):
        animation = self.animations[self.status]
        
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
            
        image = animation[int(self.frame_index)]
        
        if self.facing_right:
            self.image = image
        else:
            self.image = pygame.transform.flip(image, True, False) 

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
            
            if self.damage_sound: 
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