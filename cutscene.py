import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Cutscene:
    def __init__(self, surface, lines):
        self.surface = surface
        self.lines = lines

        self._line_index = 0
        self._char_index = 0.0
        self._typewriter_speed = 2  # caracteres por frame

        self.font = pygame.font.Font(None, 52)
        self.font_hint = pygame.font.Font(None, 30)

        self._overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 180))

    def _current_line(self):
        return self.lines[self._line_index]

    def _is_line_complete(self):
        return int(self._char_index) >= len(self._current_line())

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
            if not self._is_line_complete():
                # revela a linha inteira imediatamente
                self._char_index = float(len(self._current_line()))
            else:
                # avança para a próxima linha
                self._line_index += 1
                self._char_index = 0.0
                if self._line_index >= len(self.lines):
                    return "DONE"
        return None

    def update(self):
        if not self._is_line_complete():
            self._char_index += self._typewriter_speed
            if self._char_index > len(self._current_line()):
                self._char_index = float(len(self._current_line()))

    def draw(self):
        self.surface.blit(self._overlay, (0, 0))

        visible_text = self._current_line()[:int(self._char_index)]
        text_surf = self.font.render(visible_text, True, (240, 220, 160))
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.surface.blit(text_surf, text_rect)

        # dica piscante
        if pygame.time.get_ticks() % 1000 < 500:
            hint = "[ESPAÇO] continuar"
            hint_surf = self.font_hint.render(hint, True, (180, 180, 180))
            hint_rect = hint_surf.get_rect(bottomright=(SCREEN_WIDTH - 30, SCREEN_HEIGHT - 20))
            self.surface.blit(hint_surf, hint_rect)
