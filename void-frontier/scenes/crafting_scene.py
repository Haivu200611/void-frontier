# =========================
# CRAFTING SCENE
# =========================

import pygame
from scenes.scene_base import Scene
from settings import *


class CraftingScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.options = ["habitat", "battery"]
        self.selected = 0

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.game.scene_manager.pop()

                if e.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)

                if e.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)

                if e.key == pygame.K_RETURN:
                    self.craft()

    def craft(self):
        space_scene = self.game.scene_manager.stack[0]
        item = self.options[self.selected]

        if space_scene.crafting.craft(item):
            print(f"Crafted {item}")
        else:
            print("Not enough resources")

    def draw(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont(None, 40)

        for i, opt in enumerate(self.options):
            color = GREEN if i == self.selected else WHITE
            text = font.render(opt, True, color)
            screen.blit(text, (WIDTH//2 - 100, 200 + i * 50))