# Changelog - Roguelike Sprawl

All notable changes to this project will be documented in this file.

## [Unreleased] - 2026-06-30

### Added - Phase 1-5 Gameplay Expansion (ADR-0060, ADR-0061)

#### **Phase 1 — Dungeon Mode**
- `engine/state.py: AppState.dungeon_mode: bool = False` flag.
- `engine/app.py` — `D` key toggles dungeon mode in the matrix screen.
- `engine/dungeon_view.py: render_dungeon_matrix()` — 2-D grid renderer
  using `_get_room_position()` for layout.
- 8 unit tests (`tests/unit/test_dungeon_view.py`).

#### **Phase 1.5 — Combat VFX Overlay**
- 4 cinematic spawners in `combat/effects.py`:
  - `spawn_jackin_glitch()` — JAC-IN glitch burst + slow-mo.
  - `spawn_room_flash()` — short color flash on ICE clear.
  - `spawn_data_acquired()` — DATA fragment pickup VFX + cinematic.
  - `spawn_jackout_whiteout()` — JAC-OUT whiteout burst.
- Each takes a `CombatEffects` container (first positional arg).
- 12 unit tests (`tests/unit/test_combat_vfx.py`).

#### **Phase 2 — Procedural BSP Dungeon**
- `matrix/dungeon_generator.py: ProceduralDungeonGenerator` —
  BSP partition + Kruskal MST + character dead-end branching.
- Configurable `min_leaf_size` / `room_padding`.
- 23 unit tests (`tests/unit/test_procedural_dungeon.py`).

#### **Phase 3 — Mission → Room Mapping**
- `matrix/mission_mapper.py: missions_to_rooms()` — list[RoomType].
- `matrix/mission_mapper.py: mission_to_graph()` — MatrixGraph + BSP.
- Bridges `data/missions/missions.json` (16 missions) to dungeon shape.
- 31 unit tests (`tests/unit/test_mission_mapper.py`).

#### **Phase 4 — ECS Dungeon Integration**
- `ecs/room_entity.py: node_to_entity()` / `room_to_entity()`.
- `ecs/dungeon_system.py: DungeonSystem` —
  populate / on_enter / on_exit / defeat / cleared / visited.
- 22 unit tests (`tests/unit/test_dungeon_ecs.py`).

#### **Phase 5 — Novel Integration (ADR-0061)**
- New `novel/` subpackage: `NovelCatalog` / `NovelManifest` /
  `NovelDispatcher` / `NovelRuntime` / `load_novel_runtime()`.
- 6 `HookKind`s: `narrative`, `excerpt`, `event`, `combat`,
  `item`, `cinematic`. Extensible via `register_hook_action()`.
- 39 unit tests (`tests/unit/test_novel.py`).

### Added - Operator Demos

- 5 headless demos in `prototype/scripts/` to exercise Phase 1-5
  without opening a window:
  - `play_dungeon_mode.py`  (Phase 1)
  - `play_vfx_overlay.py`   (Phase 1.5)
  - `play_mission_mapping.py` (Phase 3)
  - `play_ecs_dungeon.py`   (Phase 4)
  - `play_novel_runtime.py` (Phase 5)

### Docs - Phase 1-5

- ADR-0060 (`Dungeon Exploration Redesign`) — Accepted.
- ADR-0061 (`Novel Integration Architecture`) — Accepted.
- `docs/DUNGEON_*.md` (3 files) — design + verification checklist.
- `dashboard/dungeon.html` + `dashboard/novel.html` — ADR landing pages.
- `dashboard/play.html` + `data/play_game.json` — interactive demo.
- `dashboard/README.md` — page ↔ data-source map.

## [Phase 5.1] - 2026-06-18

### Added - UX Improvements

#### **Enhanced Current Node Visibility** (5 Indicators!)
- **Bright cyan border**: `#═══║` instead of gray `+---\|`
- **Yellow text**: Node name and stats in bright yellow
- **Dark cyan background**: Interior tinted for visibility
- **Arrow markers**: `> < v ^` pointing from all 4 sides
- **"[ YOU ]" label**: Displayed above current node
- **Title bar update**: Shows "MATRIX — [Current Node Name] [Type]"
- **Impossible to miss**: Multiple redundant visual cues

#### **Comprehensive Status System**
- **Real-time action feedback**: Every player action now shows a status message
- **Status message log**: Messages appear in footer (last 20 stored)
- **Context-aware indicators**: Clear indication of what each action does

#### **Matrix Screen Enhancements**
- **Current node status panel** (Side):
  - Node name and type
  - ZDR and combat status
  - Context-specific instructions ("→ SPACE: Extract data")
  - Visited node counter
- **Movement feedback**: Shows direction and destination
  - ">>> Moved ↑ UP to DATA-7F (Data)"
  - ">>> No node in direction ← LEFT"
- **Action feedback**: Confirms every action
  - ">>> SCAN: DATA-7F (data)"
  - ">>> EXTRACT: Data retrieved from DATA-7F"
  - ">>> ENGAGE: Initiating combat with ICE-Guardian"
- **Dynamic controls**: Bottom bar shows context-specific hints
  - At DATA node: "SPACE: Extract data (mission objective)"
  - At ICE node: "SPACE: Engage ICE (combat)"
  - At EXIT node: "SPACE: Jack out (exit matrix)"

#### **Combat Screen Enhancements**
- **Skill selection feedback**:
  - ">>> Selected: ICE BREAKER"
  - ">>> Used skill: ATTACK"
- **Error feedback** when skill unavailable:
  - ">>> ICE BREAKER on cooldown (1.5s)"
  - ">>> Not enough AP (2/3)"

#### **Visual Improvements**
- Clearer "WHAT TO DO" section in side panels
- Arrow symbols in movement messages (↑ ↓ ← →)
- Action-specific control hints
- Real-time cooldown display in skills menu

### Changed
- Matrix action menu now opens with **SPACE** instead of ENTER (more intuitive)
- Footer now displays most recent status message alongside step counter
- Side panels prioritize current context over generic info

### Technical
- Added `engine/logger.py` - Centralized logging system (not yet integrated)
- Added `AppState.status_messages` - In-game message queue
- Added `AppState.context_hint` - Dynamic help text
- Updated `layout.py:draw_footer()` - Supports status messages
- Enhanced all input handlers with status logging

---

## [Phase 5.0] - 2026-06-18

### Added - Arrow Key Navigation

#### **Complete Menu Navigation**
- **Matrix Action Menu**:
  - ↑↓ to select action
  - ENTER to confirm
  - Visual cursor (`>`) shows selection
  - Color coding: Cyan (selected), White (available), Gray (locked)
  - `[LOCKED]` indicator for Phase 6+ features

- **Combat Skill Menu**:
  - ↑↓ to select skill
  - ENTER to use skill
  - Real-time cooldown display
  - Visual feedback for disabled skills
  - Cooldown shown as `[1.5s]`
  - AP cost shown as `[2 AP]`

#### **Visual Distinction System**
- **Colors**:
  - Cyan `(0, 255, 255)` - Selected item
  - White `(200, 200, 200)` - Available
  - Dark Gray `(80, 80, 80)` - Disabled/Locked/Cooldown
- **Cursor**: `>` marks current selection
- **Status indicators**:
  - `[X AP]` - Action Point cost
  - `[X.Xs]` - Cooldown remaining
  - `[LOCKED]` - Feature not yet implemented

#### **Cooldown System**
- Skills now have proper cooldowns
- Cooldowns tracked in `CombatState.skill_cooldowns`
- Real-time countdown displayed
- Auto-decremented each combat tick

#### **State Management**
- `AppState.action_menu_index` - Action menu selection
- `AppState.combat_skill_index` - Skill menu selection
- `CombatState.skill_cooldowns` - Per-skill cooldown tracking

### Changed
- Number/letter shortcuts (1-9, S, E, J) still work (legacy support)
- Controls footer updated to show arrow key hints
- Menu rendering now shows selection state

### Documentation
- Added `CONTROLS.md` - Complete controls reference
- Updated `DEMO_GUIDE.md` - Arrow key navigation examples
- Updated `README.md` - Quick controls summary

---

## [Phase 5.0 Beta] - 2026-06-18 (Earlier)

### Fixed
- **Font charmap issue**: Changed `CHARMAP_CP437` → `CHARMAP_TCOD`
  - Fixed garbled text in all screens
  - Affects: `app.py`, `test_tcod.py`, `full_demo.py`, `prologue.py`
- **Tileset indentation error**: Fixed `tileset` loading in demo scripts

### Added
- `scripts/text_demo.py` - Text-only story viewer (no graphics)
- `scripts/test_tcod.py` - Font rendering diagnostic tool
- `DEMO_GUIDE.md` - Complete playthrough guide (391 lines)

---

## [Phase 5.0 Alpha] - 2026-06-17

### Added - Full Game Flow Demo

#### **Cinematic Story System**
- Typing effects (3 speeds: INSTANT, FAST, NORMAL, SLOW)
- Glitch effects (random cyberpunk visual corruption)
- NPC portraits (ASCII, e.g., `♠F♠` for Finn)
- Bilingual support (English + Korean placeholders)

#### **Story Scenes**
- **Prologue**: Gibson's iconic opening (6 story lines)
- **Briefing - The Finn**: First mission briefing (5 story lines)

#### **Game Flow Integration**
- Seamless transitions: Prologue → Briefing → Matrix → Combat
- Auto-progression between scenes
- `scripts/full_demo.py` - Complete demo experience

#### **Demo Variants**
- `make demo` - Standard speed
- `make demo-fast` - 3x faster typing
- `make demo-skip` - Skip prologue

---

## [Phase 4] - Earlier

### Implemented
- Matrix exploration (5x5 grid, fog of war)
- RT-MS combat system
- Hub screen (4-panel layout)
- Action menu system
- ECS architecture
- 124 unit tests

---

## Version History

- **Phase 5.1** - UX Improvements (Status system, Context-aware UI)
- **Phase 5.0** - Arrow Key Navigation + Full Game Flow Demo
- **Phase 4** - Core Systems (Matrix, Combat, Hub)
- **Phase 3** - ECS Architecture
- **Phase 2** - Basic Combat
- **Phase 1** - Project Setup

## [Phase 5.2] - 2026-06-18 - Sound System

### Added - Audio Integration (Phases 1-6 Complete)

#### **SoundManager Core** (`src/roguelike_sprawl/audio/sound_manager.py`)
- 267 lines, zero external Python dependencies
- Cross-platform: macOS (afplay), Linux (aplay), Windows (winsound)
- Auto-generates 27 placeholder WAVs on first use (synthesized via `wave` module)
- Thread-safe, non-blocking playback with subprocess management
- Volume (0.0-1.0, clamped), mute toggle, master controls

#### **Sound Categories** (27 sounds across 5 categories)
- **UI** (5): menu_select, menu_confirm, menu_cancel, error, notification
- **Story** (3): text_typing, dialogue_advance, event_trigger
- **Combat** (12): hit_normal, hit_crit, hit_miss, skill_physical, skill_magic,
  skill_heal, skill_buff, skill_debuff, block, stun, victory, defeat
- **Movement** (4): nav_step, jack_in, jack_out, nav_block
- **Items** (3): equip, pickup, cant

#### **Settings UI** (`src/roguelike_sprawl/engine/settings_ui.py`)
- `get_volume()`, `set_volume()`, `adjust_volume(±delta)` helpers
- `is_muted()`, `toggle_mute()` helpers
- `render_settings_overlay()` for HUD display
- Global hotkeys wired in `app.py`:
  - **M** = Toggle mute
  - **+** / **=** = Volume up
  - **-** = Volume down

#### **Engine Integration** (7 modules)
- `story_cinematic.py` - typing + event trigger sounds
- `combat_view.py` - 14 SkillEffect types mapped to sounds
- `cyberspace_browser.py` - jack-in on server select
- `cyberspace_view.py` - nav_step + nav_block feedback
- `action_menu.py` - menu select/cancel
- `npc_view.py` - dialogue navigation
- `hub.py` - mission select (helper)
- `status_panel.py` - AUDIO section at bottom of right panel

#### **safe_play() Helper**
- Single entry point for engine modules
- Swallows all exceptions (sound must never break gameplay)
- Replaces 7 duplicate `_play_*_sound` helpers

#### **Testing**
- `tests/unit/test_sound_manager.py` - 12 tests (manager, volume, mute, play)
- `tests/unit/test_settings_ui.py` - 8 tests (volume adjust, mute toggle, clamp)
- All 144 tests passing (was 124, +20 new)

#### **Makefile Targets**
- `make sound-test` - Check audio backends
- `make sound-manager` - Run sound tests
- `make sound-demo` - Play all 27 sounds
- `make sound-demo-full` - Full game demo with sound
- `make sound-clean` - Remove generated WAVs

### Documentation
- `SOUND_PLAN.md` - All 6 phases checked, status section added

### Verified
- **mypy strict**: 0 errors (61 source files)
- **ruff**: 0 issues
- **pytest**: 144/144 passing
- **sound assets**: 27/27 auto-generated

## [Phase 5.3] - 2026-06-18 - Jockey Avatar (ADR-0016)

### Added - Avatar System

#### **`src/roguelike_sprawl/avatar/`** module
- `state.py` - Data models: AvatarState, ProgramSlot, Status, ConstructKind, AvatarLines
- `renderer.py` - Pure ASCII stick-figure renderer with color palette
- `__init__.py` - Public API exports

#### **Head (HP) Visualization**
- 100% HP: `◉P◉` (green, full integrity)
- 75% HP: `◉P·` (yellow-green)
- 50% HP: `◉P/` (yellow, tilted/glitching)
- 25% HP: `◉Px` (red, critical)
- 0% HP: `X` (dark red, flatline)

#### **Body Pose (Status)**
- SAFE / MATCH / TOUGH: upright ` /|\ ` / ` \|/ `
- DEADLY: crouched ` /\ ` / ` \/ `
- FUTILE: glitching ` .\ ` / ` /, `

#### **Program Arms (Tier + State)**
- T5: `★X★` (starred, gold)
- T4: `▓X▓` (filled, purple)
- T3: `|X|` (double border, cyan)
- T2: `:X:` (single border, gray)
- T1: `·X·` (faded, dim)
- Depleted: `~X~` (one-shot used)
- Empty/locked: `═══` (meta-progression)

#### **Deck & Wetware**
- Deck: `║DK{N}║` (torso, tier shown)
- Wetware: `▓▓▓▓` (legs, count = tier)

#### **Construct Companion** (echo)
- Dixie: `◆D◆`
- Loa: `◯L◯`
- 3Jane: `▲▲J▲▲`

#### **Public API**
- `render_avatar_lines(state)` -> AvatarLines (text + color)
- `render_avatar(console, x, y, state, border=True)` - direct console rendering
- `build_avatar_state(hp, max_hp, ppl, zdr, ...)` - from raw game values

### Testing
- `tests/unit/test_avatar.py` - 28 tests covering:
  - 4 HP state visualizations
  - 5 status pose mappings
  - 5 program tiers
  - Depleted state
  - Empty/locked slot
  - Deck tier (T0-T5)
  - Wetware tier (T0-T5)
  - 3 construct kinds
  - 4 integration scenarios (full, damaged, critical, dead)
  - 6 state property tests

### Demo
- `scripts/demo_avatar.py` - 6 scenarios + reference tables

### Verified
- **mypy strict**: 0 errors (64 source files)
- **ruff**: 0 issues
- **pytest**: 172/172 passing (was 144, +28 new)
