# =========================
# ASTEROID
# =========================

import random

import pygame

from asset_loader import load_animation
from data_loader import get_asteroid_data
from settings import (
    ASTEROID_DRAG,
    ASTEROID_DRIFT_MAX_SPEED,
    ASTEROID_DRIFT_MIN_SPEED,
    ASTEROID_MAX_SPEED,
)


class Asteroid(pygame.sprite.Sprite):
    def __init__(self, pos, asteroid_type, hp_scale=1.0):
        super().__init__()

        self.type = asteroid_type
        data = get_asteroid_data(self.type)

        # --- STATS ---
        self.hp = int(data.get("hp", 50) * hp_scale)

        # --- ANIMATION ---
        fallback_colors = {
            "iron": (170, 170, 170),
            "titanium": (145, 165, 190),
            "silicon": (196, 177, 139),
            "copper": (210, 140, 70),
            "ice": (120, 210, 255),
            "carbon": (115, 115, 125),
        }
        self.frames = load_animation(
            f"assets/images/asteroids/asteroid_{self.type}",
            fallback_size=(48, 48),
            fallback_color=fallback_colors.get(self.type, (200, 200, 200)),
        )
        self.frame = 0
        self.anim_speed = 4

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.vel = self._create_drift_velocity()
        self.drag = ASTEROID_DRAG
        self.max_speed = ASTEROID_MAX_SPEED
        self.mass = max(25.0, float(self.hp) * 0.9)

    def mine(self, power):
        self.hp -= power

    def is_destroyed(self):
        return self.hp <= 0

    def drop(self):
        data = get_asteroid_data(self.type)
        drops = data.get("drops", {})

        result = {}
        for item, (min_v, max_v) in drops.items():
            result[item] = random.randint(min_v, max_v)

        return result

    def _create_drift_velocity(self):
        angle = random.uniform(0.0, 360.0)
        speed = random.uniform(ASTEROID_DRIFT_MIN_SPEED, ASTEROID_DRIFT_MAX_SPEED)
        return pygame.Vector2(speed, 0).rotate(angle)

    def apply_impulse(self, impulse):
        self.vel += pygame.Vector2(impulse) / self.mass
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)

    def resolve_player_collision(self, player):
        offset = self.pos - player.pos
        if offset.length_squared() < 0.001:
            offset = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            if offset.length_squared() < 0.001:
                offset = pygame.Vector2(1, 0)

        normal = offset.normalize()
        relative_speed = max(0.0, (player.vel - self.vel).dot(normal))

        # Push asteroid and damp player based on impact speed.
        # Tuned down to keep close-range mining playable.
        self.apply_impulse(normal * relative_speed * 0.95)
        player.vel -= normal * relative_speed * 0.28

        # Resolve overlap so both objects separate immediately.
        asteroid_radius = max(self.rect.width, self.rect.height) * 0.5
        player_radius = max(player.rect.width, player.rect.height) * 0.38
        distance = self.pos.distance_to(player.pos)
        min_distance = asteroid_radius + player_radius
        if distance < min_distance:
            penetration = min_distance - distance + 0.4
            self.pos += normal * penetration * 0.62
            player.pos -= normal * penetration * 0.38
            player.rect.center = player.pos

        return relative_speed

    def update(self, dt):
        self.pos += self.vel * dt
        self.vel *= self.drag
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)

        self.frame += self.anim_speed * dt
        if self.frame >= len(self.frames):
            self.frame = 0

        center = self.pos
        self.image = self.frames[int(self.frame)]
        self.rect = self.image.get_rect(center=center)
