import pygame
from settings import *
from sprites import Tile

LEVEL_MAP = [
    '                            ',
    '                            ',
    '                            ',
    '                            ',
    '                            ',
    '                            ',
    '                            ',
    '                            ',
    'XXXXXXXXXXXXXXXXXXXXXXXXXXXX'
]

class Level:
    def __init__(self, surface):
        self.display_surface = surface
        
        self.tiles = pygame.sprite.Group()
        
        # Constrói o cenário
        self.setup_level(LEVEL_MAP)

    def setup_level(self, layout):
        """Lê o mapa e cria os objetos nas posições corretas."""
        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                if cell == 'X':
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    tile = Tile((x, y), TILE_SIZE)
                    self.tiles.add(tile)

    def run(self):
        """Atualiza e desenha a fase completa."""
        self.display_surface.fill((30, 80, 40))
        
        self.tiles.draw(self.display_surface)