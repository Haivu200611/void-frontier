# =========================
# HAZARD
# =========================

import pygame


class RadiationZone:
    def __init__(self, pos, radius):
        self.pos = pygame.Vector2(pos)
        self.radius = radius

    def affect(self, player):
        dist = player.pos.distance_to(self.pos)
        return dist < self.radius

    def draw(self, screen, cam):
        pygame.draw.circle(
            screen,
            (100, 255, 100),
            (int(self.pos.x - cam.x), int(self.pos.y - cam.y)),
            self.radius,
            1
        )


class EMPStorm:
    def __init__(self, pos, radius):
        self.pos = pygame.Vector2(pos)
        self.radius = radius

    def affect(self, player):
        return player.pos.distance_to(self.pos) < self.radius