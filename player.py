import pygame
from settings import STAGE_THRESHOLDS

PLAYER_IDLE_PATH   = 'assets/player_spritesheet/Idle.png'
PLAYER_WALK_PATH   = 'assets/player_spritesheet/Walk.png'
PLAYER_RUN_PATH    = 'assets/player_spritesheet/Run.png'
PLAYER_JUMP_PATH   = 'assets/player_spritesheet/Jump.png'
PLAYER_ATTACK_PATH = 'assets/player_spritesheet/Attack_1.png'
PLAYER_HURT_PATH   = 'assets/player_spritesheet/Hurt.png'
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

        self.on_ground = False

        # Escada
        self.on_ladder     = False
        self.ladder_speed  = 4

        # Coyote time — frames que ainda pode pular após sair da plataforma
        self.coyote_time = 6           # quantidade de frames de graça
        self.coyote_timer = 0          # contador regressivo

        # Buffer de pulo — frames que o jogo "lembra" que você quis pular
        self.jump_buffer_time = 10     # quantidade de frames do buffer
        self.jump_buffer_timer = 0     # contador regressivo

        # --- Double-tap para correr ---
        self._last_tap_key  = None   # qual tecla foi pressionada por último
        self._last_tap_time = 0      # momento do último tap
        self._double_tap_window = 300  # ms entre os dois taps
        self.is_running = False

        # Velocidade atual — usada para acelerar gradualmente
        self.current_speed = 5      # começa na velocidade de caminhada
        self.walk_speed = 5         # velocidade ao andar
        self.run_speed = 9          # velocidade ao correr

        # Tolerância para não cancelar corrida ao soltar brevemente
        self.run_release_buffer = 8    # frames de graça ao soltar a tecla
        self.run_release_timer = 0     # contador regressivo
            
        # 3. Status e Direção
        self.status = 'idle'
        self.facing_right = True

        # 4. Status do Jogador
        self.max_health = 5
        self.current_health = 5
        self.memories = 0
        self.is_invincible = False

        # Progressão de habilidades
        self.stage = 'rastro_confuso'
        self.can_shoot = False
        self.brado_ready = False
        self._brado_cooldown = 8000
        self._last_brado_time = 0
        self.pending_brado = False
        self.invincibility_duration = 1000 
        self.hurt_time = 0

        # 5. Poder de fogo
        self._fire_cooldown = 400   # ms entre disparos
        self._last_fire_time = 0
        self.pending_fire = False   # sinaliza ao Level para criar o projétil

        # Animação de ataque
        self.is_attacking = False

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
        self.animations = {'idle': [], 'walk': [], 'run': [], 'jump': [], 'attack': [], 'hurt': []}
        scale = 0.80

        try:
            player_idle   = pygame.image.load(PLAYER_IDLE_PATH).convert_alpha()
            player_walk   = pygame.image.load(PLAYER_WALK_PATH).convert_alpha()
            player_run    = pygame.image.load(PLAYER_RUN_PATH).convert_alpha()
            player_jump   = pygame.image.load(PLAYER_JUMP_PATH).convert_alpha()
            player_attack = pygame.image.load(PLAYER_ATTACK_PATH).convert_alpha()
            player_hurt   = pygame.image.load(PLAYER_HURT_PATH).convert_alpha()

            frames_idle   = 5
            frames_walk   = 8
            frames_run    = 8
            frames_jump   = 7
            frames_attack = 5
            frames_hurt   = 2

            for sheet, key, frames in [
                (player_idle,   'idle',   frames_idle),
                (player_walk,   'walk',   frames_walk),
                (player_run,    'run',    frames_run),
                (player_jump,   'jump',   frames_jump),
                (player_attack, 'attack', frames_attack),
                (player_hurt,   'hurt',   frames_hurt),
            ]:
                fw = sheet.get_width() // frames
                fh = sheet.get_height()
                for i in range(frames):
                    self.animations[key].append(
                        self.get_frame(sheet, i * fw, 0, fw, fh, scale)
                    )

        except FileNotFoundError as e:
            print(f"Erro ao carregar imagem: {e}")
            fallback = pygame.Surface((32, 64))
            fallback.fill((255, 50, 50))
            for key in self.animations:
                self.animations[key].append(fallback)

        # Pré-gera todos os frames espelhados (esquerda) de uma vez
        self.animations_flipped = {}
        for key, frames in self.animations.items():
            self.animations_flipped[key] = [
                pygame.transform.flip(f, True, False) for f in frames
            ]

    def get_input(self):
        keys = pygame.key.get_pressed()

        # Knockback ativo — amortece e bloqueia input
        if self.is_invincible:
            self.direction.x *= 0.85
            return

        # Movimento horizontal
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            self.facing_right = False
        else:
            self.direction.x = 0

        # Movimento vertical na escada
        if self.on_ladder:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.direction.y = -self.ladder_speed
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.direction.y = self.ladder_speed
            else:
                self.direction.y = 0
            return   # não processa pulo enquanto estiver na escada

        # Pulo — registra intenção no buffer
        if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
            self.jump_buffer_timer = self.jump_buffer_time  # ← guarda a intenção
    
    def get_brado_cooldown_ratio(self):
        """Retorna o quanto do cooldown já passou: 0.0 = recém usado, 1.0 = pronto."""
        if not self.brado_ready:
            return None
        elapsed = pygame.time.get_ticks() - self._last_brado_time
        return min(elapsed / self._brado_cooldown, 1.0)

    def update_stage(self):
        """Reavalia o estágio com base nas memórias atuais."""
        m = self.memories

        if m >= STAGE_THRESHOLDS['guardiao_desperto']:
            if self.stage != 'guardiao_desperto':
                self.stage = 'guardiao_desperto'
                self.max_health += 2
                self.current_health = min(self.current_health + 2, self.max_health)
            self.can_shoot = True
            self.brado_ready = True

        elif m >= STAGE_THRESHOLDS['sussurro_mata']:
            self.stage = 'sussurro_mata'
            self.can_shoot = True
            self.brado_ready = True

        elif m >= STAGE_THRESHOLDS['passos_invisiveis']:
            self.stage = 'passos_invisiveis'
            self.can_shoot = True

        else:
            self.stage = 'rastro_confuso'

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            now = pygame.time.get_ticks()

            # Disparo da Fire Arrow — tecla Z
            if event.key == pygame.K_z:
                if self.can_shoot:
                    if now - self._last_fire_time >= self._fire_cooldown:
                        self._last_fire_time = now
                        self.is_attacking = True
                        self.frame_index = 0

            # Brado do Curupira — tecla X
            if event.key == pygame.K_x:
                if self.brado_ready:
                    if now - self._last_brado_time >= self._brado_cooldown:
                        self._last_brado_time = now
                        self.pending_brado = True

            if event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_LEFT, pygame.K_a):
                
                # Mesma direção pressionada dentro da janela? → É double-tap
                mesma_direita = (event.key in (pygame.K_RIGHT, pygame.K_d) and
                                self._last_tap_key in (pygame.K_RIGHT, pygame.K_d))
                mesma_esquerda = (event.key in (pygame.K_LEFT, pygame.K_a) and
                                self._last_tap_key in (pygame.K_LEFT, pygame.K_a))

                if (mesma_direita or mesma_esquerda) and (now - self._last_tap_time <= self._double_tap_window):
                    self.is_running = True
                    self.run_release_timer = self.run_release_buffer  # renova ao ativar

                self._last_tap_time = now
                self._last_tap_key = event.key

        # Soltou a tecla — inicia o buffer antes de cancelar
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_LEFT, pygame.K_a):
                self.run_release_timer = self.run_release_buffer  # não cancela ainda

    def get_status(self):
        if self.is_invincible:
            self.status = 'hurt'
        elif self.is_attacking:
            self.status = 'attack'
        elif self.on_ladder and self.direction.y != 0:
            self.status = 'jump'
        elif not self.on_ground:
            self.status = 'jump'
        elif self.is_running and self.direction.x != 0:
            self.status = 'run'    # ← só ativa com double-tap
        elif self.direction.x != 0:
            self.status = 'walk'   # ← novo status para andar devagar
        else:
            self.status = 'idle' 

    def animate(self):
        animation = self.animations[self.status]

        if self.frame_index >= len(animation):
            self.frame_index = 0

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.is_attacking = False
                self.pending_fire = True
            if self.status != 'hurt':
                self.frame_index = 0
            else:
                self.frame_index = len(animation) - 1

        idx = int(self.frame_index)

        if self.facing_right:
            self.image = self.animations[self.status][idx]
        else:
            self.image = self.animations_flipped[self.status][idx]

    def apply_gravity(self):
        if self.on_ladder:
            self.rect.y += self.direction.y
            return
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed
        if self.jump_sound:
            self.jump_sound.play()

    def take_damage(self, amount, knockback_direction=0):
        if not self.is_invincible:
            self.current_health -= amount
            self.is_invincible = True
            self.hurt_time = pygame.time.get_ticks()
            
            # Aplica o impulso de knockback
            self.direction.x = knockback_direction * 3  # empurra horizontalmente
            self.direction.y = -5                        # pequeno salto para cima
            
            if self.damage_sound: 
                self.damage_sound.play()

    def invincibility_timer(self):
        if self.is_invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time >= self.invincibility_duration:
                self.is_invincible = False

    def blink(self):
        """Retorna True nos frames em que o player deve ficar invisível."""
        if self.is_invincible:
            # pygame.time.get_ticks() retorna ms — divide para controlar velocidade
            # % 200 cria um ciclo de 200ms, metade visível metade invisível
            return pygame.time.get_ticks() % 200 < 100
        return False

    def update_run(self):
        """Gerencia o cancelamento suave da corrida e a aceleração gradual."""

        # Desconta o buffer de cancelamento
        if self.run_release_timer > 0:
            self.run_release_timer -= 1
        elif self.direction.x == 0:
            # Só cancela a corrida quando o buffer esgotou E parou de mover
            self.is_running = False

        # Aceleração gradual — interpola entre walk e run speed
        if self.is_running and self.direction.x != 0:
            # Acelera progressivamente até run_speed
            self.current_speed = min(self.current_speed + 0.4, self.run_speed)
        else:
            # Desacelera progressivamente até walk_speed
            self.current_speed = max(self.current_speed - 0.4, self.walk_speed)

    def update_jump_timers(self):
        """Gerencia coyote time, jump buffer e executa pulo quando apropriado."""
        # Não processa pulo durante knockback
        if self.is_invincible:
            self.jump_buffer_timer = 0  # descarta intenção acumulada
            return

        # Coyote timer: conta enquanto estiver no ar após sair de plataforma
        if self.on_ground:
            self.coyote_timer = self.coyote_time  # renova enquanto estiver no chão
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1               # esgota após sair da borda

        # Buffer timer: conta regressivamente após apertar pulo
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1

        # Executa o pulo se há intenção no buffer E ainda pode pular
        pode_pular = self.on_ground or self.coyote_timer > 0
        if self.jump_buffer_timer > 0 and pode_pular:
            self.jump()
            self.jump_buffer_timer = 0  # consome o buffer
            self.coyote_timer = 0       # consome o coyote time

    def update(self):
        self.get_input()
        self.update_jump_timers()
        self.update_run()
        self.get_status()
        self.animate() 
        self.invincibility_timer()