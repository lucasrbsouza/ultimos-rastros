import os
import pygame

WATER_IMAGE_PATH = 'assets/watersheet.png'
TILE_IMAGE_PATH = 'assets/Tileset.png'
MEMORY_IMAGE_PATH = 'assets/Rune.png'
ENEMY_FRAMES_PATH = 'assets/enemies/fly/fly_{:02d}.png'
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
    def __init__(self, pos, size):
        super().__init__()

        self._frames_left = []
        i = 1
        while True:
            path = ENEMY_FRAMES_PATH.format(i)
            if not os.path.exists(path):
                break
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (size, size))
            self._frames_left.append(img)
            i += 1
        if not self._frames_left:
            fallback = pygame.Surface((size, size))
            fallback.fill((200, 50, 50))
            self._frames_left.append(fallback)

        self._frames_right = [pygame.transform.flip(f, True, False) for f in self._frames_left]

        self._frame_index = 0.0
        self._anim_speed  = 0.1
        self.image = self._frames_left[0]
        self.rect  = self.image.get_rect(topleft=pos)

        # ── Origem (ponto de spawn — âncora da patrulha) ──────────────
        self.origin_x = pos[0]

        # ── Configurações ──────────────────────────────────────────────
        self.patrol_speed  = 2
        self.chase_speed   = 4
        self.patrol_range  = 120   # pixels para cada lado da origem
        self.detect_range  = 300   # distância para detectar o jogador
        self.lose_range    = 450   # distância para desistir da perseguição
        self.attack_range  = 20    # distância para causar dano (toque)

        # ── Estado ─────────────────────────────────────────────────────
        # 'patrol' → 'chase' → volta p/ 'patrol' se perder o jogador
        self.state     = 'patrol'
        self.direction = -1        # 1 = direita, -1 = esquerda

        # ── Patrulha ───────────────────────────────────────────────────
        self.patrol_distance = 0

        # ── Referência ao jogador (injetada pelo Level) ────────────────
        self.player_ref = None     # Level faz: enemy.player_ref = player_sprite

        # ── Vida ───────────────────────────────────────────────────────
        self.health = 3
        self._hurt_time = 0          # ms do último dano recebido
        self._hurt_duration = 300    # ms piscando após levar dano

        # ── Confusão (brado) ───────────────────────────────────────────
        self._confused_until   = 0
        self._confused_targets = []

    def confuse(self, all_affected):
        """Entra em estado confuso: ataca outros inimigos próximos por 5 segundos."""
        self.state = 'confused'
        self._confused_until = pygame.time.get_ticks() + 5000
        self._confused_targets = [e for e in all_affected if e is not self]

    def take_damage(self, amount=1):
        """Recebe dano e retorna True se morreu."""
        self.health -= amount
        self._hurt_time = pygame.time.get_ticks()
        if self.health <= 0:
            self.kill()
            return True
        return False

    # ── helpers ─────────────────────────────────────────────────────────
    def _dist_to_player(self):
        if self.player_ref is None:
            return float('inf')
        return abs(self.player_ref.rect.centerx - self.rect.centerx)

    def _face(self, direction):
        self.direction = direction

    # ── estados ─────────────────────────────────────────────────────────
    def _patrol(self):
        self.rect.x += self.patrol_speed * self.direction
        self.patrol_distance += self.patrol_speed

        if self.patrol_distance >= self.patrol_range:
            self._face(self.direction * -1)
            self.patrol_distance = 0

        # Detectou o jogador → perseguir
        if self._dist_to_player() <= self.detect_range:
            self.state = 'chase'
            self.patrol_distance = 0

    def _chase(self):
        if self.player_ref is None:
            self.state = 'patrol'
            return

        dist = self._dist_to_player()

        # Perdeu o jogador → volta a patrulhar
        if dist > self.lose_range:
            self.state = 'patrol'
            return

        # Move em direção ao jogador
        dx = self.player_ref.rect.centerx - self.rect.centerx
        self._face(1 if dx > 0 else -1)

        # Só se move se não está no alcance de ataque
        if dist > self.attack_range:
            self.rect.x += self.chase_speed * self.direction

    # ── update ──────────────────────────────────────────────────────────
    def update(self, x_shift):
        now = pygame.time.get_ticks()

        # câmera
        self.rect.x    += x_shift
        self.origin_x  += x_shift   # ancora junto com o mundo

        # Estado confuso: persegue outros inimigos, não o player
        if self.state == 'confused':
            if now >= self._confused_until:
                self.state = 'patrol'
            else:
                if self._confused_targets:
                    target = self._confused_targets[0]
                    if target.alive():
                        dx = target.rect.centerx - self.rect.centerx
                        self.direction = 1 if dx > 0 else -1
                        self.rect.x += self.direction * self.chase_speed
                self._frame_index = (self._frame_index + self._anim_speed) % len(self._frames_left)
                frames = self._frames_right if self.direction == 1 else self._frames_left
                self.image = frames[int(self._frame_index)]
                if now - self._hurt_time < self._hurt_duration:
                    self.image.set_alpha(80 if (now // 80) % 2 == 0 else 255)
                else:
                    self.image.set_alpha(255)
                return

        if self.state == 'patrol':
            self._patrol()
        elif self.state == 'chase':
            self._chase()

        # Avança animação
        self._frame_index = (self._frame_index + self._anim_speed) % len(self._frames_left)
        frames = self._frames_right if self.direction == 1 else self._frames_left
        self.image = frames[int(self._frame_index)]

        # Pisca enquanto está machucado
        now = pygame.time.get_ticks()
        if now - self._hurt_time < self._hurt_duration:
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