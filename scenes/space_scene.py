# =========================
# SPACE SCENE (GAMEPLAY)
# =========================

import pygame

from scenes.scene_base import Scene
from settings import MINING_POWER, MINE_RANGE, SPAWN_POS, WIDTH, HEIGHT

from entities.player import Player
from systems.world import World
from systems.survival import Survival
from systems.inventory import Inventory
from systems.crafting import Crafting
from systems.narrative import Narrative

from ui.hud import HUD
from ui.inventory_ui import InventoryUI


class SpaceScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.player = Player(SPAWN_POS)
        self.world = World()

        self.survival = Survival()
        self.inventory = Inventory()
        self.crafting = Crafting(self.inventory)
        self.narrative = Narrative()

        self.hud = HUD()
        self.inventory_ui = InventoryUI(self.inventory)

        self.camera = pygame.Vector2()
        self.zone_name = "epsilon"

        self.status_message = "Escape pod deployed. Explore nearby asteroids."
        self.status_timer = 6.0

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
                    result = self.world.interact(self.player, self.narrative)
                    if result:
                        self.set_status(result)

                # ending choices at Xenith
                if self.narrative.get_ending() == "pending_choice":
                    if e.key == pygame.K_1:
                        self.trigger_ending("destroy_xenite")
                    if e.key == pygame.K_2:
                        self.trigger_ending("call_earth")
                    if e.key == pygame.K_3:
                        self.trigger_ending("take_xenite")

            if self.inventory_ui.visible and e.type == pygame.KEYDOWN:
                self.inventory_ui.handle_input(e)

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.mine()

    # -------------------------
    # STATUS
    # -------------------------
    def set_status(self, message, duration=3.0):
        self.status_message = message
        self.status_timer = duration

    # -------------------------
    # ENDING
    # -------------------------
    def trigger_ending(self, choice):
        self.narrative.set_final_choice(choice)
        ending = self.narrative.get_ending()

        if ending == "good":
            self.set_status("Ending: Destroy Xenite. Humanity survives.", 6.0)
        elif ending == "neutral":
            self.set_status("Ending: Call Earth. Signal sent.", 6.0)
        else:
            self.set_status("Ending: Take Xenite. Unknown future.", 6.0)

        print(f"ENDING: {ending}")
        self.game.running = False

    # -------------------------
    # MINING
    # -------------------------
    def mine(self):
        mouse_world = pygame.Vector2(pygame.mouse.get_pos()) + self.camera

        for asteroid in list(self.world.asteroids):
            if not asteroid.rect.collidepoint(mouse_world):
                continue

            if self.player.pos.distance_to(asteroid.rect.center) > MINE_RANGE:
                self.set_status("Target out of drill range")
                continue

            mining_power = MINING_POWER + self.player.mining_power_bonus
            asteroid.mine(mining_power)

            if asteroid.is_destroyed():
                drops = asteroid.drop()
                for item, amount in drops.items():
                    if amount > 0:
                        self.inventory.add(item, amount)

                self.world.asteroids.remove(asteroid)

            break

    # -------------------------
    # CRAFT HOOK
    # -------------------------
    def handle_craft(self, item):
        if not self.crafting.craft(item):
            return False, "Not enough resources"

        item_kind = self.crafting.classify(item)

        if item_kind == "module":
            drop_pos = self.player.pos + pygame.Vector2(130, 0)
            self.world.add_module(item, drop_pos)
            return True, f"Built {item}"

        if item_kind == "suit":
            self.player.apply_suit_upgrade(item)
            return True, f"Suit upgraded: {item}"

        if item == "battery_pack":
            self.survival.restore("battery", 35)
            return True, "Used battery pack"

        if item == "ration_pack":
            self.survival.restore("hunger", 35)
            return True, "Used ration pack"

        return True, f"Crafted {item}"

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, dt):
        self.player.update(dt)
        self.zone_name = self.world.get_zone_name(self.player.pos)

        # progression gate: far zones unlock by log progress
        unlocked_radius = self.world.get_unlocked_radius(self.narrative)
        distance_from_spawn = self.player.pos.distance_to(pygame.Vector2(SPAWN_POS))
        if distance_from_spawn > unlocked_radius:
            direction = (self.player.pos - pygame.Vector2(SPAWN_POS)).normalize()
            self.player.pos = pygame.Vector2(SPAWN_POS) + direction * unlocked_radius
            self.player.vel *= 0.3
            self.player.rect.center = self.player.pos
            self.set_status("Zone locked. Collect more logs to go deeper.", 2.2)

        extra_drain = self.world.update(self.player, self.narrative, self.survival, dt)

        # suit combat path reduces hazard drain
        if self.player.hazard_resistance > 0:
            for stat in list(extra_drain.keys()):
                extra_drain[stat] *= 1.0 - self.player.hazard_resistance

        self.survival.update(dt, extra_drain=extra_drain)

        # camera follow
        self.camera.x = self.player.pos.x - WIDTH // 2
        self.camera.y = self.player.pos.y - HEIGHT // 2

        if self.status_timer > 0:
            self.status_timer -= dt

        if self.survival.is_dead():
            print("GAME OVER")
            self.game.running = False

    # -------------------------
    # DRAW
    # -------------------------
    def draw(self, screen):
        screen.fill((5, 5, 20))
        self.world.draw(screen, self.camera)

        screen.blit(self.player.image, self.player.rect.move(-self.camera))

        self.hud.draw(
            screen,
            self.survival,
            self.player,
            self.world,
            self.narrative,
            self.zone_name,
            self.narrative.get_ending(),
        )
        self.inventory_ui.draw(screen)

        if self.status_timer > 0 and self.status_message:
            font = pygame.font.SysFont(None, 26)
            text = font.render(self.status_message, True, (255, 255, 255))
            screen.blit(text, (WIDTH // 2 - 220, HEIGHT - 48))
