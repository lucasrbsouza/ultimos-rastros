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
        self.font = pygame.font.Font(None, 36)
        
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
            key_surf = pygame.font.Font(None, 28).render('[CHAVE]', True, (255, 215, 0))
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

        label_surf = pygame.font.Font(None, 22).render(label, True, label_color)
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
        hint_surf = pygame.font.Font(None, 24).render(text, True, (180, 180, 180))
        rect = hint_surf.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 8))
        self.display_surface.blit(hint_surf, rect)