# =========================
# SAVE / LOAD SYSTEM
# =========================

import json
import os

import pygame

from settings import SAVE_PATH, SPAWN_POS


class SaveSystem:
    def __init__(self, path=SAVE_PATH):
        self.path = path

    def has_save(self):
        return os.path.isfile(self.path)

    def save(self, scene):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        payload = {
            "player": {
                "pos": [float(scene.player.pos.x), float(scene.player.pos.y)],
                "vel": [float(scene.player.vel.x), float(scene.player.vel.y)],
                "max_speed": scene.player.max_speed,
                "accel": scene.player.accel,
                "mining_power_bonus": scene.player.mining_power_bonus,
                "hazard_resistance": scene.player.hazard_resistance,
            },
            "survival": scene.survival.stats,
            "inventory": scene.inventory.get_all(),
            "narrative": {
                "unlocked_logs": sorted(scene.narrative.unlocked_logs),
                "terminals": sorted(scene.narrative.terminals),
                "final_choice": scene.narrative.final_choice,
            },
            "world": scene.world.export_state(),
            "mission_stage": scene.objectives.stage,
        }

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def load(self, scene):
        if not self.has_save():
            return False

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return False

        player = data.get("player", {})
        px, py = player.get("pos", SPAWN_POS)
        vx, vy = player.get("vel", [0.0, 0.0])
        scene.player.pos = pygame.Vector2(px, py)
        scene.player.vel = pygame.Vector2(vx, vy)
        scene.player.rect.center = scene.player.pos
        scene.player.max_speed = float(player.get("max_speed", scene.player.max_speed))
        scene.player.accel = float(player.get("accel", scene.player.accel))
        scene.player.mining_power_bonus = int(
            player.get("mining_power_bonus", scene.player.mining_power_bonus)
        )
        scene.player.hazard_resistance = float(
            player.get("hazard_resistance", scene.player.hazard_resistance)
        )

        for stat, value in data.get("survival", {}).items():
            scene.survival.stats[stat] = max(0.0, min(100.0, float(value)))

        scene.inventory.items = {
            str(k): int(v) for k, v in data.get("inventory", {}).items() if int(v) > 0
        }

        narrative = data.get("narrative", {})
        scene.narrative.unlocked_logs = set(
            int(v) for v in narrative.get("unlocked_logs", []) if isinstance(v, int)
        )
        scene.narrative.terminals = set(str(v) for v in narrative.get("terminals", []))
        scene.narrative.final_choice = narrative.get("final_choice")

        scene.world.import_state(data.get("world", {}))

        stage = data.get("mission_stage")
        if isinstance(stage, str):
            scene.objectives.set_stage(stage)

        return True
