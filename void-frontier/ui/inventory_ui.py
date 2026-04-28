# =========================
# INVENTORY UI
# =========================

import pygame
from settings import *


class InventoryUI:
    def __init__(self, inventory):
        self.inventory = inventory
        self.visible = False
        self.selected = 0

        self.font = pygame.font.SysFont(None, 32)

    # -------------------------
    # TOGGLE
    # -------------------------
    def toggle(self):
        self.visible = not self.visible

    # -------------------------
    # INPUT
    # -------------------------
    def handle_input(self, event):
        items = list(self.inventory.get_all().keys())

        if not items:
            return

        if event.key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(items)

        if event.key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(items)

    # -------------------------
    # DRAW
    # -------------------------
    def draw(self, screen):
        if not self.visible:
            return

        # overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        items = list(self.inventory.get_all().items())

        for i, (name, amount) in enumerate(items):
            color = GREEN if i == self.selected else WHITE
            text = self.font.render(f"{name}: {amount}", True, color)

            screen.blit(text, (WIDTH // 2 - 100, 200 + i * 40))