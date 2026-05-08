# =========================
# MENU SCENE
# =========================

import pygame
import os

from asset_loader import load_image
from scenes.scene_base import Scene
from scenes.space_scene import SpaceScene
from settings import *


class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.background = self._load_background()

    def _load_background(self):
        bg_folder = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets",
            "images",
            "background",
        )
        if not os.path.isdir(bg_folder):
            return None

        for filename in sorted(os.listdir(bg_folder)):
            if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                continue
            image = load_image(f"assets/images/background/{filename}")
            return pygame.transform.smoothscale(image, (WIDTH, HEIGHT))

        return None

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    self.game.scene_manager.set(SpaceScene(self.game))
                if e.key == pygame.K_c:
                    self.game.scene_manager.set(SpaceScene(self.game, load_requested=True))

    def draw(self, screen):
        if self.background is not None:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(BLACK)

        font = pygame.font.SysFont(None, 60)
        title = font.render("VOID FRONTIER", True, WHITE)
        sub = font.render("SPACE: New Run  |  C: Continue", True, WHITE)

        screen.blit(title, (WIDTH//2 - 200, HEIGHT//2 - 50))
        screen.blit(sub, (WIDTH//2 - 280, HEIGHT//2 + 20))
