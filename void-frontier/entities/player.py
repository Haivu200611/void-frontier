# =========================
# PLAYER
# =========================

import pygame
from settings import *
from asset_loader import load_animation


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        # --- ANIMATION ---
        self.animations = {
            "idle": load_animation(
                "assets/images/player/player_idle",
                fallback_size=(56, 56),
                fallback_color=(0, 210, 255)
            ),
            "move": load_animation(
                "assets/images/player/player_move",
                fallback_size=(56, 56),
                fallback_color=(140, 220, 255)
            ),
            "thrust": load_animation(
                "assets/images/player/player_thruster",
                fallback_size=(56, 56),
                fallback_color=(255, 180, 0)
            )
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

    # -------------------------
    # INPUT
    # -------------------------
    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.acc = pygame.Vector2(0, 0)

        if keys[pygame.K_w]: self.acc.y = -1
        if keys[pygame.K_s]: self.acc.y = 1
        if keys[pygame.K_a]: self.acc.x = -1
        if keys[pygame.K_d]: self.acc.x = 1

        if self.acc.length() > 0:
            self.acc = self.acc.normalize() * PLAYER_ACCEL
            self.state = "thrust"
        else:
            self.state = "idle"

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, dt):
        self.handle_input()

        # physics zero-g
        self.vel += self.acc * dt
        self.vel *= PLAYER_FRICTION

        if self.vel.length() > PLAYER_MAX_SPEED:
            self.vel.scale_to_length(PLAYER_MAX_SPEED)

        self.pos += self.vel * dt
        self.rect.center = self.pos

        self.update_animation(dt)

    # -------------------------
    # ANIMATION
    # -------------------------
    def update_animation(self, dt):
        frames = self.animations[self.state]

        self.frame += self.anim_speed * dt
        if self.frame >= len(frames):
            self.frame = 0

        self.image = frames[int(self.frame)]
