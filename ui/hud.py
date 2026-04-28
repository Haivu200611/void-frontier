# =========================
# HUD
# =========================

import pygame
from settings import *


class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 24)

    # -------------------------
    # BAR
    # -------------------------
    def draw_bar(self, screen, x, y, value, color, label):
        width = 200
        height = 16

        # background
        pygame.draw.rect(screen, (40, 40, 40), (x, y, width, height))

        # fill
        fill_width = int(width * (value / 100))
        pygame.draw.rect(screen, color, (x, y, fill_width, height))

        # text
        text = self.font.render(f"{label}: {int(value)}", True, WHITE)
        screen.blit(text, (x, y - 18))

    # -------------------------
    # RADAR
    # -------------------------
    def draw_radar(self, screen, player, world):
        size = 120
        rx = WIDTH - size - 10
        ry = 10

        pygame.draw.rect(screen, (20, 20, 20), (rx, ry, size, size))
        pygame.draw.rect(screen, WHITE, (rx, ry, size, size), 1)

        center_x = rx + size // 2
        center_y = ry + size // 2

        # player
        pygame.draw.circle(screen, CYAN, (center_x, center_y), 3)

        # asteroids
        for a in world.asteroids:
            dx = (a.rect.centerx - player.pos.x) * 0.02
            dy = (a.rect.centery - player.pos.y) * 0.02

            if abs(dx) < size // 2 and abs(dy) < size // 2:
                pygame.draw.circle(
                    screen,
                    WHITE,
                    (int(center_x + dx), int(center_y + dy)),
                    2
                )

    # -------------------------
    # DRAW
    # -------------------------
    def draw(self, screen, survival, player, world):
        self.draw_bar(screen, 10, 10, survival.oxygen, (0, 200, 255), "OXY")
        self.draw_bar(screen, 10, 35, survival.battery, (255, 255, 0), "BAT")
        self.draw_bar(screen, 10, 60, survival.temperature, (255, 100, 100), "TMP")

        self.draw_radar(screen, player, world)