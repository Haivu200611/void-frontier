# =========================
# HAZARD
# =========================

import pygame

from settings import (
    DEBRIS_IMPACT_DAMAGE,
    EMP_BATTERY_DRAIN,
    RADIATION_PRESSURE_DRAIN,
    RADIATION_TEMPERATURE_DRAIN,
)


class HazardBase:
    COLOR = (255, 255, 255)

    def __init__(self, pos, radius):
        self.pos = pygame.Vector2(pos)
        self.radius = radius

    def contains(self, player):
        return player.pos.distance_to(self.pos) < self.radius

    def get_drain(self, dt):
        return {}

    def on_contact(self, player, survival, dt):
        return

    def draw(self, screen, cam):
        pygame.draw.circle(
            screen,
            self.COLOR,
            (int(self.pos.x - cam.x), int(self.pos.y - cam.y)),
            self.radius,
            1,
        )


class RadiationZone(HazardBase):
    COLOR = (120, 255, 120)

    def get_drain(self, dt):
        return {
            "pressure": RADIATION_PRESSURE_DRAIN,
            "temperature": RADIATION_TEMPERATURE_DRAIN,
        }


class EMPStorm(HazardBase):
    COLOR = (120, 200, 255)

    def get_drain(self, dt):
        return {"battery": EMP_BATTERY_DRAIN}


class DebrisField(HazardBase):
    COLOR = (255, 140, 100)

    def on_contact(self, player, survival, dt):
        survival.damage(DEBRIS_IMPACT_DAMAGE * dt)
        player.vel *= 0.92
