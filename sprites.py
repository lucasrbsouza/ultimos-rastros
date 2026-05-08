import os
import math
import pygame

WATER_IMAGE_PATH = 'assets/watersheet.png'
TILE_IMAGE_PATH = 'assets/Tileset.png'
MEMORY_IMAGE_PATH = 'assets/Rune.png'
ENEMY_FRAMES_PATH = 'assets/enemies/fly/fly_{:02d}.png'

# ── Enemy configs ────────────────────────────────────────────────────────────
# ai: 'patrol' = bounce only  |  'advanced' = full state machine
ENEMY_CONFIGS = {
    # ── Simple patrol (fly + slimes) ─────────────────────────────────────────
    'fly':          {'ai': 'patrol', 'health': 2, 'patrol_speed': 2, 'patrol_range': 120, 'folder': 'fly'},
    'slime_normal': {'ai': 'patrol', 'health': 1, 'patrol_speed': 1, 'patrol_range': 100, 'folder': 'slime_normal'},
    'slime_fire':   {'ai': 'patrol', 'health': 2, 'patrol_speed': 2, 'patrol_range': 100, 'folder': 'slime_fire'},
    'slime_spike':  {'ai': 'patrol', 'health': 1, 'patrol_speed': 1, 'patrol_range': 100, 'folder': 'slime_spike'},
    # ── Advanced AI ──────────────────────────────────────────────────────────
    'plent': {
        'ai': 'advanced', 'health': 6, 'patrol_speed': 1, 'chase_speed': 3,
        'patrol_range': 150, 'detect_range': 260, 'lose_range': 400,
        'melee_range': 90,  'melee_damage': 1,  'attack_cooldown': 1500,
        'ranged_range': 220,'ranged_damage': 2,  'ranged_cooldown': 3500,
        'folder': 'Plent',
        'anims': {'walk':'Walk.png','idle':'Idle.png',
                  'atk_m1':'Attack_1.png','atk_m2':'Attack_2.png','atk_m3':'Attack_3.png',
                  'atk_r':'Cloud_posion.png','hurt':'Hurt.png','dead':'Dead.png'},
    },
    'skeleton': {
        'ai': 'advanced', 'health': 5, 'patrol_speed': 2, 'chase_speed': 4,
        'patrol_range': 130, 'detect_range': 280, 'lose_range': 420,
        'melee_range': 85,  'melee_damage': 1,  'attack_cooldown': 1200,
        'ranged_range': None,'ranged_damage': 0,
        'folder': 'Skeleton',
        'anims': {'walk':'Walk.png','run':'Run.png','idle':'Idle.png',
                  'atk_m1':'Attack_1.png','atk_m2':'Attack_2.png','atk_m3':'Attack_3.png',
                  'atk_r':'Special_attack.png','hurt':'Hurt.png','dead':'Dead.png'},
    },
    'orc_warrior': {
        'ai': 'advanced', 'health': 4, 'patrol_speed': 2, 'chase_speed': 4,
        'patrol_range': 100, 'detect_range': 250, 'lose_range': 380,
        'melee_range': 90,  'melee_damage': 1,  'attack_cooldown': 1400,
        'ranged_range': None,'ranged_damage': 0,
        'folder': 'Orc_Warrior',
        'anims': {'walk':'Walk.png','run':'Run.png','idle':'Idle.png',
                  'atk_m1':'Attack_1.png','atk_m2':'Attack_2.png','atk_m3':'Attack_3.png',
                  'atk_r':'Run+Attack.png','hurt':'Hurt.png','dead':'Dead.png'},
    },
    'orc_berserk': {
        'ai': 'advanced', 'health': 5, 'patrol_speed': 3, 'chase_speed': 5,
        'patrol_range': 120, 'detect_range': 270, 'lose_range': 400,
        'melee_range': 90,  'melee_damage': 1,  'attack_cooldown': 1000,
        'ranged_range': None,'ranged_damage': 0,
        'folder': 'Orc_Berserk',
        'anims': {'walk':'Walk.png','run':'Run.png','idle':'Idle.png',
                  'atk_m1':'Attack_1.png','atk_m2':'Attack_2.png','atk_m3':'Attack_3.png',
                  'atk_r':'Run+Attack.png','hurt':'Hurt.png','dead':'Dead.png'},
    },
    'orc_shaman': {
        'ai': 'advanced', 'health': 8, 'patrol_speed': 2, 'chase_speed': 3,
        'patrol_range': 160, 'detect_range': 320, 'lose_range': 480,
        'melee_range': 80,  'melee_damage': 1,  'attack_cooldown': 1800,
        'ranged_range': 250,'ranged_damage': 2,  'ranged_cooldown': 4000,
        'folder': 'Orc_Shaman',
        'anims': {'walk':'Walk.png','run':'Run.png','idle':'Idle.png',
                  'atk_m1':'Attack_1.png','atk_m2':'Attack_2.png',
                  'atk_r':'Magic_1.png','atk_r2':'Magic_2.png',
                  'hurt':'Hurt.png','dead':'Dead.png'},
    },
}

# ── Sprite loading helpers ───────────────────────────────────────────────────

def _load_enemy_sheet(folder, sheet, size):
    """Carrega spritesheet horizontal onde frame_w == frame_h (quadrado)."""
    path = f'assets/enemies/{folder}/{sheet}'
    try:
        img = pygame.image.load(path).convert_alpha()
        fh = img.get_height()
        n  = img.get_width() // fh
        frames = []
        for i in range(n):
            frame = img.subsurface((i * fh, 0, fh, fh))
            frames.append(pygame.transform.scale(frame, (size, size)))
        return frames
    except Exception:
        s = pygame.Surface((size, size)); s.fill((200, 50, 50)); return [s]

def _load_folder_frames(folder, size):
    """Carrega todos os PNGs de uma pasta (fly/slimes — frames individuais)."""
    import glob
    paths = sorted(glob.glob(f'assets/enemies/{folder}/*.png'))
    frames = []
    for p in paths:
        try:
            img = pygame.image.load(p).convert_alpha()
            frames.append(pygame.transform.scale(img, (size, size)))
        except Exception:
            pass
    if not frames:
        s = pygame.Surface((size, size)); s.fill((200, 50, 50)); frames.append(s)
    return frames

def _make_lr(raw_frames):
    """Retorna (left, right). Raw encara direita → right=original, left=flip."""
    right = raw_frames
    left  = [pygame.transform.flip(f, True, False) for f in raw_frames]
    return left, right

GOAL_IMAGE_PATH = 'assets/goal.png'

class BaseTile(pygame.sprite.Sprite):
    """Classe base contendo a lógica comum para todos os blocos."""
    def __init__(self, pos, size, coluna, linha):
        super().__init__()
        
        # Tamanho original de cada bloco na folha de desenho (pixel art)
        # Para o Tileset.png enviado, 16 pixels é o padrão.
        self.original_grid_size = 16 
        
        self.image = self.extract_tile(size, coluna, linha)
        self.rect = self.image.get_rect(topleft=pos)

    def extract_tile(self, target_size, coluna, linha):
        """Fatia uma imagem específica da folha de tileset."""
        try:
            sheet = pygame.image.load(TILE_IMAGE_PATH).convert_alpha()
            
            # Cria superfície vazia transparente
            tile_surface = pygame.Surface((self.original_grid_size, self.original_grid_size), pygame.SRCALPHA)
            
            # Recorta a parte específica
            # x_no_desenho = coluna * tamanho_original
            # y_no_desenho = linha * tamanho_original
            area_de_corte = (coluna * self.original_grid_size, linha * self.original_grid_size, self.original_grid_size, self.original_grid_size)
            tile_surface.blit(sheet, (0, 0), area_de_corte)
            
            # Redimensiona para o tamanho real do jogo (60px)
            return pygame.transform.scale(tile_surface, (target_size, target_size))
            
        except Exception as e:
            print(f"Erro ao carregar tile: {e}")
            fallback = pygame.Surface((target_size, target_size))
            fallback.fill((100, 80, 50)) # Marrom escuro como fallback
            return fallback

    def update(self, x_shift):
        self.rect.x += x_shift



class Tile(BaseTile):
    """O bloco de superfície (Grama). Usado pelo caractere 'X'."""
    def __init__(self, pos, size):
        # Coordenadas do bloco de grama no seu desenho (Coluna 1, Linha 0)
        super().__init__(pos, size, coluna=1, linha=0)

class Dirt(BaseTile):
    """O bloco de preenchimento (Terra). Usado pelo caractere 'D'."""
    def __init__(self, pos, size):
        # Coordenadas do bloco de terra genérica no seu desenho (Coluna 1, Linha 2)
        # Se preferir um bloco de terra mais escuro, tente coluna=1, linha=1
        super().__init__(pos, size, coluna=1, linha=2)

class Water(BaseTile):
    """O bloco de preenchimento (Terra). Usado pelo caractere 'D'."""
    def __init__(self, pos, size):
        # Coordenadas do bloco de terra genérica no seu desenho (Coluna 1, Linha 2)
        # Se preferir um bloco de terra mais escuro, tente coluna=1, linha=1
        super().__init__(pos, size, coluna=10, linha=5)

class Memory(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        
        # ── CORREÇÃO: guarda a posição original do mapa (nunca muda com câmera) ──
        self.map_pos = (pos[0], pos[1])
        
        self.frames = []
        self.frame_index = 0
        self.animation_speed = 0.15 # Velocidade da animação (ajuste a gosto)
        
        try:
            # Carrega a imagem da Runa
            sheet = pygame.image.load(MEMORY_IMAGE_PATH).convert_alpha()
            
            # ATENÇÃO: Defina aqui quantos 'quadros' a sua animação tem.
            # Se a Rune.png tiver 4 desenhos lado a lado, coloque 4.
            num_frames = 4 
            
            frame_width = sheet.get_width() // num_frames
            frame_height = sheet.get_height()
            
            # Recorta cada quadro do spritesheet
            for i in range(num_frames):
                frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame_surface.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                
                # Redimensiona para o tamanho do jogo
                frame_surface = pygame.transform.scale(frame_surface, (size // 2, size // 2))
                self.frames.append(frame_surface)
                
            self.image = self.frames[self.frame_index]
            
        except FileNotFoundError:
            # Fallback caso a imagem falte
            fallback_image = pygame.Surface((size // 2, size // 2))
            fallback_image.fill((255, 220, 50))
            self.frames = [fallback_image]
            self.image = self.frames[0]
            
        # Posicionamento
        center_x = pos[0] + (size // 2)
        center_y = pos[1] + (size // 2)
        self.rect = self.image.get_rect(center=(center_x, center_y))

    def animate(self):
        """Alterna os quadros para criar a animação."""
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
            
        self.image = self.frames[int(self.frame_index)]

    def update(self, x_shift):
        """Atualiza a posição (câmera) e a animação."""
        self.animate() # Roda a animação
        self.rect.x += x_shift # Move com a câmera


class Enemy(pygame.sprite.Sprite):
    """
    ai='patrol'  → fly/slimes: bounca na patrol_range, sem detecção.
    ai='advanced'→ Plent/Skeleton/Orcs: patrol→chase→atk_melee/atk_ranged→dying.
    """

    def __init__(self, pos, size, enemy_type='fly'):
        super().__init__()
        cfg = ENEMY_CONFIGS.get(enemy_type, ENEMY_CONFIGS['fly'])
        self._ai_type    = cfg['ai']
        self._enemy_type = enemy_type

        # ── Carregar animações ─────────────────────────────────────────
        # _anims: { nome: (frames_left, frames_right) }
        self._anims = {}
        if self._ai_type == 'patrol':
            raw = _load_folder_frames(cfg['folder'], size)
            # fly/slimes: frames encaram esquerda por padrão (fly_01 aponta esq)
            # slimes também encaram esquerda → left=original, right=flip
            self._anims['walk'] = (raw, [pygame.transform.flip(f, True, False) for f in raw])
        else:
            for anim_name, sheet_file in cfg['anims'].items():
                raw = _load_enemy_sheet(cfg['folder'], sheet_file, size)
                self._anims[anim_name] = _make_lr(raw)  # right=original(encar dir), left=flip

        self._anim       = 'walk'
        self._frame_idx  = 0.0
        self._anim_speed = 0.12
        self.direction   = -1

        self.image = self._get_frame()
        self.rect  = self.image.get_rect(topleft=pos)
        self.origin_x = pos[0]

        # ── Stats ──────────────────────────────────────────────────────
        self.patrol_speed  = cfg.get('patrol_speed', 2)
        self.chase_speed   = cfg.get('chase_speed', 4)
        self.patrol_range  = cfg.get('patrol_range', 120)
        self.detect_range  = cfg.get('detect_range', 300)
        self.lose_range    = cfg.get('lose_range', 450)
        self._melee_range  = cfg.get('melee_range', 80)
        self._ranged_range = cfg.get('ranged_range', None)
        self._melee_dmg    = cfg.get('melee_damage', 1)
        self._ranged_dmg   = cfg.get('ranged_damage', 2)
        self._atk_cd       = cfg.get('attack_cooldown', 1500)
        self._ratk_cd      = cfg.get('ranged_cooldown', 3500)

        # ── Estado ─────────────────────────────────────────────────────
        self.state           = 'patrol'
        self.patrol_distance = 0
        self.is_attacking    = False
        self.current_attack_damage = 0
        self.current_attack_range  = 0
        self._last_atk_time  = 0
        self._last_ratk_time = 0

        # ── Vida ───────────────────────────────────────────────────────
        self.health        = cfg.get('health', 3)
        self._hurt_time    = 0
        self._hurt_dur     = 300
        self._dying        = False

        # ── Compat ─────────────────────────────────────────────────────
        self._last_attack_time = 0   # usado por level.py check_damage (contato)
        self._attack_cooldown  = self._atk_cd

        # ── Projétil ranged pendente ───────────────────────────────────
        self.pending_ranged_proj = False

        # ── Física ─────────────────────────────────────────────────────
        self._has_gravity = (enemy_type != 'fly')
        self.velocity_y   = 0.0
        self.gravity      = 0.8
        self.on_ground    = False

        # ── Refs ───────────────────────────────────────────────────────
        self.player_ref  = None
        self.enemies_ref = None
        self._confused_until   = 0
        self._confused_targets = []

    # ── Helpers ─────────────────────────────────────────────────────────

    def _get_frame(self):
        left_f, right_f = self._anims.get(self._anim, list(self._anims.values())[0])
        frames = right_f if self.direction == 1 else left_f
        return frames[int(self._frame_idx) % len(frames)]

    def _advance_loop(self):
        left_f, _ = self._anims.get(self._anim, list(self._anims.values())[0])
        n = len(left_f)
        self._frame_idx = (self._frame_idx + self._anim_speed) % n

    def _advance_once(self):
        """Avança animação uma vez. Retorna True ao completar o ciclo."""
        left_f, _ = self._anims.get(self._anim, list(self._anims.values())[0])
        n = len(left_f)
        self._frame_idx += self._anim_speed
        if self._frame_idx >= n:
            self._frame_idx = float(n - 1)
            return True
        return False

    def _set_anim(self, name):
        if self._anim != name:
            self._anim = name
            self._frame_idx = 0.0

    def _dist_to_player(self):
        if self.player_ref is None:
            return float('inf')
        return abs(self.player_ref.rect.centerx - self.rect.centerx)

    def _face_player(self):
        if self.player_ref:
            dx = self.player_ref.rect.centerx - self.rect.centerx
            self.direction = 1 if dx > 0 else -1

    # ── Público ─────────────────────────────────────────────────────────

    def confuse(self, all_affected):
        self.state = 'confused'
        self._confused_until   = pygame.time.get_ticks() + 5000
        self._confused_targets = [e for e in all_affected if e is not self]

    def take_damage(self, amount=1):
        self.health -= amount
        self._hurt_time = pygame.time.get_ticks()
        if self.health <= 0:
            if self._ai_type == 'advanced' and 'dead' in self._anims:
                self._dying = True
                self._set_anim('dead')
                self._frame_idx = 0.0
                self.is_attacking = False
            else:
                self.kill()
            return True
        if self._ai_type == 'advanced' and 'hurt' in self._anims:
            # Pisca — sem estado separado, só flash via _hurt_time
            pass
        return False

    def _separate_from_others(self):
        if self.enemies_ref is None:
            return
        for other in self.enemies_ref:
            if other is self:
                continue
            if self.rect.colliderect(other.rect):
                if self.rect.centerx <= other.rect.centerx:
                    self.rect.x -= 2
                else:
                    self.rect.x += 2

    # ── Lógica patrol (fly/slimes) ───────────────────────────────────────

    def _update_patrol(self):
        self.rect.x          += self.patrol_speed * self.direction
        self.patrol_distance += self.patrol_speed
        if self.patrol_distance >= self.patrol_range:
            self.direction       = -self.direction
            self.patrol_distance = 0
        self._set_anim('walk')
        self._advance_loop()

    # ── Lógica advanced (Plent/Skeleton/Orcs) ───────────────────────────

    def _enter_atk_melee(self, now):
        import random
        melee_anims = [k for k in self._anims if k.startswith('atk_m')]
        self._set_anim(random.choice(melee_anims) if melee_anims else 'atk_m1')
        self.state                = 'atk_melee'
        self.is_attacking         = True
        self.current_attack_damage = self._melee_dmg
        self.current_attack_range  = self._melee_range
        self._last_atk_time        = now

    def _enter_atk_ranged(self, now):
        ranged_anims = [k for k in self._anims if k.startswith('atk_r')]
        self._set_anim(ranged_anims[0] if ranged_anims else 'atk_r')
        self.state           = 'atk_ranged'
        self._last_ratk_time = now
        if self._enemy_type == 'plent':
            # dano via projétil CloudPoison — sem range check
            self.is_attacking          = False
            self.current_attack_damage = 0
            self.current_attack_range  = 0
            self.pending_ranged_proj   = True
        else:
            self.is_attacking          = True
            self.current_attack_damage = self._ranged_dmg
            self.current_attack_range  = self._ranged_range or self._melee_range

    def _update_advanced(self, now):
        dist = self._dist_to_player()

        # ── Moribundo ─────────────────────────────────────────────────
        if self._dying:
            done = self._advance_once()
            if done:
                self.kill()
            return

        # ── Animação hurt (flash) ──────────────────────────────────────
        # Não troca estado, só pisca via _hurt_time

        # ── Ataque corpo-a-corpo ───────────────────────────────────────
        if self.state == 'atk_melee':
            self._face_player()
            done = self._advance_once()
            if done:
                self.is_attacking = False
                self.state = 'chase' if dist <= self.lose_range else 'patrol'
            return

        # ── Ataque ranged ──────────────────────────────────────────────
        if self.state == 'atk_ranged':
            self._face_player()
            done = self._advance_once()
            if done:
                self.is_attacking = False
                self.state = 'chase' if dist <= self.lose_range else 'patrol'
            return

        # ── Confuso ────────────────────────────────────────────────────
        if self.state == 'confused':
            if now >= self._confused_until:
                self.state = 'patrol'
            else:
                if self._confused_targets:
                    t = self._confused_targets[0]
                    if t.alive():
                        dx = t.rect.centerx - self.rect.centerx
                        self.direction = 1 if dx > 0 else -1
                        self.rect.x += self.direction * self.chase_speed
                self._set_anim('walk')
                self._advance_loop()
                return

        # ── Patrulha ───────────────────────────────────────────────────
        if self.state == 'patrol':
            self.rect.x          += self.patrol_speed * self.direction
            self.patrol_distance += self.patrol_speed
            if self.patrol_distance >= self.patrol_range:
                self.direction       = -self.direction
                self.patrol_distance = 0
            self._set_anim('walk')
            if dist <= self.detect_range:
                self.state = 'chase'
                self.patrol_distance = 0
            return

        # ── Perseguição ────────────────────────────────────────────────
        if self.state == 'chase':
            if dist > self.lose_range:
                self.state = 'patrol'
                return
            self._face_player()
            run_anim = 'run' if 'run' in self._anims else 'walk'
            self._set_anim(run_anim)

            # Decide atacar
            can_melee  = (now - self._last_atk_time  >= self._atk_cd)
            can_ranged = (self._ranged_range is not None and
                          now - self._last_ratk_time >= self._ratk_cd)

            if dist <= self._melee_range and can_melee:
                self._enter_atk_melee(now)
                return
            if self._ranged_range and dist <= self._ranged_range and dist > self._melee_range and can_ranged:
                self._enter_atk_ranged(now)
                return

            # Move em direção ao player
            if dist > self._melee_range:
                self.rect.x += self.chase_speed * self.direction

        self._advance_loop()
        self._separate_from_others()

    def apply_gravity(self):
        """Aplica gravidade verticalmente (chamado externamente por level.py)."""
        if not self._has_gravity:
            return
        self.velocity_y += self.gravity
        self.rect.y     += int(self.velocity_y)

    # ── update ──────────────────────────────────────────────────────────

    def update(self, x_shift):
        now = pygame.time.get_ticks()

        self.rect.x   += x_shift
        self.origin_x += x_shift

        # Voz da Floresta — congela
        if self.player_ref and self.player_ref.voz_floresta_active:
            self._set_anim('walk')
            self._advance_loop()
            self.image = self._get_frame()
            self.image.set_alpha(180)
            return

        if self._ai_type == 'patrol':
            self._update_patrol()
        else:
            self._update_advanced(now)

        self.image = self._get_frame()

        # Flash ao levar dano
        if now - self._hurt_time < self._hurt_dur:
            self.image.set_alpha(80 if (now // 80) % 2 == 0 else 255)
        else:
            self.image.set_alpha(255)

class Goal(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.image = pygame.image.load(GOAL_IMAGE_PATH).convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift

class FireArrow(pygame.sprite.Sprite):
    """Projétil de fogo disparado pelo jogador."""
    FRAMES_PATH = 'assets/player_power/Fire Arrow/PNG/Fire Arrow_Frame_{:02d}.png'
    
    SPEED = 10
    SIZE = (48, 48)

    def __init__(self, pos, facing_right):
        super().__init__()

        self.frames = []
        for i in range(1, 9):
            try:
                img = pygame.image.load(self.FRAMES_PATH.format(i)).convert_alpha()
                img = pygame.transform.scale(img, self.SIZE)
                self.frames.append(img)
            except FileNotFoundError:
                fallback = pygame.Surface(self.SIZE, pygame.SRCALPHA)
                fallback.fill((255, 140, 0))
                self.frames.append(fallback)

        self.facing_right = facing_right
        if facing_right:
            self.frames = [pygame.transform.flip(f, True, False) for f in self.frames]

        self.frame_index = 0
        self.animation_speed = 0.3
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=pos)
        self.velocity = self.SPEED if facing_right else -self.SPEED

    def update(self, x_shift=0):
        self.rect.x += self.velocity + x_shift

        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

        # Remove se sair da tela (margem generosa)
        if self.rect.right < -100 or self.rect.left > 1380:
            self.kill()


class CloudPoison(pygame.sprite.Sprite):
    """Projétil de nuvem venenosa do Plent — viaja horizontalmente."""
    SPEED    = 5
    SIZE     = 60
    MAX_DIST = 350
    DAMAGE   = 2

    def __init__(self, pos, facing_right):
        super().__init__()
        raw = _load_enemy_sheet('Plent', 'Cloud_posion.png', self.SIZE)
        if facing_right:
            self.frames = [pygame.transform.flip(f, True, False) for f in raw]
        else:
            self.frames = raw
        self.frame_index = 0.0
        self.anim_speed  = 0.15
        self.image       = self.frames[0]
        self.rect        = self.image.get_rect(center=pos)
        self.velocity    = self.SPEED if facing_right else -self.SPEED
        self._traveled   = 0

    def update(self, x_shift=0):
        self.rect.x    += self.velocity + x_shift
        self._traveled += abs(self.velocity)
        self.frame_index = (self.frame_index + self.anim_speed) % len(self.frames)
        self.image       = self.frames[int(self.frame_index)]
        if self._traveled >= self.MAX_DIST or self.rect.right < -100 or self.rect.left > 1380:
            self.kill()


class StaticObject(pygame.sprite.Sprite):
    """Classe genérica para objetos de cenário estáticos (árvores, pedras, etc)."""
    def __init__(self, pos, folder_name, image_name, tile_size):
        super().__init__()
        
        # Constrói o caminho dinamicamente
        path = f'assets/objetos/{folder_name}/{image_name}'
        
        try:
            self.image = pygame.image.load(path).convert_alpha()
            
            # Se a pixel art for muito pequena, podemos dobrar o tamanho dela.
            # Se as suas árvores já estiverem num tamanho bom, pode remover essa linha abaixo.
            width, height = self.image.get_size()
            self.image = pygame.transform.scale(self.image, (width * 2, height * 2))
            
            # O pulo do gato: alinhamos o fundo da imagem (bottomleft) 
            # com a base do tile onde você colocou a letra no mapa.
            self.rect = self.image.get_rect(bottomleft=(pos[0], pos[1] + tile_size))
            
        except FileNotFoundError:
            print(f"Erro ao carregar objeto: {path}")
            self.image = pygame.Surface((tile_size, tile_size))
            self.image.fill((255, 0, 255)) # Rosa choque para indicar erro
            self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift


class Key(pygame.sprite.Sprite):
    """Chave coletável. Caractere 'K' no mapa."""
    def __init__(self, pos, size):
        super().__init__()
        self.map_pos = (pos[0], pos[1])

        try:
            img = pygame.image.load(KEY_IMAGE_PATH).convert_alpha()
            img = pygame.transform.scale(img, (size // 2, size // 2))
            self.image = img
        except FileNotFoundError:
            surf = pygame.Surface((size // 2, size // 2), pygame.SRCALPHA)
            pygame.draw.polygon(surf, (255, 215, 0), [
                (size // 4, 2), (size // 4 + 6, 8), (size // 4 + 6, size // 2 - 4),
                (size // 4 - 6, size // 2 - 4), (size // 4 - 6, 8)
            ])
            self.image = surf

        center_x = pos[0] + size // 2
        center_y = pos[1] + size // 2
        self.rect = self.image.get_rect(center=(center_x, center_y))

    def update(self, x_shift):
        self.rect.x += x_shift


class LockedDoor(pygame.sprite.Sprite):
    """Porta trancada. Caractere 'L' no mapa. Só abre quando o jogador tiver a chave."""
    def __init__(self, pos, size):
        super().__init__()
        self.is_open = False
        self._size = size

        self._locked_image = self._make_locked(size)
        self._open_image   = self._make_open(size)
        self.image = self._locked_image
        self.rect  = self.image.get_rect(topleft=pos)

    def _make_locked(self, size):
        try:
            img = pygame.image.load(DOOR_IMAGE_PATH).convert_alpha()
            return pygame.transform.scale(img, (size, size))
        except FileNotFoundError:
            surf = pygame.Surface((size, size))
            surf.fill((139, 69, 19))
            pygame.draw.rect(surf, (80, 40, 10), surf.get_rect(), 4)
            pygame.draw.circle(surf, (255, 200, 0), (size // 2, size // 2 - 4), 8, 3)
            pygame.draw.rect(surf, (255, 200, 0), (size // 2 - 6, size // 2 + 2, 12, 10))
            return surf

    def _make_open(self, size):
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill((139, 69, 19, 80))
        pygame.draw.rect(surf, (200, 150, 50, 120), surf.get_rect(), 4)
        return surf

    def open(self):
        """Abre a porta visualmente."""
        self.is_open = True
        self.image = self._open_image

    def update(self, x_shift):
        self.rect.x += x_shift


class Heart(pygame.sprite.Sprite):
    """Coletável de vida. Caractere 'R' no mapa. Recupera 1 HP ao coletar."""
    _SIZE = 36   # tamanho base do coração

    def __init__(self, pos, size):
        super().__init__()
        self.map_pos = (pos[0], pos[1])
        self._tick = 0

        try:
            img = pygame.image.load('assets/heart.png').convert_alpha()
            self._base_img = pygame.transform.scale(img, (self._SIZE, self._SIZE))
        except FileNotFoundError:
            surf = pygame.Surface((self._SIZE, self._SIZE), pygame.SRCALPHA)
            pygame.draw.circle(surf, (220, 30, 60), (self._SIZE // 2, self._SIZE // 2), self._SIZE // 2)
            self._base_img = surf

        self.image = self._base_img
        cx = pos[0] + size // 2
        cy = pos[1] + size // 2
        self.rect = self.image.get_rect(center=(cx, cy))

    def _pulse(self):
        self._tick += 1
        scale = 1.0 + 0.18 * math.sin(self._tick * 0.08)
        new_size = max(4, int(self._SIZE * scale))
        cx, cy = self.rect.center
        self.image = pygame.transform.scale(self._base_img, (new_size, new_size))
        self.rect  = self.image.get_rect(center=(cx, cy))

    def update(self, x_shift):
        self.rect.x += x_shift
        self._pulse()


KEY_IMAGE_PATH   = 'assets/objetos/key.png'
DOOR_IMAGE_PATH  = 'assets/objetos/door.png'
LADDER_IMAGE_PATH = 'assets/objetos/Ladders/'

class Ladder(pygame.sprite.Sprite):
    """Superfície escalável. Usado pelo caractere 'C' no mapa."""
    def __init__(self, pos, size):
        super().__init__()

        path = None
        try:
            arquivos = sorted(f for f in os.listdir(LADDER_IMAGE_PATH)
                              if f.lower().endswith(('.png', '.jpg')))
            if arquivos:
                path = LADDER_IMAGE_PATH + arquivos[0]
        except FileNotFoundError:
            pass

        if path:
            try:
                self.image = pygame.image.load(path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (size, size))
            except Exception:
                self.image = self._fallback(size)
        else:
            self.image = self._fallback(size)

        self.rect = self.image.get_rect(topleft=pos)

    def _fallback(self, size):
        surf = pygame.Surface((size, size))
        surf.fill((139, 90, 43))
        return surf

    def update(self, x_shift):
        self.rect.x += x_shift