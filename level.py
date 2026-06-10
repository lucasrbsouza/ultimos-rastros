import pygame
from background import ParallaxBackground
from settings import *
from sprites import Tile, Memory, Enemy, Goal, Dirt, Water, StaticObject, FireArrow, CloudPoison, Ladder, Key, LockedDoor, Heart
from player import Player
from ui import HUD, draw_run_streaks
from levels import *
from save_system import save_game, load_game, delete_save
from config import CONFIG, apply_god_powers

COLLECT_SOUND_PATH = 'assets/sounds/collect.wav'
BG_GAME_PATH = 'assets/backgrounds_statics/bg_game.png'

class Level:
    def __init__(self, surface, save_data=None, phase_index=0):
        """
        save_data:   dicionário retornado por load_game(), ou None para novo jogo.
        phase_index: índice da fase atual (0, 1 ou 2).
        """
        self.display_surface = surface
        self.phase_index = phase_index

        self.tiles = pygame.sprite.Group()
        self.water_tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.memories = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.goal = pygame.sprite.GroupSingle()
        self.projectiles = pygame.sprite.Group()
        self.ladders = pygame.sprite.Group()
        self.keys = pygame.sprite.Group()
        self.doors = pygame.sprite.GroupSingle()
        self.enemy_projectiles = pygame.sprite.Group()
        self.hearts = pygame.sprite.Group()

        self.hud = HUD(self.display_surface)
        self.world_shift = 0

        # acumulador de deslocamento total do mundo
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

        self.setup_level(ALL_LEVELS[self.phase_index], save_data)

    def setup_level(self, layout, save_data=None):
        self.tiles = pygame.sprite.Group()
        self.water_tiles = pygame.sprite.Group()
        self.memories = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.goal = pygame.sprite.GroupSingle()
        self.objects = pygame.sprite.Group()
        self.ladders = pygame.sprite.Group()
        self.keys = pygame.sprite.Group()
        self.doors = pygame.sprite.GroupSingle()
        self.hearts = pygame.sprite.Group()

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
                
                elif cell in ('E', 'F', 'T', 'V', 'N', 'S', 'A', 'B', 'H'):
                    _type_map = {
                        'E': 'fly',
                        'F': 'slime_normal', 'T': 'slime_fire', 'V': 'slime_spike',
                        'N': 'plent', 'S': 'skeleton',
                        'A': 'orc_warrior', 'B': 'orc_berserk', 'H': 'orc_shaman',
                    }
                    etype = _type_map[cell]
                    _simple = ('fly', 'slime_normal', 'slime_fire', 'slime_spike')
                    esize = TILE_SIZE if etype in _simple else int(TILE_SIZE * 1.5)
                    ey = y - (esize - TILE_SIZE)  # alinha bottom ao chão
                    enemy_sprite = Enemy((x, ey), esize, etype)
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
                    self.water_tiles.add(water_tile)
                
                elif cell in ['1', '2', '3']:
                    tree = StaticObject((x, y), 'Trees', f'{cell}.png', TILE_SIZE)
                    self.objects.add(tree)
                elif cell in ['4', '5', '6']:
                    tree = StaticObject((x, y), 'Bushes', f'{cell}.png', TILE_SIZE)
                    self.objects.add(tree)

                elif cell == 'C':
                    ladder = Ladder((x, y), TILE_SIZE)
                    self.ladders.add(ladder)

                elif cell == 'K':
                    key_sprite = Key((x, y), TILE_SIZE)
                    self.keys.add(key_sprite)

                elif cell == 'L':
                    door_sprite = LockedDoor((x, y), TILE_SIZE)
                    self.doors.add(door_sprite)

                elif cell == 'R':
                    heart_sprite = Heart((x, y), TILE_SIZE)
                    self.hearts.add(heart_sprite)

        # ── CORREÇÃO: Aplica estado salvo ao player (incluindo posição) ──
        if save_data:
            player = self.player.sprite
            player.memories       = save_data.get('memories', 0)
            player.current_health = save_data.get('health', player.max_health)

            # Restaura posição do jogador e reposiciona a câmera no ponto salvo
            if 'player_x' in save_data and 'player_y' in save_data:
                map_x = save_data['player_x']
                player.rect.y = save_data['player_y']

                # Desloca o mundo p/ trazer o jogador ao centro da tela.
                # Sem rolar para antes do início da fase (offset <= 0).
                anchor = SCREEN_WIDTH // 2
                initial_offset = min(0, anchor - map_x)
                self.total_world_offset = initial_offset
                player.rect.x = map_x + initial_offset
                if initial_offset:
                    self._apply_world_offset(initial_offset)
                    self.parallax.update(initial_offset)

        for enemy in self.enemies:
            enemy.player_ref = self.player.sprite
            enemy.enemies_ref = self.enemies

        if CONFIG.god_mode and self.player.sprite:
            apply_god_powers(self.player.sprite)

    def _apply_world_offset(self, dx):
        """Desloca todos os sprites do mundo de uma vez — usado ao recarregar
        um save para reposicionar a câmera no ponto onde o jogador parou.
        Espelha exatamente o que .update(world_shift) faz a cada frame."""
        groups = [self.tiles, self.water_tiles, self.memories, self.enemies,
                  self.goal, self.objects, self.ladders, self.keys, self.doors,
                  self.hearts]
        for group in groups:
            for sprite in group.sprites():
                sprite.rect.x += dx

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
            # current_speed é controlado por update_run() (anda/corre);
            # não sobrescrever aqui senão a corrida nunca acelera.

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.current_speed
        for sprite in self._active_tiles:
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

    def enemy_collision(self):
        """Gravidade + colisão horizontal e vertical dos inimigos com tiles."""
        for enemy in list(self.enemies):
            if not enemy._has_gravity:
                continue

            # Colisão horizontal (empurra pra fora de tiles)
            for tile in self.tiles.sprites():
                if tile.rect.colliderect(enemy.rect):
                    if enemy.direction == 1:
                        enemy.rect.right = tile.rect.left
                    else:
                        enemy.rect.left  = tile.rect.right

            # Gravidade + colisão vertical
            enemy.apply_gravity()
            enemy.on_ground = False
            for tile in self.tiles.sprites():
                if tile.rect.colliderect(enemy.rect):
                    if enemy.velocity_y > 0:
                        enemy.rect.bottom = tile.rect.top
                        enemy.velocity_y  = 0
                        enemy.on_ground   = True
                    elif enemy.velocity_y < 0:
                        enemy.rect.top   = tile.rect.bottom
                        enemy.velocity_y = 0

            # Mata se cair no buraco
            if enemy.rect.top > SCREEN_HEIGHT:
                enemy.kill()

    def check_ladder(self):
        player = self.player.sprite
        player.on_ladder = bool(pygame.sprite.spritecollide(player, self.ladders, False))

    def check_collectibles(self):
        player = self.player.sprite
        collided_memories = pygame.sprite.spritecollide(player, self.memories, True)
        if collided_memories:
            player.memories += len(collided_memories)
            player.score += 50 * len(collided_memories)
            player.update_stage()

            # ── CORREÇÃO: salva map_pos (posição original) em vez de rect.topleft ──
            for memory in collided_memories:
                self.collected_positions.add(memory.map_pos)

            save_game(player, self.collected_positions, self.total_world_offset, self.phase_index)

            if self.collect_sound:
                self.collect_sound.play()

    def check_stomp(self):
        """Pular em cima do inimigo causa 1 de dano e faz o player quicar."""
        player = self.player.sprite
        if player.direction.y <= 0:
            return
        for enemy in list(self.enemies):
            if player.rect.colliderect(enemy.rect):
                overlap = player.rect.bottom - enemy.rect.top
                if 0 < overlap < 25 and player.rect.centery < enemy.rect.centery:
                    enemy.take_damage(1)
                    player.direction.y = -10
                    player.score += 50
                    return

    def check_damage(self):
        """Verifica colisão com inimigos e aplica dano."""
        if DEV_MODE or CONFIG.god_mode:
            return
        player = self.player.sprite

        if player.is_invincible or player.sombra_mata_active:
            return

        now = pygame.time.get_ticks()

        # Dano por contato (fly + stomp)
        hit_enemies = pygame.sprite.spritecollide(player, self.enemies, False)
        if hit_enemies:
            enemy = hit_enemies[0]
            if player.rect.bottom - enemy.rect.top < 25 and player.rect.centery < enemy.rect.centery:
                return
            if now - enemy._last_attack_time < enemy._attack_cooldown:
                return
            enemy._last_attack_time = now
            knockback_direction = 1 if enemy.rect.centerx < player.rect.centerx else -1
            player.take_damage(1, knockback_direction)
            return

        # Dano por range: inimigos em estado de ataque (advanced AI)
        for enemy in self.enemies:
            if not enemy.is_attacking:
                continue
            dist = abs(enemy.rect.centerx - player.rect.centerx)
            if dist > enemy.current_attack_range:
                continue
            if now - enemy._last_atk_time < enemy._atk_cd:
                continue
            knockback_direction = 1 if enemy.rect.centerx < player.rect.centerx else -1
            player.take_damage(enemy.current_attack_damage, knockback_direction)
            return

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

    def _spawn_enemy_projectiles(self):
        """Spawna projéteis de inimigos (ex: CloudPoison do Plent)."""
        for enemy in list(self.enemies):
            if not enemy.pending_ranged_proj:
                continue
            enemy.pending_ranged_proj = False
            facing_right = (enemy.direction == 1)
            offset_x = 40 if facing_right else -40
            spawn_pos = (enemy.rect.centerx + offset_x, enemy.rect.centery)
            cloud = CloudPoison(spawn_pos, facing_right)
            self.enemy_projectiles.add(cloud)

    def _check_enemy_projectiles(self):
        """Aplica dano ao jogador atingido por projéteis de inimigos."""
        player = self.player.sprite
        if player.is_invincible or player.sombra_mata_active:
            return
        for proj in list(self.enemy_projectiles):
            if proj.rect.colliderect(player.rect):
                knockback = 1 if proj.velocity > 0 else -1
                player.take_damage(CloudPoison.DAMAGE, knockback)
                proj.kill()
                return

    def check_projectiles(self):
        """Verifica colisão de projéteis com inimigos."""
        player = self.player.sprite
        for arrow in list(self.projectiles):
            hit = pygame.sprite.spritecollide(arrow, self.enemies, False)
            if hit:
                arrow.kill()
                damage = 1
                if player.chama_ancestral_charges > 0:
                    damage = 3
                    player.chama_ancestral_charges -= 1
                died = hit[0].take_damage(damage)
                if died:
                    player.score += 100

    def check_key_and_door(self):
        """Coleta chave e abre a porta se o jogador tiver a chave."""
        player = self.player.sprite

        collected_keys = pygame.sprite.spritecollide(player, self.keys, True)
        if collected_keys:
            player.has_key = True
            if self.collect_sound:
                self.collect_sound.play()

        door = self.doors.sprite
        if door and not door.is_open and player.has_key:
            if door.rect.colliderect(player.rect):
                door.open()

    def check_hearts(self):
        """Coleta coração e recupera 1 HP (máximo max_health)."""
        player = self.player.sprite
        collected = pygame.sprite.spritecollide(player, self.hearts, True)
        if collected:
            player.current_health = min(player.current_health + 1, player.max_health)
            if self.collect_sound:
                self.collect_sound.play()

    def check_phase_exit(self):
        """Retorna 'NEXT_PHASE' se o jogador entrar na porta aberta."""
        door = self.doors.sprite
        if door and door.is_open:
            if door.rect.colliderect(self.player.sprite.rect):
                return "NEXT_PHASE"
        return None

    def check_death(self):
        """Morre se cair no buraco, tocar água OU se a vida zerar."""
        if DEV_MODE or CONFIG.god_mode:
            return False
        player = self.player.sprite
        if player.rect.top > SCREEN_HEIGHT or player.current_health <= 0:
            return True
        if pygame.sprite.spritecollide(player, self.water_tiles, False):
            return True
        return False

    def check_victory(self):
        """Verifica se o jogador encostou no objetivo final (apenas na fase 3)."""
        if self.phase_index == 2 and pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
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

        self.water_tiles.update(self.world_shift)
        self.draw_visible(self.water_tiles)

        self.objects.update(self.world_shift)
        self.draw_visible(self.objects)

        self.ladders.update(self.world_shift)
        self.ladders.draw(self.display_surface)
        
        self.memories.update(self.world_shift)
        self.memories.draw(self.display_surface)

        self.hearts.update(self.world_shift)
        self.hearts.draw(self.display_surface)
        
        self.enemies.update(self.world_shift)
        self.enemy_collision()
        self.enemies.draw(self.display_surface)
        
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        self.keys.update(self.world_shift)
        self.keys.draw(self.display_surface)

        self.doors.update(self.world_shift)
        self.doors.draw(self.display_surface)

        self.check_ladder()
        self.player.update()
        self.scroll_x()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        self.check_collectibles()
        self.check_hearts()
        self.check_key_and_door()
        self.check_stomp()
        self.check_damage()

        self._spawn_fire_arrow()
        self.projectiles.update(self.world_shift)
        self.check_projectiles()
        self.projectiles.draw(self.display_surface)

        self._spawn_enemy_projectiles()
        self.enemy_projectiles.update(self.world_shift)
        self._check_enemy_projectiles()
        self.enemy_projectiles.draw(self.display_surface)

        player = self.player.sprite

        visual_rect = player.image.get_rect(midbottom=player.rect.midbottom)

        if player.blink():
            player.image.set_alpha(40)
        else:
            player.image.set_alpha(255)

        self.display_surface.blit(player.image, visual_rect)

        # Flash Sombra da Mata
        if player.sombra_mata_active:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((80, 40, 120, 30))
            self.display_surface.blit(flash_surf, (0, 0))

        # Feedback de corrida no mapa
        draw_run_streaks(self.display_surface, player)

        self.hud.show_health(player.current_health, player.max_health)
        self.hud.show_memories(player.memories, player.stage, player.has_key)
        self.hud.show_power_cooldown(
            player.get_x_power_cooldown_ratio(),
            player.get_active_power_name(),
            player.sombra_mata_active or player.voz_floresta_active,
        )
        self.hud.show_score(player.score)
        self.hud.show_hints(player)
        self.hud.show_power_switch(player)

        if self.check_death():
            return "GAMEOVER"

        phase_result = self.check_phase_exit()
        if phase_result:
            return phase_result

        if self.check_victory():
            memories_count = self.player.sprite.memories
            if memories_count >= GOOD_ENDING_THRESHOLD:
                return "VICTORY_GOOD"
            else:
                return "VICTORY_BAD"

        return None