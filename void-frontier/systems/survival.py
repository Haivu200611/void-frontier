# =========================
# SURVIVAL SYSTEM
# =========================

from settings import *


class Survival:
    def __init__(self):
        self.oxygen = 100.0
        self.temperature = 100.0
        self.battery = 100.0
        self.hunger = 100.0
        self.pressure = 100.0

    def update(self, dt):
        self.oxygen -= OXYGEN_DECAY * dt
        self.temperature -= TEMPERATURE_DECAY * dt
        self.battery -= BATTERY_DECAY * dt
        self.hunger -= HUNGER_DECAY * dt

    # -------------------------
    # EFFECTS
    # -------------------------
    def damage(self, amount):
        self.oxygen -= amount

    def heal_oxygen(self, amount):
        self.oxygen = min(100, self.oxygen + amount)

    def restore_temperature(self, amount):
        self.temperature = min(100, self.temperature + amount)

    # -------------------------
    # CHECK
    # -------------------------
    def is_dead(self):
        return (
            self.oxygen <= 0 or
            self.temperature <= 0 or
            self.pressure <= 0
        )