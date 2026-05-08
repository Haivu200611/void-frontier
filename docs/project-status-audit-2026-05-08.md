# Báo Cáo Kỹ Thuật Trạng Thái Project - Void Frontier

Ngày audit: 2026-05-08  
Phạm vi: toàn bộ source code trong `d:\void-frontier\void-frontier` (Python, JSON data, cấu trúc assets)

## 1. Tổng quan project
- Game hiện tại: game 2D sinh tồn ngoài không gian, điều khiển nhân vật bay zero-g để khai thác asteroid, quản lý chỉ số sống còn, thu thập log/terminal và mở khóa kết thúc.
- Genre: `2D Space Survival Exploration`.
- Gameplay loop hiện tại (thực tế theo code):
  - Bay khám phá quanh spawn
  - Mine asteroid bằng click chuột trái
  - Thu resource vào inventory
  - Craft module/suit/consumable
  - Chịu drain survival + hazard
  - Tương tác log/terminal để mở tiến độ zone và endgame choice
- Góc nhìn game: top-down 2D camera follow player.
- Công nghệ sử dụng:
  - Python 3
  - pygame
  - Data-driven JSON (`data/asteroids.json`, `data/recipes.json`, `data/logs/*.json`)
- Kiến trúc tổng thể:
  - `main.py` chạy game loop chuẩn pygame
  - Scene stack manager (`SceneManager`) điều hướng menu/gameplay/overlay
  - Gameplay chính nằm ở `SpaceScene` + các system tách lớp (`World`, `Survival`, `Inventory`, `Crafting`, `Narrative`)
  - Entity layer cho player/asteroid/hazard/module
  - UI layer riêng cho HUD và Inventory overlay

## 2. Cấu trúc source code
### 2.1 Toàn bộ folder
```text
void-frontier/
├─ assets/
│  ├─ fonts/
│  ├─ images/
│  │  ├─ asteroids/
│  │  │  ├─ asteroid_carbon/
│  │  │  ├─ asteroid_copper/
│  │  │  ├─ asteroid_ice/
│  │  │  ├─ asteroid_iron/
│  │  │  ├─ asteroid_silicon/
│  │  │  └─ asteroid_titanium/
│  │  ├─ background/
│  │  ├─ effects/
│  │  │  ├─ effect_explosion/
│  │  │  ├─ effect_mining/
│  │  │  └─ effect_thruster/
│  │  ├─ modules/
│  │  │  ├─ module_greenhouse/
│  │  │  ├─ module_habitat/
│  │  │  ├─ module_hangar/
│  │  │  ├─ module_lab/
│  │  │  └─ module_signal_tower/
│  │  ├─ player/
│  │  │  ├─ player_death/
│  │  │  ├─ player_idle/
│  │  │  ├─ player_move/
│  │  │  └─ player_thruster/
│  │  └─ ui/
│  │     ├─ ui_hud/
│  │     └─ ui_icons/
│  └─ sounds/
│     ├─ ambient/
│     ├─ fx/
│     └─ logs/
├─ data/
│  ├─ logs/
│  └─ __pycache__/
├─ docs/
├─ entities/
│  └─ __pycache__/
├─ scenes/
│  └─ __pycache__/
├─ systems/
│  └─ __pycache__/
├─ ui/
│  └─ __pycache__/
└─ __pycache__/
```

### 2.2 Vai trò từng folder
- `scenes/`: scene flow (menu, gameplay, crafting overlay, station placeholder).
- `systems/`: gameplay systems (world streaming, survival, inventory, crafting, narrative, physics helper cũ).
- `entities/`: object gameplay (player, asteroid, hazard, module, particle).
- `ui/`: HUD, inventory overlay, dialogue UI.
- `data/`: data tĩnh cho asteroid/recipe/log.
- `assets/`: texture/audio/font; có nhiều placeholder `Add.md`.
- `docs/`: tài liệu mô tả kỹ thuật.
- `__pycache__/`: file bytecode runtime.

### 2.3 Vai trò từng file quan trọng
- `main.py`: entrypoint, init pygame, main loop, dispatch event/update/draw.
- `settings.py`: gameplay constants toàn cục.
- `asset_loader.py`: load image/animation/sound/font + fallback placeholder.
- `asset_manifest.py`: validate tập asset core lúc boot.
- `data_loader.py`: nạp asteroid/recipe/log từ JSON.

- `scenes/scene_manager.py`: scene stack (`set/push/pop`).
- `scenes/menu_scene.py`: menu start game.
- `scenes/space_scene.py`: gameplay scene chính.
- `scenes/crafting_scene.py`: overlay crafting.
- `scenes/station_scene.py`: scene station, hiện chưa có luồng vào.

- `systems/world.py`: chunk loading, spawn asteroid/hazard/narrative node, zone unlock, radar data, collision handling, world rendering.
- `systems/survival.py`: quản lý 5 stat và death condition.
- `systems/inventory.py`: container item số lượng.
- `systems/crafting.py`: recipe check/consume/classify item.
- `systems/narrative.py`: log/terminal progression + ending state.
- `systems/physics.py`: helper physics độc lập, hiện không được gọi.

- `entities/player.py`: input zero-g + motion + suit upgrade stat.
- `entities/asteroid.py`: hp, drop, drift movement, impact response.
- `entities/hazard.py`: hazard types và drain/damage logic.
- `entities/module.py`: base modules và aura effect hồi stat.
- `entities/particle.py`: particle system, hiện không tích hợp.

- `ui/hud.py`: stat bars, radar, meta/progress, warning.
- `ui/inventory_ui.py`: inventory overlay toggle/selection.
- `ui/dialogue_ui.py`: typewriter dialogue box, hiện không tích hợp.

### 2.4 File core gameplay
- Core gameplay hiện tại nằm chủ yếu ở:
  - `scenes/space_scene.py`
  - `systems/world.py`
  - `entities/player.py`
  - `systems/survival.py`

### 2.5 File quản lý state/game loop
- Vòng lặp game tổng: `main.py` (`Game.run`).
- Scene state tổng: `scenes/scene_manager.py`.
- Runtime gameplay state: `scenes/space_scene.py` (player/world/survival/inventory/crafting/narrative/camera/status).

## 3. Gameplay hiện tại đã có gì
Chỉ liệt kê thứ thực sự tồn tại trong code runtime.

- Movement:
  - Có `WASD` thrust theo vector.
  - Có quán tính zero-g (`vel += acc*dt`, drag nhẹ).
  - Có giới hạn tốc độ tối đa.
- Jetpack:
  - Có animation state `thrust` khi có input.
  - Không có resource tiêu hao riêng cho thrust (battery không giảm theo thrust trong code hiện tại).
- Mining:
  - Click chuột trái để mine asteroid nếu click trúng rect asteroid và trong `MINE_RANGE`.
  - Damage mine = `MINING_POWER + mining_power_bonus`.
  - Asteroid nổ thì drop item theo JSON vào inventory.
- Inventory:
  - Có add/has/remove/get_all.
  - Có UI overlay bật/tắt bằng `I`.
- Crafting:
  - Có scene overlay (`TAB`), chọn item bằng `UP/DOWN`, craft bằng `ENTER`.
  - Recipe đọc từ JSON.
  - Craft thành công: module spawn gần player hoặc apply suit upgrade hoặc dùng consumable hồi stat.
- Building:
  - Có đặt module trực tiếp sau craft (không có placement preview/grid/rotate).
  - Module hoạt động theo bán kính aura (habitat/greenhouse/hangar).
- Survival systems:
  - Có 5 stat: oxygen/temperature/battery/hunger/pressure.
  - Drain theo thời gian + extra drain từ hazard.
  - Pressure = 0 làm oxygen tụt thêm; hunger = 0 làm temperature tụt thêm.
  - Chết khi oxygen hoặc temperature hoặc pressure về 0.
- Combat:
  - Không có combat với enemy.
  - Chỉ có va chạm player-asteroid và hazard damage.
- Dialogue:
  - Có class `DialogueUI`, nhưng không được gọi trong scene gameplay.
- Quest:
  - Không có quest system riêng.
  - Có progression dạng log/terminal count và HUD mission progress.
- Scene switching:
  - Có Menu -> Space.
  - Có push/pop Crafting overlay.
  - Có quay lại Menu khi chết.
  - `StationScene` tồn tại nhưng không có đường vào.
- Save/load:
  - Không có save/load progression runtime.
- UI systems:
  - HUD stat bars + radar + zone/log/terminal/module/progress + warning low stat + hint controls.
  - Inventory overlay.
  - Crafting overlay.
- Audio:
  - Có loader `load_sound`, có fallback silent object.
  - Không có chỗ nào trong gameplay gọi phát âm thanh.
- Particle effects:
  - Có `Particle`/`ParticleSystem` class.
  - Không được instantiate/cập nhật/vẽ ở luồng gameplay.
- Physics:
  - Player physics chạy trong `entities/player.py`.
  - Asteroid drift + collision response trong `entities/asteroid.py` và `World.handle_player_asteroid_collisions`.
  - `systems/physics.py` không được dùng.
- World generation:
  - Có chunk streaming theo vị trí player.
  - Spawn asteroid/hazard/narrative node theo zone + random chance.
  - Có unload nội dung xa player theo chu kỳ.
- AI/NPC:
  - Không có NPC/AI runtime.
- Anything else:
  - Có multiple ending state (`good/neutral/bad/pending_choice/incomplete`) dựa vào lựa chọn 1/2/3 khi đủ log+terminal.
  - Chọn ending hiện tại sẽ `print` và thoát game ngay (`self.game.running = False`).

## 4. Các system đã hoàn thiện
### 4.1 Hoạt động tốt (đang chạy thật trong gameplay)
- Main loop + scene manager cơ bản.
- Player zero-g movement + active brake.
- Asteroid mining + drop resource.
- Inventory data model + inventory UI.
- Crafting theo recipe + consume resource.
- World chunk load/unload theo vị trí.
- Hazard drain tích hợp vào survival.
- Survival drain/death + HUD warning.
- Zone progression gate bằng số log.
- Log/terminal interaction + mission progress HUD.

### 4.2 Tương đối hoàn chỉnh trong phạm vi prototype hiện tại
- Radar hiển thị asteroid gần player.
- Module support effect (habitat/greenhouse/hangar).
- Suit upgrade effect (explorer/engineer/combat).
- Asset fallback strategy (thiếu texture vẫn chạy).

### 4.3 Mới mức prototype / chưa polish
- Crafting UX (text list cơ bản, không preview cost/insufficient breakdown).
- Narrative presentation (chỉ status text, chưa hiển thị nội dung log/dialogue trong gameplay).
- Ending flow (không có ending scene/cutscene, chọn xong thoát process).
- Va chạm asteroid-player (logic có, chưa có feedback audiovisual đầy đủ).

### 4.4 Có code nhưng chưa dùng tới
- `systems/physics.py`.
- `entities/particle.py`.
- `ui/dialogue_ui.py`.
- `scenes/station_scene.py`.
- `data/settings.py` (runtime dùng `settings.py` ở root).

## 5. Các feature còn thiếu
### 5.1 Thiếu để thành gameplay loop hoàn chỉnh hơn
- Nội dung đọc log/terminal trong game (hiện chỉ unlock count, không hiển thị text log).
- Luồng kết thúc game in-world (ending scene thay vì thoát ứng dụng).
- Cơ chế mục tiêu/goal từng phase (hiện chủ yếu tự khám phá).

### 5.2 Thiếu để playable bền vững
- Save/load (mất toàn bộ progress khi thoát).
- Audio gameplay (SFX/BGM chưa tích hợp call runtime).
- Cân bằng spawn/progression có kiểm soát (hiện random thuần, không seed/biên bản sinh đảm bảo pacing).

### 5.3 Thiếu để thành vertical slice
- Trình bày narrative hoàn chỉnh (UI đọc log, terminal interaction depth).
- Combat/NPC layer (nếu design hướng survival adventure có xung đột).
- Content pass cho zone (unique encounter/objective thay vì chỉ tăng hazard/resource table).

### 5.4 Thiếu để release alpha
- Save system + checkpoint.
- Full UX pass cho menu/pause/settings/game over/ending.
- Telemetry/debug controls rõ ràng cho balancing.
- Test coverage hoặc ít nhất smoke test runtime theo scene.
- Asset/audio pass đồng bộ (hiện nhiều thư mục placeholder).

## 6. Kiến trúc hiện tại có vấn đề gì
### 6.1 Circular import
- Không có vòng lặp import cứng gây crash tại load-time.
- Có coupling vòng mềm giữa `menu_scene` và `space_scene` (Menu import SpaceScene; SpaceScene import MenuScene trong nhánh death) nhưng đang né circular bằng local import.

### 6.2 Tight coupling
- `SpaceScene` biết quá nhiều system và orchestration chi tiết (player/world/survival/inventory/crafting/narrative/UI/input/ending).
- `CraftingScene` truy cập trực tiếp `self.game.scene_manager.stack[0]` để gọi gameplay scene.

### 6.3 File quá lớn
- `systems/world.py` ~287 dòng: gom nhiều trách nhiệm (streaming, spawning, hazards, progression, interaction, collision, radar, render).
- `scenes/space_scene.py` ~203 dòng: scene vừa input/update/draw vừa business rules gameplay.

### 6.4 Logic đặt sai chỗ / rủi ro maintain
- Ending logic đặt trong `SpaceScene.trigger_ending` và dừng hẳn game loop ngay, không tách thành ending scene/state handler.
- `SceneManager.push` gọi `exit()` scene dưới, nên overlay semantics không đúng nghĩa "pause+resume" nếu sau này `exit()` có side effects.

### 6.5 Update loop issues
- Mọi asteroid vẫn bị iterate mỗi frame cho collision broad-phase; khi world đông sẽ tăng CPU cost.
- `InventoryUI` visible nhưng gameplay vẫn update bình thường (không pause simulation), có thể gây trải nghiệm không mong muốn.

### 6.6 Rendering issues
- Render pipeline đơn giản, chưa có layer batching/culling cho tất cả object types ngoài rect viewport check.
- Background load theo file đầu tiên trong folder, không có explicit asset chọn theo config.

### 6.7 Performance risks
- Spawn random chunk + nhiều object update/draw trong Python thuần có thể bottleneck ở quy mô lớn.
- `get_radar_points` scan qua nhóm asteroid hiện có; có cap 220 điểm nhưng vẫn duyệt list trước khi đủ cap (dù break sớm khi đạt cap).

### 6.8 Memory risks
- Hiện tại không thấy leak rõ ràng nghiêm trọng.
- `log_nodes`/`terminal_nodes` không cleanup theo chunk, nhưng bị chặn số lượng bởi `TOTAL_LOGS` và `TOTAL_TERMINALS` nên bounded.

### 6.9 Bad architecture decisions (mức audit hiện tại)
- Phụ thuộc scene stack index cứng (`stack[0]`) trong crafting overlay.
- Một số module mang tính "dead code" chưa được tích hợp nhưng đã tồn tại song song, làm nhiễu kiến trúc runtime thực.

## 7. Flow hoạt động của game
### 7.1 Main loop
- `Game.run()`:
  - `dt = clock.tick(FPS) / 1000`
  - `handle_events()`
  - `update()`
  - `draw()`
- Thoát vòng lặp thì `pygame.quit()` và `sys.exit()`.

### 7.2 Scene flow
- Start: `MenuScene`.
- `SPACE` ở menu -> `SceneManager.set(SpaceScene)`.
- Trong Space:
  - `TAB` -> `SceneManager.push(CraftingScene)`.
  - `ESC` trong Crafting -> `pop()` quay lại Space.
- Khi chết (`survival.is_dead`) -> `SceneManager.set(MenuScene)`.
- `StationScene` không được gọi ở bất kỳ đâu.

### 7.3 Event handling flow
- `Game.handle_events` lấy toàn bộ pygame events.
- `QUIT` ở mức game -> `running=False`.
- Events chuyển cho scene hiện tại.
- `SpaceScene.handle_events` xử lý:
  - `I`, `TAB`, `E`, `1/2/3`, inventory input, LMB mine.

### 7.4 Update flow
- `SpaceScene.update`:
  - update player
  - tính zone hiện tại
  - gate theo unlocked radius
  - update world (chunk/hazard/module)
  - apply hazard resistance suit
  - update survival
  - resolve collision feedback
  - camera follow
  - status timer
  - check death

### 7.5 Render flow
- `Game.draw`: fill nền + gọi `scene.draw` + `pygame.display.flip()`.
- `SpaceScene.draw`:
  - draw background
  - draw world (asteroid/module/hazard/log node/terminal node)
  - draw player
  - draw HUD
  - draw inventory overlay
  - draw status message

### 7.6 Entity management
- Asteroid quản lý bằng `pygame.sprite.Group` trong `World`.
- Hazard/module/log/terminal quản lý bằng list.
- Player là object đơn trong `SpaceScene`.

### 7.7 Resource loading
- `asset_loader` cache image/animation/sound theo path.
- Thiếu ảnh -> placeholder surface.
- `data_loader` load asteroid/recipe tại import time; logs load khi init `Narrative`.

## 8. Dependency mapping
### 8.1 Module dependency (rút gọn)
```text
main.py
 ├─ settings.py
 ├─ asset_manifest.py
 └─ scenes/
    ├─ scene_manager.py
    └─ menu_scene.py
       └─ space_scene.py
          ├─ entities/player.py
          ├─ systems/world.py
          │  ├─ entities/asteroid.py
          │  │  └─ data_loader.py
          │  ├─ entities/hazard.py
          │  └─ entities/module.py
          ├─ systems/survival.py
          ├─ systems/inventory.py
          ├─ systems/crafting.py
          │  └─ data_loader.py
          ├─ systems/narrative.py
          │  └─ data_loader.py
          └─ ui/
             ├─ hud.py
             └─ inventory_ui.py
```

### 8.2 System gọi system nào
- `SpaceScene` là orchestration point:
  - gọi `player.update`
  - gọi `world.update` để lấy `extra_drain`
  - điều chỉnh `extra_drain` theo `player.hazard_resistance`
  - gọi `survival.update`
  - gọi `world.handle_player_asteroid_collisions`
- Crafting flow:
  - `CraftingScene` -> `SpaceScene.handle_craft` -> `Crafting.craft`
  - sau đó áp dụng effect sang `World`/`Player`/`Survival`.
- Narrative flow:
  - `SpaceScene` nhấn `E` -> `World.interact` -> `Narrative.unlock_*`
  - HUD đọc `Narrative` để hiện progress và trạng thái ending.

### 8.3 Luồng dữ liệu
- `data/*.json` -> `data_loader` -> `Asteroid`/`Crafting`/`Narrative`.
- Input người chơi -> `SpaceScene` -> mutate state (`player`, `world`, `inventory`, `narrative`, `survival`).
- Runtime state -> `HUD`/overlay để render.

## 9. Đánh giá mức độ hoàn thành
- Ước lượng tổng thể: khoảng `35% - 45%` so với một game survival hoàn chỉnh.
- Mức độ hiện tại: `Prototype tiến xa / Early playable`.

Lý do:
- Đã có core runtime loop chơi được: di chuyển, mine, survival, craft, progression gate.
- Chưa có nhiều thành phần bắt buộc để lên vertical slice/alpha:
  - không save/load
  - narrative presentation chưa hoàn chỉnh
  - audio/particle/combat/NPC chưa tích hợp runtime
  - ending flow chỉ dừng game
  - nhiều code subsystem chưa dùng

Kết luận cấp độ:
- `Prototype`: đạt.
- `Early playable`: đạt mức cơ bản.
- `Vertical slice`: chưa đạt.
- `Alpha`: chưa đạt.
- `Beta`: chưa đạt.

## 10. Hướng phát triển tiếp theo (ưu tiên)
Chỉ liệt kê việc quan trọng nhất theo thứ tự:

1. Hoàn thiện persistence (`save/load`) cho progress cốt lõi: player progression, inventory, logs/terminals, modules, zone unlock.
2. Hoàn thiện narrative runtime: hiển thị nội dung log/terminal trong gameplay (thay vì chỉ tăng count/status text).
3. Chuẩn hóa ending flow thành scene/state riêng (không thoát process ngay).
4. Tích hợp các subsystem đang "dead code" hoặc loại bỏ khỏi runtime scope hiện tại (`DialogueUI`, `ParticleSystem`, `systems.physics`, `StationScene`) để giảm nhiễu kiến trúc.
5. Tách nhỏ `SpaceScene` và `World` theo trách nhiệm để giảm tight coupling trước khi mở rộng feature.

## Ghi nhận bổ sung từ audit
- Không tìm thấy `TODO`, `FIXME`, `XXX`, `HACK` trong source `.py`.
- Dữ liệu log hiện có 23 file (`id` liên tục 1..23, schema nhất quán `id/title/text/audio`).
- Assets có nhiều thư mục placeholder `Add.md`; runtime vẫn chạy nhờ fallback placeholder image.
