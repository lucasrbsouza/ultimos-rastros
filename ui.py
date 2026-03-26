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
        
    def show_memories(self, amount, stage):
        """Desenha o contador de memórias e o estágio atual."""
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

    def show_brado_cooldown(self, ratio):
        """Exibe o indicador de cooldown do Brado. ratio None = não exibe."""
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

        fill_color = (100, 255, 150) if is_ready else (200, 130, 40)
        if fill_w > 0:
            pygame.draw.rect(self.display_surface, fill_color,
                             (bar_x, bar_y, fill_w, bar_h), border_radius=4)

        pygame.draw.rect(self.display_surface, (80, 80, 80),
                         (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)

        label = 'PRONTO  [X]' if is_ready else 'Brado...'
        label_color = (100, 255, 150) if is_ready else (180, 120, 40)
        label_surf = pygame.font.Font(None, 22).render(label, True, label_color)
        self.display_surface.blit(label_surf, (bar_x + bar_w + 8, bar_y - 2))