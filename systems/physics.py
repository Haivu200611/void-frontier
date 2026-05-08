# =========================
# PHYSICS / COLLISION SYSTEM
# =========================

from dataclasses import dataclass

import pygame


# Layers (bitmask)
LAYER_PLAYER = 0x01
LAYER_STATIC = 0x02
LAYER_ASTEROID = 0x04
LAYER_TRIGGER = 0x08


BODY_DYNAMIC = "dynamic"
BODY_STATIC = "static"
BODY_SENSOR = "sensor"


def apply_velocity(player, dt):
    player.pos += player.vel * dt
    player.rect.center = player.pos


def apply_friction(player, factor=None):
    if factor is None:
        factor = getattr(player, "drag", 0.98)
    player.vel *= factor


def clamp_speed(player, max_speed):
    if player.vel.length() > max_speed:
        player.vel.scale_to_length(max_speed)


def handle_collision(player, objects):
    for obj in objects:
        if player.rect.colliderect(obj.rect):
            player.vel *= -0.5


@dataclass
class Collider:
    owner: object
    rect: pygame.Rect
    body_type: str = BODY_STATIC
    is_trigger: bool = False
    layer: int = LAYER_STATIC
    mask: int = LAYER_PLAYER | LAYER_STATIC | LAYER_ASTEROID | LAYER_TRIGGER
    restitution: float = 0.0


@dataclass
class CollisionEvent:
    kind: str
    source: object
    target: object
    normal: pygame.Vector2


class PhysicsSystem:
    def __init__(self, cell_size=192):
        self.cell_size = max(64, int(cell_size))

    # -------------------------
    # BROAD PHASE (Spatial Grid)
    # -------------------------
    def _grid_keys_for_rect(self, rect):
        x0 = rect.left // self.cell_size
        y0 = rect.top // self.cell_size
        x1 = rect.right // self.cell_size
        y1 = rect.bottom // self.cell_size
        keys = []
        for gx in range(x0, x1 + 1):
            for gy in range(y0, y1 + 1):
                keys.append((gx, gy))
        return keys

    def _build_grid(self, colliders):
        grid = {}
        for collider in colliders:
            for key in self._grid_keys_for_rect(collider.rect):
                grid.setdefault(key, []).append(collider)
        return grid

    def _query_nearby(self, collider, grid):
        seen = set()
        result = []
        for key in self._grid_keys_for_rect(collider.rect):
            for other in grid.get(key, []):
                if other is collider:
                    continue
                oid = id(other)
                if oid in seen:
                    continue
                seen.add(oid)
                result.append(other)
        return result

    @staticmethod
    def _can_collide(a, b):
        return (a.mask & b.layer) != 0 and (b.mask & a.layer) != 0

    @staticmethod
    def _overlap_on_axis(a, b, axis):
        if axis == "x":
            return a.bottom > b.top and a.top < b.bottom
        return a.right > b.left and a.left < b.right

    # -------------------------
    # NARROW PHASE
    # -------------------------
    @staticmethod
    def check_aabb_collision(a, b):
        return a.rect.colliderect(b.rect)

    @staticmethod
    def _resolve_axis(dynamic, target, axis, restitution):
        overlap_left = dynamic.rect.right - target.rect.left
        overlap_right = target.rect.right - dynamic.rect.left
        overlap_top = dynamic.rect.bottom - target.rect.top
        overlap_bottom = target.rect.bottom - dynamic.rect.top

        if axis == "x":
            if overlap_left < overlap_right:
                dynamic.rect.right = target.rect.left
                normal = pygame.Vector2(-1, 0)
            else:
                dynamic.rect.left = target.rect.right
                normal = pygame.Vector2(1, 0)

            dynamic.owner.pos.x = dynamic.rect.centerx
            if restitution > 0:
                dynamic.owner.vel.x = -dynamic.owner.vel.x * restitution
            else:
                dynamic.owner.vel.x = 0
            return normal

        if overlap_top < overlap_bottom:
            dynamic.rect.bottom = target.rect.top
            normal = pygame.Vector2(0, -1)
        else:
            dynamic.rect.top = target.rect.bottom
            normal = pygame.Vector2(0, 1)

        dynamic.owner.pos.y = dynamic.rect.centery
        if restitution > 0:
            dynamic.owner.vel.y = -dynamic.owner.vel.y * restitution
        else:
            dynamic.owner.vel.y = 0
        return normal

    def _find_swept_hit(self, dynamic, candidates, delta, axis):
        if delta == 0:
            return None, 1.0

        start_rect = dynamic.rect.copy()
        best_t = 1.0
        hit = None

        for other in candidates:
            if other.is_trigger or other.body_type == BODY_SENSOR:
                continue
            if not self._can_collide(dynamic, other):
                continue
            if not self._overlap_on_axis(start_rect, other.rect, axis):
                continue

            if axis == "x":
                if delta > 0:
                    if start_rect.right > other.rect.left:
                        continue
                    t = (other.rect.left - start_rect.right) / delta
                else:
                    if start_rect.left < other.rect.right:
                        continue
                    t = (other.rect.right - start_rect.left) / delta
            else:
                if delta > 0:
                    if start_rect.bottom > other.rect.top:
                        continue
                    t = (other.rect.top - start_rect.bottom) / delta
                else:
                    if start_rect.top < other.rect.bottom:
                        continue
                    t = (other.rect.bottom - start_rect.top) / delta

            if 0.0 <= t < best_t:
                best_t = t
                hit = other

        return hit, best_t

    # -------------------------
    # UPDATE (Dynamic vs World)
    # -------------------------
    def update(self, dt, dynamic_colliders, world_colliders):
        if dt <= 0:
            return []

        all_colliders = list(dynamic_colliders) + list(world_colliders)
        grid = self._build_grid(all_colliders)
        events = []

        for dynamic in dynamic_colliders:
            if dynamic.body_type != BODY_DYNAMIC:
                continue
            if not hasattr(dynamic.owner, "vel") or not hasattr(dynamic.owner, "pos"):
                continue

            candidates = self._query_nearby(dynamic, grid)

            # Move & resolve on X (enables sliding on Y).
            delta_x = dynamic.owner.vel.x * dt
            hit_x, hit_time_x = self._find_swept_hit(dynamic, candidates, delta_x, "x")
            dynamic.owner.pos.x += delta_x * (hit_time_x if hit_x is not None else 1.0)
            dynamic.rect.centerx = int(dynamic.owner.pos.x)
            if hit_x is not None:
                normal = self._resolve_axis(dynamic, hit_x, "x", hit_x.restitution)
                events.append(CollisionEvent("collision", dynamic.owner, hit_x.owner, normal))

            for other in candidates:
                if not self._can_collide(dynamic, other):
                    continue
                if not dynamic.rect.colliderect(other.rect):
                    continue
                if dynamic.is_trigger or other.is_trigger or other.body_type == BODY_SENSOR:
                    events.append(CollisionEvent("trigger", dynamic.owner, other.owner, pygame.Vector2()))
                    continue
                normal = self._resolve_axis(dynamic, other, "x", other.restitution)
                events.append(CollisionEvent("collision", dynamic.owner, other.owner, normal))

            # Move & resolve on Y.
            delta_y = dynamic.owner.vel.y * dt
            hit_y, hit_time_y = self._find_swept_hit(dynamic, candidates, delta_y, "y")
            dynamic.owner.pos.y += delta_y * (hit_time_y if hit_y is not None else 1.0)
            dynamic.rect.centery = int(dynamic.owner.pos.y)
            if hit_y is not None:
                normal = self._resolve_axis(dynamic, hit_y, "y", hit_y.restitution)
                events.append(CollisionEvent("collision", dynamic.owner, hit_y.owner, normal))

            for other in candidates:
                if not self._can_collide(dynamic, other):
                    continue
                if not dynamic.rect.colliderect(other.rect):
                    continue
                if dynamic.is_trigger or other.is_trigger or other.body_type == BODY_SENSOR:
                    events.append(CollisionEvent("trigger", dynamic.owner, other.owner, pygame.Vector2()))
                    continue
                normal = self._resolve_axis(dynamic, other, "y", other.restitution)
                events.append(CollisionEvent("collision", dynamic.owner, other.owner, normal))

        return events
