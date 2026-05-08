# =========================
# DIALOGUE UI
# =========================

import pygame

from settings import HEIGHT, WHITE, WIDTH


class DialogueUI:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 28)
        self.active = False
        self.text_queue = []
        self.current_text = ""
        self.displayed_text = ""
        self.timer = 0.0
        self.speed = 42  # characters per second

    def start(self, texts):
        self.text_queue = [str(t) for t in texts if str(t).strip()]
        self.next()

    def next(self):
        if self.text_queue:
            self.current_text = self.text_queue.pop(0)
            self.displayed_text = ""
            self.timer = 0.0
            self.active = True
        else:
            self.active = False

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt * self.speed
        length = int(self.timer)
        if length >= len(self.current_text):
            self.displayed_text = self.current_text
        else:
            self.displayed_text = self.current_text[:length]

    def handle_input(self, event):
        if not self.active:
            return
        if event.key == pygame.K_RETURN:
            if self.displayed_text != self.current_text:
                self.displayed_text = self.current_text
            else:
                self.next()

    def _wrap_text(self, text, max_width):
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            trial = f"{current} {word}".strip()
            if self.font.size(trial)[0] <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def draw(self, screen):
        if not self.active:
            return

        box = pygame.Rect(44, HEIGHT - 180, WIDTH - 88, 130)
        pygame.draw.rect(screen, (4, 6, 15), box)
        pygame.draw.rect(screen, WHITE, box, 2)

        lines = self._wrap_text(self.displayed_text, box.width - 24)[:3]
        for i, line in enumerate(lines):
            text = self.font.render(line, True, WHITE)
            screen.blit(text, (box.x + 12, box.y + 16 + i * 30))

        hint = self.font.render("ENTER to continue", True, WHITE)
        screen.blit(hint, (box.x + box.width - 190, box.y + box.height - 30))
