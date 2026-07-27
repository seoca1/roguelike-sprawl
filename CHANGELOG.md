# Changelog

All notable changes to roguelike_sprawl will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] — Phase α-L (2026-07-26)

### Per-Boss VFX Themes (Phase B-3.5+, 2026-07-27)

- **6 boss VFX themes** in `BOSS_VFX_THEMES` dict:
  - WINTERMUTE: neural/ice blue (1.2x shake, RGB 150,150,255)
  - GOLIATH: military/red (1.5x shake, RGB 255,80,80)
  - BLACK_ICE: corruption/magenta (1.3x shake, RGB 180,100,220)
  - WATCHDOG: predator/amber (1.1x shake, RGB 255,220,100)
  - TA_CONSTRUCT: corporate/white (1.0x shake, RGB 255,255,255)
  - DEFAULT: fallback
- `VFXTheme` dataclass (frozen, slots=True) with per-theme shake
  intensity multiplier + hit flash color/duration + particle config
- `get_vfx_config(ice_type)` lookup; `ICE_TYPE_TO_VFX_KEY` mapping
- `_trigger_aoe_visuals()` applies per-boss shake multiplier and
  custom hit flash color/duration
- `BossPhase` and `BossSpec` gain `vfx_theme` field

### VFX Bug Fix (2026-07-27)

- `apply_phase_aoe()` now accepts optional `ice_type` parameter
- `_trigger_aoe_visuals()` uses passed `ice_type` (was incorrectly
  reading `phase.ice_type` which doesn't exist on `PhaseProfile`)
- `combat_tick.py`: computes `IceType` BEFORE `apply_phase_aoe()` and
  passes it. Without this fix, all bosses fell back to `phase.color`
  and the per-boss VFX theme colors never triggered.
- Verified: Wintermute phase 3 → hit_flash_color=(150,150,255),
  TA_Prime phase 3 → hit_flash_color=(255,255,255), per-boss shake
  multipliers applied.

### Matrix Zone Depth Fix (2026-07-27)

- `ZoneDepth.SOHO` (3-5, London-style black market): base ZDR 3
- `ZoneDepth.TOKYO` (5-8, Yakuza underworld): base ZDR 6
- Both zones were defined in `ZoneDepth` enum but missing from
  `_BASE_ZDR` dict → would raise `KeyError` if those zones were used

### Mission Source Field (18 missions, 2026-07-27)

- Added `story.source` field to 18 Bridge/Blue Ant era missions
  (previously missing → broke 3 integration tests)
- Source values mapped to existing `search_index.json` slugs:
  - `bridge_scaffold` → `bridge-construct`
  - `chevette_run` → `chevette-run`
  - `kombinat_node_hack` → `kombinat-node-hack`
  - `bigend_laney_lunch` → `bigend-laney-lunch`
  - `coolhunter_laney_tokyo` → `coolhunter-laney-tokyo`
  - `tokyo_courier_run` → `tokyo-courier-run`

### Cross-Project Integration (Fiction ↔ roguelike_sprawl)

- **Phase α** (initial bidirectional): 100 Fiction stories now linked to
  missions via `game_mission_id` frontmatter; missions declare Fiction
  source via `story.source` field. Validator: `verify_story_links.py`.
- **Phase G**: 81/81 GN scenes now declare `mission_id` (was 7/81).
- **Phase G**: 33 missions got `reward_credits` + `reward_tier` backfilled
  by grade (75-2200 credits, T1-T5).
- **Phase J**: 4 missions got `stage_flow` field (data-driven).
- **Phase F**: 19 historical orphans resolved (13 Bridge + 4 Blue Ant
  sources removed, 2 new Fiction short stories written).
- **Cross-project wiki**: `wiki/world/cross-project-integration.md` (198
  lines) — single source of truth for the integration mechanism.

### Boss B-3 Enhancements (Phase A-E, G-L)

- **B-3 base (A)**: Added `aoe_damage` + `spawn_minions` fields to
  `PhaseProfile` and `BossPhase` dataclasses. New helpers:
  `spawn_phase_minions()` + `apply_phase_aoe()`.
- **B-3 usage (G)**: 2 boss profiles populated with B-3 features:
  - WINTERMUTE phase 2: 2× `wintermute_proxy` spawn
  - WINTERMUTE phase 3: `wintermute_fragment` spawn + 15 AoE
  - TA_CONSTRUCT_PRIME phase 2: `romantics_ice` spawn
  - TA_CONSTRUCT_PRIME phase 3: 2× adds + 20 AoE
- **B-3 spread (I)**: 3 more profiles populated:
  - GOLIATH PRIME phase 2: 2× `watchdog` spawn
  - GOLIATH PRIME phase 3: `corporate_guard` spawn + 25 AoE
  - BLACK ICE LORD phase 1: `romantics_ice` spawn
  - BLACK ICE LORD phase 2: `romantics_ice_elite` spawn + 10 AoE
  - WATCHDOG ALPHA phase 2: 2× `watchdog` spawn (pack howl)
- **B-3 wiring (H)**: `maybe_boss_phase_transition()` now calls B-3
  helpers. Combat main loop fires `spawn_phase_minions` + `apply_phase_aoe`
  on phase change.
- **B-3.5 visuals (I)**: `apply_phase_aoe()` triggers screen shake + hit
  flash. Intensity scales with `aoe_damage` (capped 8.0).
- **Boss B-3 coverage**: 5/5 boss profiles use B-3 features.
- **Tests**: 7 new B-3 tests (`test_spawn_phase_minions_*`,
  `test_apply_phase_aoe_*`, `test_wintermute_phase_3_*`,
  `test_ta_prime_phase_3_*`, `test_apply_phase_aoe_triggers_visual_effects`).
- **ADR-0125** (Boss Phase AoE + Minion Spawn) documents design decision.

### Combat Quick Wins (Phase A)

- **A-1**: Removed dead `get_total_shield()` method (was
  `... * 0 + ...`, always returned 0).
- **A-2**: Added `ice_kind` field to all 58 ICE entries (was 7 mapped to
  archetypes). `registry.py` now reads `data["ice_kind"]`.
- **A-3**: Skill menu shows `T1`-`T6` tier badge (T1 grey → T6 gold).
- **A-4**: Documented `RunState.mark_advance()` non-idempotent behavior
  with explicit test gating.
- **A-5**: ADR-0112 already documents effects.py 1246 LOC justification.

### Stage Flow (Phase C-1, J)

- **C-1**: `get_mission_flow()` reads `stage_flow` from mission JSON.
  `MISSION_FLOWS` dict is now the fallback only. 4 missions have data-
  driven stage flows (first_jack, watchdog_patrol, ice_run, data_retrieval).
- **C-1 tests**: 4 new (TestDataDrivenStageFlow class).
- **C-2**: Consolidated 12 `start_chapter_N`/`complete_chapter_N` methods
  into single `start_chapter(n)` / `complete_chapter(n)`.
- **C-3**: Hub footer shows `Phase X/Y (Z%)` (was: just step counter).

### Game Loop Architecture (Phase D-2)

- **D-2 partial**: Extracted 3 helpers: `combat_tick.py`,
  `cyberspace_map_view.py`, `arc_phase.py`.
- **D-2 deep2**: Extracted `screen_dispatch.py` (render dispatch).
- **D-2 deep3**: Extracted `main_loop.py` (per-screen tick dispatch).
- **D-2 deep4**: Extracted `input_dispatch.py` (input dispatch).

**app.py: 825 → 279 LOC (-66%)**

### Player Onboarding (Phase E)

- **E-1**: AAR (After Action Report) shown in REWARD screen below
  materials. Displays damage dealt/received, crits, max combo,
  peak alarm, duration.
- **E-2**: First-combat tutorial overlay (`show_first_combat_tutorial`
  flag). Pressing SPACE/ENTER/RETURN dismisses. ">>> Tutorial
  dismissed. Good luck, cowboy."

### Cross-Project & Tools

- **Pre-commit hook**: `scripts/git-hooks/pre-commit` validates
  cross-project links on every commit (WARN-only). `scripts/git-hooks/README.md`.
- **Wiki**: `wiki/world/cross-project-integration.md` (198 lines) and
  Phase J-K log entries.

### Statistics

| Metric | Value |
|---|---|
| Tests | 3123 passed, 592 skipped |
| Lint | All checks passed |
| ADRs | 54 Accepted |
| ADR-0125 | Boss Phase AoE + Minion Spawn (Phase B-3 enhancement) |
| app.py LOC | 279 (was 825) |
| New modules | 6 (combat_tick, cyberspace_map_view, arc_phase, screen_dispatch, main_loop, input_dispatch) |
| Boss B-3 coverage | 5/5 |
| GN scene coverage | 81/81 |
| Cross-project orphans | 0 |
| Mission reward backfill | 33/33 |
| Mission stage_flow backfill | 4 |

### Module Size Reductions (Phase A → L)

| Phase | app.py LOC | Change | Cumulative |
|---|---|---|---|
| A | 825 | — | — |
| D-2 partial | 685 | -140 | -140 |
| D-2 deep2 | 519 | -166 | -306 |
| D-2 deep3 | 457 | -62 | -368 |
| D-2 deep4 | 279 | -178 | **-546 (-66%)** |

### Module Architecture (post-Phase L)

```
engine/
├── app.py                   (279 LOC: main loop, hotkeys, init)
├── combat_tick.py           (28 LOC: boss phase transition)
├── cyberspace_map_view.py   (61 LOC: CYBERSPACE_MAP render)
├── arc_phase.py             (41 LOC: ARC_PHASE state advance)
├── screen_dispatch.py       (271 LOC: render dispatch, 30+ screens)
├── main_loop.py             (148 LOC: per-screen tick dispatch)
└── input_dispatch.py        (224 LOC: input dispatch, 30+ screens)
```

## [0.7.11] — 2026-07-10 (Pre-Phase α)

Initial state. Cross-project links existed in source but not formalized.
19 orphan mission sources (Bridge/Blue Ant + 2 Sprawl-uncertain).
Boss system had multi-phase but no AoE damage or minion spawn.
app.py: ~825 LOC single-file dispatcher.

---

## Phase Index

| Phase | Focus | Key Result |
|---|---|---|
| α | Cross-project initial | Bidirectional Fiction↔mission link |
| β-1/2 | UI integration + GN scene | Mission select Fiction link, 7→56 GN scenes |
| γ | (in original Phase F) | 19 orphan cleanup |
| A | Combat quick wins | ICE kind, tier badge, dead code removed |
| B-1/2/3 | Boss enhancements | spawn_minions + aoe_damage, all 5 bosses |
| C-1/2/3 | Stage flow | Data-driven stage_flow, chapter consolidation |
| D-2 | Game loop refactor | 6 modules extracted, app.py -66% |
| E-1/2 | Player onboarding | AAR, first-combat tutorial |
| F | (in original Phase F) | Wiki + orphan cleanup |
| G | (in original Phase G) | GN 81/81, reward backfill, B-3 usage |
| H | (in original Phase H) | B-3 wiring + tests + wiki |
| I | (in original Phase I) | B-3.5 visuals + pre-commit + B-3 spread |
| J | (in original Phase J) | C-1 stage_flow + D-2 deep2 + E-2 |
| K | (in original Phase K) | D-2 deep3 main_loop + wiki + log |
| L | (in original Phase L) | D-2 deep4 input_dispatch |
| M | (this commit) | CHANGELOG + boss profile wiki |

## References

- `decisions/` — 54 Accepted ADRs (architecture decisions)
- `design/systems/combat.md` — Combat system design
- `design/systems/difficulty-rating.md` — PPL/ZDR formulas
- `wiki/world/cross-project-integration.md` — Cross-project integration
- `prototype/scripts/verify_story_links.py` — Cross-project validator
- `prototype/docs/balance/E3-balance-audit.md` — Balance audit report
- `prototype/tests/` — 3123 tests passing

## Contributing

See:
- `AGENTS.md` — Project agent guide
- `decisions/README.md` — ADR index
- `prototype/scripts/verify_story_links.py` — Run cross-project validator
- `prototype/scripts/git-hooks/` — Pre-commit hook (cross-project)

Run tests:
```bash
cd prototype
uv run python -m pytest tests/unit/  # 3123 passed
uv run ruff check src/ scripts/ tests/  # All checks passed
uv run python scripts/verify_story_links.py  # 0 orphans
```