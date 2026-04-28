# =========================
# ASSET LOADER
# =========================

import pygame
import os

IMAGE_CACHE = {}
ANIMATION_CACHE = {}


def _make_placeholder(size=(64, 64), color=(255, 0, 255)):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill((25, 25, 35))
    pygame.draw.rect(surface, color, surface.get_rect(), 3)
    pygame.draw.line(surface, color, (0, 0), (size[0] - 1, size[1] - 1), 2)
    pygame.draw.line(surface, color, (size[0] - 1, 0), (0, size[1] - 1), 2)
    return surface


# -------------------------
# LOAD SINGLE IMAGE
# -------------------------
def load_image(path):
    if path not in IMAGE_CACHE:
        try:
            IMAGE_CACHE[path] = pygame.image.load(path).convert_alpha()
        except (FileNotFoundError, pygame.error):
            IMAGE_CACHE[path] = _make_placeholder()
    return IMAGE_CACHE[path]


# -------------------------
# LOAD ANIMATION (folder)
# -------------------------
def load_animation(folder, fallback_size=(64, 64), fallback_color=(255, 0, 255)):
    cache_key = (folder, fallback_size, fallback_color)

    if cache_key in ANIMATION_CACHE:
        return ANIMATION_CACHE[cache_key]

    frames = []

    if os.path.isdir(folder):
        for file in sorted(os.listdir(folder)):
            if file.lower().endswith(".png"):
                path = os.path.join(folder, file)
                frames.append(load_image(path))

    if not frames:
        frames = [_make_placeholder(fallback_size, fallback_color)]

    ANIMATION_CACHE[cache_key] = frames
    return frames


# -------------------------
# LOAD SOUND
# -------------------------
def load_sound(path):
    return pygame.mixer.Sound(path)


# -------------------------
# LOAD FONT
# -------------------------
def load_font(path, size):
    return pygame.font.Font(path, size)
