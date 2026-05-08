# =========================
# OBJECTIVE / MISSION FLOW
# =========================


class Objectives:
    STAGES = [
        "bootstrap",
        "reach_ares",
        "stabilize_base",
        "unlock_xenith",
        "final_choice",
    ]

    def __init__(self):
        self.stage = "bootstrap"

    def set_stage(self, stage):
        if stage in self.STAGES:
            self.stage = stage

    def update(self, narrative, world):
        logs = len(narrative.unlocked_logs)
        terminals = len(narrative.terminals)
        modules = len(world.modules)

        if narrative.get_ending() == "pending_choice":
            self.stage = "final_choice"
        elif logs >= 20:
            self.stage = "unlock_xenith"
        elif logs >= 5 and modules >= 3:
            self.stage = "stabilize_base"
        elif logs >= 5:
            self.stage = "reach_ares"
        else:
            self.stage = "bootstrap"

    def get_lines(self):
        if self.stage == "bootstrap":
            return [
                "Objective: Gather resources and collect 5 logs",
                "Tip: Mine nearby asteroids, build first module",
            ]
        if self.stage == "reach_ares":
            return [
                "Objective: Reach ARES-7 progression",
                "Tip: Build 3 modules to stabilize your survival loop",
            ]
        if self.stage == "stabilize_base":
            return [
                "Objective: Push to outer zones and gather 20 logs",
                "Tip: Use suit upgrades for mining and hazard resistance",
            ]
        if self.stage == "unlock_xenith":
            return [
                "Objective: Unlock all terminals and logs",
                "Tip: Explore deep space and interact with signal nodes",
            ]
        return [
            "Objective: Final choice available",
            "Press 1/2/3 to select ending path",
        ]
