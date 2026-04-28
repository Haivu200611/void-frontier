# =========================
# MODULES
# =========================

import pygame
from settings import *


class Module:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)

    def update(self, player, survival):
        pass

    def draw(self, screen, cam):
        pass


class Habitat(Module):
    def __init__(self, pos):
        super().__init__(pos)

        self.image = pygame.Surface((60, 60))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=pos)

    def update(self, player, survival):
        dist = player.pos.distance_to(self.pos)

        if dist < 100:
            survival.heal_oxygen(10 * 0.016)

    def draw(self, screen, cam):
        screen.blit(self.image, self.rect.move(-cam))