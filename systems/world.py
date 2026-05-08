# =========================
# WORLD SYSTEM
# =========================

import random
from collections import deque

import pygame

from entities.asteroid import Asteroid
from entities.hazard import DebrisField, EMPStorm, RadiationZone
from entities.module import Greenhouse, Habitat, Hangar, Lab, SignalTower
from systems.physics import BODY_SENSOR, BODY_STATIC, Collider, LAYER_PLAYER, LAYER_STATIC, LAYER_TRIGGER
from settings import (
    ASTEROIDS_PER_CHUNK,
    CHUNK_SIZE,
    CHUNK_LOAD_RADIUS,
    RADAR_MAX_ASTEROIDS,
    SPAWN_POS,
    TOTAL_LOGS,
    TOTAL_TERMINALS,
    MAX_CHUNK_LOADS_PER_FRAME,
    WORLD_CLEANUP_INTERVAL,
    WORLD_KEEP_CHUNK_RADIUS,
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

ZONE_BASE_DRAIN = {
    "epsilon": {},
    "ares-7": {"battery": 0.35, "temperature": 0.2},
    "outer-belt": {"battery": 0.7, "temperature": 0.45, "pressure": 0.35},
    "xenith": {"battery": 1.0, "temperature": 0.8, "pressure": 0.65, "oxygen": 0.4},
}


class World:
    def __init__(self):
        self.asteroids = pygame.sprite.Group()
        self.hazards = []
        self.modules = []
        self._cleanup_timer = 0.0

        self.loaded_chunks = set()
        self.pending_chunks = deque()
        self.pending_chunk_set = set()
        self.log_nodes = []
        self.terminal_nodes = []
        self._next_log_id = 1
        self._next_terminal_id = 1
        self._active_asteroids = []
        self.station_node = {
            "id": "ares-7-station",
            "pos": pygame.Vector2(SPAWN_POS[0] + 1900, SPAWN_POS[1] - 380),
        }

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
        if (cx, cy) in self.pending_chunk_set:
            return
        self.pending_chunks.append((cx, cy))
        self.pending_chunk_set.add((cx, cy))

    def _spawn_chunk(self, cx, cy, narrative):
        chunk_center = pygame.Vector2(
            cx * CHUNK_SIZE + CHUNK_SIZE * 0.5,
            cy * CHUNK_SIZE + CHUNK_SIZE * 0.5,
        )
        zone_name = self.get_zone_name(chunk_center)

        if not self.is_zone_unlocked(zone_name, narrative):
            return

        self.loaded_chunks.add((cx, cy))

        for _ in range(ASTEROIDS_PER_CHUNK):
            attempts = 0
            x = cx * CHUNK_SIZE + random.randint(0, CHUNK_SIZE)
            y = cy * CHUNK_SIZE + random.randint(0, CHUNK_SIZE)
            # Keep early gameplay stable: avoid immediate asteroid overlap near spawn point.
            while (
                pygame.Vector2(x, y).distance_to(pygame.Vector2(SPAWN_POS)) < 220
                and attempts < 4
            ):
                x = cx * CHUNK_SIZE + random.randint(0, CHUNK_SIZE)
                y = cy * CHUNK_SIZE + random.randint(0, CHUNK_SIZE)
                attempts += 1
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
                return {
                    "kind": "log",
                    "message": f"Collected log #{node['id']}",
                    "id": node["id"],
                }

        for terminal in self.terminal_nodes:
            if not terminal["used"] and player.pos.distance_to(terminal["pos"]) < 100:
                terminal["used"] = True
                narrative.unlock_terminal(terminal["id"])
                return {
                    "kind": "terminal",
                    "message": f"Unlocked {terminal['id']}",
                    "id": terminal["id"],
                }

        if (
            narrative.progress() >= ZONE_UNLOCK_REQUIREMENTS.get("ares-7", 5)
            and player.pos.distance_to(self.station_node["pos"]) < 120
        ):
            return {
                "kind": "station",
                "message": "Docked at ARES-7 station",
                "id": self.station_node["id"],
            }

        return None

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, player, narrative, survival, dt):
        cx, cy = self.get_chunk(player.pos)
        zone_name = self.get_zone_name(player.pos)

        for dx in range(-CHUNK_LOAD_RADIUS, CHUNK_LOAD_RADIUS + 1):
            for dy in range(-CHUNK_LOAD_RADIUS, CHUNK_LOAD_RADIUS + 1):
                self.load_chunk(cx + dx, cy + dy, narrative)

        processed = 0
        while self.pending_chunks and processed < MAX_CHUNK_LOADS_PER_FRAME:
            target_cx, target_cy = self.pending_chunks.popleft()
            self.pending_chunk_set.discard((target_cx, target_cy))
            if (target_cx, target_cy) in self.loaded_chunks:
                continue
            self._spawn_chunk(target_cx, target_cy, narrative)
            processed += 1

        self._cleanup_timer += dt
        if self._cleanup_timer >= WORLD_CLEANUP_INTERVAL:
            self._cleanup_timer = 0.0
            self.unload_far_content(cx, cy)

        update_radius_px = CHUNK_SIZE * (CHUNK_LOAD_RADIUS + 1.5)
        update_radius_sq = update_radius_px * update_radius_px
        self._active_asteroids = []
        for asteroid in self.asteroids:
            dx = asteroid.rect.centerx - player.pos.x
            dy = asteroid.rect.centery - player.pos.y
            if dx * dx + dy * dy <= update_radius_sq:
                self._active_asteroids.append(asteroid)
                asteroid.update(dt)

        extra_drain = {}
        for stat, rate in ZONE_BASE_DRAIN.get(zone_name, {}).items():
            extra_drain[stat] = extra_drain.get(stat, 0.0) + rate
        for hazard in self.hazards:
            dx = hazard.pos.x - player.pos.x
            dy = hazard.pos.y - player.pos.y
            max_relevant = hazard.radius + CHUNK_SIZE
            if dx * dx + dy * dy > max_relevant * max_relevant:
                continue
            if hazard.contains(player):
                drains = hazard.get_drain(dt)
                for stat, rate in drains.items():
                    extra_drain[stat] = extra_drain.get(stat, 0.0) + rate
                hazard.on_contact(player, survival, dt)

        for module in self.modules:
            module.update(player, survival, dt)

        return extra_drain

    def unload_far_content(self, cx, cy):
        keep_radius = WORLD_KEEP_CHUNK_RADIUS
        self.loaded_chunks = {
            (x, y)
            for (x, y) in self.loaded_chunks
            if abs(x - cx) <= keep_radius and abs(y - cy) <= keep_radius
        }

        for asteroid in list(self.asteroids):
            ax, ay = self.get_chunk(pygame.Vector2(asteroid.rect.center))
            if abs(ax - cx) > keep_radius or abs(ay - cy) > keep_radius:
                self.asteroids.remove(asteroid)
        self._active_asteroids = [
            asteroid for asteroid in self._active_asteroids if asteroid in self.asteroids
        ]

        kept_hazards = []
        for hazard in self.hazards:
            hx, hy = self.get_chunk(hazard.pos)
            if abs(hx - cx) <= keep_radius and abs(hy - cy) <= keep_radius:
                kept_hazards.append(hazard)
        self.hazards = kept_hazards

    def get_radar_points(self, player_pos, size):
        scale = 0.02
        half_size = size // 2
        points = []
        source = self._active_asteroids if self._active_asteroids else self.asteroids
        for asteroid in source:
            dx = int((asteroid.rect.centerx - player_pos.x) * scale)
            dy = int((asteroid.rect.centery - player_pos.y) * scale)
            if abs(dx) < half_size and abs(dy) < half_size:
                points.append((dx, dy))
                if len(points) >= RADAR_MAX_ASTEROIDS:
                    break
        return points

    def handle_player_asteroid_collisions(self, player):
        max_impact_speed = 0.0
        px = player.pos.x
        py = player.pos.y

        for asteroid in self._active_asteroids:
            # Cheap broad-phase check before rect collision.
            if abs(asteroid.rect.centerx - px) > 220 or abs(asteroid.rect.centery - py) > 220:
                continue

            if not asteroid.rect.colliderect(player.rect):
                continue

            impact_speed = asteroid.resolve_player_collision(player)
            if impact_speed > max_impact_speed:
                max_impact_speed = impact_speed

        return max_impact_speed

    # -------------------------
    # DRAW
    # -------------------------
    def draw(self, screen, cam):
        viewport = pygame.Rect(
            int(cam.x) - 128,
            int(cam.y) - 128,
            screen.get_width() + 256,
            screen.get_height() + 256,
        )

        for a in self.asteroids:
            if a.rect.colliderect(viewport):
                screen.blit(a.image, a.rect.move(-cam))

        for module in self.modules:
            if module.rect.colliderect(viewport):
                module.draw(screen, cam)

        for h in self.hazards:
            h_rect = pygame.Rect(
                int(h.pos.x - h.radius),
                int(h.pos.y - h.radius),
                int(h.radius * 2),
                int(h.radius * 2),
            )
            if h_rect.colliderect(viewport):
                h.draw(screen, cam)

        for node in self.log_nodes:
            if node["collected"]:
                continue
            if not viewport.collidepoint(int(node["pos"].x), int(node["pos"].y)):
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
            if not viewport.collidepoint(int(terminal["pos"].x), int(terminal["pos"].y)):
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

        pygame.draw.rect(
            screen,
            (190, 190, 220),
            pygame.Rect(
                int(self.station_node["pos"].x - cam.x - 12),
                int(self.station_node["pos"].y - cam.y - 12),
                24,
                24,
            ),
            2,
        )

    def get_interaction_hint(self, player, narrative):
        for node in self.log_nodes:
            if not node["collected"] and player.pos.distance_to(node["pos"]) < 110:
                return "Press E to collect log"
        for terminal in self.terminal_nodes:
            if not terminal["used"] and player.pos.distance_to(terminal["pos"]) < 120:
                return "Press E to unlock terminal"
        if (
            narrative.progress() >= ZONE_UNLOCK_REQUIREMENTS.get("ares-7", 5)
            and player.pos.distance_to(self.station_node["pos"]) < 130
        ):
            return "Press E to dock at ARES-7 station"
        return ""

    def get_collision_colliders(self, narrative):
        colliders = []

        # Base modules are treated as static obstacles.
        for module in self.modules:
            rect = module.rect.inflate(-10, -10)
            colliders.append(
                Collider(
                    owner=module,
                    rect=rect.copy(),
                    body_type=BODY_STATIC,
                    layer=LAYER_STATIC,
                    mask=LAYER_PLAYER,
                    restitution=0.0,
                )
            )

        # Station has a small solid hull once unlocked.
        if narrative.progress() >= ZONE_UNLOCK_REQUIREMENTS.get("ares-7", 5):
            station_hull = pygame.Rect(0, 0, 72, 72)
            station_hull.center = (
                int(self.station_node["pos"].x),
                int(self.station_node["pos"].y),
            )
            colliders.append(
                Collider(
                    owner=self.station_node,
                    rect=station_hull,
                    body_type=BODY_STATIC,
                    layer=LAYER_STATIC,
                    mask=LAYER_PLAYER,
                    restitution=0.0,
                )
            )

        # Triggers: near-interaction sensors for logs/terminals/station.
        for node in self.log_nodes:
            if node["collected"]:
                continue
            rect = pygame.Rect(0, 0, 92, 92)
            rect.center = (int(node["pos"].x), int(node["pos"].y))
            colliders.append(
                Collider(
                    owner={"kind": "log", "id": node["id"]},
                    rect=rect,
                    body_type=BODY_SENSOR,
                    is_trigger=True,
                    layer=LAYER_TRIGGER,
                    mask=LAYER_PLAYER,
                )
            )

        for terminal in self.terminal_nodes:
            if terminal["used"]:
                continue
            rect = pygame.Rect(0, 0, 100, 100)
            rect.center = (int(terminal["pos"].x), int(terminal["pos"].y))
            colliders.append(
                Collider(
                    owner={"kind": "terminal", "id": terminal["id"]},
                    rect=rect,
                    body_type=BODY_SENSOR,
                    is_trigger=True,
                    layer=LAYER_TRIGGER,
                    mask=LAYER_PLAYER,
                )
            )

        if narrative.progress() >= ZONE_UNLOCK_REQUIREMENTS.get("ares-7", 5):
            rect = pygame.Rect(0, 0, 126, 126)
            rect.center = (
                int(self.station_node["pos"].x),
                int(self.station_node["pos"].y),
            )
            colliders.append(
                Collider(
                    owner={"kind": "station", "id": self.station_node["id"]},
                    rect=rect,
                    body_type=BODY_SENSOR,
                    is_trigger=True,
                    layer=LAYER_TRIGGER,
                    mask=LAYER_PLAYER,
                )
            )

        return colliders

    def export_state(self):
        return {
            "modules": [
                {"key": module.key, "pos": [float(module.pos.x), float(module.pos.y)]}
                for module in self.modules
            ],
            "log_nodes": [
                {
                    "id": node["id"],
                    "pos": [float(node["pos"].x), float(node["pos"].y)],
                    "zone": node.get("zone", "epsilon"),
                    "collected": bool(node["collected"]),
                }
                for node in self.log_nodes
            ],
            "terminal_nodes": [
                {
                    "id": node["id"],
                    "pos": [float(node["pos"].x), float(node["pos"].y)],
                    "zone": node.get("zone", "epsilon"),
                    "used": bool(node["used"]),
                }
                for node in self.terminal_nodes
            ],
            "next_log_id": self._next_log_id,
            "next_terminal_id": self._next_terminal_id,
        }

    def import_state(self, payload):
        self.modules = []
        self.log_nodes = []
        self.terminal_nodes = []
        self.loaded_chunks = set()
        self.pending_chunks = deque()
        self.pending_chunk_set = set()
        self.asteroids.empty()
        self.hazards = []
        self._active_asteroids = []

        for module_data in payload.get("modules", []):
            pos = module_data.get("pos", [SPAWN_POS[0], SPAWN_POS[1]])
            self.add_module(module_data.get("key", ""), pygame.Vector2(pos[0], pos[1]))

        for node in payload.get("log_nodes", []):
            pos = node.get("pos", [SPAWN_POS[0], SPAWN_POS[1]])
            self.log_nodes.append(
                {
                    "id": int(node.get("id", 1)),
                    "pos": pygame.Vector2(pos[0], pos[1]),
                    "zone": node.get("zone", "epsilon"),
                    "collected": bool(node.get("collected", False)),
                }
            )

        for terminal in payload.get("terminal_nodes", []):
            pos = terminal.get("pos", [SPAWN_POS[0], SPAWN_POS[1]])
            self.terminal_nodes.append(
                {
                    "id": str(terminal.get("id", "terminal_1")),
                    "pos": pygame.Vector2(pos[0], pos[1]),
                    "zone": terminal.get("zone", "epsilon"),
                    "used": bool(terminal.get("used", False)),
                }
            )

        self._next_log_id = int(payload.get("next_log_id", self._next_log_id))
        self._next_terminal_id = int(
            payload.get("next_terminal_id", self._next_terminal_id)
        )
