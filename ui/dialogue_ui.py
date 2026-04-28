# =========================
# DIALOGUE UI
# =========================

import pygame
from settings import *


class DialogueUI:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 28)

        self.active = False
        self.text_queue = []

        self.current_text = ""
        self.displayed_text = ""

        self.timer = 0
        self.speed = 40  # ký tự / giây

    # -------------------------
    # START
    # -------------------------
    def start(self, texts):
        self.text_queue = list(texts)
        self.next()

    def next(self):
        if self.text_queue:
            self.current_text = self.text_queue.pop(0)
            self.displayed_text = ""
            self.timer = 0
            self.active = True
        else:
            self.active = False

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, dt):
        if not self.active:
            return

        self.timer += dt * self.speed
        length = int(self.timer)

        self.displayed_text = self.current_text[:length]

    # -------------------------
    # INPUT
    # -------------------------
    def handle_input(self, event):
        if not self.active:
            return

        if event.key == pygame.K_RETURN:
            self.next()

    # -------------------------
    # DRAW
    # -------------------------
    def draw(self, screen):
        if not self.active:
            return

        box = pygame.Rect(50, HEIGHT - 140, WIDTH - 100, 90)

        pygame.draw.rect(screen, (0, 0, 0), box)
        pygame.draw.rect(screen, WHITE, box, 2)

        text = self.font.render(self.displayed_text, True, WHITE)
        screen.blit(text, (box.x + 10, box.y + 20))