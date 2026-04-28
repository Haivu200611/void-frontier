# =========================
# MENU SCENE
# =========================

import pygame
from scenes.scene_base import Scene
from scenes.space_scene import SpaceScene
from settings import *


class MenuScene(Scene):
    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    self.game.scene_manager.set(SpaceScene(self.game))

    def draw(self, screen):
        screen.fill(BLACK)

        font = pygame.font.SysFont(None, 60)
        title = font.render("VOID FRONTIER", True, WHITE)
        sub = font.render("Press SPACE to Start", True, WHITE)

        screen.blit(title, (WIDTH//2 - 200, HEIGHT//2 - 50))
        screen.blit(sub, (WIDTH//2 - 220, HEIGHT//2 + 20))