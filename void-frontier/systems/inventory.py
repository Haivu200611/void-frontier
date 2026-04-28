# =========================
# INVENTORY SYSTEM
# =========================

class Inventory:
    def __init__(self):
        self.items = {}

    def add(self, item, amount=1):
        self.items[item] = self.items.get(item, 0) + amount

    def has(self, item, amount):
        return self.items.get(item, 0) >= amount

    def remove(self, item, amount):
        if self.has(item, amount):
            self.items[item] -= amount

            if self.items[item] <= 0:
                del self.items[item]

    def get_all(self):
        return self.items