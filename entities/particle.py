# =========================
# PARTICLE SYSTEM
# =========================

import pygame
import random


class Particle:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)

        self.vel = pygame.Vector2(
            random.uniform(-50, 50),
            random.uniform(-50, 50)
        )

        self.life = random.uniform(0.3, 1.0)

    def update(self, dt):
        self.pos += self.vel * dt
        self.life -= dt

    def draw(self, screen, cam):
        if self.life > 0:
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (int(self.pos.x - cam.x), int(self.pos.y - cam.y)),
                2
            )


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, pos, count=5):
        for _ in range(count):
            self.particles.append(Particle(pos))

    def update(self, dt):
        for p in self.particles:
            p.update(dt)

        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, screen, cam):
        for p in self.particles:
            p.draw(screen, cam)