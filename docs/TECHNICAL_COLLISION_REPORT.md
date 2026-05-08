# TECHNICAL_COLLISION_REPORT

## 1. Mục tiêu nâng cấp
Đợt nâng cấp này mở rộng hệ thống va chạm 2D cho Void Frontier theo hướng incremental, không rewrite project:
- Không cho player xuyên qua vật cản tĩnh (module, station hull).
- Thêm trigger/sensor để nhận biết vùng tương tác (log, terminal, station).
- Giữ đặc tính zero-g inertia hiện có.
- Bổ sung bước chống tunneling cơ bản cho chuyển động nhanh theo trục (swept-axis).
- Giữ kiến trúc hiện có: scene/world/entity vẫn là trung tâm gameplay, physics chỉ là subsystem.

## 2. Phân tích trạng thái trước khi nâng cấp

### 2.1 Trước nâng cấp `systems/physics.py`
- Chỉ có helper đơn giản (`apply_velocity`, `apply_friction`, `clamp_speed`, `handle_collision`).
- Không có layer/mask, không có trigger, không có broadphase, không có tách penetration chuẩn.

### 2.2 Flow runtime trước nâng cấp
- Player update trực tiếp trong `entities/player.py`.
- Va chạm player-asteroid xử lý riêng trong `world.handle_player_asteroid_collisions()` + `asteroid.resolve_player_collision()`.
- Chưa có hệ thống va chạm tổng quát cho static objects như module/station.

## 3. Thiết kế mới

## 3.1 Thành phần chính
- `Collider`:
  - `owner`, `rect`, `body_type` (`dynamic/static/sensor`), `is_trigger`, `layer`, `mask`, `restitution`.
- `CollisionEvent`:
  - Trả về event collision/trigger để gameplay layer xử lý callback/hint.
- `PhysicsSystem`:
  - Broad phase: spatial hash grid.
  - Narrow phase: AABB (`pygame.Rect.colliderect`).
  - Response: stop/slide theo từng trục, có hỗ trợ bounce qua `restitution`.
  - CCD-lite: swept-axis hit time để giảm tunneling khi di chuyển nhanh.

## 3.2 Collision layers/masks
Định nghĩa bitmask trong `systems/physics.py`:
- `LAYER_PLAYER = 0x01`
- `LAYER_STATIC = 0x02`
- `LAYER_ASTEROID = 0x04`
- `LAYER_TRIGGER = 0x08`

Rule lọc pair:
- Chỉ xử lý nếu `(a.mask & b.layer) != 0` và `(b.mask & a.layer) != 0`.

## 3.3 Broad Phase
Spatial hash theo `cell_size`:
- Gán collider vào các cell dựa trên `rect`.
- Query candidate từ cell hiện tại + lân cận của dynamic collider.
- Giảm so sánh pair không cần thiết khi world đông object.

## 3.4 Narrow Phase + Response
- Narrow phase dùng AABB.
- Resolution theo trục:
  1. Move theo X -> resolve va chạm X -> zero/bounce `vel.x`
  2. Move theo Y -> resolve va chạm Y -> zero/bounce `vel.y`
- Cách này cho hiệu ứng trượt (slide): dừng theo trục va chạm, giữ trục còn lại.

## 3.5 Swept-axis (CCD-lite)
- Trước khi cộng full delta, physics tìm `time-of-hit` sớm nhất trên từng trục cho static colliders.
- Dynamic collider chỉ di chuyển đến điểm chạm (`delta * t_hit`) rồi resolve.
- Giảm trường hợp xuyên tường khi `vel * dt` lớn.

## 3.6 Trigger/Sensor
- Collider `body_type = sensor` hoặc `is_trigger = True` chỉ phát event, không đẩy vị trí.
- Event trigger được dùng để tạo interaction hints trong gameplay HUD.

## 4. Tích hợp vào project hiện tại

## 4.1 File thay đổi
- `systems/physics.py`:
  - Nâng cấp thành subsystem va chạm hoàn chỉnh.
- `systems/world.py`:
  - Thêm `get_collision_colliders(narrative)`:
    - Static colliders: modules, station hull.
    - Trigger colliders: log/terminal/station vùng tương tác.
- `scenes/space_scene.py`:
  - Tạo `self.physics = PhysicsSystem(...)`.
  - Thêm `_run_collision_step(dt)` trong update flow.
  - Đồng bộ `player.rect` từ vị trí resolved của physics.
  - Dùng trigger events để dựng interaction hint.

## 4.2 Thứ tự update mới trong gameplay
1. Input -> player velocity update.
2. Physics collision step (player vs static/trigger).
3. World update (spawn/hazard/module effects).
4. Survival update.
5. Asteroid impact logic riêng (giữ hệ cũ để có impulse/bounce đặc thù).
6. Camera + render.

## 5. Tương tác với zero-g
- Inertia vẫn giữ nguyên (không thêm gravity).
- Va chạm chỉ loại thành phần vận tốc theo trục va chạm.
- Player vẫn có thể trượt dọc bề mặt khi giữ thrust.

## 6. Test và kiểm thử
Thêm test tại `tests/test_collision_system.py`:
- `test_aabb_collision_overlap`
- `test_collision_response_stop_and_slide`
- `test_trigger_event`
- `test_bounce_restitution`

Kết quả:
- `python -m unittest discover -s tests -v` -> PASS.
- Smoke runtime (`Menu -> SPACE -> SpaceScene`) -> PASS.

## 7. Giới hạn hiện tại và hướng mở rộng
- Hệ thống hiện tập trung AABB + swept-axis một trục, chưa triển khai SAT polygon.
- Asteroid-player vẫn dùng solver riêng để giữ cảm giác impact hiện có.
- Nếu cần mở rộng thêm:
  - Bổ sung dynamic-dynamic generic solver cho nhiều loại entity.
  - Thêm lựa chọn `pygame.mask` cho pixel-perfect collision ở đối tượng đặc biệt.
  - Mở rộng callback `on_collision()` theo owner interface.

## 8. Kết luận
Hệ va chạm mới đã được tích hợp vào runtime theo cách modular, ít phá vỡ kiến trúc cũ, xử lý tốt hơn các case stop/slide/trigger và giảm nguy cơ tunneling. Đây là nền tảng phù hợp để tiếp tục mở rộng gameplay survival-space mà không cần overhaul toàn bộ project.
