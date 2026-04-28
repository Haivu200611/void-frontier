# =========================
# SPACE SCENE (GAMEPLAY)
# =========================

import pygame

from scenes.scene_base import Scene
from settings import *

from entities.player import Player
from systems.world import World
from systems.survival import Survival
from systems.inventory import Inventory
from systems.crafting import Crafting

from ui.hud import HUD
from ui.inventory_ui import InventoryUI


class SpaceScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.player = Player((1000, 1000))
        self.world = World()

        self.survival = Survival()
        self.inventory = Inventory()
        self.crafting = Crafting(self.inventory)

        self.hud = HUD()
        self.inventory_ui = InventoryUI(self.inventory)

        self.camera = pygame.Vector2()

    # -------------------------
    # INPUT
    # -------------------------
    def handle_events(self, events):
        for e in events:
            if e.type == pygame.QUIT:
                self.game.running = False

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_i:
                    self.inventory_ui.toggle()

                if e.key == pygame.K_TAB:
                    from scenes.crafting_scene import CraftingScene
                    self.game.scene_manager.push(CraftingScene(self.game))

                if e.key == pygame.K_e:
                    from scenes.station_scene import StationScene
                    self.game.scene_manager.push(StationScene(self.game))

            if self.inventory_ui.visible:
                if e.type == pygame.KEYDOWN:
                    self.inventory_ui.handle_input(e)

            if e.type == pygame.MOUSEBUTTONDOWN:
                self.mine()

    # -------------------------
    # MINING
    # -------------------------
    def mine(self):
        mouse_world = pygame.Vector2(pygame.mouse.get_pos()) + self.camera

        for a in list(self.world.asteroids):
            if a.rect.collidepoint(mouse_world):
                a.mine(MINING_POWER)

                if a.is_destroyed():
                    drops = a.drop()
                    for k, v in drops.items():
                        self.inventory.add(k, v)

                    self.world.asteroids.remove(a)

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, dt):
        self.player.update(dt)
        self.survival.update(dt)
        self.world.update(self.player, dt)

        # camera follow
        self.camera.x = self.player.pos.x - WIDTH // 2
        self.camera.y = self.player.pos.y - HEIGHT // 2

        if self.survival.is_dead():
            print("GAME OVER")
            self.game.running = False

    # -------------------------
    # DRAW
    # -------------------------
    def draw(self, screen):
        screen.fill(SPACE_BLUE)

        self.world.draw(screen, self.camera)

        # player
        screen.blit(
            self.player.image,
            self.player.rect.move(-self.camera)
        )

        self.hud.draw(screen, self.survival, self.player, self.world)
        self.inventory_ui.draw(screen)
