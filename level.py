import pygame
from settings import *
from sprites import Tile, Memory
from player import Player
from ui import HUD

LEVEL_MAP = [
    '                                                            ',
    '                                                            ',
    '                                                            ',
    '                   M                                        ',
    '       C          XXX                                       ',
    '                        XXX                        XXX         ',
    '                              XXX                           ',
    '                 XXX                     M                  ',
    'XXXXXXXXX   XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
]

class Level:
    def __init__(self, surface):
        self.display_surface = surface
        
        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.memories = pygame.sprite.Group() # Novo grupo para os coletáveis
        
        self.hud = HUD(self.display_surface) # Instanciando o HUD
        self.world_shift = 0 
        
        self.setup_level(LEVEL_MAP)

    def setup_level(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                
                if cell == 'X':
                    tile = Tile((x, y), TILE_SIZE)
                    self.tiles.add(tile)
                elif cell == 'C':
                    player_sprite = Player((x, y))
                    self.player.add(player_sprite)
                elif cell == 'M':
                    memory_sprite = Memory((x, y), TILE_SIZE)
                    self.memories.add(memory_sprite)

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        margin_left = SCREEN_WIDTH // 4
        margin_right = SCREEN_WIDTH - (SCREEN_WIDTH // 4)

        if player_x < margin_left and direction_x < 0:
            self.world_shift = 5 
            player.speed = 0     
        elif player_x > margin_right and direction_x > 0:
            self.world_shift = -5 
            player.speed = 0      
        else:
            self.world_shift = 0  
            player.speed = 5      

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed
        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0: 
                    player.rect.left = sprite.rect.right
                elif player.direction.x > 0: 
                    player.rect.right = sprite.rect.left

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0: 
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0 
                elif player.direction.y < 0: 
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0

    def check_collectibles(self):
        """Verifica se o jogador encostou em alguma memória."""
        player = self.player.sprite
        # O 'True' no final diz ao Pygame para deletar a memória da tela automaticamente
        collided_memories = pygame.sprite.spritecollide(player, self.memories, True)
        if collided_memories:
            # Aumenta o contador do jogador para cada memória coletada neste frame
            player.memories += len(collided_memories)

    def check_death(self):
        if self.player.sprite.rect.top > SCREEN_HEIGHT:
            return True
        return False

    def run(self):
        self.display_surface.fill((30, 80, 40))
        
        # Desenha o cenário e as memórias
        self.tiles.update(self.world_shift)
        self.tiles.draw(self.display_surface)
        
        self.memories.update(self.world_shift)
        self.memories.draw(self.display_surface)
        
        self.scroll_x()
        
        # Atualiza o jogador e colisões
        self.player.update()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        self.check_collectibles() # Checa a coleta depois de mover
        
        self.player.draw(self.display_surface)
        
        # Desenha a Interface por último (para ficar por cima de tudo)
        self.hud.show_health(self.player.sprite.current_health, self.player.sprite.max_health)
        self.hud.show_memories(self.player.sprite.memories)
        
        if self.check_death():
            return "GAMEOVER"
        
        return None