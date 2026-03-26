import pygame
from background import ParallaxBackground
from settings import *
from sprites import Tile, Memory, Enemy, Goal, Dirt, Water, StaticObject, FireArrow, Ladder
from player import Player
from ui import HUD
from levels import *
from save_system import save_game, load_game, delete_save

COLLECT_SOUND_PATH = 'assets/sounds/collect.wav'
BG_GAME_PATH = 'assets/backgrounds_statics/bg_game.png'

class Level:
    def __init__(self, surface, save_data=None):
        """
        save_data: dicionário retornado por load_game(), ou None para novo jogo.
        """
        self.display_surface = surface

        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.memories = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.goal = pygame.sprite.GroupSingle()
        self.projectiles = pygame.sprite.Group()
        self.ladders = pygame.sprite.Group()

        self.hud = HUD(self.display_surface)
        self.world_shift = 0

        # ── CORREÇÃO: acumulador de deslocamento total do mundo ──
        self.total_world_offset = 0

        # Posições (tuplas) das memórias já coletadas — carregadas do save ou vazias
        if save_data and 'collected_positions' in save_data:
            self.collected_positions = set(
                tuple(pos) for pos in save_data['collected_positions']
            )
        else:
            self.collected_positions = set()

        try:
            self.collect_sound = pygame.mixer.Sound(COLLECT_SOUND_PATH)
            self.collect_sound.set_volume(0.6)
        except FileNotFoundError:
            self.collect_sound = None

        self.parallax = ParallaxBackground(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.setup_level(LEVEL_MAP, save_data)

    def setup_level(self, layout, save_data=None):
        self.tiles = pygame.sprite.Group()
        self.memories = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.goal = pygame.sprite.GroupSingle()
        self.objects = pygame.sprite.Group()
        self.ladders = pygame.sprite.Group()
        
        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                
                if cell == 'X':
                    tile = Tile((x, y), TILE_SIZE)
                    self.tiles.add(tile)
                
                elif cell == 'D':
                    dirt_tile = Dirt((x, y), TILE_SIZE)
                    self.tiles.add(dirt_tile)

                elif cell == 'P': 
                    player_sprite = Player((x, y))
                    self.player.add(player_sprite)
                
                elif cell == 'E':
                    enemy_sprite = Enemy((x, y), TILE_SIZE)
                    self.enemies.add(enemy_sprite)
                
                elif cell == 'M':
                    # ── CORREÇÃO: compara com a posição do mapa (x, y) ──
                    if (x, y) not in self.collected_positions:
                        memory_sprite = Memory((x, y), TILE_SIZE)
                        self.memories.add(memory_sprite)
                
                elif cell == 'G':
                    goal_sprite = Goal((x, y), TILE_SIZE)
                    self.goal.add(goal_sprite)

                elif cell == 'W':
                    water_tile = Water((x, y), TILE_SIZE)
                    self.tiles.add(water_tile)
                
                elif cell in ['1', '2', '3']:
                    tree = StaticObject((x, y), 'Trees', f'{cell}.png', TILE_SIZE)
                    self.objects.add(tree)
                elif cell in ['4', '5', '6']:
                    tree = StaticObject((x, y), 'Bushes', f'{cell}.png', TILE_SIZE)
                    self.objects.add(tree)

                elif cell == 'C':
                    ladder = Ladder((x, y), TILE_SIZE)
                    self.ladders.add(ladder)

        # ── CORREÇÃO: Aplica estado salvo ao player (incluindo posição) ──
        if save_data:
            player = self.player.sprite
            player.memories       = save_data.get('memories', 0)
            player.current_health = save_data.get('health', player.max_health)

            # Restaura posição do jogador se existir no save
            if 'player_x' in save_data and 'player_y' in save_data:
                player.rect.x = save_data['player_x']
                player.rect.y = save_data['player_y']

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
            player.current_speed = 0
        elif player_x > margin_right and direction_x > 0:
            self.world_shift = -5
            player.current_speed = 0
        else:
            self.world_shift = 0
            if not player.is_invincible:
                player.current_speed = player.walk_speed      

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.current_speed
        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left

    def vertical_movement_collision(self):
        self.player.sprite.apply_gravity()
        self.player.sprite.on_ground = False

        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(self.player.sprite.rect):
                
                if self.player.sprite.direction.y > 0:
                    self.player.sprite.rect.bottom = sprite.rect.top
                    self.player.sprite.direction.y = 0
                    self.player.sprite.on_ground = True
                    self.player.sprite.on_ladder = False

                elif self.player.sprite.direction.y < 0:
                    self.player.sprite.rect.top = sprite.rect.bottom
                    self.player.sprite.direction.y = 0

    def check_ladder(self):
        player = self.player.sprite
        player.on_ladder = bool(pygame.sprite.spritecollide(player, self.ladders, False))

    def check_collectibles(self):
        player = self.player.sprite
        collided_memories = pygame.sprite.spritecollide(player, self.memories, True)
        if collided_memories:
            player.memories += len(collided_memories)
            player.update_stage()

            # ── CORREÇÃO: salva map_pos (posição original) em vez de rect.topleft ──
            for memory in collided_memories:
                self.collected_positions.add(memory.map_pos)

            save_game(player, self.collected_positions, self.total_world_offset)

            if self.collect_sound:
                self.collect_sound.play()

    def check_brado(self):
        """Executa o brado do Curupira: dano em área e confunde inimigos."""
        player = self.player.sprite
        if not player.pending_brado:
            return

        player.pending_brado = False
        brado_range = 200

        affected = []
        for enemy in self.enemies:
            dist = pygame.math.Vector2(
                enemy.rect.centerx - player.rect.centerx,
                enemy.rect.centery - player.rect.centery
            ).length()
            if dist <= brado_range:
                affected.append(enemy)

        for enemy in affected:
            enemy.confuse(affected)

        self._brado_flash_timer = 20

    def check_damage(self):
        """Verifica colisão com inimigos e aplica dano."""
        player = self.player.sprite

        if player.is_invincible:
            return

        hit_enemies = pygame.sprite.spritecollide(player, self.enemies, False)
        if hit_enemies:
            enemy = hit_enemies[0]
            
            if enemy.rect.centerx < player.rect.centerx:
                knockback_direction = 1
            else:
                knockback_direction = -1
            
            player.take_damage(1, knockback_direction)

    def _spawn_fire_arrow(self):
        """Cria um projétil na posição do jogador se ele sinalizou o disparo."""
        player = self.player.sprite
        if player.pending_fire:
            player.pending_fire = False
            # Lança da lateral do jogador na direção que ele está olhando
            offset_x = 30 if player.facing_right else -30
            spawn_pos = (player.rect.centerx + offset_x, player.rect.centery)
            arrow = FireArrow(spawn_pos, player.facing_right)
            self.projectiles.add(arrow)

    def check_projectiles(self):
        """Verifica colisão de projéteis com inimigos."""
        for arrow in list(self.projectiles):
            hit = pygame.sprite.spritecollide(arrow, self.enemies, False)
            if hit:
                arrow.kill()
                hit[0].take_damage(1)

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

    def draw_visible(self, group):
        """Desenha apenas os sprites que estão dentro da tela visível."""
        visible_area = self.display_surface.get_rect().inflate(TILE_SIZE * 2, TILE_SIZE * 2)

        for sprite in group:
            if visible_area.colliderect(sprite.rect):
                self.display_surface.blit(sprite.image, sprite.rect)

    def run(self):
        self.parallax.update(self.world_shift)
        self.parallax.draw(self.display_surface)
        
        # ── CORREÇÃO: acumula o deslocamento total ──
        self.total_world_offset += self.world_shift

        self.tiles.update(self.world_shift)
        self.draw_visible(self.tiles)

        self.objects.update(self.world_shift)
        self.draw_visible(self.objects)

        self.ladders.update(self.world_shift)
        self.ladders.draw(self.display_surface)
        
        self.memories.update(self.world_shift)
        self.memories.draw(self.display_surface)
        
        self.enemies.update(self.world_shift) 
        self.enemies.draw(self.display_surface)
        
        self.goal.update(self.world_shift) 
        self.goal.draw(self.display_surface) 
        
        self.check_ladder()
        self.player.update()
        self.scroll_x()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        self.check_collectibles()
        self.check_damage()

        self._spawn_fire_arrow()
        self.projectiles.update(self.world_shift)
        self.check_projectiles()
        self.projectiles.draw(self.display_surface)

        self.check_brado()

        player = self.player.sprite

        visual_rect = player.image.get_rect(midbottom=player.rect.midbottom)

        if player.blink():
            player.image.set_alpha(40)
        else:
            player.image.set_alpha(255)

        self.display_surface.blit(player.image, visual_rect)

        # Flash do brado
        if hasattr(self, '_brado_flash_timer') and self._brado_flash_timer > 0:
            self._brado_flash_timer -= 1
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(60 * (self._brado_flash_timer / 20))
            pygame.draw.circle(flash_surf, (100, 255, 150, alpha),
                               player.rect.center, 200)
            self.display_surface.blit(flash_surf, (0, 0))

        self.hud.show_health(self.player.sprite.current_health, self.player.sprite.max_health)
        self.hud.show_memories(self.player.sprite.memories, self.player.sprite.stage)
        self.hud.show_brado_cooldown(self.player.sprite.get_brado_cooldown_ratio())
        
        if self.check_death():
            return "GAMEOVER"
            
        if self.check_victory():
            memories_count = self.player.sprite.memories
            if memories_count >= GOOD_ENDING_THRESHOLD:
                return "VICTORY_GOOD"
            else:
                return "VICTORY_BAD"
        
        return None