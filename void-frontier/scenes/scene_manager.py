# =========================
# SCENE MANAGER
# =========================

class SceneManager:
    def __init__(self, game):
        self.game = game
        self.stack = []

    def set(self, scene):
        if self.stack:
            self.stack[-1].exit()
        self.stack = [scene]
        scene.enter()

    def push(self, scene):
        if self.stack:
            self.stack[-1].exit()
        self.stack.append(scene)
        scene.enter()

    def pop(self):
        if self.stack:
            self.stack[-1].exit()
            self.stack.pop()

        if self.stack:
            self.stack[-1].enter()

    def current(self):
        return self.stack[-1] if self.stack else None

    def handle_events(self, events):
        if self.stack:
            self.stack[-1].handle_events(events)

    def update(self, dt):
        if self.stack:
            self.stack[-1].update(dt)

    def draw(self, screen):
        if self.stack:
            self.stack[-1].draw(screen)