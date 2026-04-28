# =========================
# CRAFTING SYSTEM
# =========================

from data_loader import get_recipe


class Crafting:
    def __init__(self, inventory):
        self.inv = inventory

    def can_craft(self, item):
        recipe = get_recipe(item)
        return all(self.inv.has(k, v) for k, v in recipe.items())

    def craft(self, item):
        if not self.can_craft(item):
            return False

        recipe = get_recipe(item)

        for k, v in recipe.items():
            self.inv.remove(k, v)

        return True