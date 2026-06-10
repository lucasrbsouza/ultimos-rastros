import pygame
from settings import *

class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        
        # Cores para o efeito visual de hover
        self.color_normal = (50, 80, 60) 
        self.color_hover = (70, 110, 80)
        self.color_text = COLOR_TEXT
        
        self.is_hovered = False

    def update(self, mouse_pos):
        """Verifica se o mouse está sobre o botão."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        """Verifica se o botão foi clicado com o botão esquerdo do mouse."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

    def draw(self, screen):
        """Renderiza o botão na tela."""
        # Altera a cor se o mouse estiver por cima
        current_color = self.color_hover if self.is_hovered else self.color_normal
        pygame.draw.rect(screen, current_color, self.rect, border_radius=8)

        # Desenha o texto centralizado no retângulo
        text_surf = self.font.render(self.text, True, self.color_text)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class HUD:
    def __init__(self, surface):
        self.display_surface = surface
        # Fontes cacheadas — evita recriar Font a cada frame (input lag)
        self.font        = pygame.font.Font(None, 36)
        self.font_key    = pygame.font.Font(None, 28)
        self.font_cd     = pygame.font.Font(None, 22)
        self.font_hint   = pygame.font.Font(None, 24)
        self.font_switch = pygame.font.Font(None, 30)
        
    def show_health(self, current, maximum):
        """Desenha a barra de vida no canto superior esquerdo."""
        bar_width = 30
        bar_height = 20
        # Fundo vermelho (vida perdida)
        pygame.draw.rect(self.display_surface, (150, 50, 50), (20, 20, maximum * bar_width, bar_height))
        # Frente verde (vida atual)
        pygame.draw.rect(self.display_surface, (50, 200, 80), (20, 20, current * bar_width, bar_height))
        
    def show_memories(self, amount, stage, has_key=False):
        """Desenha o contador de memórias, estágio atual e indicador de chave."""
        text_surf = self.font.render(f'Memórias: {amount}', True, COLOR_TEXT)
        self.display_surface.blit(text_surf, text_surf.get_rect(topleft=(20, 50)))

        stage_names = {
            'rastro_confuso':    ('Rastro Confuso',    (160, 160, 160)),
            'passos_invisiveis': ('Passos Invisíveis',  (100, 200, 255)),
            'sussurro_mata':     ('Sussurro da Mata',   (100, 255, 150)),
            'guardiao_desperto': ('Guardião Desperto',  (255, 215,   0)),
        }
        nome, cor = stage_names.get(stage, ('???', (255, 255, 255)))
        stage_surf = self.font.render(nome, True, cor)
        self.display_surface.blit(stage_surf, stage_surf.get_rect(topleft=(20, 78)))

        if has_key:
            key_surf = self.font_key.render('[CHAVE]', True, (255, 215, 0))
            self.display_surface.blit(key_surf, key_surf.get_rect(topright=(SCREEN_WIDTH - 20, 50)))

    def show_score(self, score):
        """Exibe a pontuação no canto superior direito."""
        text_surf = self.font.render(f'{score}', True, (255, 230, 80))
        self.display_surface.blit(text_surf, text_surf.get_rect(topright=(SCREEN_WIDTH - 20, 20)))

    def show_power_cooldown(self, ratio, power_name, power_active=False):
        """Exibe cooldown do poder X ativo. ratio None = sem poder."""
        if ratio is None:
            return

        bar_x    = 20
        bar_y    = 108
        bar_w    = 160
        bar_h    = 10
        fill_w   = int(bar_w * ratio)
        is_ready = ratio >= 1.0

        pygame.draw.rect(self.display_surface, (40, 40, 40),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=4)

        if power_active:
            fill_color = (120, 80, 200)
        elif is_ready:
            fill_color = (100, 255, 150)
        else:
            fill_color = (200, 130, 40)

        if fill_w > 0:
            pygame.draw.rect(self.display_surface, fill_color,
                             (bar_x, bar_y, fill_w, bar_h), border_radius=4)

        pygame.draw.rect(self.display_surface, (80, 80, 80),
                         (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)

        short_name = power_name.split()[-1] if power_name else 'X'
        if power_active:
            label = f'ATIVO [{short_name}]'
            label_color = (160, 100, 255)
        elif is_ready:
            label = f'PRONTO [X]'
            label_color = (100, 255, 150)
        else:
            label = f'CD: {short_name}'
            label_color = (180, 120, 40)

        label_surf = self.font_cd.render(label, True, label_color)
        self.display_surface.blit(label_surf, (bar_x + bar_w + 8, bar_y - 2))

    def show_hints(self, player):
        """Dicas de tecla no rodapé central — só mostra poderes desbloqueados."""
        hints = ['[Q] Poderes']
        if player.can_shoot:
            hints.append('[Z] Atacar')
        if player.active_powers:
            hints.append('[X] Poder')
        if len(player.active_powers) > 1:
            hints.append('[SHIFT] Trocar')
        hints.append('[H] Ajuda')

        text = '   '.join(hints)
        hint_surf = self.font_hint.render(text, True, (180, 180, 180))
        rect = hint_surf.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 8))
        self.display_surface.blit(hint_surf, rect)

    def show_power_switch(self, player):
        """Banner transitório ao trocar o poder X com SHIFT — diz qual poder está ativo."""
        t = getattr(player, 'power_switch_feedback_time', 0)
        if not t:
            return
        elapsed = pygame.time.get_ticks() - t
        duration = 1500
        if elapsed > duration:
            return
        name = player.get_active_power_name()
        if not name:
            return

        # mantém visível e some nos últimos 450ms
        if elapsed < duration - 450:
            alpha = 255
        else:
            alpha = max(0, int(255 * (duration - elapsed) / 450))

        text = self.font_switch.render(f'Poder X: {name}', True, (210, 180, 255))
        pad_x, pad_y = 14, 9
        box_w = text.get_width() + pad_x * 2
        box_h = text.get_height() + pad_y * 2
        toast = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        toast.fill((28, 14, 48, 220))
        pygame.draw.rect(toast, (150, 100, 230), toast.get_rect(), 2, border_radius=8)
        toast.blit(text, (pad_x, pad_y))
        toast.set_alpha(alpha)
        # logo abaixo da barra de cooldown do poder (bar_y=108, bar_h=10)
        self.display_surface.blit(toast, (20, 126))


# ── Feedback de corrida no mapa (linhas de velocidade) ──────────────────────
_STREAK_MAX_LEN = 220
_streak_line_surf = None   # surface pequena reutilizada por linha
_vignette_top = None       # banda superior (construída 1x)
_vignette_bottom = None    # banda inferior (construída 1x)


def draw_run_streaks(surface, player):
    """Linhas de velocidade + vinheta nas bordas enquanto corre.
    Usa run_anim_intensity (ramp por is_running) — NÃO current_speed, que é
    zerado nas margens. Desenho barato: blits pequenos + 2 bandas cacheadas,
    sem surface fullscreen com alpha por frame (evitava travar o jogo ao correr)."""
    ratio = getattr(player, 'run_anim_intensity', 0.0)
    if ratio <= 0.05:
        return
    ratio = min(ratio, 1.0)

    global _streak_line_surf, _vignette_top, _vignette_bottom
    if _streak_line_surf is None:
        _streak_line_surf = pygame.Surface((_STREAK_MAX_LEN, 3), pygame.SRCALPHA)

    ticks = pygame.time.get_ticks()
    moving_right = player.direction.x > 0
    ls = _streak_line_surf
    for i in range(12):
        y = (i * 53 + 31) % SCREEN_HEIGHT
        length = int((60 + (i * 37) % 120) * (0.4 + 0.6 * ratio))
        length = max(8, min(length, _STREAK_MAX_LEN))
        speed_px = 22 + (i % 5) * 8
        x = (ticks * speed_px // 16 + i * 97) % (SCREEN_WIDTH + length)
        sx = (SCREEN_WIDTH - x) if moving_right else (x - length)
        a = min(int(60 * ratio) + (i % 3) * 12, 130)
        ls.fill((0, 0, 0, 0))
        pygame.draw.line(ls, (205, 255, 215, a), (0, 1), (length, 1), 2)
        surface.blit(ls, (sx, y), (0, 0, length, 3))

    # vinheta nas bordas — bandas construídas 1x, só ajusta alpha por frame
    if _vignette_top is None:
        band = max(SCREEN_HEIGHT // 8, 1)
        _vignette_top = pygame.Surface((SCREEN_WIDTH, band), pygame.SRCALPHA)
        _vignette_bottom = pygame.Surface((SCREEN_WIDTH, band), pygame.SRCALPHA)
        for j in range(band):
            pygame.draw.line(_vignette_top, (8, 16, 10, int(150 * (1 - j / band))),
                             (0, j), (SCREEN_WIDTH, j))
            pygame.draw.line(_vignette_bottom, (8, 16, 10, int(150 * (j / band))),
                             (0, j), (SCREEN_WIDTH, j))
    band_h = _vignette_top.get_height()
    _vignette_top.set_alpha(int(200 * ratio))
    _vignette_bottom.set_alpha(int(200 * ratio))
    surface.blit(_vignette_top, (0, 0))
    surface.blit(_vignette_bottom, (0, SCREEN_HEIGHT - band_h))