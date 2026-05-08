# =========================
# MODULES
# =========================

import pygame
from asset_loader import load_image


class Module:
    COLOR = (255, 255, 255)
    RADIUS = 90
    TEXTURE_PATH = None

    def __init__(self, pos, key):
        self.pos = pygame.Vector2(pos)
        self.key = key
        self.image = self._build_image()
        self.rect = self.image.get_rect(center=pos)

    def _build_image(self):
        if self.TEXTURE_PATH:
            return load_image(self.TEXTURE_PATH)
        image = pygame.Surface((60, 60))
        image.fill(self.COLOR)
        return image

    def in_range(self, player):
        return player.pos.distance_to(self.pos) < self.RADIUS

    def update(self, player, survival, dt):
        return

    def draw(self, screen, cam):
        screen.blit(self.image, self.rect.move(-cam))


class Habitat(Module):
    COLOR = (0, 180, 110)
    TEXTURE_PATH = "assets/images/modules/module_habitat/texture.png"

    def __init__(self, pos):
        super().__init__(pos, "habitat")

    def update(self, player, survival, dt):
        if self.in_range(player):
            survival.restore("oxygen", 9.0 * dt)
            survival.restore("temperature", 6.0 * dt)


class Lab(Module):
    COLOR = (105, 150, 255)
    TEXTURE_PATH = "assets/images/modules/module_lab/texture.png"

    def __init__(self, pos):
        super().__init__(pos, "lab")

    def update(self, player, survival, dt):
        if self.in_range(player):
            survival.restore("battery", 6.5 * dt)


class Greenhouse(Module):
    COLOR = (70, 205, 90)
    TEXTURE_PATH = "assets/images/modules/module_greenhouse/texture.png"

    def __init__(self, pos):
        super().__init__(pos, "greenhouse")

    def update(self, player, survival, dt):
        if self.in_range(player):
            survival.restore("hunger", 8.0 * dt)


class Hangar(Module):
    COLOR = (190, 170, 150)
    TEXTURE_PATH = "assets/images/modules/module_hangar/texture.png"

    def __init__(self, pos):
        super().__init__(pos, "hangar")

    def update(self, player, survival, dt):
        if self.in_range(player):
            survival.restore("pressure", 8.0 * dt)


class SignalTower(Module):
    COLOR = (255, 220, 120)
    TEXTURE_PATH = "assets/images/modules/module_signal_tower/texture.png"

    def __init__(self, pos):
        super().__init__(pos, "signal_tower")

    def update(self, player, survival, dt):
        if self.in_range(player):
            survival.restore("oxygen", 2.5 * dt)
            survival.restore("pressure", 2.5 * dt)
