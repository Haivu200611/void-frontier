# =========================
# HUD
# =========================

import pygame

from settings import GREEN, HEIGHT, LOW_STAT_THRESHOLD, RED, WHITE, WIDTH, YELLOW


class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 20)

    # -------------------------
    # BAR
    # -------------------------
    def draw_bar(self, screen, x, y, value, color, label):
        width = 220
        height = 15

        pygame.draw.rect(screen, (35, 35, 35), (x, y, width, height))
        fill_width = int(width * (max(0.0, value) / 100.0))
        pygame.draw.rect(screen, color, (x, y, fill_width, height))

        text = self.font.render(f"{label}: {int(value)}", True, WHITE)
        screen.blit(text, (x, y - 17))

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

        pygame.draw.circle(screen, (0, 255, 255), (center_x, center_y), 3)

        for a in world.asteroids:
            dx = (a.rect.centerx - player.pos.x) * 0.02
            dy = (a.rect.centery - player.pos.y) * 0.02
            if abs(dx) < size // 2 and abs(dy) < size // 2:
                pygame.draw.circle(screen, WHITE, (int(center_x + dx), int(center_y + dy)), 2)

    # -------------------------
    # META INFO
    # -------------------------
    def draw_meta(self, screen, world, narrative, zone_name, ending_state):
        logs_now, logs_total = narrative.logs_progress()
        terminals_now, terminals_total = narrative.terminals_progress()

        lines = [
            f"Zone: {zone_name.upper()}",
            f"Logs: {logs_now}/{logs_total}",
            f"Terminals: {terminals_now}/{terminals_total}",
            f"Modules: {len(world.modules)}",
        ]

        if ending_state == "pending_choice":
            lines.append("Endgame: press 1/2/3 to choose ending")

        x = 10
        y = HEIGHT - 110
        for i, line in enumerate(lines):
            txt = self.small_font.render(line, True, WHITE)
            screen.blit(txt, (x, y + i * 20))

    # -------------------------
    # WARNINGS
    # -------------------------
    def draw_warnings(self, screen, survival):
        low_stats = [k for k, v in survival.stats.items() if v <= LOW_STAT_THRESHOLD]
        if not low_stats:
            return

        warning = self.font.render("LOW: " + ", ".join(low_stats).upper(), True, RED)
        screen.blit(warning, (WIDTH // 2 - 130, 12))

    # -------------------------
    # DRAW
    # -------------------------
    def draw(self, screen, survival, player, world, narrative, zone_name, ending_state):
        self.draw_bar(screen, 10, 10, survival.oxygen, (0, 200, 255), "OXY")
        self.draw_bar(screen, 10, 34, survival.temperature, (255, 120, 120), "TMP")
        self.draw_bar(screen, 10, 58, survival.battery, (240, 220, 70), "BAT")
        self.draw_bar(screen, 10, 82, survival.hunger, (110, 220, 110), "FOOD")
        self.draw_bar(screen, 10, 106, survival.pressure, (230, 230, 255), "PRESS")

        self.draw_radar(screen, player, world)
        self.draw_meta(screen, world, narrative, zone_name, ending_state)
        self.draw_warnings(screen, survival)

        hint = self.small_font.render("E interact | LMB mine | TAB craft | SHIFT brake", True, YELLOW)
        screen.blit(hint, (WIDTH // 2 - 180, HEIGHT - 24))
