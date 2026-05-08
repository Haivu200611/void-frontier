# =========================
# CRAFTING SCENE
# =========================

import pygame

from data_loader import get_recipe
from scenes.scene_base import Scene
from settings import GREEN, HEIGHT, WHITE, WIDTH


class CraftingScene(Scene):
    def __init__(self, game, space_scene):
        super().__init__(game)
        self.space_scene = space_scene

        self.options = space_scene.crafting.get_options()
        self.selected = 0
        self.feedback = ""

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.game.scene_manager.pop()

                if e.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)

                if e.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)

                if e.key == pygame.K_RETURN:
                    self.craft()

    def craft(self):
        item = self.options[self.selected]

        ok, msg = self.space_scene.handle_craft(item)
        self.feedback = msg
        if ok:
            print(msg)

    def draw(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont(None, 38)
        tiny = pygame.font.SysFont(None, 24)

        title = font.render("CRAFTING", True, WHITE)
        screen.blit(title, (WIDTH // 2 - 80, 120))

        for i, opt in enumerate(self.options):
            can_craft = self.space_scene.crafting.can_craft(opt)
            if i == self.selected:
                color = GREEN if can_craft else (255, 180, 80)
            else:
                color = WHITE if can_craft else (180, 180, 180)
            text = tiny.render(opt, True, color)
            screen.blit(text, (WIDTH // 2 - 160, 200 + i * 26))

        selected_item = self.options[self.selected]
        recipe = get_recipe(selected_item)
        cost_text = ", ".join([f"{k}:{v}" for k, v in recipe.items()])
        cost_surface = tiny.render(f"Cost: {cost_text}", True, WHITE)
        screen.blit(cost_surface, (WIDTH // 2 - 160, HEIGHT - 110))

        if self.feedback:
            msg = tiny.render(self.feedback, True, WHITE)
            screen.blit(msg, (WIDTH // 2 - 160, HEIGHT - 70))
