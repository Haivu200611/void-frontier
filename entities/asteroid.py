# =========================
# ASTEROID
# =========================

import random

import pygame

from asset_loader import load_animation
from data_loader import get_asteroid_data


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

    def update(self, dt):
        self.frame += self.anim_speed * dt
        if self.frame >= len(self.frames):
            self.frame = 0

        self.image = self.frames[int(self.frame)]
