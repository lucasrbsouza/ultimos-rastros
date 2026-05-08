import pygame
import sys
import time
from settings import *
from menu import MainMenu, GameOverMenu, VictoryMenu, CreditsMenu, HistoryMenu
from level import Level
from save_system import delete_save, load_game, has_save, save_history
from cutscene import Cutscene
from boss_arena import BossArena
from settings import CUTSCENE_TEXTS, PROLOG_TEXT, VICTORY_GOOD_TEXT, VICTORY_BAD_TEXT
from shop import ShopScreen

MENU_BGM_PATH = 'assets/sounds/menu_bgm.mp3'
GAME_BGM_PATH = 'assets/sounds/game_bgm.mp3'
GAMEOVER_SOUND_PATH = 'assets/sounds/gameover.mp3'
VICTORY_SOUND_PATH = 'assets/sounds/victory.mp3'

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Surface lógica: resolução fixa do jogo (tudo é desenhado aqui)
        self.render_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Janela real: abre em modo janela redimensionável.
        # pygame.SCALED escala a render_surface automaticamente mantendo aspect ratio
        # com letterbox preto nas bordas quando necessário.
        # F11 alterna para tela cheia.
        self.window = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.RESIZABLE | pygame.SCALED
        )
        pygame.display.set_caption("Últimos Rastros")
        self.clock = pygame.time.Clock()
        self.is_running = True

        # Todos os componentes recebem a surface lógica (1280×680)
        self.main_menu = MainMenu(self.render_surface)
        self.game_over_menu = GameOverMenu(self.render_surface)
        self.victory_menu = VictoryMenu(self.render_surface)
        self.credits_menu = CreditsMenu(self.render_surface)
        self.history_menu = HistoryMenu(self.render_surface)
        self.level = None

        # Rastreamento de sessão
        self._session_start = None
        self._session_deaths = 0
        self._last_phase = 0
        self._last_memories = 0
        self._last_score = 0
        self.cutscene = None
        self.shop = None
        self._next_phase_index = 0
        self._carried_memories = 0
        self._carried_health = 5
        self._carried_score = 0
        self._carried_shop = {}
        self._pending_victory = None
        self._pending_score = 0

        # Boss fight
        self.boss_arena      = None
        self._boss_queue     = []
        self._boss_queue_idx = 0

        self.current_state = None
        self.change_state("MENU")

    def _start_session(self):
        self._session_start = time.time()
        self._session_deaths = 0

    def change_state(self, new_state):
        old_state = self.current_state
        self.current_state = new_state

        if new_state == "MENU" and old_state == "CREDITS":
            pygame.mixer.music.unpause()
            return

        if new_state == "MENU" and old_state == "HISTORY":
            pygame.mixer.music.unpause()
            return

        # Recria o menu principal para que has_save seja reavaliado
        if new_state == "MENU":
            self.main_menu = MainMenu(self.render_surface)

        # Mantém a música ao entrar nos Créditos / Histórico / Cutscene / Shop
        if new_state in ("CREDITS", "HISTORY", "CUTSCENE", "CUTSCENE_PROLOG", "SHOP", "BOSS_FIGHT"):
            pygame.mixer.music.unpause()
            return

        pygame.mixer.music.stop()

        try:
            if new_state == "MENU":
                pygame.mixer.music.load(MENU_BGM_PATH)
                pygame.mixer.music.play(-1)
            elif new_state == "GAMEPLAY":
                pygame.mixer.music.load(GAME_BGM_PATH)
                pygame.mixer.music.play(-1)
            elif new_state == "GAMEOVER":
                pygame.mixer.music.load(GAMEOVER_SOUND_PATH)
                pygame.mixer.music.play(0)
            elif new_state == "VICTORY":
                pygame.mixer.music.load(VICTORY_SOUND_PATH)
                pygame.mixer.music.play(0)

        except pygame.error:
            print(f"Aviso: Música para o estado {new_state} não encontrada na pasta assets.")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            # F11 alterna entre tela cheia e janela
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self._toggle_fullscreen()

            if self.current_state == "MENU":
                action = self.main_menu.handle_event(event)
                if action == "CONTINUE":
                    save_data = load_game()
                    phase = save_data.get('phase', 0) if save_data else 0
                    self.level = Level(self.render_surface, save_data, phase_index=phase)
                    if self._session_start is None:
                        self._start_session()
                    self.change_state("GAMEPLAY")
                elif action == "NEW_GAME":
                    delete_save()
                    self.level = Level(self.render_surface, phase_index=0)
                    self._start_session()
                    self.cutscene = Cutscene(self.render_surface, PROLOG_TEXT)
                    self._pending_victory = None
                    self.change_state("CUTSCENE_PROLOG")
                elif action == "HISTORY":
                    self.history_menu = HistoryMenu(self.render_surface)
                    self.change_state("HISTORY")
                elif action == "CREDITS":
                    self.change_state("CREDITS")
                elif action == "QUIT":
                    self.is_running = False

            elif self.current_state == "GAMEPLAY":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.change_state("MENU")
                    elif event.key == pygame.K_q:
                        self.shop = ShopScreen(self.render_surface, self.level.player.sprite)
                        self.change_state("SHOP")
                self.level.player.sprite.handle_event(event)

            elif self.current_state == "BOSS_FIGHT":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.change_state("MENU")
                self.boss_arena.player.sprite.handle_event(event)

            elif self.current_state == "SHOP":
                action = self.shop.handle_event(event)
                if action == "CLOSE":
                    self.change_state("GAMEPLAY")

            elif self.current_state == "GAMEOVER":
                action = self.game_over_menu.handle_event(event)
                if action == "RETRY":
                    delete_save()
                    self._session_deaths += 1
                    self.level = Level(self.render_surface, phase_index=self._last_phase)
                    player = self.level.player.sprite
                    player.memories = self._last_memories
                    player.score    = self._last_score
                    self._restore_shop_flags(player)
                    player.update_stage()
                    self.change_state("GAMEPLAY")
                elif action == "MENU":
                    self._session_start = None
                    self.change_state("MENU")

            elif self.current_state == "VICTORY":
                action = self.victory_menu.handle_event(event)
                if action == "MENU":
                    self.change_state("MENU")
                elif action == "QUIT":
                    self.is_running = False

            elif self.current_state == "CREDITS":
                action = self.credits_menu.handle_event(event)
                if action == "MENU":
                    self.change_state("MENU")

            elif self.current_state == "HISTORY":
                action = self.history_menu.handle_event(event)
                if action == "MENU":
                    self.change_state("MENU")

            elif self.current_state == "CUTSCENE":
                action = self.cutscene.handle_event(event)
                if action == "DONE":
                    if self._pending_victory:
                        self._finish_victory(self._pending_victory)
                        self._pending_victory = None
                    else:
                        self._load_next_phase()

            elif self.current_state == "CUTSCENE_PROLOG":
                action = self.cutscene.handle_event(event)
                if action == "DONE":
                    self.change_state("GAMEPLAY")

    def _save_shop_flags(self, player):
        self._carried_shop = {
            'can_shoot':           player.can_shoot,
            'sussurro_comprado':   player.sussurro_comprado,
            'active_powers':       list(player.active_powers),
            'active_power_index':  player.active_power_index,
            'chama_ancestral_charges': player.chama_ancestral_charges,
            'guardiao_vida_bought': player.guardiao_vida_bought,
            'max_health':          player.max_health,
        }

    def _restore_shop_flags(self, player):
        s = self._carried_shop
        player.can_shoot                 = s.get('can_shoot', False)
        player.sussurro_comprado         = s.get('sussurro_comprado', False)
        player.active_powers             = list(s.get('active_powers', []))
        player.active_power_index        = s.get('active_power_index', 0)
        player.chama_ancestral_charges   = s.get('chama_ancestral_charges', 0)
        player.guardiao_vida_bought      = s.get('guardiao_vida_bought', False)
        player.max_health                = s.get('max_health', 5)
        player.current_health            = min(player.current_health, player.max_health)

    def _extract_player_data(self, player):
        return {
            'memories':               player.memories,
            'health':                 player.current_health,
            'score':                  player.score,
            'can_shoot':              player.can_shoot,
            'sussurro_comprado':      player.sussurro_comprado,
            'active_powers':          list(player.active_powers),
            'active_power_index':     player.active_power_index,
            'chama_ancestral_charges': player.chama_ancestral_charges,
            'guardiao_vida_bought':   getattr(player, 'guardiao_vida_bought', False),
            'max_health':             player.max_health,
        }

    def _start_boss_fight(self, boss_queue, player_data, after_victory=None):
        """Inicia a sequência de boss fight. after_victory=string p/ VICTORY após a fila."""
        self._boss_queue      = boss_queue
        self._boss_queue_idx  = 0
        self._pending_victory = after_victory
        self.boss_arena = BossArena(self.render_surface, boss_queue[0], player_data)
        self.change_state("BOSS_FIGHT")

    def _load_next_phase(self):
        self.level = Level(self.render_surface, phase_index=self._next_phase_index)
        player = self.level.player.sprite
        player.memories       = self._carried_memories
        player.current_health = self._carried_health
        player.score          = self._carried_score
        self._restore_shop_flags(player)
        player.update_stage()
        self.change_state("GAMEPLAY")

    def _finish_victory(self, game_status):
        elapsed = time.time() - self._session_start if self._session_start else 0
        save_history(elapsed, self._session_deaths)
        delete_save()
        self._session_start = None
        ending_type = 'good' if game_status == "VICTORY_GOOD" else 'bad'
        self.victory_menu = VictoryMenu(self.render_surface, ending=ending_type,
                                        score=self._pending_score)
        self.change_state("VICTORY")

    def _toggle_fullscreen(self):
        """Alterna entre tela cheia e janela redimensionável (F11)."""
        flags = self.window.get_flags()
        if flags & pygame.FULLSCREEN:
            self.window = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                pygame.RESIZABLE | pygame.SCALED
            )
        else:
            self.window = pygame.display.set_mode(
                (0, 0),
                pygame.FULLSCREEN | pygame.SCALED
            )

    def update(self):
        if self.current_state == "MENU":
            self.main_menu.update()
        elif self.current_state == "GAMEOVER":
            self.game_over_menu.update()
        elif self.current_state == "VICTORY":
            self.victory_menu.update()
        elif self.current_state == "CREDITS":
            self.credits_menu.update()
        elif self.current_state == "HISTORY":
            self.history_menu.update()
        elif self.current_state in ("CUTSCENE", "CUTSCENE_PROLOG"):
            self.cutscene.update()
        elif self.current_state == "SHOP":
            self.shop.update()

    def draw(self):
        if self.current_state == "MENU":
            self.main_menu.draw()

        elif self.current_state == "GAMEPLAY":
            game_status = self.level.run()
            if game_status == "GAMEOVER":
                self._last_phase = self.level.phase_index
                old_player = self.level.player.sprite
                self._last_memories = old_player.memories
                self._last_score = old_player.score
                self._save_shop_flags(old_player)
                self.game_over_menu = GameOverMenu(self.render_surface)
                self.change_state("GAMEOVER")
            elif game_status == "NEXT_PHASE":
                next_phase = self.level.phase_index + 1
                old_player = self.level.player.sprite
                old_player.score += 500
                self._next_phase_index = next_phase
                self._save_shop_flags(old_player)
                pdata = self._extract_player_data(old_player)
                self._carried_memories = pdata['memories']
                self._carried_health   = pdata['health']
                self._carried_score    = pdata['score']
                # Fase 0→boss Plent | Fase 1→boss Skeleton | Fase 2 não tem porta
                _phase_boss = {0: ['plent'], 1: ['skeleton']}
                boss_queue = _phase_boss.get(self.level.phase_index)
                if boss_queue:
                    self._start_boss_fight(boss_queue, pdata, after_victory=None)
                else:
                    if next_phase - 1 in CUTSCENE_TEXTS:
                        self.cutscene = Cutscene(self.render_surface, CUTSCENE_TEXTS[next_phase - 1])
                        self.change_state("CUTSCENE")
                    else:
                        self._load_next_phase()
            elif game_status in ("VICTORY_GOOD", "VICTORY_BAD"):
                old_player = self.level.player.sprite
                old_player.score += 500
                self._save_shop_flags(old_player)
                pdata = self._extract_player_data(old_player)
                self._pending_score    = pdata['score']
                self._carried_memories = pdata['memories']
                self._carried_health   = pdata['health']
                self._carried_score    = pdata['score']
                # Fase 3: sequência dos 3 Orcs, depois victory
                self._start_boss_fight(
                    ['orc_warrior', 'orc_berserk', 'orc_shaman'],
                    pdata,
                    after_victory=game_status,
                )

        elif self.current_state == "BOSS_FIGHT":
            result = self.boss_arena.run()
            if result == "WIN":
                old_player = self.boss_arena.player.sprite
                old_player.score += 300
                pdata = self._extract_player_data(old_player)
                self._carried_memories = pdata['memories']
                self._carried_health   = pdata['health']
                self._carried_score    = pdata['score']
                self._save_shop_flags(old_player)

                self._boss_queue_idx += 1
                if self._boss_queue_idx < len(self._boss_queue):
                    # Próximo boss na fila (sequência de Orcs)
                    next_boss = self._boss_queue[self._boss_queue_idx]
                    self.boss_arena = BossArena(self.render_surface, next_boss, pdata)
                    # Mantém estado BOSS_FIGHT, apenas troca a arena
                else:
                    # Fila completa
                    if self._pending_victory is not None:
                        # Vinha de VICTORY_GOOD/BAD → agora vai pra cutscene de vitória
                        victory_type = self._pending_victory
                        self._pending_score   = pdata['score']
                        self._pending_victory = None
                        victory_text = VICTORY_GOOD_TEXT if victory_type == "VICTORY_GOOD" else VICTORY_BAD_TEXT
                        self.cutscene = Cutscene(self.render_surface, victory_text)
                        self.change_state("CUTSCENE")
                        self._pending_victory = victory_type  # restore p/ handler da cutscene
                    else:
                        # Vinha de NEXT_PHASE (fases 0 ou 1) → próxima fase
                        if self._next_phase_index - 1 in CUTSCENE_TEXTS:
                            self.cutscene = Cutscene(
                                self.render_surface,
                                CUTSCENE_TEXTS[self._next_phase_index - 1]
                            )
                            self.change_state("CUTSCENE")
                        else:
                            self._load_next_phase()

            elif result == "LOSE":
                self._session_deaths += 1
                self._last_phase    = self.level.phase_index if self.level else 0
                self._last_memories = self._carried_memories
                self._last_score    = self._carried_score
                self.game_over_menu = GameOverMenu(self.render_surface)
                self.change_state("GAMEOVER")

        elif self.current_state == "SHOP":
            self.shop.draw()

        elif self.current_state == "GAMEOVER":
            self.game_over_menu.draw()

        elif self.current_state == "VICTORY":
            self.victory_menu.draw()
        elif self.current_state == "CREDITS":
            self.credits_menu.draw()
        elif self.current_state == "HISTORY":
            self.history_menu.draw()
        elif self.current_state in ("CUTSCENE", "CUTSCENE_PROLOG"):
            self.cutscene.draw()

        # Escala a surface lógica para a janela real (pygame.SCALED faz isso automaticamente
        # ao fazer blit da render_surface para a window)
        self.window.blit(self.render_surface, (0, 0))
        pygame.display.flip()

    def run(self):
        while self.is_running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
