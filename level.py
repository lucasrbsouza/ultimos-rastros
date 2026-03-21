import pygame
from settings import *
from sprites import Tile
from player import Player

LEVEL_MAP = [
    '                            ',
    '                            ',
    '                            ',
    '                            ',
    '       C                    ',
    '                            ',
    '                            ',
    '                            ',
    'XXXXXXXXXXXXXXXXXXXXXXXXXXXX'
]

class Level:
    def __init__(self, surface):
        self.display_surface = surface
        
        # Grupos de Sprites
        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle() # Grupo especial para conter apenas 1 sprite
        
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

    def horizontal_movement_collision(self):
        player = self.player.sprite
        
        # Move o jogador no eixo X
        player.rect.x += player.direction.x * player.speed

        # Checa colisão com todos os blocos do cenário
        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0: # Estava indo para a esquerda
                    player.rect.left = sprite.rect.right
                elif player.direction.x > 0: # Estava indo para a direita
                    player.rect.right = sprite.rect.left

    def vertical_movement_collision(self):
        player = self.player.sprite
        
        # Aplica a gravidade no eixo Y
        player.apply_gravity()

        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0: # Caindo (bateu no chão)
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0 # Zera a gravidade para não atravessar o chão
                elif player.direction.y < 0: # Pulando (bateu a cabeça no teto)
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0

    def run(self):
        self.display_surface.fill((30, 80, 40))
        
        # Desenha os blocos do cenário
        self.tiles.draw(self.display_surface)
        
        # Atualiza a intenção de movimento do jogador (Teclado)
        self.player.update()
        
        # Aplica as colisões garantindo que ele não atravesse nada
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        
        # Desenha o jogador na tela
        self.player.draw(self.display_surface)