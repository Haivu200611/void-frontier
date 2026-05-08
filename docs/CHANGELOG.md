# CHANGELOG

## 2026-05-08 - Collision System Upgrade Pass

### Added
- Added modular collision architecture in `systems/physics.py`:
  - `Collider` component model (`dynamic/static/sensor`).
  - Collision layers/masks (`PLAYER`, `STATIC`, `ASTEROID`, `TRIGGER`).
  - `CollisionEvent` output for gameplay callbacks.
  - Broad-phase spatial hash grid.
  - Narrow-phase AABB checks and axis-based response.
  - Swept-axis (CCD-lite) for fast movement tunneling prevention.
- Added unit tests in `tests/test_collision_system.py`:
  - AABB overlap validation.
  - Stop/slide response.
  - Trigger events.
  - Restitution bounce.
- Added `TECHNICAL_COLLISION_REPORT.md` with full technical design and integration notes.

### Changed
- Upgraded `scenes/space_scene.py`:
  - Integrated `PhysicsSystem` into update loop for player-vs-static and trigger sensors.
  - Added trigger-driven interaction hints path.
- Upgraded `systems/world.py`:
  - Added collision collider export method (`get_collision_colliders`).
  - Added static colliders for modules and station hull.
  - Added sensor colliders for log/terminal/station interaction ranges.
- Kept existing asteroid impact logic while extending collision coverage for non-asteroid world geometry.

### Validation
- `python -m unittest discover -s tests -v` passed.
- Headless runtime smoke test (`Menu -> SPACE -> SpaceScene`) passed.

## 2026-05-08 - Vertical Slice Upgrade Pass

### Added
- Added `systems/audio_manager.py`:
  - Runtime audio manager with ambient + SFX channels.
  - Hooks for `ambient`, `jetpack`, `mining`, `explosion`, `click`, `warning`, `impact` sounds.
- Added `systems/save_system.py`:
  - JSON save/load for player progression, survival stats, inventory, narrative progress, world modules/nodes, mission stage.
  - Supports quick keys `F5` (save) and `F9` (load).
- Added `systems/objectives.py`:
  - Lightweight mission flow and progression stages.
- Added `entities/effect.py`:
  - Transient VFX layer for mining/explosion/thruster feedback.

### Changed
- Upgraded `scenes/space_scene.py` from prototype loop to playable loop:
  - Integrated dialogue presentation for logs/terminals.
  - Integrated particle and texture VFX feedback.
  - Integrated screen shake on impacts/explosions.
  - Integrated station docking flow and station scene usage.
  - Integrated objective progression display and survival warning SFX triggers.
  - Added quick save/load flow and continue-run support.
  - Added death transition using `player_death` texture.
- Upgraded `scenes/station_scene.py`:
  - Converted from placeholder to actionable dock scene:
    - Refill survival systems
    - Save progress
    - Return to space
- Upgraded `scenes/crafting_scene.py`:
  - Removed hard dependency on `scene_manager.stack[0]`.
  - Added recipe cost display and craftability visual states.
- Upgraded `scenes/menu_scene.py`:
  - Added `C` key to continue from save.
- Upgraded `scenes/scene_manager.py` and `scenes/scene_base.py`:
  - Added `pause/resume` lifecycle and fixed overlay semantics (`push` now pauses, `pop` resumes).
- Upgraded `systems/world.py`:
  - Added chunk-load budget queue (`MAX_CHUNK_LOADS_PER_FRAME`) to reduce frame spikes.
  - Added station interaction node and interaction hints.
  - Added base zone drain scaling to improve risk/reward pacing.
  - Added save-state export/import for modules/log nodes/terminal nodes.
  - Optimized collision/radar usage via active asteroid subset.
- Upgraded `entities/player.py`:
  - Integrated `systems.physics` helper usage (`apply_friction`, `clamp_speed`, `apply_velocity`).
  - Exposed thrust state API for feedback systems.
- Upgraded `entities/module.py`:
  - Added support effects for `lab` (battery restoration) and `signal_tower` (oxygen/pressure stabilization).
- Upgraded `ui/dialogue_ui.py`:
  - Rebuilt to support practical typewriter + wrapped multiline dialogue.
- Upgraded `ui/hud.py`:
  - Added objective lines and context interaction hint rendering.
- Upgraded `ui/inventory_ui.py`:
  - Added icon rendering from existing UI icon assets.
- Upgraded `main.py`:
  - Added `dt` clamp via `MAX_DT` to stabilize updates on frame hitches.
- Upgraded `settings.py`:
  - Added runtime stability, VFX shake, chunk budget, and save constants.

### Integrated Previously Unused Systems
- `ui/dialogue_ui.py` is now integrated into gameplay narrative interactions.
- `entities/particle.py` is now used for mining/thruster/explosion feedback.
- `scenes/station_scene.py` is now reachable and functional via station docking.
- `systems/physics.py` is now used by the player movement update path.

### Runtime Validation
- `python -m compileall .` passed.
- Headless smoke test with `SDL_VIDEODRIVER=dummy` passed (`Game` init + event/update/draw loop).

