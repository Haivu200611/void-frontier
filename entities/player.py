# =========================
# PLAYER
# =========================

import pygame

from asset_loader import load_animation
from settings import PLAYER_ACCEL, PLAYER_BRAKE_ACCEL, PLAYER_DRAG, PLAYER_MAX_SPEED
from systems.physics import apply_friction, apply_velocity, clamp_speed


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        self.animations = {
            "idle": load_animation(
                "assets/images/player/player_idle",
                fallback_size=(56, 56),
                fallback_color=(0, 210, 255),
            ),
            "move": load_animation(
                "assets/images/player/player_move",
                fallback_size=(56, 56),
                fallback_color=(140, 220, 255),
            ),
            "thrust": load_animation(
                "assets/images/player/player_thruster",
                fallback_size=(56, 56),
                fallback_color=(255, 180, 0),
            ),
        }

        self.state = "idle"
        self.frame = 0
        self.anim_speed = 8

        self.image = self.animations["idle"][0]
        self.rect = self.image.get_rect(center=pos)

        # --- PHYSICS ---
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2()
        self.acc = pygame.Vector2()

        self.accel = PLAYER_ACCEL
        self.brake_accel = PLAYER_BRAKE_ACCEL
        self.max_speed = PLAYER_MAX_SPEED
        self.drag = PLAYER_DRAG

        # progression stats (suit upgrades)
        self.mining_power_bonus = 0
        self.hazard_resistance = 0.0
        self._thrusting = False

    # -------------------------
    # INPUT
    # -------------------------
    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        self.acc = pygame.Vector2(0, 0)

        if keys[pygame.K_w]:
            self.acc.y -= 1
        if keys[pygame.K_s]:
            self.acc.y += 1
        if keys[pygame.K_a]:
            self.acc.x -= 1
        if keys[pygame.K_d]:
            self.acc.x += 1

        if self.acc.length_squared() > 0:
            self.acc = self.acc.normalize() * self.accel
            self.state = "thrust"
            self._thrusting = True
        elif self.vel.length_squared() > 4:
            self.state = "move"
            self._thrusting = False
        else:
            self.state = "idle"
            self._thrusting = False

        # active brake in zero-g
        if keys[pygame.K_LSHIFT] or keys[pygame.K_SPACE]:
            if self.vel.length_squared() > 0.01:
                prev_vel = self.vel.copy()
                brake_dir = -self.vel.normalize()
                self.vel += brake_dir * self.brake_accel * dt
                if prev_vel.dot(self.vel) <= 0:
                    self.vel = pygame.Vector2()

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, dt, apply_motion=True):
        self.handle_input(dt)

        # zero-g inertia: thrust changes velocity, drag is low
        self.vel += self.acc * dt
        apply_friction(self, self.drag)
        clamp_speed(self, self.max_speed)
        if apply_motion:
            apply_velocity(self, dt)
        else:
            self.rect.center = self.pos

        self.update_animation(dt)

    def is_thrusting(self):
        return self._thrusting

    # -------------------------
    # PROGRESSION
    # -------------------------
    def apply_suit_upgrade(self, upgrade_name):
        if upgrade_name == "suit_explorer_mk1":
            self.max_speed += 90
            self.accel += 60
        elif upgrade_name == "suit_engineer_mk1":
            self.mining_power_bonus += 8
        elif upgrade_name == "suit_combat_mk1":
            self.hazard_resistance = min(0.45, self.hazard_resistance + 0.25)

    # -------------------------
    # ANIMATION
    # -------------------------
    def update_animation(self, dt):
        frames = self.animations[self.state]

        self.frame += self.anim_speed * dt
        if self.frame >= len(frames):
            self.frame = 0

        self.image = frames[int(self.frame)]
