import pygame

WATER_IMAGE_PATH = 'assets/watersheet.png'
TILE_IMAGE_PATH = 'assets/Tileset.png'
MEMORY_IMAGE_PATH = 'assets/Rune.png'
ENEMY_IMAGE_PATH = 'assets/enemy.svg'
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
        self.image = pygame.image.load(GOAL_IMAGE_PATH).convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift

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