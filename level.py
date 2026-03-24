import pygame
from background import ParallaxBackground
from settings import *
from sprites import Tile, Memory, Enemy, Goal, Dirt, Water, StaticObject
from player import Player
from ui import HUD
from levels import *

COLLECT_SOUND_PATH = 'assets/sounds/collect.wav'
BG_GAME_PATH = 'assets/backgrounds/bg_game.png'

class Level:
    def __init__(self, surface):
        self.display_surface = surface
        
        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.memories = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.goal = pygame.sprite.GroupSingle()
        
        self.hud = HUD(self.display_surface)
        self.world_shift = 0 
        
        try:
            self.collect_sound = pygame.mixer.Sound(COLLECT_SOUND_PATH)
            self.collect_sound.set_volume(0.6)
        except FileNotFoundError:
            self.collect_sound = None

        # Carrega o background da Gameplay
        try:
            self.collect_sound = pygame.mixer.Sound(COLLECT_SOUND_PATH)
            self.collect_sound.set_volume(0.6)
        except FileNotFoundError:
            self.collect_sound = None

        # --- NOVO: Inicializa o Parallax ---
        self.parallax = ParallaxBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
            
        self.setup_level(LEVEL_MAP)

    def setup_level(self, layout):
        self.tiles = pygame.sprite.Group()
        self.memories = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.goal = pygame.sprite.GroupSingle()
        self.objects = pygame.sprite.Group()
        
        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                
                if cell == 'X':
                    # Cria superfície (grama)
                    tile = Tile((x, y), TILE_SIZE)
                    self.tiles.add(tile)
                
                elif cell == 'D': # Novo bloco de terra
                    # Cria preenchimento (terra)
                    dirt_tile = Dirt((x, y), TILE_SIZE)
                    self.tiles.add(dirt_tile) # Adiciona no mesmo grupo para colisões

                elif cell == 'P': 
                    player_sprite = Player((x, y))
                    self.player.add(player_sprite)
                
                elif cell == 'E':
                    enemy_sprite = Enemy((x, y), TILE_SIZE)
                    self.enemies.add(enemy_sprite)
                
                elif cell == 'M':
                    memory_sprite = Memory((x, y), TILE_SIZE)
                    self.memories.add(memory_sprite)
                
                elif cell == 'G':
                    goal_sprite = Goal((x, y), TILE_SIZE)
                    self.goal.add(goal_sprite)

                elif cell == 'W':
                    water_tile = Water((x, y), TILE_SIZE)
                    self.tiles.add(water_tile)
                
                elif cell in ['1', '2', '3']:
                    # pos = (x,y), folder = 'Trees', image = '1.png', etc.
                    tree = StaticObject((x, y), 'Trees', f'{cell}.png', TILE_SIZE)
                    self.objects.add(tree)
                elif cell in ['4', '5', '6']:
                    # pos = (x,y), folder = 'Trees', image = '1.png', etc.
                    tree = StaticObject((x, y), 'Bushes', f'{cell}.png', TILE_SIZE)
                    self.objects.add(tree)
        for enemy in self.enemies:
          enemy.player_ref = self.player.sprite

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
        self.player.sprite.apply_gravity()

        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(self.player.sprite.rect):
                
                # Caindo — pousa em cima da plataforma
                if self.player.sprite.direction.y > 0:
                    self.player.sprite.rect.bottom = sprite.rect.top
                    self.player.sprite.direction.y = 0
                    self.player.sprite.on_ground = True   # ← aterrisou

                # Subindo — bateu embaixo da plataforma
                elif self.player.sprite.direction.y < 0:
                    self.player.sprite.rect.top = sprite.rect.bottom
                    self.player.sprite.direction.y = 1   # ← era 0, agora inicia a queda imediatamente

        # Se não encostou em nada caindo, está no ar
        if self.player.sprite.direction.y != 0:
            self.player.sprite.on_ground = False

    def check_collectibles(self):
        player = self.player.sprite
        collided_memories = pygame.sprite.spritecollide(player, self.memories, True)
        if collided_memories:
            player.memories += len(collided_memories)
            
            if self.collect_sound:
                self.collect_sound.play()

    def check_damage(self):
        """Verifica colisão com inimigos e aplica dano."""
        player = self.player.sprite
        if pygame.sprite.spritecollide(player, self.enemies, False):
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
        self.parallax.update(self.world_shift)
        self.parallax.draw(self.display_surface)
        
        self.tiles.update(self.world_shift)
        self.tiles.draw(self.display_surface)

        self.objects.update(self.world_shift)
        self.objects.draw(self.display_surface)
        
        self.memories.update(self.world_shift)
        self.memories.draw(self.display_surface)
        
        self.enemies.update(self.world_shift) 
        self.enemies.draw(self.display_surface)
        
        self.goal.update(self.world_shift) 
        self.goal.draw(self.display_surface) 
        
        self.scroll_x()
        
        self.player.update()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        
        self.check_collectibles()
        self.check_damage()
        
        player = self.player.sprite
        # Cria um retângulo virtual para a arte, centralizando-o sobre os pés do hitbox
        visual_rect = player.image.get_rect(midbottom=player.rect.midbottom)
        # Desenha a imagem na tela usando a posição do retângulo visual
        self.display_surface.blit(player.image, visual_rect)
        
        self.hud.show_health(self.player.sprite.current_health, self.player.sprite.max_health)
        self.hud.show_memories(self.player.sprite.memories)
        
        if self.check_death():
            return "GAMEOVER"
            
        if self.check_victory(): 
            return "VICTORY"
        
        return None