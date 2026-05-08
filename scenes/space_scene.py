# =========================
# SPACE SCENE (GAMEPLAY)
# =========================

import os

import pygame

from asset_loader import load_image
from scenes.scene_base import Scene
from scenes.station_scene import StationScene
from settings import (
    HEIGHT,
    MAX_DT,
    MINE_RANGE,
    MINING_POWER,
    MINING_VFX_COOLDOWN,
    SHAKE_BASE,
    SHAKE_DECAY,
    SHAKE_STRONG,
    SPAWN_POS,
    THRUSTER_TRAIL_INTERVAL,
    WIDTH,
)

from entities.effect import EffectLayer
from entities.particle import ParticleSystem
from entities.player import Player
from systems.audio_manager import AudioManager
from systems.crafting import Crafting
from systems.inventory import Inventory
from systems.narrative import Narrative
from systems.objectives import Objectives
from systems.physics import BODY_DYNAMIC, Collider, LAYER_PLAYER, LAYER_STATIC, LAYER_TRIGGER, PhysicsSystem
from systems.save_system import SaveSystem
from systems.survival import Survival
from systems.world import World
from ui.dialogue_ui import DialogueUI
from ui.hud import HUD
from ui.inventory_ui import InventoryUI


class SpaceScene(Scene):
    def __init__(self, game, load_requested=False):
        super().__init__(game)
        self.background = self._load_background()

        self.player = Player(SPAWN_POS)
        self.world = World()

        self.survival = Survival()
        self.inventory = Inventory()
        self.crafting = Crafting(self.inventory)
        self.narrative = Narrative()
        self.objectives = Objectives()
        self.save_system = SaveSystem()
        self.audio = AudioManager()
        self.physics = PhysicsSystem(cell_size=192)

        self.hud = HUD()
        self.inventory_ui = InventoryUI(self.inventory)
        self.dialogue_ui = DialogueUI()
        self.particles = ParticleSystem()
        self.effects = EffectLayer()

        self.camera = pygame.Vector2()
        self.zone_name = "epsilon"
        self.camera_shake = 0.0
        self.thruster_timer = 0.0
        self.warning_cd = 0.0
        self.mining_vfx_cd = 0.0
        self.impact_feedback_cd = 0.0
        self.dead_timer = 0.0
        self.player_dead = False
        self.trigger_hints = set()

        self.status_message = "Escape pod deployed. Explore nearby asteroids."
        self.status_timer = 6.0
        self.status_font = pygame.font.SysFont(None, 26)

        self.audio.play_ambient()
        if load_requested and self.save_system.load(self):
            self.set_status("Save loaded. Mission resumed.", 4.0)
        elif load_requested:
            self.set_status("No save found. Started a new run.", 4.0)

    def _load_background(self):
        bg_folder = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets",
            "images",
            "background",
        )
        if not os.path.isdir(bg_folder):
            return None

        for filename in sorted(os.listdir(bg_folder)):
            if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                continue
            image = load_image(f"assets/images/background/{filename}")
            return pygame.transform.smoothscale(image, (WIDTH, HEIGHT))

        return None

    def set_status(self, message, duration=3.0):
        self.status_message = message
        self.status_timer = duration

    def pause(self):
        self.audio.play_sfx("click", volume=0.45)

    def resume(self):
        self.audio.play_sfx("click", volume=0.45)

    def exit(self):
        self.audio.stop_ambient()

    # -------------------------
    # INPUT
    # -------------------------
    def handle_events(self, events):
        for e in events:
            if e.type == pygame.QUIT:
                self.game.running = False
                continue

            if e.type == pygame.KEYDOWN and self.dialogue_ui.active:
                self.dialogue_ui.handle_input(e)
                continue

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_i:
                    self.inventory_ui.toggle()
                    self.audio.play_sfx("click", volume=0.45)
                elif e.key == pygame.K_TAB:
                    from scenes.crafting_scene import CraftingScene

                    self.audio.play_sfx("click", volume=0.45)
                    self.game.scene_manager.push(CraftingScene(self.game, self))
                elif e.key == pygame.K_e:
                    result = self.world.interact(self.player, self.narrative)
                    if result:
                        self._handle_interaction_result(result)
                elif e.key == pygame.K_F5:
                    self.save_system.save(self)
                    self.set_status("Progress saved.", 2.5)
                    self.audio.play_sfx("click", volume=0.55)
                elif e.key == pygame.K_F9:
                    if self.save_system.load(self):
                        self.set_status("Save loaded.", 2.5)
                    else:
                        self.set_status("No save file found.", 2.5)
                    self.audio.play_sfx("click", volume=0.55)
                elif self.narrative.get_ending() == "pending_choice":
                    if e.key == pygame.K_1:
                        self.trigger_ending("destroy_xenite")
                    elif e.key == pygame.K_2:
                        self.trigger_ending("call_earth")
                    elif e.key == pygame.K_3:
                        self.trigger_ending("take_xenite")

            if self.inventory_ui.visible and e.type == pygame.KEYDOWN:
                self.inventory_ui.handle_input(e)

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.mine()

    def _handle_interaction_result(self, result):
        kind = result.get("kind")
        message = result.get("message", "")
        self.set_status(message)

        if kind == "log":
            log_data = self.narrative.get_log(result.get("id"))
            if log_data:
                lines = [f"[{log_data['title']}]", log_data["text"]]
                self.dialogue_ui.start(lines)
            self.audio.play_sfx("click", volume=0.52)
        elif kind == "terminal":
            terminal_id = result.get("id", "terminal")
            lines = [
                f"{terminal_id} online.",
                "Signal packet decoded. Zone data updated.",
            ]
            self.dialogue_ui.start(lines)
            self.audio.play_sfx("click", volume=0.55)
        elif kind == "station":
            self.audio.play_sfx("click", volume=0.55)
            self.game.scene_manager.push(StationScene(self.game, self))

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
        self.save_system.save(self)
        self.game.running = False

    # -------------------------
    # FEEDBACK
    # -------------------------
    def _apply_shake(self, value):
        self.camera_shake = max(self.camera_shake, value)

    def _emit_thruster_feedback(self, dt):
        if not self.player.is_thrusting():
            return
        self.thruster_timer -= dt
        if self.thruster_timer > 0:
            return
        self.thruster_timer = THRUSTER_TRAIL_INTERVAL
        self.particles.emit(self.player.pos - pygame.Vector2(0, -6), count=2)
        self.effects.spawn(
            self.player.pos,
            "assets/images/effects/effect_thruster/texture.png",
            duration=0.16,
            scale=0.55,
        )
        self.audio.play_sfx("jetpack", volume=0.35)

    def _handle_warning_feedback(self, dt):
        self.warning_cd -= dt
        if self.warning_cd > 0:
            return
        low_stats = [v for v in self.survival.stats.values() if v <= 20]
        if low_stats:
            self.warning_cd = 1.3
            self.audio.play_sfx("warning", volume=0.4)

    def _run_collision_step(self, dt):
        player_collider = Collider(
            owner=self.player,
            rect=self.player.rect.inflate(-16, -16).copy(),
            body_type=BODY_DYNAMIC,
            is_trigger=False,
            layer=LAYER_PLAYER,
            mask=LAYER_STATIC | LAYER_TRIGGER,
            restitution=0.0,
        )
        world_colliders = self.world.get_collision_colliders(self.narrative)
        events = self.physics.update(dt, [player_collider], world_colliders)

        # Sync sprite rect from resolved physics position.
        self.player.rect.center = (int(self.player.pos.x), int(self.player.pos.y))
        self.trigger_hints = set()
        for event in events:
            if event.kind != "trigger":
                continue
            target = event.target
            if isinstance(target, dict) and target.get("kind"):
                self.trigger_hints.add(target["kind"])

    # -------------------------
    # MINING
    # -------------------------
    def mine(self):
        if self.player_dead:
            return
        mouse_world = pygame.Vector2(pygame.mouse.get_pos()) + self.camera

        for asteroid in list(self.world.asteroids):
            if not asteroid.rect.collidepoint(mouse_world):
                continue

            if self.player.pos.distance_to(asteroid.rect.center) > MINE_RANGE:
                self.set_status("Target out of drill range")
                continue

            mining_power = MINING_POWER + self.player.mining_power_bonus
            asteroid.mine(mining_power)
            self.audio.play_sfx("mining", volume=0.55)

            if self.mining_vfx_cd <= 0:
                self.effects.spawn(
                    asteroid.rect.center,
                    "assets/images/effects/effect_mining/texture.png",
                    duration=0.22,
                    scale=0.7,
                )
                self.particles.emit(asteroid.rect.center, count=5)
                self.mining_vfx_cd = MINING_VFX_COOLDOWN

            if asteroid.is_destroyed():
                drops = asteroid.drop()
                for item, amount in drops.items():
                    if amount > 0:
                        self.inventory.add(item, amount)
                self.effects.spawn(
                    asteroid.rect.center,
                    "assets/images/effects/effect_explosion/texture.png",
                    duration=0.32,
                    scale=1.0,
                )
                self.particles.emit(asteroid.rect.center, count=13)
                self.audio.play_sfx("explosion", volume=0.6)
                self._apply_shake(SHAKE_BASE)
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
            self.audio.play_sfx("click", volume=0.58)
            self.set_status(f"Built {item}", 2.2)
            return True, f"Built {item}"

        if item_kind == "suit":
            self.player.apply_suit_upgrade(item)
            self.audio.play_sfx("click", volume=0.58)
            self.set_status(f"Suit upgraded: {item}", 2.2)
            return True, f"Suit upgraded: {item}"

        if item == "battery_pack":
            self.survival.restore("battery", 35)
            self.audio.play_sfx("click", volume=0.58)
            self.set_status("Used battery pack", 2.0)
            return True, "Used battery pack"

        if item == "ration_pack":
            self.survival.restore("hunger", 35)
            self.audio.play_sfx("click", volume=0.58)
            self.set_status("Used ration pack", 2.0)
            return True, "Used ration pack"

        self.audio.play_sfx("click", volume=0.58)
        return True, f"Crafted {item}"

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, dt):
        dt = min(dt, MAX_DT)
        self.mining_vfx_cd = max(0.0, self.mining_vfx_cd - dt)
        self.dialogue_ui.update(dt)
        self.effects.update(dt)
        self.particles.update(dt)
        self._handle_warning_feedback(dt)

        if self.player_dead:
            self.dead_timer -= dt
            if self.dead_timer <= 0:
                print("GAME OVER")
                from scenes.menu_scene import MenuScene

                self.game.scene_manager.set(MenuScene(self.game))
            return

        if not self.inventory_ui.visible and not self.dialogue_ui.active:
            # Motion is resolved by PhysicsSystem to avoid double integration.
            self.player.update(dt, apply_motion=False)
            self._run_collision_step(dt)
            self._emit_thruster_feedback(dt)

        self.zone_name = self.world.get_zone_name(self.player.pos)

        unlocked_radius = self.world.get_unlocked_radius(self.narrative)
        distance_from_spawn = self.player.pos.distance_to(pygame.Vector2(SPAWN_POS))
        if distance_from_spawn > unlocked_radius:
            direction = (self.player.pos - pygame.Vector2(SPAWN_POS)).normalize()
            self.player.pos = pygame.Vector2(SPAWN_POS) + direction * unlocked_radius
            self.player.vel *= 0.3
            self.player.rect.center = self.player.pos
            self.set_status("Zone locked. Collect more logs to go deeper.", 2.2)
            self._apply_shake(SHAKE_BASE * 0.5)

        extra_drain = self.world.update(self.player, self.narrative, self.survival, dt)
        if self.player.hazard_resistance > 0:
            for stat in list(extra_drain.keys()):
                extra_drain[stat] *= 1.0 - self.player.hazard_resistance

        self.survival.update(dt, extra_drain=extra_drain)
        self.objectives.update(self.narrative, self.world)

        impact_speed = self.world.handle_player_asteroid_collisions(self.player)
        if self.impact_feedback_cd > 0:
            self.impact_feedback_cd -= dt
        elif impact_speed > 110:
            if impact_speed > 300:
                self.set_status("Asteroid impact: STRONG", 0.6)
                self._apply_shake(SHAKE_STRONG)
            elif impact_speed > 190:
                self.set_status("Asteroid impact: MEDIUM", 0.55)
                self._apply_shake(SHAKE_BASE + 2.0)
            else:
                self.set_status("Asteroid impact: LIGHT", 0.5)
                self._apply_shake(SHAKE_BASE)
            self.audio.play_sfx("impact", volume=0.48)
            self.impact_feedback_cd = 0.26

        self.camera.x = self.player.pos.x - WIDTH // 2
        self.camera.y = self.player.pos.y - HEIGHT // 2

        if self.camera_shake > 0:
            shake_x = pygame.math.Vector2(1, 0).rotate(pygame.time.get_ticks() * 0.2)
            self.camera += shake_x * (self.camera_shake * 0.35)
            self.camera_shake = max(0.0, self.camera_shake - SHAKE_DECAY * dt)

        if self.status_timer > 0:
            self.status_timer -= dt

        if self.survival.is_dead():
            self.player_dead = True
            self.dead_timer = 1.1
            self.player.image = load_image("assets/images/player/player_death/texture.png")
            self.set_status("Life support failure. Returning to menu...", 1.0)
            self.audio.play_sfx("warning", volume=0.62)

    # -------------------------
    # DRAW
    # -------------------------
    def draw(self, screen):
        if self.background is not None:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill((5, 5, 20))

        self.world.draw(screen, self.camera)
        self.effects.draw(screen, self.camera)
        self.particles.draw(screen, self.camera)
        screen.blit(self.player.image, self.player.rect.move(-self.camera))

        self.hud.draw(
            screen,
            self.survival,
            self.player,
            self.world,
            self.narrative,
            self.zone_name,
            self.narrative.get_ending(),
            self.objectives,
            self._build_interaction_hint(),
        )
        self.inventory_ui.draw(screen)
        self.dialogue_ui.draw(screen)

        if self.status_timer > 0 and self.status_message:
            text = self.status_font.render(self.status_message, True, (255, 255, 255))
            screen.blit(text, (WIDTH // 2 - 260, HEIGHT - 52))

    def _build_interaction_hint(self):
        # Prefer trigger-driven hints from the collision system; fallback to distance checks.
        if "log" in self.trigger_hints:
            return "Press E to collect log"
        if "terminal" in self.trigger_hints:
            return "Press E to unlock terminal"
        if "station" in self.trigger_hints:
            return "Press E to dock at ARES-7 station"
        return self.world.get_interaction_hint(self.player, self.narrative)
