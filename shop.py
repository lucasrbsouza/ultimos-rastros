import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, SHOP_POWERS


class ShopScreen:
    def __init__(self, surface, player):
        self.surface = surface
        self.player = player
        self.selected = 0

        self.font_title  = pygame.font.Font(None, 56)
        self.font_item   = pygame.font.Font(None, 34)
        self.font_small  = pygame.font.Font(None, 26)
        self.font_hint   = pygame.font.Font(None, 24)

        self._overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 210))

        self._panel_w = 700
        self._panel_h = 70
        self._panel_x = (SCREEN_WIDTH - self._panel_w) // 2
        self._panel_y0 = 130

    # ── status de cada poder ─────────────────────────────────────────────
    def _get_status(self, power):
        pid = power['id']
        p   = self.player

        if pid == 'rastro_confuso':
            return 'ativo'
        if pid == 'sussurro_mata' and p.sussurro_comprado:
            return 'ativo'
        if pid == 'flecha_fogo' and p.can_shoot:
            return 'ativo'
        if pid == 'voz_floresta' and 'voz_floresta' in p.active_powers:
            return 'ativo'
        if pid == 'sombra_mata' and 'sombra_mata' in p.active_powers:
            return 'ativo'
        if pid == 'guardiao_vida' and p.guardiao_vida_bought:
            return 'ativo'
        if pid == 'chama_ancestral' and p.chama_ancestral_charges > 0:
            return 'carga'

        cost = power['cost']
        if cost == 0:
            return 'ativo'
        if p.memories == cost:
            return 'exato'
        if p.memories > cost:
            return 'pode'
        return 'bloq'

    def _status_label(self, status, charges=0):
        if status == 'ativo':
            return '[ATIVO]',    (80, 220, 100)
        if status == 'carga':
            return f'[{charges}×]', (80, 220, 100)
        if status == 'pode':
            return '[COMPRAR]',  (80, 220, 100)
        if status == 'exato':
            return '[COMPRAR]',  (255, 215, 0)
        return '[BLOQ.]',        (120, 120, 120)

    def _can_buy(self, power):
        status = self._get_status(power)
        if status in ('ativo',):
            if power['id'] != 'chama_ancestral':
                return False
        if power['id'] == 'guardiao_vida' and self.player.guardiao_vida_bought:
            return False
        return self.player.memories >= power['cost'] and power['cost'] > 0

    def _buy(self, power):
        pid = power['id']
        p   = self.player
        p.memories -= power['cost']

        if pid == 'sussurro_mata':
            p.sussurro_comprado = True
        elif pid == 'flecha_fogo':
            p.can_shoot = True
        elif pid == 'voz_floresta':
            if 'voz_floresta' not in p.active_powers:
                p.active_powers.append('voz_floresta')
        elif pid == 'chama_ancestral':
            p.chama_ancestral_charges += 1
        elif pid == 'guardiao_vida':
            p.guardiao_vida_bought = True
            p.max_health += 2
            p.current_health = min(p.current_health + 2, p.max_health)
        elif pid == 'sombra_mata':
            # Poder X extra — SHIFT alterna entre os poderes ativos comprados
            if 'sombra_mata' not in p.active_powers:
                p.active_powers.append('sombra_mata')

    # ── eventos ─────────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                return 'CLOSE'
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(SHOP_POWERS)
            if event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(SHOP_POWERS)
            if event.key in (pygame.K_RETURN, pygame.K_z):
                power = SHOP_POWERS[self.selected]
                if self._can_buy(power):
                    self._buy(power)
        return None

    def update(self):
        pass

    # ── desenho ─────────────────────────────────────────────────────────
    def draw(self):
        self.surface.blit(self._overlay, (0, 0))

        # Título
        title = self.font_title.render('Poderes', True, (240, 200, 80))
        self.surface.blit(title, title.get_rect(midtop=(SCREEN_WIDTH // 2, 50)))

        # Memórias disponíveis
        mem_surf = self.font_small.render(
            f'Memórias disponíveis: {self.player.memories}', True, (200, 200, 200))
        self.surface.blit(mem_surf, mem_surf.get_rect(midtop=(SCREEN_WIDTH // 2, 100)))

        for i, power in enumerate(SHOP_POWERS):
            py = self._panel_y0 + i * (self._panel_h + 6)
            is_sel = (i == self.selected)

            bg_color = (60, 80, 60) if is_sel else (30, 40, 30)
            border_color = (140, 220, 100) if is_sel else (60, 80, 60)
            panel_rect = pygame.Rect(self._panel_x, py, self._panel_w, self._panel_h)
            pygame.draw.rect(self.surface, bg_color,    panel_rect, border_radius=8)
            pygame.draw.rect(self.surface, border_color, panel_rect, 2, border_radius=8)

            status  = self._get_status(power)
            charges = self.player.chama_ancestral_charges if power['id'] == 'chama_ancestral' else 0
            label, lcolor = self._status_label(status, charges)

            # Nome
            name_surf = self.font_item.render(power['name'], True, (240, 230, 180))
            self.surface.blit(name_surf, (self._panel_x + 14, py + 8))

            # Custo
            cost_txt = 'Grátis' if power['cost'] == 0 else f'{power["cost"]} mem.'
            cost_color = (200, 200, 200) if status not in ('pode', 'exato') else (100, 255, 150)
            cost_surf = self.font_small.render(cost_txt, True, cost_color)
            self.surface.blit(cost_surf, (self._panel_x + 14, py + 42))

            # Descrição
            desc_surf = self.font_small.render(power['description'], True, (160, 160, 160))
            self.surface.blit(desc_surf, (self._panel_x + 200, py + 24))

            # Status
            status_surf = self.font_item.render(label, True, lcolor)
            self.surface.blit(status_surf,
                              status_surf.get_rect(midright=(self._panel_x + self._panel_w - 14,
                                                             py + self._panel_h // 2)))

        # Dicas
        hint = '[↑↓] Navegar   [ENTER/Z] Comprar   [ESC/Q] Fechar'
        hint_surf = self.font_hint.render(hint, True, (130, 130, 130))
        self.surface.blit(hint_surf,
                          hint_surf.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 10)))
