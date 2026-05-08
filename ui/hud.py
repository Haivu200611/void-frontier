# =========================
# HUD
# =========================

import pygame

from asset_loader import asset_exists, load_image
from settings import GREEN, HEIGHT, LOW_STAT_THRESHOLD, RED, WHITE, WIDTH, YELLOW


class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 20)
        self.bar_width = 220
        self.bar_height = 15
        self.bar_bg = None
        self.bar_fill = None
        self.icons = {}
        self.hint_surface = self.small_font.render(
            "E interact | LMB mine | TAB craft | SHIFT brake", True, YELLOW
        )

        if asset_exists("assets/images/ui/ui_hud/bar_bg.png"):
            self.bar_bg = pygame.transform.smoothscale(
                load_image("assets/images/ui/ui_hud/bar_bg.png"),
                (self.bar_width, self.bar_height),
            )
        if asset_exists("assets/images/ui/ui_hud/bar_fill.png"):
            self.bar_fill = pygame.transform.smoothscale(
                load_image("assets/images/ui/ui_hud/bar_fill.png"),
                (self.bar_width, self.bar_height),
            )

        icon_map = {
            "oxygen": "assets/images/ui/ui_icons/ice.png",
            "temperature": "assets/images/ui/ui_icons/carbon.png",
            "battery": "assets/images/ui/ui_icons/battery.png",
            "hunger": "assets/images/ui/ui_icons/carbon.png",
            "pressure": "assets/images/ui/ui_icons/titanium.png",
        }
        for stat, path in icon_map.items():
            if asset_exists(path):
                self.icons[stat] = pygame.transform.smoothscale(load_image(path), (16, 16))

    # -------------------------
    # BAR
    # -------------------------
    def draw_bar(self, screen, x, y, value, color, label, stat_key):
        width = self.bar_width
        height = self.bar_height

        icon = self.icons.get(stat_key)
        icon_offset = 0
        if icon is not None:
            screen.blit(icon, (x, y - 1))
            icon_offset = 22

        bar_x = x + icon_offset
        fill_width = int(width * (max(0.0, value) / 100.0))

        if self.bar_bg is not None and self.bar_fill is not None:
            screen.blit(self.bar_bg, (bar_x, y))
            if fill_width > 0:
                fill_area = pygame.Rect(0, 0, fill_width, height)
                screen.blit(self.bar_fill.subsurface(fill_area), (bar_x, y))
        else:
            pygame.draw.rect(screen, (35, 35, 35), (bar_x, y, width, height))
            pygame.draw.rect(screen, color, (bar_x, y, fill_width, height))

        text = self.font.render(f"{label}: {int(value)}", True, WHITE)
        screen.blit(text, (bar_x, y - 17))

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

        for dx, dy in world.get_radar_points(player.pos, size):
            pygame.draw.circle(screen, WHITE, (center_x + dx, center_y + dy), 2)

    # -------------------------
    # META INFO
    # -------------------------
    def draw_meta(self, screen, world, narrative, zone_name, ending_state, objectives):
        logs_now, logs_total = narrative.logs_progress()
        terminals_now, terminals_total = narrative.terminals_progress()
        progress_pct = int(((logs_now + terminals_now) / (logs_total + terminals_total)) * 100)

        lines = [
            f"Zone: {zone_name.upper()}",
            f"Logs: {logs_now}/{logs_total}",
            f"Terminals: {terminals_now}/{terminals_total}",
            f"Modules: {len(world.modules)}",
            f"Mission progress: {progress_pct}%",
        ]

        if ending_state == "pending_choice":
            lines.append("Endgame: press 1/2/3 to choose ending")
        else:
            lines.extend(objectives.get_lines())

        x = 10
        y = HEIGHT - 150
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
    def draw(
        self,
        screen,
        survival,
        player,
        world,
        narrative,
        zone_name,
        ending_state,
        objectives,
        interaction_hint,
    ):
        self.draw_bar(screen, 10, 10, survival.oxygen, (0, 200, 255), "OXY", "oxygen")
        self.draw_bar(screen, 10, 34, survival.temperature, (255, 120, 120), "TMP", "temperature")
        self.draw_bar(screen, 10, 58, survival.battery, (240, 220, 70), "BAT", "battery")
        self.draw_bar(screen, 10, 82, survival.hunger, (110, 220, 110), "FOOD", "hunger")
        self.draw_bar(screen, 10, 106, survival.pressure, (230, 230, 255), "PRESS", "pressure")

        self.draw_radar(screen, player, world)
        self.draw_meta(screen, world, narrative, zone_name, ending_state, objectives)
        self.draw_warnings(screen, survival)

        screen.blit(self.hint_surface, (WIDTH // 2 - 180, HEIGHT - 24))
        if interaction_hint:
            hint = self.small_font.render(interaction_hint, True, WHITE)
            screen.blit(hint, (WIDTH // 2 - 155, HEIGHT - 48))
