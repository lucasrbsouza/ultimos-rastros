import pygame
from settings import *
from ui import Button
from save_system import has_save, load_history
import math, random

BG_MENU_PATH = 'assets/backgrounds_statics/bg_menu.png'
BG_GAMEOVER_PATH = 'assets/backgrounds_statics/bg_gameover.png'
BG_VICTORY_PATH = 'assets/backgrounds_statics/bg_victory.png'

class MainMenu:
    def __init__(self, screen):
        
        self._particle_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.screen = screen
        self.clock_ticks = 0

        # --- Fontes ---
        self.font_title    = pygame.font.Font(None, 112)
        self.font_subtitle = pygame.font.Font(None, 32)
        self.font_button   = pygame.font.Font(None, 36)

        # --- Background ---
        try:
            self.bg_image = pygame.transform.scale(
                pygame.image.load(BG_MENU_PATH).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        except FileNotFoundError:
            self.bg_image = None

        # --- Botões (entram escalonados da direita) ---
        btn_w, btn_h = 230, 46
        btn_gap = 58   # espaçamento entre botões
        cx = SCREEN_WIDTH // 2 - btn_w // 2

        # Verifica se existe save para montar os botões corretos
        self.has_save = has_save()

        if self.has_save:
            n_btns = 5
            total_h = btn_h + (n_btns - 1) * btn_gap
            # centraliza o bloco na metade inferior da tela com margem de 20px do fundo
            base_y = min(
                SCREEN_HEIGHT // 2 + 20,
                SCREEN_HEIGHT - total_h - 20
            )
            self.btn_continue = Button(cx, base_y,                 btn_w, btn_h, "Continuar",  self.font_button)
            self.btn_new_game = Button(cx, base_y + btn_gap,       btn_w, btn_h, "Novo Jogo",  self.font_button)
            self.btn_history  = Button(cx, base_y + btn_gap * 2,   btn_w, btn_h, "Histórico",  self.font_button)
            self.btn_credits  = Button(cx, base_y + btn_gap * 3,   btn_w, btn_h, "Créditos",   self.font_button)
            self.btn_quit     = Button(cx, base_y + btn_gap * 4,   btn_w, btn_h, "Sair",       self.font_button)
            self._btn_offsets = [160, 160, 160, 160, 160]
            self._btn_delays  = [0, 0, 0, 0, 0]
        else:
            n_btns = 4
            total_h = btn_h + (n_btns - 1) * btn_gap
            base_y = min(
                SCREEN_HEIGHT // 2 + 20,
                SCREEN_HEIGHT - total_h - 20
            )
            self.btn_play    = Button(cx, base_y,               btn_w, btn_h, "Jogar",     self.font_button)
            self.btn_history = Button(cx, base_y + btn_gap,     btn_w, btn_h, "Histórico", self.font_button)
            self.btn_credits = Button(cx, base_y + btn_gap * 2, btn_w, btn_h, "Créditos",  self.font_button)
            self.btn_quit    = Button(cx, base_y + btn_gap * 3, btn_w, btn_h, "Sair",      self.font_button)
            self._btn_offsets = [160, 160, 160, 160]
            self._btn_delays  = [0, 0, 0, 0]

        # --- Partículas (vaga-lumes verdes subindo) ---
        self.particles = [self._new_particle(random.randint(0, SCREEN_HEIGHT))
                          for _ in range(60)]

        # --- Folhas decorativas orbitando o título ---
        self.leaves = [
            {
                "angle": random.uniform(0, math.pi * 2),
                "dist":  random.uniform(200, 340),
                "speed": random.uniform(0.003, 0.008) * random.choice([-1, 1]),
                "size":  random.uniform(3, 6),
                "color": random.choice([
                    (80, 180, 90), (100, 220, 110),
                    (60, 160, 80), (140, 255, 140),
                ]),
            }
            for _ in range(20)
        ]

        # --- Vinheta (bordas escuras permanentes) ---
        self.vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(80):
            t = i / 80
            alpha = int(160 * (t ** 2.2))
            rw = int(SCREEN_WIDTH  * 0.9 * (1 - t * 0.35))
            rh = int(SCREEN_HEIGHT * 0.9 * (1 - t * 0.35))
            pygame.draw.ellipse(
                self.vignette,
                (0, 0, 0, alpha),
                (SCREEN_WIDTH  // 2 - rw,
                 SCREEN_HEIGHT // 2 - rh,
                 rw * 2, rh * 2)
            )

        # --- Surfaces pré-alocadas (sem realocação em cada frame) ---
        self._particle_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._leaf_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # --- Linha de brilho pré-renderizada ---
        self._glow_line = self._build_glow_line(width=460, color=(80, 180, 100))

        # --- Animação ---
        self.fade_alpha     = 255
        self.title_alpha    = 255
        self.subtitle_alpha = 255

    # ── helpers ─────────────────────────────────────────────────────────────
    def _new_particle(self, start_y=None):
        return {
            "x":     random.uniform(0, SCREEN_WIDTH),
            "y":     start_y if start_y is not None else SCREEN_HEIGHT + 5,
            "speed": random.uniform(0.3, 1.0),
            "size":  random.uniform(1.5, 3.5),
            "alpha": random.randint(80, 200),
            "phase": random.uniform(0, math.pi * 2),
            "color": random.choice([
                (100, 220, 120), (140, 255, 150),
                (80,  200, 100), (180, 255, 180),
                (200, 240, 140),
            ]),
        }

    def _draw_particles(self):
        self._particle_surf.fill((0, 0, 0, 0))
        t = self.clock_ticks * 0.015
        for p in self.particles:
            p["y"] -= p["speed"]
            p["x"] += math.sin(t + p["phase"]) * 0.6
            if p["y"] < -10:
                p.update(self._new_particle())
            r, g, b = p["color"]
            pygame.draw.circle(self._particle_surf, (r, g, b, 28),
                               (int(p["x"]), int(p["y"])), int(p["size"] * 2.8))
            pygame.draw.circle(self._particle_surf, (r, g, b, p["alpha"]),
                               (int(p["x"]), int(p["y"])), int(p["size"]))
        self.screen.blit(self._particle_surf, (0, 0))

    def _draw_leaves(self):
        """Pontos de luz orbitando o título em elipse achatada."""
        self._leaf_surf.fill((0, 0, 0, 0))
        cx = SCREEN_WIDTH  // 2
        cy = SCREEN_HEIGHT // 2 - 130
        for lf in self.leaves:
            lf["angle"] += lf["speed"]
            lx = cx + math.cos(lf["angle"]) * lf["dist"]
            ly = cy + math.sin(lf["angle"]) * lf["dist"] * 0.28
            r, g, b = lf["color"]
            pygame.draw.circle(self._leaf_surf, (r, g, b, 35), (int(lx), int(ly)), int(lf["size"] * 2.2))
            pygame.draw.circle(self._leaf_surf, (r, g, b, 200), (int(lx), int(ly)), int(lf["size"]))
        self.screen.blit(self._leaf_surf, (0, 0))

    def _build_glow_line(self, width, color):
        """Constrói a linha de brilho uma única vez."""
        surf = pygame.Surface((width, 4), pygame.SRCALPHA)
        r, g, b = color
        for i in range(width):
            fade = math.sin((i / width) * math.pi) ** 1.5
            surf.set_at((i, 1), (r, g, b, int(fade * 190)))
            surf.set_at((i, 2), (r, g, b, int(fade * 70)))
        return surf

    def _draw_glow_line(self, y):
        """Desenha a linha pré-renderizada."""
        x = SCREEN_WIDTH // 2 - self._glow_line.get_width() // 2
        self.screen.blit(self._glow_line, (x, y))

    def _draw_title(self, text, cx, cy, alpha):
        font = self.font_title
        pulse = 0.5 + 0.5 * math.sin(self.clock_ticks * 0.025)
        color = (
            int(160 + 50 * pulse),
            int(225 + 30 * pulse),
            int(165 + 40 * pulse),
        )
        # camadas de glow verde
        for off, op in [(10, 18), (6, 45), (3, 85)]:
            g = font.render(text, True, (80, 200, 100))
            g.set_alpha(int(op * alpha / 255))
            gr = g.get_rect(center=(cx + off // 2, cy + off // 2))
            self.screen.blit(g, gr)
        # texto principal
        ts = font.render(text, True, color)
        ts.set_alpha(alpha)
        self.screen.blit(ts, ts.get_rect(center=(cx, cy)))

    def _draw_button_with_offset(self, btn, offset_x, alpha):
        """Desenha botão deslocado horizontalmente com fade."""
        # salva posição original
        orig_x = btn.rect.x
        btn.rect.x += int(offset_x)
        btn.draw(self.screen)
        btn.rect.x = orig_x
        # fade de entrada
        if alpha < 255:
            fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade.fill((10, 18, 12))
            fade.set_alpha(255 - alpha)
            self.screen.blit(fade, (0, 0))

    # ── ciclo principal ──────────────────────────────────────────────────────
    def update(self):
        self.clock_ticks += 1
        t = self.clock_ticks

        mouse_pos = pygame.mouse.get_pos()
        if self.has_save:
            self.btn_continue.update(mouse_pos)
            self.btn_new_game.update(mouse_pos)
        else:
            self.btn_play.update(mouse_pos)
        self.btn_history.update(mouse_pos)
        self.btn_credits.update(mouse_pos)
        self.btn_quit.update(mouse_pos)

        for i in range(len(self._btn_offsets)):
            if t > self._btn_delays[i]:
                self._btn_offsets[i] = max(0, self._btn_offsets[i] - 18)

    def handle_event(self, event):
        if self.has_save:
            if self.btn_continue.is_clicked(event):
                return "CONTINUE"
            if self.btn_new_game.is_clicked(event):
                return "NEW_GAME"
        else:
            if self.btn_play.is_clicked(event):
                return "NEW_GAME"
        if self.btn_history.is_clicked(event):
            return "HISTORY"
        if self.btn_credits.is_clicked(event):
            return "CREDITS"
        if self.btn_quit.is_clicked(event):
            return "QUIT"
        return None

    def draw(self):
        # ── background ──
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill((10, 18, 12))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((8, 16, 10))
        self.screen.blit(overlay, (0, 0))

        self._draw_particles()
        self.screen.blit(self.vignette, (0, 0))
        self._draw_leaves()

        # ── título ──
        title_cy = SCREEN_HEIGHT // 2 - 130
        self._draw_title("Últimos Rastros", SCREEN_WIDTH // 2, title_cy, self.title_alpha)

        # ── linha decorativa ──
        self._draw_glow_line(SCREEN_HEIGHT // 2 - 60)

        # ── subtítulo pulsante ──
        pulse = 0.5 + 0.5 * math.sin(self.clock_ticks * 0.04)
        sub_color = (int(120 + 40 * pulse), int(190 + 30 * pulse), int(130 + 30 * pulse))
        sub_surf = pygame.font.Font(None, 32).render(
            "Uma jornada de memórias perdidas", True, sub_color
        )
        sub_surf.set_alpha(self.subtitle_alpha)
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 28))
        self.screen.blit(sub_surf, sub_rect)

        # ── botões deslizando ──
        if self.has_save:
            buttons = [self.btn_continue, self.btn_new_game, self.btn_history, self.btn_credits, self.btn_quit]
        else:
            buttons = [self.btn_play, self.btn_history, self.btn_credits, self.btn_quit]

        for i, btn in enumerate(buttons):
            off   = self._btn_offsets[i]
            alpha = int(255 * (1 - off / 160))
            orig_x = btn.rect.x
            btn.rect.x += int(off)
            btn.draw(self.screen)
            btn.rect.x = orig_x
            if alpha < 255:
                fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                fade.fill((8, 16, 10))
                fade.set_alpha(255 - alpha)
                self.screen.blit(fade, (0, 0))

class GameOverMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock_ticks = 0

        # --- Fontes ---
        self.font_title    = pygame.font.Font(None, 96)
        self.font_subtitle = pygame.font.Font(None, 34)
        self.font_button   = pygame.font.Font(None, 36)

        # --- Background ---
        try:
            self.bg_image = pygame.transform.scale(
                pygame.image.load(BG_GAMEOVER_PATH).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        except FileNotFoundError:
            self.bg_image = None

        # --- Botões ---
        btn_w, btn_h = 240, 50
        cx = SCREEN_WIDTH // 2 - btn_w // 2
        self.btn_retry = Button(cx, SCREEN_HEIGHT // 2 + 80,  btn_w, btn_h, "Tentar Novamente", self.font_button)
        self.btn_menu  = Button(cx, SCREEN_HEIGHT // 2 + 148, btn_w, btn_h, "Menu Principal",   self.font_button)

        # --- Partículas de cinza/brasa ---
        self.particles = [self._new_particle(random.randint(0, SCREEN_HEIGHT))
                          for _ in range(70)]

        # --- Raios de "vinheta" pulsante ---
        self.vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(80):
            t = i / 80
            alpha = int(180 * (t ** 2))
            r = int(SCREEN_WIDTH  * 0.85 * (1 - t * 0.4))
            pygame.draw.ellipse(
                self.vignette,
                (0, 0, 0, alpha),
                (SCREEN_WIDTH  // 2 - r,
                 SCREEN_HEIGHT // 2 - int(r * 0.6),
                 r * 2, int(r * 1.2))
            )

        # --- Surface pré-alocada (sem realocação em cada frame) ---
        self._particle_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # --- Linha de brilho pré-renderizada ---
        self._glow_line = self._build_glow_line(width=500, color=(160, 30, 20))

        # --- Animação (rápida, lição aprendida) ---
        self.fade_alpha     = 0
        self.title_offset_y = -60    # cai do topo
        self.subtitle_alpha = 0
        self.btn_alpha      = 0
        self.shake_timer    = 12     # frames de tremor inicial

    # ── helpers ─────────────────────────────────────────────────────────────
    def _new_particle(self, start_y=None):
        """Brasas/cinzas subindo lentamente."""
        return {
            "x":     random.uniform(0, SCREEN_WIDTH),
            "y":     start_y if start_y is not None else SCREEN_HEIGHT + 5,
            "speed": random.uniform(0.4, 1.2),
            "vx":    random.uniform(-0.4, 0.4),
            "size":  random.uniform(1.5, 4.0),
            "alpha": random.randint(60, 180),
            "phase": random.uniform(0, math.pi * 2),
            "color": random.choice([
                (180, 40,  20),
                (220, 80,  30),
                (140, 30,  15),
                (100, 100, 100),
                (160, 160, 160),
            ]),
        }

    def _draw_particles(self):
        self._particle_surf.fill((0, 0, 0, 0))
        t = self.clock_ticks * 0.018
        for p in self.particles:
            p["y"] -= p["speed"]
            p["x"] += math.sin(t + p["phase"]) * 0.5 + p["vx"]
            if p["y"] < -10:
                p.update(self._new_particle())
            r, g, b = p["color"]
            # halo
            pygame.draw.circle(self._particle_surf, (r, g, b, 25),
                               (int(p["x"]), int(p["y"])), int(p["size"] * 2.5))
            # núcleo
            pygame.draw.circle(self._particle_surf, (r, g, b, p["alpha"]),
                               (int(p["x"]), int(p["y"])), int(p["size"]))
        self.screen.blit(self._particle_surf, (0, 0))

    def _build_glow_line(self, width, color):
        """Constrói a linha de brilho uma única vez."""
        surf = pygame.Surface((width, 4), pygame.SRCALPHA)
        r, g, b = color
        for i in range(width):
            fade = math.sin((i / width) * math.pi) ** 1.5
            surf.set_at((i, 1), (r, g, b, int(fade * 200)))
            surf.set_at((i, 2), (r, g, b, int(fade * 70)))
        return surf

    def _draw_glow_line(self, y):
        """Desenha a linha pré-renderizada."""
        x = SCREEN_WIDTH // 2 - self._glow_line.get_width() // 2
        self.screen.blit(self._glow_line, (x, y))

    def _draw_panel(self, x, y, w, h):
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((10, 2, 2, 210))
        self.screen.blit(panel, (x, y))
        pulse = 0.5 + 0.5 * math.sin(self.clock_ticks * 0.045)
        borda_alpha = int(100 + 100 * pulse)
        pygame.draw.rect(self.screen,
                         (160, 25, 15, borda_alpha),
                         (x, y, w, h), 2, border_radius=8)

    def _draw_title(self, text, cx, cy, offset_y, alpha):
        font = self.font_title
        # shake nos primeiros frames
        sx = random.randint(-2, 2) if self.shake_timer > 0 else 0
        sy = random.randint(-2, 2) if self.shake_timer > 0 else 0

        # 3 camadas de glow vermelho escuro
        for off, op in [(10, 20), (6, 50), (3, 90)]:
            g = font.render(text, True, (200, 0, 0))
            g.set_alpha(int(op * alpha / 255))
            gr = g.get_rect(center=(cx + off // 2 + sx, cy + offset_y + off // 2 + sy))
            self.screen.blit(g, gr)

        # texto principal vermelho
        title_surf = font.render(text, True, (230, 60, 50))
        title_surf.set_alpha(alpha)
        tr = title_surf.get_rect(center=(cx + sx, cy + offset_y + sy))
        self.screen.blit(title_surf, tr)

    # ── ciclo principal ──────────────────────────────────────────────────────
    def update(self):
        self.clock_ticks += 1
        t = self.clock_ticks

        mouse_pos = pygame.mouse.get_pos()
        self.btn_retry.update(mouse_pos)
        self.btn_menu.update(mouse_pos)

        if self.shake_timer > 0:
            self.shake_timer -= 1

        self.fade_alpha = min(255, self.fade_alpha + 12)

        # título desce do topo
        if self.title_offset_y < 0:
            self.title_offset_y = min(0, self.title_offset_y + 5)

        if t > 15:
            self.subtitle_alpha = min(255, self.subtitle_alpha + 12)

        if t > 25:
            self.btn_alpha = min(255, self.btn_alpha + 12)

    def handle_event(self, event):
        if self.btn_retry.is_clicked(event):
            return "RETRY"
        if self.btn_menu.is_clicked(event):
            return "MENU"
        return None

    def draw(self):
        # ── background ──
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill((18, 4, 4))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(170)
        overlay.fill((12, 2, 2))
        self.screen.blit(overlay, (0, 0))

        self._draw_particles()

        # vinheta pulsante nas bordas
        pulse_v = 0.75 + 0.25 * math.sin(self.clock_ticks * 0.04)
        self.vignette.set_alpha(int(220 * pulse_v))
        self.screen.blit(self.vignette, (0, 0))

        # ── painel central ──
        panel_w, panel_h = 580, 360
        panel_x = SCREEN_WIDTH  // 2 - panel_w // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_h // 2
        self._draw_panel(panel_x, panel_y, panel_w, panel_h)

        # ── título com queda + tremor ──
        self._draw_title(
            "A Floresta Esqueceu...",
            SCREEN_WIDTH  // 2,
            SCREEN_HEIGHT // 2 - 100,
            self.title_offset_y,
            self.fade_alpha
        )

        # ── linha decorativa ──
        self._draw_glow_line(SCREEN_HEIGHT // 2 - 46)

        # ── subtítulo ──
        pulse_c = 0.5 + 0.5 * math.sin(self.clock_ticks * 0.05)
        sub_color = (int(180 + 40 * pulse_c), int(60 + 20 * pulse_c), int(50 + 20 * pulse_c))
        sub_surf = pygame.font.Font(None, 34).render(
            "As memórias se perderam na escuridão", True, sub_color
        )
        sub_surf.set_alpha(self.subtitle_alpha)
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10))
        self.screen.blit(sub_surf, sub_rect)

        # ── botões com fade-in ──
        self.btn_retry.draw(self.screen)
        self.btn_menu.draw(self.screen)
        if self.btn_alpha < 255:
            fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade.fill((12, 2, 2))
            fade.set_alpha(255 - self.btn_alpha)
            self.screen.blit(fade, (0, 0))

class VictoryMenu:
    def __init__(self, screen, ending='good'):
        self.screen = screen
        self.clock_ticks = 0

        # --- Fontes ---
        self.font_title    = pygame.font.Font(None, 108)
        self.font_subtitle = pygame.font.Font(None, 38)
        self.font_button   = pygame.font.Font(None, 36)

        # --- Background ---
        try:
            self.bg_image = pygame.transform.scale(
                pygame.image.load(BG_VICTORY_PATH).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        except FileNotFoundError:
            self.bg_image = None

        # --- Botões ---
        btn_w, btn_h = 240, 50
        cx = SCREEN_WIDTH // 2 - btn_w // 2
        self.btn_menu = Button(cx, SCREEN_HEIGHT // 2 + 80,  btn_w, btn_h, "Menu Principal", self.font_button)
        self.btn_quit = Button(cx, SCREEN_HEIGHT // 2 + 148, btn_w, btn_h, "Sair do Jogo",   self.font_button)

        # --- Partículas de confete/ouro ---
        self.particles = [self._new_particle(random.randint(0, SCREEN_HEIGHT))
                          for _ in range(80)]

        # --- Estrelas de brilho ao redor do título ---
        self.stars = [{"angle": random.uniform(0, math.pi * 2),
                       "dist":  random.uniform(160, 280),
                       "speed": random.uniform(0.004, 0.012),
                       "size":  random.uniform(2, 5),
                       "color": random.choice([(255,215,0),(255,245,120),(255,180,50),(200,255,180)])}
                      for _ in range(18)]

        # --- Surfaces pré-alocadas (sem realocação em cada frame) ---
        self._particle_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._star_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # --- Linha de brilho pré-renderizada ---
        self._glow_line = self._build_glow_line(width=520, color=(220, 170, 30))

        # --- Textos do final ---
        if ending == 'good':
            self.title_text    = "A Floresta Lembra"
            self.subtitle_text = "O Curupira vive enquanto houver memória."
        else:
            self.title_text    = "O Silêncio Vence"
            self.subtitle_text = "Sem memórias, o guardião se apaga para sempre."

        # --- Animação ---
        self.fade_alpha    = 0
        self.title_scale   = 0.3       # cresce até 1.0 no pop-in
        self.subtitle_alpha = 0
        self.btn_alpha     = 0

    # ── helpers ─────────────────────────────────────────────────────────────
    def _new_particle(self, start_y=None):
        return {
            "x":     random.uniform(0, SCREEN_WIDTH),
            "y":     start_y if start_y is not None else -8,
            "vy":    random.uniform(0.8, 2.4),      # cai para baixo
            "vx":    random.uniform(-0.6, 0.6),
            "size":  random.uniform(3, 7),
            "alpha": random.randint(160, 255),
            "rot":   random.uniform(0, 360),
            "rot_v": random.uniform(-2, 2),
            "color": random.choice([
                (255, 215, 0), (255, 245, 100), (255, 140, 0),
                (200, 255, 160), (140, 230, 255), (255, 180, 200),
            ]),
        }

    def _draw_particles(self):
        self._particle_surf.fill((0, 0, 0, 0))
        for p in self.particles:
            p["y"]   += p["vy"]
            p["x"]   += p["vx"]
            p["rot"] += p["rot_v"]
            if p["y"] > SCREEN_HEIGHT + 10:
                p.update(self._new_particle())

            r, g, b = p["color"]
            s = int(p["size"])
            cx, cy = int(p["x"]), int(p["y"])
            # losango simples como confete
            pts = [
                (cx,     cy - s),
                (cx + s, cy    ),
                (cx,     cy + s),
                (cx - s, cy    ),
            ]
            pygame.draw.polygon(self._particle_surf, (r, g, b, p["alpha"]), pts)
        self.screen.blit(self._particle_surf, (0, 0))

    def _draw_stars(self):
        """Estrelinhas orbitando o centro do título."""
        self._star_surf.fill((0, 0, 0, 0))
        cx = SCREEN_WIDTH  // 2
        cy = SCREEN_HEIGHT // 2 - 120
        for st in self.stars:
            st["angle"] += st["speed"]
            sx = cx + math.cos(st["angle"]) * st["dist"]
            sy = cy + math.sin(st["angle"]) * st["dist"] * 0.35  # elipse achatada
            r, g, b = st["color"]
            # halo
            pygame.draw.circle(self._star_surf, (r, g, b, 40), (int(sx), int(sy)), int(st["size"] * 2.5))
            # núcleo
            pygame.draw.circle(self._star_surf, (r, g, b, 220), (int(sx), int(sy)), int(st["size"]))
        self.screen.blit(self._star_surf, (0, 0))

    def _build_glow_line(self, width, color):
        """Constrói a linha de brilho uma única vez."""
        surf = pygame.Surface((width, 4), pygame.SRCALPHA)
        r, g, b = color
        for i in range(width):
            t = i / width
            fade = math.sin(t * math.pi) ** 1.5
            surf.set_at((i, 1), (r, g, b, int(fade * 200)))
            surf.set_at((i, 2), (r, g, b, int(fade * 80)))
        return surf

    def _draw_glow_line(self, y):
        """Desenha a linha pré-renderizada."""
        x = SCREEN_WIDTH // 2 - self._glow_line.get_width() // 2
        self.screen.blit(self._glow_line, (x, y))

    def _draw_panel(self, x, y, w, h):
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((12, 8, 2, 200))
        self.screen.blit(panel, (x, y))
        pulse = 0.5 + 0.5 * math.sin(self.clock_ticks * 0.045)
        borda_alpha = int(120 + 100 * pulse)
        pygame.draw.rect(self.screen,
                         (200, 160, 30, borda_alpha),
                         (x, y, w, h), 2, border_radius=8)

    def _draw_title_glow(self, text, cx, cy, scale, alpha):
        """Título com pop-in de escala + halo dourado."""
        base_size = int(108 * max(scale, 0.05))
        font = pygame.font.Font(None, base_size)

        # camadas de glow
        for offset, op in [(10, 25), (6, 55), (3, 100)]:
            glow_surf = font.render(text, True, (255, 200, 0))
            glow_surf.set_alpha(int(op * alpha / 255))
            gr = glow_surf.get_rect(center=(cx + offset // 2, cy + offset // 2))
            self.screen.blit(glow_surf, gr)

        # texto principal dourado
        title_surf = font.render(text, True, (255, 228, 80))
        title_surf.set_alpha(alpha)
        tr = title_surf.get_rect(center=(cx, cy))
        self.screen.blit(title_surf, tr)

    # ── ciclo principal ──────────────────────────────────────────────────────
    def update(self):
        self.clock_ticks += 1
        t = self.clock_ticks

        mouse_pos = pygame.mouse.get_pos()
        self.btn_menu.update(mouse_pos)
        self.btn_quit.update(mouse_pos)

        # fade-in geral: era +5  → agora +12  (chega em ~21 frames)
        self.fade_alpha = min(255, self.fade_alpha + 12)

        # pop-in do título: era +0.035 → agora +0.07
        if self.title_scale < 1.0:
            self.title_scale = min(1.0, self.title_scale + 0.07)

        # subtítulo: era esperar 40 frames → agora 15
        if t > 15:
            self.subtitle_alpha = min(255, self.subtitle_alpha + 12)

        # botões: era esperar 65 frames → agora 25
        if t > 25:
            self.btn_alpha = min(255, self.btn_alpha + 12)

    def handle_event(self, event):
        if self.btn_menu.is_clicked(event):
            return "MENU"
        if self.btn_quit.is_clicked(event):
            return "QUIT"
        return None

    def draw(self):
        # ── background ──
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill((14, 10, 2))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(155)
        overlay.fill((10, 6, 0))
        self.screen.blit(overlay, (0, 0))

        self._draw_particles()

        # ── painel central ──
        panel_w, panel_h = 580, 380
        panel_x = SCREEN_WIDTH  // 2 - panel_w // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_h // 2
        self._draw_panel(panel_x, panel_y, panel_w, panel_h)

        # ── estrelas orbitando ──
        self._draw_stars()

        # ── título com pop-in e glow ──
        title_cx = SCREEN_WIDTH  // 2
        title_cy = SCREEN_HEIGHT // 2 - 100
        self._draw_title_glow(self.title_text, title_cx, title_cy,
                               self.title_scale, self.fade_alpha)

        # ── linha decorativa ──
        self._draw_glow_line(SCREEN_HEIGHT // 2 - 46)

        # ── subtítulo ──
        pulse = 0.5 + 0.5 * math.sin(self.clock_ticks * 0.05)
        sub_color = (
            int(200 + 40 * pulse),
            int(190 + 30 * pulse),
            int(120 + 30 * pulse),
        )
        sub_surf = pygame.font.Font(None, 38).render(
            self.subtitle_text, True, sub_color
        )
        sub_surf.set_alpha(self.subtitle_alpha)
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 14))
        self.screen.blit(sub_surf, sub_rect)

        # ── botões com fade-in ──
        btn_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.btn_menu.draw(self.screen)
        self.btn_quit.draw(self.screen)
        if self.btn_alpha < 255:
            fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade.fill((10, 6, 0))
            fade.set_alpha(255 - self.btn_alpha)
            self.screen.blit(fade, (0, 0))

class CreditsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock_ticks = 0

        # --- Fontes ---
        self.font_title    = pygame.font.Font(None, 90)
        self.font_label    = pygame.font.Font(None, 26)
        self.font_value    = pygame.font.Font(None, 34)
        self.font_button   = pygame.font.Font(None, 36)

        # --- Background ---
        try:
            self.bg_image = pygame.transform.scale(
                pygame.image.load(BG_MENU_PATH).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        except FileNotFoundError:
            self.bg_image = None

        # --- Botão Voltar ---
        btn_w, btn_h = 220, 48
        self.btn_back = Button(
            SCREEN_WIDTH // 2 - btn_w // 2,
            SCREEN_HEIGHT - 100,
            btn_w, btn_h, "<- Voltar", self.font_button
        )

        # --- Dados dos créditos (label, valor) ---
        self.credits_data = [
            ("PROJETO",      "Últimos Rastros"),
            ("DESENVOLVEDOR","José Lucas Silva Souza"),
            ("INSTITUIÇÃO",  "Icev – Instituto de Ensino Superior"),
            ("DISCIPLINA",   "Desenvolvimento de Jogos"),
            ("ANO",          "2026"),
        ]

        # --- Partículas (pirilampos/faíscas) ---
        self.particles = [self._new_particle(random.randint(0, SCREEN_HEIGHT))
                          for _ in range(55)]

        # --- Surface pré-alocada (sem realocação em cada frame) ---
        self._particle_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # --- Linha de brilho pré-renderizada ---
        self._glow_line = self._build_glow_line(width=480, color=(100, 200, 140))

        # --- Animação de entrada ---
        self.fade_alpha  = 0          # fade-in geral
        self.line_timers = [0.0] * len(self.credits_data)  # por linha

    # ── helpers ────────────────────────────────────────────────────────────
    def _new_particle(self, start_y=None):
        return {
            "x":     random.uniform(0, SCREEN_WIDTH),
            "y":     start_y if start_y is not None else SCREEN_HEIGHT + 5,
            "speed": random.uniform(0.3, 1.1),
            "size":  random.uniform(1.5, 3.5),
            "alpha": random.randint(80, 220),
            "phase": random.uniform(0, math.pi * 2),   # oscilação lateral
            "color": random.choice([
                (140, 220, 160), (180, 255, 200),
                (100, 200, 230), (255, 240, 140),
            ]),
        }

    def _draw_particles(self):
        self._particle_surf.fill((0, 0, 0, 0))
        t = self.clock_ticks * 0.015
        for p in self.particles:
            p["y"] -= p["speed"]
            p["x"] += math.sin(t + p["phase"]) * 0.5
            if p["y"] < -10:
                p.update(self._new_particle())

            r, g, b = p["color"]
            # halo externo
            pygame.draw.circle(self._particle_surf, (r, g, b, 30),
                               (int(p["x"]), int(p["y"])),
                               int(p["size"] * 2.8))
            # núcleo
            pygame.draw.circle(self._particle_surf, (r, g, b, p["alpha"]),
                               (int(p["x"]), int(p["y"])),
                               int(p["size"]))
        self.screen.blit(self._particle_surf, (0, 0))

    def _build_glow_line(self, width, color):
        """Constrói a linha de brilho uma única vez."""
        surf = pygame.Surface((width, 4), pygame.SRCALPHA)
        r, g, b = color
        for i in range(width):
            t = i / width
            fade = math.sin(t * math.pi) ** 1.5
            surf.set_at((i, 1), (r, g, b, int(fade * 180)))
            surf.set_at((i, 2), (r, g, b, int(fade * 80)))
        return surf

    def _draw_glow_line(self, y):
        """Desenha a linha pré-renderizada."""
        x = SCREEN_WIDTH // 2 - self._glow_line.get_width() // 2
        self.screen.blit(self._glow_line, (x, y))

    def _draw_panel(self, x, y, w, h, alpha=210):
        """Painel escuro semi-transparente com borda brilhante."""
        # fundo
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((8, 20, 14, alpha))
        self.screen.blit(panel, (x, y))
        # borda com pulso
        pulse = 0.5 + 0.5 * math.sin(self.clock_ticks * 0.04)
        borda_alpha = int(100 + 80 * pulse)
        pygame.draw.rect(self.screen,
                         (80, 180, 110, borda_alpha),
                         (x, y, w, h), 2, border_radius=6)

    def _eased_alpha(self, timer, duration=40):
        t = min(timer / duration, 1.0)
        return int(255 * (t * t * (3 - 2 * t)))   # smoothstep

    # ── ciclo principal ─────────────────────────────────────────────────────
    def update(self):
        self.clock_ticks += 1
        mouse_pos = pygame.mouse.get_pos()
        self.btn_back.update(mouse_pos)

        # fade-in geral
        if self.fade_alpha < 255:
            self.fade_alpha = min(255, self.fade_alpha + 6)

        # linhas aparecem em cascata
        for i in range(len(self.line_timers)):
            if self.clock_ticks > 30 + i * 18:
                self.line_timers[i] = min(self.line_timers[i] + 2, 40)

    def handle_event(self, event):
        if self.btn_back.is_clicked(event):
            return "MENU"
        return None

    def draw(self):
        # ── background ──
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill((10, 18, 14))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(165)
        overlay.fill((5, 14, 10))
        self.screen.blit(overlay, (0, 0))

        self._draw_particles()

        # ── painel central ──
        panel_w, panel_h = 620, 430
        panel_x = SCREEN_WIDTH  // 2 - panel_w // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_h // 2 + 20
        self._draw_panel(panel_x, panel_y, panel_w, panel_h)

        # ── título ──
        pulse_t = 0.5 + 0.5 * math.sin(self.clock_ticks * 0.03)
        title_color = (
            int(160 + 60 * pulse_t),
            int(220 + 35 * pulse_t),
            int(170 + 40 * pulse_t),
        )
        title_surf = self.font_title.render("Créditos", True, title_color)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, panel_y - 52))
        title_surf.set_alpha(self.fade_alpha)
        self.screen.blit(title_surf, title_rect)

        # linha decorativa abaixo do título
        self._draw_glow_line(panel_y - 22)

        # ── linhas de crédito ──
        row_h   = 72
        start_y = panel_y + 38
        pad_x   = 48

        for i, (label, value) in enumerate(self.credits_data):
            alpha = self._eased_alpha(self.line_timers[i])
            base_y = start_y + i * row_h

            # sublabel (categoria)
            lbl_surf = self.font_label.render(label, True, (100, 180, 130))
            lbl_surf.set_alpha(alpha)
            self.screen.blit(lbl_surf, (panel_x + pad_x, base_y))

            # valor
            val_surf = self.font_value.render(value, True, (230, 255, 235))
            val_surf.set_alpha(alpha)
            self.screen.blit(val_surf, (panel_x + pad_x, base_y + 22))

            # separador sutil entre linhas (exceto a última)
            if i < len(self.credits_data) - 1:
                sep = pygame.Surface((panel_w - pad_x * 2, 1), pygame.SRCALPHA)
                sep.fill((80, 140, 100, 60))
                self.screen.blit(sep, (panel_x + pad_x, base_y + 62))

        # ── botão voltar ──
        btn_surf = pygame.Surface((SCREEN_WIDTH, 80), pygame.SRCALPHA)
        self.btn_back.draw(self.screen)


class HistoryMenu:
    ITEMS_PER_PAGE = 10

    def __init__(self, screen):
        self.screen = screen
        self.clock_ticks = 0

        self.font_title  = pygame.font.Font(None, 72)
        self.font_header = pygame.font.Font(None, 26)
        self.font_row    = pygame.font.Font(None, 28)
        self.font_button = pygame.font.Font(None, 34)

        try:
            self.bg_image = pygame.transform.scale(
                pygame.image.load(BG_MENU_PATH).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        except FileNotFoundError:
            self.bg_image = None

        self.history = list(reversed(load_history()))  # mais recente primeiro
        self.page = 0
        self.total_pages = max(1, math.ceil(len(self.history) / self.ITEMS_PER_PAGE))

        btn_w, btn_h = 180, 44
        cy_btns = SCREEN_HEIGHT - 72
        self.btn_back = Button(
            SCREEN_WIDTH // 2 - btn_w // 2, cy_btns,
            btn_w, btn_h, "<- Voltar", self.font_button
        )
        self.btn_prev = Button(
            SCREEN_WIDTH // 2 - btn_w - 20, cy_btns,
            btn_w, btn_h, "< Anterior", self.font_button
        )
        self.btn_next = Button(
            SCREEN_WIDTH // 2 + 20, cy_btns,
            btn_w, btn_h, "Próxima >", self.font_button
        )

        self._particle_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.particles = [self._new_particle(random.randint(0, SCREEN_HEIGHT)) for _ in range(50)]
        self._glow_line = self._build_glow_line(500, (80, 180, 100))
        self.fade_alpha = 0

    def _new_particle(self, start_y=None):
        return {
            "x": random.uniform(0, SCREEN_WIDTH),
            "y": start_y if start_y is not None else SCREEN_HEIGHT + 5,
            "speed": random.uniform(0.3, 1.0),
            "size": random.uniform(1.5, 3.0),
            "alpha": random.randint(80, 180),
            "phase": random.uniform(0, math.pi * 2),
            "color": random.choice([(100,220,120),(140,255,150),(80,200,100),(180,255,180)]),
        }

    def _draw_particles(self):
        self._particle_surf.fill((0, 0, 0, 0))
        t = self.clock_ticks * 0.015
        for p in self.particles:
            p["y"] -= p["speed"]
            p["x"] += math.sin(t + p["phase"]) * 0.5
            if p["y"] < -10:
                p.update(self._new_particle())
            r, g, b = p["color"]
            pygame.draw.circle(self._particle_surf, (r, g, b, 25), (int(p["x"]), int(p["y"])), int(p["size"] * 2.5))
            pygame.draw.circle(self._particle_surf, (r, g, b, p["alpha"]), (int(p["x"]), int(p["y"])), int(p["size"]))
        self.screen.blit(self._particle_surf, (0, 0))

    def _build_glow_line(self, width, color):
        surf = pygame.Surface((width, 4), pygame.SRCALPHA)
        r, g, b = color
        for i in range(width):
            fade = math.sin((i / width) * math.pi) ** 1.5
            surf.set_at((i, 1), (r, g, b, int(fade * 180)))
            surf.set_at((i, 2), (r, g, b, int(fade * 70)))
        return surf

    def _draw_glow_line(self, y):
        x = SCREEN_WIDTH // 2 - self._glow_line.get_width() // 2
        self.screen.blit(self._glow_line, (x, y))

    @staticmethod
    def _fmt_time(seconds):
        s = int(seconds)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h}h {m:02d}m {s:02d}s"
        return f"{m:02d}m {s:02d}s"

    def update(self):
        self.clock_ticks += 1
        self.fade_alpha = min(255, self.fade_alpha + 8)
        mouse_pos = pygame.mouse.get_pos()
        self.btn_back.update(mouse_pos)
        if self.page > 0:
            self.btn_prev.update(mouse_pos)
        if self.page < self.total_pages - 1:
            self.btn_next.update(mouse_pos)

    def handle_event(self, event):
        if self.btn_back.is_clicked(event):
            return "MENU"
        if self.page > 0 and self.btn_prev.is_clicked(event):
            self.page -= 1
        if self.page < self.total_pages - 1 and self.btn_next.is_clicked(event):
            self.page += 1
        return None

    def draw(self):
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill((10, 18, 12))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(160)
        overlay.fill((8, 16, 10))
        self.screen.blit(overlay, (0, 0))

        self._draw_particles()

        # ── título ──
        pulse = 0.5 + 0.5 * math.sin(self.clock_ticks * 0.03)
        title_color = (int(160 + 60 * pulse), int(220 + 35 * pulse), int(170 + 40 * pulse))
        title_surf = self.font_title.render("Histórico", True, title_color)
        title_surf.set_alpha(self.fade_alpha)
        self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 68)))
        self._draw_glow_line(100)

        # ── painel ──
        panel_w, panel_h = 760, 460
        panel_x = SCREEN_WIDTH  // 2 - panel_w // 2
        panel_y = 118
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((8, 20, 14, 210))
        self.screen.blit(panel_surf, (panel_x, panel_y))
        pulse_b = 0.5 + 0.5 * math.sin(self.clock_ticks * 0.04)
        pygame.draw.rect(self.screen, (80, 180, 110, int(80 + 80 * pulse_b)),
                         (panel_x, panel_y, panel_w, panel_h), 2, border_radius=6)

        # ── cabeçalho ──
        pad = 24
        col_n   = panel_x + pad
        col_d   = panel_x + pad + 38
        col_t   = panel_x + pad + 260
        col_m   = panel_x + pad + 480
        header_y = panel_y + 14

        for text, x in [("#", col_n), ("Data", col_d), ("Tempo", col_t), ("Mortes", col_m)]:
            s = self.font_header.render(text, True, (100, 200, 130))
            s.set_alpha(self.fade_alpha)
            self.screen.blit(s, (x, header_y))

        sep = pygame.Surface((panel_w - pad * 2, 1), pygame.SRCALPHA)
        sep.fill((80, 160, 100, 80))
        self.screen.blit(sep, (panel_x + pad, header_y + 22))

        # ── linhas de dados ──
        start = self.page * self.ITEMS_PER_PAGE
        items = self.history[start: start + self.ITEMS_PER_PAGE]
        row_h = 40
        row_y = panel_y + 44

        if not self.history:
            empty = self.font_row.render("Nenhuma vitória registrada ainda.", True, (160, 200, 170))
            empty.set_alpha(self.fade_alpha)
            self.screen.blit(empty, empty.get_rect(center=(SCREEN_WIDTH // 2, panel_y + panel_h // 2)))
        else:
            for i, entry in enumerate(items):
                global_idx = start + i + 1
                even = i % 2 == 0
                if even:
                    row_bg = pygame.Surface((panel_w - pad, row_h - 2), pygame.SRCALPHA)
                    row_bg.fill((255, 255, 255, 8))
                    self.screen.blit(row_bg, (panel_x + pad // 2, row_y + i * row_h - 4))

                color = (220, 255, 230) if even else (190, 230, 200)

                def rend(txt, x, y):
                    s = self.font_row.render(txt, True, color)
                    s.set_alpha(self.fade_alpha)
                    self.screen.blit(s, (x, y))

                y = row_y + i * row_h
                rend(str(global_idx), col_n, y)
                rend(entry.get('date', '-'), col_d, y)
                rend(self._fmt_time(entry.get('time_seconds', 0)), col_t, y)
                rend(str(entry.get('deaths', 0)), col_m, y)

        # ── paginação ──
        page_text = self.font_header.render(
            f"Página {self.page + 1} de {self.total_pages}", True, (140, 200, 160)
        )
        page_text.set_alpha(self.fade_alpha)
        self.screen.blit(page_text, page_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)))

        self.btn_back.draw(self.screen)
        if self.page > 0:
            self.btn_prev.draw(self.screen)
        if self.page < self.total_pages - 1:
            self.btn_next.draw(self.screen)