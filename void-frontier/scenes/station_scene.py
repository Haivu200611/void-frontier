# =========================
# STATION SCENE
# =========================

import pygame
from scenes.scene_base import Scene
from settings import *


class StationScene(Scene):
    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.game.scene_manager.pop()

    def draw(self, screen):
        screen.fill((30, 30, 30))

        font = pygame.font.SysFont(None, 40)
        text = font.render("ARES-7 STATION", True, WHITE)
        sub = font.render("ESC to exit", True, WHITE)

        screen.blit(text, (WIDTH//2 - 150, HEIGHT//2 - 20))
        screen.blit(sub, (WIDTH//2 - 120, HEIGHT//2 + 30))