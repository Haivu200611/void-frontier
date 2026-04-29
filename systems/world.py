# =========================
# WORLD SYSTEM
# =========================

import random

import pygame

from entities.asteroid import Asteroid
from entities.hazard import DebrisField, EMPStorm, RadiationZone
from entities.module import Greenhouse, Habitat, Hangar, Lab, SignalTower
from settings import (
    ASTEROIDS_PER_CHUNK,
    CHUNK_SIZE,
    SPAWN_POS,
    TOTAL_LOGS,
    TOTAL_TERMINALS,
    ZONE_UNLOCK_REQUIREMENTS,
)


ZONE_ORDER = ["epsilon", "ares-7", "outer-belt", "xenith"]
ZONE_RADII = {
    "epsilon": 1700,
    "ares-7": 3100,
    "outer-belt": 4500,
    "xenith": 100000,
}

ZONE_ASTEROID_TABLE = {
    "epsilon": ["iron", "ice", "copper", "silicon"],
    "ares-7": ["iron", "silicon", "copper", "titanium", "carbon"],
    "outer-belt": ["titanium", "silicon", "carbon", "ice", "copper"],
    "xenith": ["titanium", "carbon", "silicon", "ice"],
}

ZONE_HAZARD_CHANCE = {
    "epsilon": {"radiation": 0.12, "emp": 0.08, "debris": 0.08},
    "ares-7": {"radiation": 0.2, "emp": 0.15, "debris": 0.12},
    "outer-belt": {"radiation": 0.3, "emp": 0.23, "debris": 0.2},
    "xenith": {"radiation": 0.4, "emp": 0.3, "debris": 0.3},
}

ZONE_HP_SCALE = {
    "epsilon": 1.0,
    "ares-7": 1.15,
    "outer-belt": 1.35,
    "xenith": 1.55,
}


class World:
    def __init__(self):
        self.asteroids = pygame.sprite.Group()
        self.hazards = []
        self.modules = []

        self.loaded_chunks = set()
        self.log_nodes = []
        self.terminal_nodes = []
        self._next_log_id = 1
        self._next_terminal_id = 1

    # -------------------------
    # ZONES
    # -------------------------
    def get_zone_name(self, pos):
        center = pygame.Vector2(SPAWN_POS)
        dist = pygame.Vector2(pos).distance_to(center)

        if dist <= ZONE_RADII["epsilon"]:
            return "epsilon"
        if dist <= ZONE_RADII["ares-7"]:
            return "ares-7"
        if dist <= ZONE_RADII["outer-belt"]:
            return "outer-belt"
        return "xenith"

    def is_zone_unlocked(self, zone_name, narrative):
        required_logs = ZONE_UNLOCK_REQUIREMENTS.get(zone_name, 0)
        return narrative.progress() >= required_logs

    def get_unlocked_radius(self, narrative):
        unlocked_zone = "epsilon"
        for zone_name in ZONE_ORDER:
            if self.is_zone_unlocked(zone_name, narrative):
                unlocked_zone = zone_name
        return ZONE_RADII[unlocked_zone]

    # -------------------------
    # CHUNK
    # -------------------------
    def get_chunk(self, pos):
        return (int(pos.x // CHUNK_SIZE), int(pos.y // CHUNK_SIZE))

    def load_chunk(self, cx, cy, narrative):
        if (cx, cy) in self.loaded_chunks:
            return

        chunk_center = pygame.Vector2(
            cx * CHUNK_SIZE + CHUNK_SIZE * 0.5,
            cy * CHUNK_SIZE + CHUNK_SIZE * 0.5,
        )
        zone_name = self.get_zone_name(chunk_center)

        if not self.is_zone_unlocked(zone_name, narrative):
            return

        self.loaded_chunks.add((cx, cy))

        for _ in range(ASTEROIDS_PER_CHUNK):
            x = cx * CHUNK_SIZE + random.randint(0, CHUNK_SIZE)
            y = cy * CHUNK_SIZE + random.randint(0, CHUNK_SIZE)
            asteroid_type = random.choice(ZONE_ASTEROID_TABLE[zone_name])
            hp_scale = ZONE_HP_SCALE[zone_name]
            self.asteroids.add(Asteroid((x, y), asteroid_type, hp_scale=hp_scale))

        hazard_rolls = ZONE_HAZARD_CHANCE[zone_name]
        hx = cx * CHUNK_SIZE + random.randint(80, CHUNK_SIZE - 80)
        hy = cy * CHUNK_SIZE + random.randint(80, CHUNK_SIZE - 80)

        if random.random() < hazard_rolls["radiation"]:
            self.hazards.append(RadiationZone((hx, hy), random.randint(120, 170)))
        if random.random() < hazard_rolls["emp"]:
            self.hazards.append(EMPStorm((hx + 60, hy + 20), random.randint(90, 150)))
        if random.random() < hazard_rolls["debris"]:
            self.hazards.append(DebrisField((hx - 50, hy + 40), random.randint(80, 130)))

        if self._next_log_id <= TOTAL_LOGS and random.random() < 0.18:
            self.log_nodes.append(
                {
                    "id": self._next_log_id,
                    "pos": pygame.Vector2(chunk_center),
                    "zone": zone_name,
                    "collected": False,
                }
            )
            self._next_log_id += 1

        if self._next_terminal_id <= TOTAL_TERMINALS and random.random() < 0.08:
            self.terminal_nodes.append(
                {
                    "id": f"terminal_{self._next_terminal_id}",
                    "pos": pygame.Vector2(chunk_center.x + 110, chunk_center.y - 80),
                    "zone": zone_name,
                    "used": False,
                }
            )
            self._next_terminal_id += 1

    # -------------------------
    # BASE BUILDING
    # -------------------------
    def add_module(self, module_key, pos):
        constructors = {
            "habitat": Habitat,
            "lab": Lab,
            "greenhouse": Greenhouse,
            "hangar": Hangar,
            "signal_tower": SignalTower,
        }
        module_cls = constructors.get(module_key)
        if module_cls:
            self.modules.append(module_cls(pos))

    # -------------------------
    # INTERACTION
    # -------------------------
    def interact(self, player, narrative):
        for node in self.log_nodes:
            if not node["collected"] and player.pos.distance_to(node["pos"]) < 90:
                node["collected"] = True
                narrative.unlock_log(node["id"])
                return f"Collected log #{node['id']}"

        for terminal in self.terminal_nodes:
            if not terminal["used"] and player.pos.distance_to(terminal["pos"]) < 100:
                terminal["used"] = True
                narrative.unlock_terminal(terminal["id"])
                return f"Unlocked {terminal['id']}"

        return None

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, player, narrative, survival, dt):
        cx, cy = self.get_chunk(player.pos)

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                self.load_chunk(cx + dx, cy + dy, narrative)

        self.asteroids.update(dt)

        extra_drain = {}
        for hazard in self.hazards:
            if hazard.contains(player):
                drains = hazard.get_drain(dt)
                for stat, rate in drains.items():
                    extra_drain[stat] = extra_drain.get(stat, 0.0) + rate
                hazard.on_contact(player, survival, dt)

        for module in self.modules:
            module.update(player, survival, dt)

        return extra_drain

    # -------------------------
    # DRAW
    # -------------------------
    def draw(self, screen, cam):
        for a in self.asteroids:
            screen.blit(a.image, a.rect.move(-cam))

        for module in self.modules:
            module.draw(screen, cam)

        for h in self.hazards:
            h.draw(screen, cam)

        for node in self.log_nodes:
            if node["collected"]:
                continue
            pygame.draw.circle(
                screen,
                (255, 190, 90),
                (int(node["pos"].x - cam.x), int(node["pos"].y - cam.y)),
                9,
            )

        for terminal in self.terminal_nodes:
            if terminal["used"]:
                continue
            pygame.draw.rect(
                screen,
                (120, 255, 220),
                pygame.Rect(
                    int(terminal["pos"].x - cam.x - 7),
                    int(terminal["pos"].y - cam.y - 12),
                    14,
                    24,
                ),
                2,
            )
