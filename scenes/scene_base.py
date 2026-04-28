# =========================
# BASE SCENE
# =========================

class Scene:
    def __init__(self, game):
        self.game = game

    def enter(self):
        """Gọi khi scene được kích hoạt"""
        pass

    def exit(self):
        """Gọi khi rời scene"""
        pass

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass