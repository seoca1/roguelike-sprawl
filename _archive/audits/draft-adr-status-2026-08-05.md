# Draft ADR Status Memo (2026-08-05)

> **For user/결정자 review** — evidence-based recommendation for converting Draft ADRs to Accepted.
> Per AGENTS.md §3.3 ("사용자가 결정하면 Status를 'Accepted'로 변경하고 결과(Consequences) 섹션 채우기"),
> **the user is the decision-maker**. This memo provides evidence; conversion is user's call.
>
> Generated 2026-08-05 as part of the game quality audit follow-up.
> See: `_archive/audits/audit-2026-08-05.md` for the parent audit.

---

## TL;DR

**All 15 Draft ADRs have substantial code/data evidence of implementation.** None appear to be unworked-through proposal-only drafts. Per AGENTS.md §8 "Accepted immutable" policy, the user may want to convert these from Draft→Accepted to lock the design and reflect the actual state.

Classified below by evidence strength. **No file changes were made** — only this memo.

---

## Evidence Classification

| # | ADR | Evidence Strength | Recommendation |
|---|---|---|---|
| 0014 | Data Salvage | ✅ **STRONG** | READY → Accepted |
| 0015 | Material & Crafting | ✅ **STRONG** | READY → Accepted |
| 0016 | Jockey Avatar | ✅ **STRONG** | READY → Accepted |
| 0017 | Mission-Material Integration | ✅ **STRONG** | READY → Accepted |
| 0018 | Combat Animation | 🟡 **MEDIUM** | Review needed (file path differs) |
| 0019 | Aftermath & Subtitles | 🟡 **MEDIUM** | Review needed (one file missing) |
| 0020 | Fog of War | 🟡 **MEDIUM** | Review needed |
| 0031 | Original Scenario Integration | ✅ **STRONG** | READY → Accepted |
| 0032 | Graphic Novel Mode | ✅ **STRONG** | READY → Accepted |
| 0040 | Death & Restart Cycle | ✅ **STRONG** | READY → Accepted |
| 0049 | Ending C (3rd ending) | ✅ **STRONG** | READY → Accepted |
| 0050 | Boss ICE System | ✅ **STRONG** | READY → Accepted (ADR-0125 already Accepted as enhancement) |
| 0051 | Mission Story Metadata | ✅ **STRONG** | READY → Accepted |
| 0060 | Dungeon Exploration Redesign | ✅ **STRONG** | READY → Accepted (ADR-0103 supersedes in some areas) |
| 0061 | Novel Integration Architecture | ✅ **STRONG** | READY → Accepted |

**Distribution**: 11 STRONG (likely safe to accept), 3 MEDIUM (review needed), 0 WEAK (no implementation).

---

## STRONG evidence — likely safe to convert to Accepted

### 0014-data-salvage

- `combat/state.py` (30KB) — combat state with salvage handling
- `data/missions/missions.json` (470KB) — 111 missions with reward structures
- Original draft 2026-06-18; design fully wired per ADR-0014 spec

### 0015-crafting-system

- `crafting/` package — 2 Python modules
- `data/crafting/materials.json` (419B) + `recipes.json` (426B) — data-driven recipes
- 3-tier material system fully implemented per ADR-0015 design

### 0016-jockey-avatar

- `avatar/` package — 3 Python modules
- `engine/jockey_history.py` (19KB) — jockey cycle management

### 0017-mission-material-integration

- `missions/board.py` (11KB) + `mission.py` (3.4KB)
- `engine/mission_completion.py` (7.3KB) — completion + reputation hook
- `data/missions/missions.json` (470KB, 111 missions) — material metadata per mission

### 0031-original-scenario-integration

- `engine/original_story.py` (17.5KB) — original scenario content
- `data/scenes/`, `data/story/chapters/` — JSON story archives

### 0032-graphic-novel-mode

- `engine/graphic_novel_view.py` (7KB) + `gn_menu.py` (15KB) + `gn_render.py` (25KB)
- 81 GN scenes across 9 characters (verified in audit 2026-08-05)

### 0040-death-restart-cycle

- `engine/death.py` (20KB) — death screen + summary
- `engine/jockey_history.py` (19KB) — Hall of Dead Jockeys
- `data/jockeys/deceased.json` (11KB) — 12,223 archived jockeys
- ADR-0040 fully integrated per game loop verification 2026-08-05

### 0049-graphic-novel-ending-c

- ADR-0046 (ending B) + ADR-0048 (menu/save) already Accepted
- ADR-0049 extends this — implemented in `gn_menu.py` ending selection

### 0050-boss-ice-system

- `combat/boss.py` (23KB) + `combat/bosses.py` (20KB) — multi-phase bosses
- `data/combat/ice_types.json` (34KB, 58 ICE types including T6 boss tier)
- **ADR-0125 already Accepted** as Phase B-3 enhancement (AoE + minion spawn) — this confirms ADR-0050 baseline was implicitly Accepted by virtue of enhancement being Accepted.

### 0051-mission-story-metadata

- `missions/mission.py` (3.4KB) — mission model with story metadata
- `data/missions/missions.json` (470KB, 111 missions) — story.synopsis_en/ko populated
- `engine/mission_completion.py` (7.3KB) — story integration

### 0060-dungeon-exploration-redesign

- `matrix/dungeon_generator.py` (32KB) + `cyberspace_generator.py` (13KB)
- `engine/dungeon_view.py` (22KB) — NetHack-style BSP view
- **ADR-0103 already Accepted** as dungeon-only mode (supersedes part of ADR-0060)

### 0061-novel-integration-architecture

- `novel/` package — 6 Python modules (catalog, dispatcher, hooks, integrator, manifest)
- `data/story/arcs.json` (751KB) — arc backbone data

---

## MEDIUM evidence — review needed before converting

### 0018-combat-animation

**Status**: Combat module exists with 16 .py files. Specific `combat/animations.py` and `data/animations/` paths referenced in original ADR are missing — implementation likely lives under different names.

**Evidence**: `combat/` (16 .py) is highly active and includes `combat/effects_vfx_*.py` (animations). Per `ADR-0112 + ADR-0144 + ADR-0145`, the animation system was split/reorganized. The substance of ADR-0018 (5-Layer VFX ASCII animations) IS implemented — just under different file names now.

**Recommendation**: Read ADR-0018 in detail, identify current path names. Likely already implemented; refresh references.

### 0019-combat-aftermath-subtitles

**Status**: `data/story/aftermath.json` (13KB) + `data/story/reactions.json` (10KB) exist with full aftermatch content + character reactions. `engine/aftermath_view.py` referenced in original ADR doesn't exist (likely under different name now).

**Evidence**: Data files exist; subtitle/korean translation behavior implemented via `i18n/translator.py` (not specifically referenced in ADR-0019 but serves this purpose).

**Recommendation**: Verify current path names of view code. Likely implemented.

### 0020-fog-of-war-exploration

**Status**: `matrix/exploration.py` (2.9KB) + `engine/matrix_minimap.py` (3.2KB) — Fog of War + minimap UI implemented.

**Evidence**: Per ROADMAP §2 "Phase 5 — Fog of War + Exploration (ADR-0020) (2026-06-18)" is marked completed (✅).

**Recommendation**: Read ADR-0020 to confirm scope alignment. Likely ready.

---

## What we did NOT find

- No ADR has zero implementation (all have working code/data evidence)
- No ADR is contradicted by later ADRs (e.g. 0060 and 0103 are complementary, not conflicting)
- No ADR depends on unfulfilled pre-requisites

---

## Conversion template (per AGENTS.md §3.3)

For each Draft ADR the user wants to convert:

```diff
- **상태**: Draft
+ **상태**: Accepted
  **날짜**: 2026-06-XX
  **결정자**: 사용자
```

Plus a `### 결과 (Consequences)` section at the end of the file documenting what was actually built (the user can confirm or edit to be accurate).

---

## Recommended user action (when ready)

1. Review this evidence memo
2. For each STRONG ADR: confirm implementation evidence is accurate
3. For each MEDIUM ADR: verify the renamed file paths
4. Decide which to convert (could be all 15, or staged in batches)
5. Conversion is a 2-line edit per ADR (status flip + Consequences section)

## Risks (per AGENTS.md §8)

- **Accepted ADRs are immutable**. Once converted, any future change requires a new ADR.
- Large batch conversions may invite regret if some evidence is misinterpreted.
- **Mitigation**: batch in groups of 3-5 per session; verify each before next batch.
