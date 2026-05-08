import os


CORE_REQUIRED_ASSETS = [
    # Player states
    "assets/images/player/player_idle/texture.png",
    "assets/images/player/player_move/texture.png",
    "assets/images/player/player_thruster/texture.png",
    # Asteroids
    "assets/images/asteroids/asteroid_iron/texture.png",
    "assets/images/asteroids/asteroid_titanium/texture.png",
    "assets/images/asteroids/asteroid_silicon/texture.png",
    "assets/images/asteroids/asteroid_copper/texture.png",
    "assets/images/asteroids/asteroid_ice/texture.png",
    "assets/images/asteroids/asteroid_carbon/texture.png",
    # Modules
    "assets/images/modules/module_habitat/texture.png",
    "assets/images/modules/module_lab/texture.png",
    "assets/images/modules/module_greenhouse/texture.png",
    "assets/images/modules/module_hangar/texture.png",
    "assets/images/modules/module_signal_tower/texture.png",
    # HUD / UI
    "assets/images/ui/ui_hud/bar_bg.png",
    "assets/images/ui/ui_hud/bar_fill.png",
    "assets/images/ui/ui_icons/iron.png",
    "assets/images/ui/ui_icons/titanium.png",
    "assets/images/ui/ui_icons/silicon.png",
    "assets/images/ui/ui_icons/copper.png",
    "assets/images/ui/ui_icons/ice.png",
    "assets/images/ui/ui_icons/carbon.png",
]


def validate_assets(project_root):
    missing = []
    present = []

    for rel_path in CORE_REQUIRED_ASSETS:
        abs_path = os.path.join(project_root, rel_path)
        if os.path.isfile(abs_path):
            present.append(rel_path)
        else:
            missing.append(rel_path)

    return {
        "required_count": len(CORE_REQUIRED_ASSETS),
        "present_count": len(present),
        "missing_count": len(missing),
        "present": present,
        "missing": missing,
    }
