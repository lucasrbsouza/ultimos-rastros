import pygame
from settings import *
from sprites import Tile
from player import Player

LEVEL_MAP = [
    '                                                            ',
    '                                                            ',
    '                                                            ',
    '                                                            ',
    '       C                                                    ',
    '                                                XXX         ',
    '                              XXX                           ',
    '                 XXX                                        ',
    'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
]

class Level:
    def __init__(self, surface):
        self.display_surface = surface
        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        
        # Variável que controla a velocidade da câmera
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

    def scroll_x(self):
        """Lógica da Câmera: move o cenário se o jogador chegar perto das bordas."""
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        # Define as margens (1/4 da tela) para a câmera começar a atuar
        margin_left = SCREEN_WIDTH // 4
        margin_right = SCREEN_WIDTH - (SCREEN_WIDTH // 4)

        if player_x < margin_left and direction_x < 0:
            self.world_shift = 5 # Empurra o mundo para a direita
            player.speed = 0     # Trava a velocidade visual do jogador
        elif player_x > margin_right and direction_x > 0:
            self.world_shift = -5 # Empurra o mundo para a esquerda
            player.speed = 0      # Trava a velocidade visual do jogador
        else:
            self.world_shift = 0  # Câmera parada
            player.speed = 5      # Jogador anda normalmente

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

    def run(self):
        self.display_surface.fill((30, 80, 40))
        
        # Atualiza a posição dos blocos com base na câmera e desenha
        self.tiles.update(self.world_shift)
        self.tiles.draw(self.display_surface)
        
        # Calcula a câmera ANTES de resolver a colisão do jogador
        self.scroll_x()
        
        # Atualiza o jogador
        self.player.update()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        self.player.draw(self.display_surface)