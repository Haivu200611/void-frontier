# =========================
# WORLD SYSTEM
# =========================

import pygame
import random

from settings import *
from entities.asteroid import Asteroid
from entities.hazard import RadiationZone


class World:
    def __init__(self):
        self.asteroids = pygame.sprite.Group()
        self.hazards = []

        self.loaded_chunks = set()

    # -------------------------
    # CHUNK
    # -------------------------
    def get_chunk(self, pos):
        return (int(pos.x // CHUNK_SIZE), int(pos.y // CHUNK_SIZE))

    def load_chunk(self, cx, cy):
        if (cx, cy) in self.loaded_chunks:
            return

        self.loaded_chunks.add((cx, cy))

        # spawn asteroid
        for _ in range(8):
            x = cx * CHUNK_SIZE + random.randint(0, CHUNK_SIZE)
            y = cy * CHUNK_SIZE + random.randint(0, CHUNK_SIZE)
            self.asteroids.add(Asteroid((x, y)))

        # spawn hazard
        if random.random() < 0.25:
            self.hazards.append(
                RadiationZone(
                    (cx * CHUNK_SIZE + 200, cy * CHUNK_SIZE + 200),
                    150
                )
            )

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, player, dt):
        cx, cy = self.get_chunk(player.pos)

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                self.load_chunk(cx + dx, cy + dy)

        self.asteroids.update(dt)

    # -------------------------
    # DRAW
    # -------------------------
    def draw(self, screen, cam):
        for a in self.asteroids:
            screen.blit(a.image, a.rect.move(-cam))

        for h in self.hazards:
            h.draw(screen, cam)
