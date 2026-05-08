# =========================
# TRANSIENT VISUAL EFFECTS
# =========================

import pygame

from asset_loader import load_image


class Effect:
    def __init__(self, pos, texture_path, duration=0.22, scale=1.0, tint=None):
        self.pos = pygame.Vector2(pos)
        self.duration = max(0.05, float(duration))
        self.life = self.duration

        base = load_image(texture_path)
        width = max(8, int(base.get_width() * scale))
        height = max(8, int(base.get_height() * scale))
        self.image = pygame.transform.smoothscale(base, (width, height))
        if tint is not None:
            self.image = self.image.copy()
            self.image.fill(tint, special_flags=pygame.BLEND_RGBA_MULT)

        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def update(self, dt):
        self.life -= dt
        alpha = max(0, min(255, int(255 * (self.life / self.duration))))
        self.image.set_alpha(alpha)

    def is_alive(self):
        return self.life > 0

    def draw(self, screen, cam):
        screen.blit(self.image, self.rect.move(-cam))


class EffectLayer:
    def __init__(self):
        self.effects = []

    def spawn(self, pos, texture_path, duration=0.22, scale=1.0, tint=None):
        self.effects.append(Effect(pos, texture_path, duration=duration, scale=scale, tint=tint))

    def update(self, dt):
        for effect in self.effects:
            effect.update(dt)
        self.effects = [e for e in self.effects if e.is_alive()]

    def draw(self, screen, cam):
        for effect in self.effects:
            effect.draw(screen, cam)
