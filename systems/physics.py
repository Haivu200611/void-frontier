# =========================
# PHYSICS SYSTEM
# =========================

def apply_velocity(player, dt):
    player.pos += player.vel * dt
    player.rect.center = player.pos


def apply_friction(player):
    player.vel *= 0.98


def clamp_speed(player, max_speed):
    if player.vel.length() > max_speed:
        player.vel.scale_to_length(max_speed)


def handle_collision(player, objects):
    for obj in objects:
        if player.rect.colliderect(obj.rect):
            player.vel *= -0.5