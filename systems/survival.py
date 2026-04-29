# =========================
# SURVIVAL SYSTEM
# =========================

from settings import (
    BATTERY_DECAY,
    HUNGER_DECAY,
    MAX_STAT,
    OXYGEN_DECAY,
    PRESSURE_DECAY,
    TEMPERATURE_DECAY,
)


class Survival:
    def __init__(self):
        self.stats = {
            "oxygen": MAX_STAT,
            "temperature": MAX_STAT,
            "battery": MAX_STAT,
            "hunger": MAX_STAT,
            "pressure": MAX_STAT,
        }

        self.base_drain = {
            "oxygen": OXYGEN_DECAY,
            "temperature": TEMPERATURE_DECAY,
            "battery": BATTERY_DECAY,
            "hunger": HUNGER_DECAY,
            "pressure": PRESSURE_DECAY,
        }

    # -------------------------
    # CORE LOOP
    # -------------------------
    def update(self, dt, extra_drain=None):
        if extra_drain is None:
            extra_drain = {}

        for stat, drain in self.base_drain.items():
            self.modify(stat, -(drain + extra_drain.get(stat, 0.0)) * dt)

        # pressure critical -> oxygen leak harder
        if self.stats["pressure"] <= 0:
            self.modify("oxygen", -10.0 * dt)

        # hunger critical -> body temperature harder to maintain
        if self.stats["hunger"] <= 0:
            self.modify("temperature", -6.0 * dt)

    # -------------------------
    # EFFECTS / HEALS
    # -------------------------
    def modify(self, stat, delta):
        if stat not in self.stats:
            return
        self.stats[stat] = max(0.0, min(MAX_STAT, self.stats[stat] + delta))

    def drain(self, stat, amount):
        self.modify(stat, -amount)

    def restore(self, stat, amount):
        self.modify(stat, amount)

    def damage(self, amount):
        self.drain("pressure", amount)

    def heal_oxygen(self, amount):
        self.restore("oxygen", amount)

    def restore_temperature(self, amount):
        self.restore("temperature", amount)

    # -------------------------
    # ACCESSORS
    # -------------------------
    @property
    def oxygen(self):
        return self.stats["oxygen"]

    @property
    def temperature(self):
        return self.stats["temperature"]

    @property
    def battery(self):
        return self.stats["battery"]

    @property
    def hunger(self):
        return self.stats["hunger"]

    @property
    def pressure(self):
        return self.stats["pressure"]

    def is_dead(self):
        return (
            self.stats["oxygen"] <= 0
            or self.stats["temperature"] <= 0
            or self.stats["pressure"] <= 0
        )
