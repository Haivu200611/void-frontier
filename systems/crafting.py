# =========================
# CRAFTING SYSTEM
# =========================

from data_loader import get_all_recipes, get_recipe

MODULE_ITEMS = {"habitat", "lab", "greenhouse", "hangar", "signal_tower"}
SUIT_ITEMS = {"suit_explorer_mk1", "suit_engineer_mk1", "suit_combat_mk1"}


class Crafting:
    def __init__(self, inventory):
        self.inv = inventory

    def get_options(self):
        return list(get_all_recipes().keys())

    def can_craft(self, item):
        recipe = get_recipe(item)
        if not recipe:
            return False
        return all(self.inv.has(k, v) for k, v in recipe.items())

    def craft(self, item):
        if not self.can_craft(item):
            return False

        recipe = get_recipe(item)

        for k, v in recipe.items():
            self.inv.remove(k, v)

        return True

    def classify(self, item):
        if item in MODULE_ITEMS:
            return "module"
        if item in SUIT_ITEMS:
            return "suit"
        return "consumable"
