import pygame
from settings import *
from sprites import Tile, Memory, Obstacle, Goal
from player import Player
from ui import HUD

LEVEL_MAP = [
#    Apresentação                  | Teste                                     | Clímax
    '                                                                                                    ',
    '                                                                                                    ',
    '                                                                                 M                  ',
    '                                                           M                                     ',
    '                                                         XXX   XXX              XXX                      ',
    '       C                        M                                      XXX            XX      G       ',
    '                               XXX           O  O               XXX                       X   X    ',
    '                                           XXX  XXX          O       X     X    O           X       ',
    'XXXXXXXXXXXXXXXXXX   XXXXXXXXXXXXXXXXXXX  XXXX  XXXX  XXX   XXX     XX    XXXXXXXXXXXXXXXXXX       '
]

class Level:
    def __init__(self, surface):
        self.display_surface = surface
        
        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.memories = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.goal = pygame.sprite.GroupSingle()
        
        self.hud = HUD(self.display_surface)
        self.world_shift = 0 
        
        # Carregamento do Som da Fase
        try:
            self.collect_sound = pygame.mixer.Sound('assets/collect.mp3')
            self.collect_sound.set_volume(0.6)
        except FileNotFoundError:
            self.collect_sound = None
            
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
                elif cell == 'O':
                    obstacle_sprite = Obstacle((x, y), TILE_SIZE)
                    self.obstacles.add(obstacle_sprite)
                elif cell == 'G': # <-- Criação do Objetivo
                    goal_sprite = Goal((x, y), TILE_SIZE)
                    self.goal.add(goal_sprite)

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
        player = self.player.sprite
        collided_memories = pygame.sprite.spritecollide(player, self.memories, True)
        if collided_memories:
            player.memories += len(collided_memories)
            
            if self.collect_sound:
                self.collect_sound.play()

    def check_damage(self):
        """Verifica colisão com obstáculos e aplica dano."""
        player = self.player.sprite
        # O 'False' significa que o obstáculo NÃO some ao encostar
        if pygame.sprite.spritecollide(player, self.obstacles, False):
            player.take_damage(1)

    def check_death(self):
        """Morre se cair no buraco OU se a vida zerar."""
        if self.player.sprite.rect.top > SCREEN_HEIGHT or self.player.sprite.current_health <= 0:
            return True
        return False

    def check_victory(self):
        """Verifica se o jogador encostou no objetivo final."""
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
            return True
        return False

    def run(self):
        self.display_surface.fill((30, 80, 40))
        
        self.tiles.update(self.world_shift)
        self.tiles.draw(self.display_surface)
        
        self.memories.update(self.world_shift)
        self.memories.draw(self.display_surface)
        
        self.obstacles.update(self.world_shift)
        self.obstacles.draw(self.display_surface)
        
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)
        
        self.scroll_x()
        
        self.player.update()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        
        self.check_collectibles()
        self.check_damage()
        
        self.player.draw(self.display_surface)
        
        self.hud.show_health(self.player.sprite.current_health, self.player.sprite.max_health)
        self.hud.show_memories(self.player.sprite.memories)
        
        if self.check_death():
            return "GAMEOVER"
            
        if self.check_victory():
            return "VICTORY"
        
        return None