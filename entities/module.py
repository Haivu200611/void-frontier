# =========================
# MODULES
# =========================

import pygame


class Module:
    COLOR = (255, 255, 255)
    RADIUS = 90

    def __init__(self, pos, key):
        self.pos = pygame.Vector2(pos)
        self.key = key
        self.image = pygame.Surface((60, 60))
        self.image.fill(self.COLOR)
        self.rect = self.image.get_rect(center=pos)

    def in_range(self, player):
        return player.pos.distance_to(self.pos) < self.RADIUS

    def update(self, player, survival, dt):
        return

    def draw(self, screen, cam):
        screen.blit(self.image, self.rect.move(-cam))


class Habitat(Module):
    COLOR = (0, 180, 110)

    def __init__(self, pos):
        super().__init__(pos, "habitat")

    def update(self, player, survival, dt):
        if self.in_range(player):
            survival.restore("oxygen", 9.0 * dt)
            survival.restore("temperature", 6.0 * dt)


class Lab(Module):
    COLOR = (105, 150, 255)

    def __init__(self, pos):
        super().__init__(pos, "lab")


class Greenhouse(Module):
    COLOR = (70, 205, 90)

    def __init__(self, pos):
        super().__init__(pos, "greenhouse")

    def update(self, player, survival, dt):
        if self.in_range(player):
            survival.restore("hunger", 8.0 * dt)


class Hangar(Module):
    COLOR = (190, 170, 150)

    def __init__(self, pos):
        super().__init__(pos, "hangar")

    def update(self, player, survival, dt):
        if self.in_range(player):
            survival.restore("pressure", 8.0 * dt)


class SignalTower(Module):
    COLOR = (255, 220, 120)

    def __init__(self, pos):
        super().__init__(pos, "signal_tower")
