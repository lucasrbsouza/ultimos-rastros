import pygame
from settings import *
from sprites import Tile, Dirt, Enemy, FireArrow, CloudPoison, ENEMY_CONFIGS
from player import Player
from ui import HUD
from background import ParallaxBackground

# Arena: 24 tiles wide (1440px), sem plataformas nem buracos
ARENA_MAP = [
    '                        ',  # 00
    '                        ',  # 01
    '                        ',  # 02
    '                        ',  # 03
    '                        ',  # 04
    '                        ',  # 05
    '                        ',  # 06
    '  P R      *          R ',  # 07  P=jogador col2, *=boss col20
    'XXXXXXXXXXXXXXXXXXXXXXXX',  # 08
    'DDDDDDDDDDDDDDDDDDDDDDDD',  # 09
    'DDDDDDDDDDDDDDDDDDDDDDDD',  # 10
    'DDDDDDDDDDDDDDDDDDDDDDDD',  # 11
    'DDDDDDDDDDDDDDDDDDDDDDDD',  # 12
]

BOSS_NAMES = {
    'plent':       'PLENT',
    'skeleton':    'SKELETON',
    'orc_warrior': 'ORC GUERREIRO',
    'orc_berserk': 'ORC BERSERK',
    'orc_shaman':  'ORC XAMÃ  (BOSS FINAL)',
}

_SIMPLE_TYPES = ('fly', 'slime_normal', 'slime_fire', 'slime_spike')


class BossArena:
    def __init__(self, surface, boss_type, player_data):
        self.display_surface = surface
        self.boss_type       = boss_type
        self.world_shift     = 0
        self.total_world_offset = 0

        self.tiles             = pygame.sprite.Group()
        self.player            = pygame.sprite.GroupSingle()
        self.enemies           = pygame.sprite.Group()
        self.projectiles       = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()

        self.hud      = HUD(surface)
        self.parallax = ParallaxBackground(SCREEN_WIDTH, SCREEN_HEIGHT)

        try:
            self.collect_sound = pygame.mixer.Sound('assets/sounds/collect.wav')
            self.collect_sound.set_volume(0.6)
        except Exception:
            self.collect_sound = None

        self._font_big   = pygame.font.SysFont(None, 64)
        self._font_small = pygame.font.SysFont(None, 26)
        self._intro_until = pygame.time.get_ticks() + 2500

        self._boss_max_hp = ENEMY_CONFIGS.get(boss_type, {}).get('health', 5)

        self._setup(player_data)

    # ── Setup ────────────────────────────────────────────────────────────

    def _setup(self, player_data):
        for row_index, row in enumerate(ARENA_MAP):
            for col_index, cell in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE

                if cell == 'X':
                    self.tiles.add(Tile((x, y), TILE_SIZE))
                elif cell == 'D':
                    self.tiles.add(Dirt((x, y), TILE_SIZE))
                elif cell == 'P':
                    self.player.add(Player((x, y)))
                elif cell == '*':
                    esize = TILE_SIZE if self.boss_type in _SIMPLE_TYPES else int(TILE_SIZE * 1.5)
                    ey = y - (esize - TILE_SIZE)
                    enemy = Enemy((x, ey), esize, self.boss_type)
                    self.enemies.add(enemy)

        player = self.player.sprite
        if player_data:
            player.memories             = player_data.get('memories', 0)
            player.current_health       = player_data.get('health', player.max_health)
            player.score                = player_data.get('score', 0)
            player.can_shoot            = player_data.get('can_shoot', False)
            player.sussurro_comprado    = player_data.get('sussurro_comprado', False)
            player.active_powers        = list(player_data.get('active_powers', []))
            player.active_power_index   = player_data.get('active_power_index', 0)
            player.chama_ancestral_charges = player_data.get('chama_ancestral_charges', 0)
            player.guardiao_vida_bought = player_data.get('guardiao_vida_bought', False)
            player.max_health           = player_data.get('max_health', 5)
            player.current_health       = min(player.current_health, player.max_health)
            player.update_stage()

        for enemy in self.enemies:
            enemy.player_ref  = player
            enemy.enemies_ref = self.enemies

    # ── Física / Colisão (igual ao Level) ────────────────────────────────

    def scroll_x(self):
        player     = self.player.sprite
        player_x   = player.rect.centerx
        direction_x = player.direction.x
        margin_l   = SCREEN_WIDTH // 4
        margin_r   = SCREEN_WIDTH - margin_l

        if player_x < margin_l and direction_x < 0:
            self.world_shift = 5
            player.current_speed = 0
        elif player_x > margin_r and direction_x > 0:
            self.world_shift = -5
            player.current_speed = 0
        else:
            self.world_shift = 0
            if not player.is_invincible:
                player.current_speed = player.walk_speed

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.current_speed
        for tile in self.tiles.sprites():
            if tile.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = tile.rect.right
                elif player.direction.x > 0:
                    player.rect.right = tile.rect.left

    def vertical_movement_collision(self):
        p = self.player.sprite
        p.apply_gravity()
        p.on_ground = False
        for tile in self.tiles.sprites():
            if tile.rect.colliderect(p.rect):
                if p.direction.y > 0:
                    p.rect.bottom  = tile.rect.top
                    p.direction.y  = 0
                    p.on_ground    = True
                    p.on_ladder    = False
                elif p.direction.y < 0:
                    p.rect.top    = tile.rect.bottom
                    p.direction.y = 0

    def enemy_collision(self):
        for enemy in list(self.enemies):
            if not enemy._has_gravity:
                continue
            for tile in self.tiles.sprites():
                if tile.rect.colliderect(enemy.rect):
                    if enemy.direction == 1:
                        enemy.rect.right = tile.rect.left
                    else:
                        enemy.rect.left  = tile.rect.right
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

    def check_stomp(self):
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
        if DEV_MODE:
            return
        player = self.player.sprite
        if player.is_invincible or player.sombra_mata_active:
            return
        now = pygame.time.get_ticks()

        hit = pygame.sprite.spritecollide(player, self.enemies, False)
        if hit:
            enemy = hit[0]
            if player.rect.bottom - enemy.rect.top < 25 and player.rect.centery < enemy.rect.centery:
                return
            if now - enemy._last_attack_time < enemy._attack_cooldown:
                return
            enemy._last_attack_time = now
            kb = 1 if enemy.rect.centerx < player.rect.centerx else -1
            player.take_damage(1, kb)
            return

        for enemy in self.enemies:
            if not enemy.is_attacking:
                continue
            dist = abs(enemy.rect.centerx - player.rect.centerx)
            if dist > enemy.current_attack_range:
                continue
            if now - enemy._last_atk_time < enemy._atk_cd:
                continue
            kb = 1 if enemy.rect.centerx < player.rect.centerx else -1
            player.take_damage(enemy.current_attack_damage, kb)
            return

    def _spawn_fire_arrow(self):
        player = self.player.sprite
        if player.pending_fire:
            player.pending_fire = False
            offset_x = 30 if player.facing_right else -30
            pos = (player.rect.centerx + offset_x, player.rect.centery)
            self.projectiles.add(FireArrow(pos, player.facing_right))

    def check_projectiles(self):
        player = self.player.sprite
        for arrow in list(self.projectiles):
            hit = pygame.sprite.spritecollide(arrow, self.enemies, False)
            if hit:
                arrow.kill()
                dmg = 1
                if player.chama_ancestral_charges > 0:
                    dmg = 3
                    player.chama_ancestral_charges -= 1
                died = hit[0].take_damage(dmg)
                if died:
                    player.score += 100

    def _spawn_enemy_projectiles(self):
        for enemy in list(self.enemies):
            if not enemy.pending_ranged_proj:
                continue
            enemy.pending_ranged_proj = False
            facing_right = (enemy.direction == 1)
            offset_x = 40 if facing_right else -40
            pos = (enemy.rect.centerx + offset_x, enemy.rect.centery)
            self.enemy_projectiles.add(CloudPoison(pos, facing_right))

    def _check_enemy_projectiles(self):
        player = self.player.sprite
        if player.is_invincible or player.sombra_mata_active:
            return
        for proj in list(self.enemy_projectiles):
            if proj.rect.colliderect(player.rect):
                kb = 1 if proj.velocity > 0 else -1
                player.take_damage(CloudPoison.DAMAGE, kb)
                proj.kill()
                return

    # ── HUD Boss ─────────────────────────────────────────────────────────

    def _draw_boss_hud(self):
        boss = next(iter(self.enemies), None)
        if boss is None:
            return
        ratio  = max(0.0, boss.health / self._boss_max_hp)
        bar_w  = 440
        bar_h  = 22
        bx     = (SCREEN_WIDTH - bar_w) // 2
        by     = 18
        pygame.draw.rect(self.display_surface, (50, 0, 0),      (bx, by, bar_w, bar_h), border_radius=5)
        pygame.draw.rect(self.display_surface, (200, 30, 30),   (bx, by, int(bar_w * ratio), bar_h), border_radius=5)
        pygame.draw.rect(self.display_surface, (255, 180, 180), (bx, by, bar_w, bar_h), 2, border_radius=5)
        name = BOSS_NAMES.get(self.boss_type, self.boss_type.upper())
        txt  = self._font_small.render(name, True, (255, 220, 220))
        self.display_surface.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, by + bar_h + 4))

    def _draw_intro(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.display_surface.blit(overlay, (0, 0))
        name = BOSS_NAMES.get(self.boss_type, self.boss_type.upper())
        txt  = self._font_big.render(name, True, (220, 60, 60))
        sub  = self._font_small.render('Prepare-se!', True, (200, 200, 200))
        self.display_surface.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        self.display_surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, SCREEN_HEIGHT // 2 + 30))

    # ── run() ────────────────────────────────────────────────────────────

    def run(self):
        now = pygame.time.get_ticks()

        self.parallax.update(self.world_shift)
        self.parallax.draw(self.display_surface)

        # Overlay escuro para dar clima de boss fight
        dark = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dark.fill((20, 0, 30, 60))
        self.display_surface.blit(dark, (0, 0))

        self.total_world_offset += self.world_shift

        self.tiles.update(self.world_shift)
        self.tiles.draw(self.display_surface)

        self.enemies.update(self.world_shift)
        self.enemy_collision()
        self.enemies.draw(self.display_surface)

        player = self.player.sprite
        player.on_ladder = False  # sem escadas na arena

        self.player.update()
        self.scroll_x()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
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

        # Desenha jogador
        visual_rect = player.image.get_rect(midbottom=player.rect.midbottom)
        player.image.set_alpha(40 if player.blink() else 255)
        self.display_surface.blit(player.image, visual_rect)

        if player.sombra_mata_active:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash.fill((80, 40, 120, 30))
            self.display_surface.blit(flash, (0, 0))

        self.hud.show_health(player.current_health, player.max_health)
        self.hud.show_memories(player.memories, player.stage, player.has_key)
        self.hud.show_power_cooldown(
            player.get_x_power_cooldown_ratio(),
            player.get_active_power_name(),
            player.sombra_mata_active or player.voz_floresta_active,
        )
        self.hud.show_score(player.score)
        self.hud.show_hints(player)

        self._draw_boss_hud()

        # Intro overlay
        if now < self._intro_until:
            self._draw_intro()

        # ── Condições de fim ──────────────────────────────────────────
        if not self.enemies:
            return "WIN"
        if not DEV_MODE and (player.current_health <= 0 or player.rect.top > SCREEN_HEIGHT):
            return "LOSE"
        return None
