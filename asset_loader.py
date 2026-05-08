# =========================
# ASSET LOADER
# =========================

import pygame
import os

IMAGE_CACHE = {}
ANIMATION_CACHE = {}
SOUND_CACHE = {}
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def _resolve_path(path):
    if os.path.isabs(path):
        return path
    return os.path.join(PROJECT_ROOT, path)


def _make_placeholder(size=(64, 64), color=(255, 0, 255)):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill((25, 25, 35))
    pygame.draw.rect(surface, color, surface.get_rect(), 3)
    pygame.draw.line(surface, color, (0, 0), (size[0] - 1, size[1] - 1), 2)
    pygame.draw.line(surface, color, (size[0] - 1, 0), (0, size[1] - 1), 2)
    return surface


def asset_exists(path):
    return os.path.isfile(_resolve_path(path))


# -------------------------
# LOAD SINGLE IMAGE
# -------------------------
def load_image(path):
    resolved_path = _resolve_path(path)
    if resolved_path not in IMAGE_CACHE:
        try:
            IMAGE_CACHE[resolved_path] = pygame.image.load(resolved_path).convert_alpha()
        except (FileNotFoundError, pygame.error):
            IMAGE_CACHE[resolved_path] = _make_placeholder()
    return IMAGE_CACHE[resolved_path]


# -------------------------
# LOAD ANIMATION (folder)
# -------------------------
def load_animation(folder, fallback_size=(64, 64), fallback_color=(255, 0, 255)):
    resolved_folder = _resolve_path(folder)
    cache_key = (resolved_folder, fallback_size, fallback_color)

    if cache_key in ANIMATION_CACHE:
        return ANIMATION_CACHE[cache_key]

    frames = []

    if os.path.isdir(resolved_folder):
        for file in sorted(os.listdir(resolved_folder)):
            if file.lower().endswith(".png"):
                path = os.path.join(resolved_folder, file)
                frames.append(load_image(path))

    if not frames:
        frames = [_make_placeholder(fallback_size, fallback_color)]

    ANIMATION_CACHE[cache_key] = frames
    return frames


# -------------------------
# LOAD SOUND
# -------------------------
def load_sound(path):
    resolved_path = _resolve_path(path)
    if resolved_path in SOUND_CACHE:
        return SOUND_CACHE[resolved_path]

    # pygame.mixer may be unavailable in some dev environments.
    if not pygame.mixer.get_init():
        class _SilentSound:
            def play(self, *args, **kwargs):
                return None

        SOUND_CACHE[resolved_path] = _SilentSound()
        return SOUND_CACHE[resolved_path]

    try:
        SOUND_CACHE[resolved_path] = pygame.mixer.Sound(resolved_path)
    except (FileNotFoundError, pygame.error):
        class _SilentSound:
            def play(self, *args, **kwargs):
                return None

        SOUND_CACHE[resolved_path] = _SilentSound()

    return SOUND_CACHE[resolved_path]


# -------------------------
# LOAD FONT
# -------------------------
def load_font(path, size):
    resolved_path = _resolve_path(path)
    if os.path.isfile(resolved_path):
        return pygame.font.Font(resolved_path, size)
    return pygame.font.SysFont(None, size)
