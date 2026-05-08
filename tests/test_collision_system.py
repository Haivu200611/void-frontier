import unittest

import pygame

from systems.physics import (
    BODY_DYNAMIC,
    BODY_SENSOR,
    BODY_STATIC,
    Collider,
    LAYER_PLAYER,
    LAYER_STATIC,
    LAYER_TRIGGER,
    PhysicsSystem,
)


class DummyBody:
    def __init__(self, rect, vel=(0, 0)):
        self.rect = rect.copy()
        self.pos = pygame.Vector2(self.rect.center)
        self.vel = pygame.Vector2(vel)


class CollisionSystemTests(unittest.TestCase):
    def setUp(self):
        self.physics = PhysicsSystem(cell_size=64)

    def test_aabb_collision_overlap(self):
        a_body = DummyBody(pygame.Rect(0, 0, 10, 10))
        b_body = DummyBody(pygame.Rect(5, 0, 10, 10))

        a = Collider(a_body, a_body.rect, body_type=BODY_DYNAMIC, layer=LAYER_PLAYER)
        b = Collider(b_body, b_body.rect, body_type=BODY_STATIC, layer=LAYER_STATIC)
        self.assertTrue(self.physics.check_aabb_collision(a, b))

    def test_collision_response_stop_and_slide(self):
        body = DummyBody(pygame.Rect(0, 0, 10, 10), vel=(20, 10))
        wall_body = DummyBody(pygame.Rect(15, 0, 10, 40))

        dynamic = Collider(
            owner=body,
            rect=body.rect,
            body_type=BODY_DYNAMIC,
            layer=LAYER_PLAYER,
            mask=LAYER_STATIC,
        )
        wall = Collider(
            owner=wall_body,
            rect=wall_body.rect,
            body_type=BODY_STATIC,
            layer=LAYER_STATIC,
            mask=LAYER_PLAYER,
        )

        self.physics.update(1.0, [dynamic], [wall])

        self.assertEqual(body.vel.x, 0)
        self.assertNotEqual(body.vel.y, 0)
        self.assertEqual(dynamic.rect.right, wall.rect.left)

    def test_trigger_event(self):
        body = DummyBody(pygame.Rect(0, 0, 10, 10))
        trigger_owner = {"kind": "log", "id": 1}

        dynamic = Collider(
            owner=body,
            rect=body.rect,
            body_type=BODY_DYNAMIC,
            layer=LAYER_PLAYER,
            mask=LAYER_TRIGGER,
        )
        trigger = Collider(
            owner=trigger_owner,
            rect=pygame.Rect(0, 0, 20, 20),
            body_type=BODY_SENSOR,
            is_trigger=True,
            layer=LAYER_TRIGGER,
            mask=LAYER_PLAYER,
        )

        events = self.physics.update(1 / 60.0, [dynamic], [trigger])
        self.assertTrue(any(ev.kind == "trigger" for ev in events))

    def test_bounce_restitution(self):
        body = DummyBody(pygame.Rect(0, 0, 10, 10), vel=(20, 0))
        wall_body = DummyBody(pygame.Rect(15, 0, 10, 30))

        dynamic = Collider(
            owner=body,
            rect=body.rect,
            body_type=BODY_DYNAMIC,
            layer=LAYER_PLAYER,
            mask=LAYER_STATIC,
        )
        wall = Collider(
            owner=wall_body,
            rect=wall_body.rect,
            body_type=BODY_STATIC,
            layer=LAYER_STATIC,
            mask=LAYER_PLAYER,
            restitution=0.5,
        )

        self.physics.update(1.0, [dynamic], [wall])
        self.assertLess(body.vel.x, 0)
        self.assertAlmostEqual(body.vel.x, -10.0, delta=0.01)


if __name__ == "__main__":
    unittest.main()
