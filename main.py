# =========================
# MAIN - VOID FRONTIER
# =========================

import pygame
import sys
import os

from asset_manifest import validate_assets
from settings import *
from scenes.scene_manager import SceneManager
from scenes.menu_scene import MenuScene


class Game:
    def __init__(self):
        pygame.init()
        self._print_asset_report()

        # Window
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        # Time
        self.clock = pygame.time.Clock()
        self.dt = 0

        # State
        self.running = True

        # Scene system
        self.scene_manager = SceneManager(self)
        self.scene_manager.set(MenuScene(self))

    def _print_asset_report(self):
        report = validate_assets(os.path.dirname(os.path.abspath(__file__)))
        print(
            f"[Assets] {report['present_count']}/{report['required_count']} core files ready"
        )
        if report["missing"]:
            print("[Assets] Missing core files (fallback placeholders will be used):")
            for item in report["missing"]:
                print(f" - {item}")

    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0
            if self.dt > MAX_DT:
                self.dt = MAX_DT

            self.handle_events()
            self.update()
            self.draw()

        self.quit()

    def handle_events(self):
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

        self.scene_manager.handle_events(events)

    def update(self):
        self.scene_manager.update(self.dt)

    def draw(self):
        self.screen.fill(SPACE_BLUE)
        self.scene_manager.draw(self.screen)
        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
