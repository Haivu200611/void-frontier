# =========================
# STATION SCENE
# =========================

import pygame

from scenes.scene_base import Scene
from settings import HEIGHT, WHITE, WIDTH, YELLOW


class StationScene(Scene):
    def __init__(self, game, space_scene):
        super().__init__(game)
        self.space_scene = space_scene
        self.options = [
            "Refill survival systems",
            "Save progress",
            "Return to space",
        ]
        self.selected = 0
        self.feedback = "Docked: ARES-7 station relay online."
        self.font = pygame.font.SysFont(None, 34)
        self.small = pygame.font.SysFont(None, 25)

    def handle_events(self, events):
        for e in events:
            if e.type != pygame.KEYDOWN:
                continue
            if e.key == pygame.K_ESCAPE:
                self.game.scene_manager.pop()
            elif e.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif e.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif e.key == pygame.K_RETURN:
                self._execute_selected()

    def _execute_selected(self):
        if self.selected == 0:
            self.space_scene.survival.restore("oxygen", 60)
            self.space_scene.survival.restore("temperature", 60)
            self.space_scene.survival.restore("battery", 60)
            self.space_scene.survival.restore("hunger", 60)
            self.space_scene.survival.restore("pressure", 60)
            self.feedback = "Suit and life support stabilized."
            self.space_scene.audio.play_sfx("click", volume=0.5)
            return

        if self.selected == 1:
            self.space_scene.save_system.save(self.space_scene)
            self.feedback = "Progress saved to local drive."
            self.space_scene.audio.play_sfx("click", volume=0.6)
            return

        self.game.scene_manager.pop()

    def draw(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(205)
        overlay.fill((8, 12, 28))
        screen.blit(overlay, (0, 0))

        title = self.font.render("ARES-7 STATION", True, WHITE)
        hint = self.small.render("UP/DOWN + ENTER | ESC to undock", True, YELLOW)

        screen.blit(title, (WIDTH // 2 - 145, 110))
        screen.blit(hint, (WIDTH // 2 - 165, 150))

        for i, text in enumerate(self.options):
            color = YELLOW if i == self.selected else WHITE
            line = self.small.render(text, True, color)
            screen.blit(line, (WIDTH // 2 - 170, 235 + i * 40))

        if self.feedback:
            fb = self.small.render(self.feedback, True, WHITE)
            screen.blit(fb, (WIDTH // 2 - 200, HEIGHT - 90))
