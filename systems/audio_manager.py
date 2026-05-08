# =========================
# AUDIO MANAGER
# =========================

import pygame

from asset_loader import load_sound


class AudioManager:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        self.ambient_channel = None
        self.sfx_channel = None
        self._init_mixer()
        self._load_sounds()

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.enabled = True
            self.ambient_channel = pygame.mixer.Channel(0)
            self.sfx_channel = pygame.mixer.Channel(1)
        except pygame.error:
            self.enabled = False

    def _load_sounds(self):
        self.sounds = {
            "ambient": load_sound("assets/sounds/ambient/space_loop.wav"),
            "jetpack": load_sound("assets/sounds/fx/jetpack.wav"),
            "mining": load_sound("assets/sounds/fx/mining.wav"),
            "explosion": load_sound("assets/sounds/fx/explosion.wav"),
            "click": load_sound("assets/sounds/fx/click.wav"),
            "warning": load_sound("assets/sounds/fx/warning.wav"),
            "impact": load_sound("assets/sounds/fx/impact.wav"),
        }

    def play_ambient(self):
        sound = self.sounds.get("ambient")
        if sound is None:
            return
        if not self.enabled or self.ambient_channel is None:
            sound.play()
            return
        if not isinstance(sound, pygame.mixer.Sound):
            sound.play()
            return
        if not self.ambient_channel.get_busy():
            self.ambient_channel.set_volume(0.3)
            self.ambient_channel.play(sound, loops=-1)

    def stop_ambient(self):
        if self.ambient_channel is not None:
            self.ambient_channel.stop()

    def play_sfx(self, key, volume=0.55):
        sound = self.sounds.get(key)
        if sound is None:
            return
        if not self.enabled or self.sfx_channel is None:
            sound.play()
            return
        if not isinstance(sound, pygame.mixer.Sound):
            sound.play()
            return
        self.sfx_channel.set_volume(volume)
        self.sfx_channel.play(sound)
