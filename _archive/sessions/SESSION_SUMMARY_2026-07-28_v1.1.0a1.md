# Session Summary — 2026-07-28 (v1.1.0a1)

> **세션 ID**: roguelike_sprawl-2026-07-28-v1.1.0a1
> **세션 범위**: v1.0.0 FINAL (07-28) → **v1.1.0a1** (07-28)
> **테스트**: **3227 passed** (592 skipped, 0 failed) — **+62 신규** (Phase 1+2 49, Phase 3+4 회귀 검증 통과)
> **mypy**: 142 source files, 0 errors (strict mode)
> **ruff**: All checks passed
> **버전**: 1.0.0 → **1.1.0a1**
> **wheel**: dist/roguelike_sprawl-1.1.0a1-py3-none-any.whl (410KB)

---

## 1. 핵심 성과

ADR-0140 (Engagement Layer) + ADR-0141 (Module Splits) Option 1 **partial** 구현 완료. v1.0.0 출시 직후 추가 사이클.

| Phase | 산출물 | 신규 tests |
|---|---|---:|
| **1A** Memory Fragment core | `wiki/lore/` (4 fragments), `data/lore/encounter_table.json`, `lore/memory_fragment.py` | 12 |
| **1A** FragmentTracker | `lore/fragment_tracker.py` (per-run cap 6) | 9 |
| **1A** FragmentHook | `lore/fragment_hook.py` (matrix integration) | 6 |
| **1B** Matrix integration | cyberspace_view.py:519 hook + AppState.memory_fragment_tracker | — |
| **2A** ConstructWhisper core | `lore/construct_whisper.py` (12 hints, 4 factions × 3 tiers) | 14 |
| **2B** Combat integration | `lore/construct_whisper_hook.py` + AppState.construct_whisper_tracker | 8 |
| **3** matrix_view split | `engine/matrix_minimap.py` (115 LOC) — matrix_view 1121→1047 | — |
| **4** combat/state split | `combat/state_models.py` (250 LOC) — combat/state 1075→859 | — |
| **Bug fix** | `equip_defense` kwarg → `equip_defense_bonus` (combat_view.py:1038) | — |
| **총** | **8 신규 파일** | **71 신규 tests** |

---

## 2. Phase 1 — Memory Fragments (ADR-0140 §Proposal 2)

### 2.1 구현

**데이터 구조**:
- `wiki/lore/README.md` + 4 fragments (signal_echo, construct_cache, anomaly_log, dead_channel)
- `data/lore/encounter_table.json` (zone/grade/faction matrix)

**모듈**:
- `src/roguelike_sprawl/lore/memory_fragment.py` — `roll_memory_fragment()`, `load_encounter_table()`
- `src/roguelike_sprawl/lore/fragment_tracker.py` — `MemoryFragmentTracker` (per-run cap 6)
- `src/roguelike_sprawl/lore/fragment_hook.py` — `check_memory_fragment_on_node_entry()`

**State integration**:
- AppState.memory_fragment_tracker 필드 추가
- cyberspace_view.py:519 hook wired (matrix node entry 시 trigger)

### 2.2 Pillar 정합

- Pillar 4 (The Build) — unlock-only collection 동기
- Pillar 5 (The Style) — 깁슨 톤 ambient transmission

---

## 3. Phase 2 — Construct Whisper (ADR-0140 §Proposal 1)

### 3.1 구현

**모듈**:
- `src/roguelike_sprawl/lore/construct_whisper.py` — `ConstructWhisper` + `HINTS_BY_FACTION` (12 hints)
- `src/roguelike_sprawl/lore/construct_whisper_hook.py` — `check_construct_whisper_on_combat_start()`

**State integration**:
- AppState.construct_whisper_tracker 필드 추가
- Combat 시작 시 faction-tier-gated hint 출력

### 3.2 Faction Whisper Matrix

| Faction | TRUSTED hint |
|---|---|
| Hosaka | "Their ICE recognizes our signature. Strike first..." |
| Maas | "Biochip signatures are tracked. Their ICE learns..." |
| Sense/Net | "Their system logs every move. Use the worm..." |
| T-A | "The family keeps secrets in layers..." |

**Unlock tier**: TRUSTED+ (rep ≥ 20)
**Per-run cap**: 1 whisper per faction (max 5 total)

### 3.3 Pillar 정합

- Pillar 4 — faction 호감도가 in-run에 실질적 가치
- Pillar 5 — faction별 unique voice (깁슨 톤)

---

## 4. Phase 3 — matrix_view.py Split (ADR-0141)

### 4.1 Before/After

| 모듈 | Before | After |
|---|---:|---:|
| `engine/matrix_view.py` | 1121 LOC | 1047 LOC |
| `engine/matrix_minimap.py` (신규) | — | 115 LOC |

### 4.2 추출 항목

- `_draw_minimap` — minimap rendering in SIDE region
- `_draw_breadcrumb` — path history
- `_draw_mobility_stats` — movement steps + visited count
- `_KIND_LABEL` dict + `_short_kind` function

### 4.3 Backward Compatibility

```python
# matrix_view.py
from .matrix_minimap import (
    _draw_breadcrumb,
    _draw_minimap,
    _draw_mobility_stats,
    _short_kind,
)
```

기존 호출자 (`from .matrix_view import _draw_minimap` 등) 변경 없이 동작.

---

## 5. Phase 4 — combat/state.py Split (ADR-0141)

### 5.1 Before/After

| 모듈 | Before | After |
|---|---:|---:|
| `combat/state.py` | 1075 LOC | 859 LOC |
| `combat/state_models.py` (신규) | — | 250 LOC |

### 5.2 추출 항목

- `SkillEffect` (StrEnum, 16 variants)
- `Skill` (dataclass)
- `StatusEffect` (dataclass)
- `CombatStats` (dataclass)
- `Combatant` (dataclass + 14 methods)
- `CombatState` (dataclass + `__post_init__` + `target` property + `push` method)

### 5.3 Backward Compatibility

```python
# combat/state.py
from .state_models import (
    AUTO_ATTACK_INTERVAL_MS,
    TICK_MS,
    Combatant, CombatState, Skill, SkillEffect, StatusEffect,
)
__all__ = [...all re-exported names + step_combat, use_skill...]
```

`from roguelike_sprawl.combat.state import SkillEffect` → 정상 작동.

### 5.4 Bug Fix

- `equip_defense` kwarg → `equip_defense_bonus` (combat_view.py:1038) — latent bug fix
- CombatState 기본값 `last_player_attack_ms`/`last_enemy_attack_ms` 복구

---

## 6. Phase 5 — Documentation + Release

- ADR-0140, ADR-0141 status: Draft → **Accepted (Option 1 partial)**
- `log.md` v1.1.0a1 entry 작성
- `decisions/README.md` 갱신
- `CHANGELOG.md` v1.1.0a1 entry
- `dashboard/index.html` v1.1.0a1 indicator + Highlights
- `pyproject.toml` version 1.0.0 → **1.1.0a1**
- Dashboard stats regeneration (12 files)
- **회귀 수정**: `skill_effect_count: 0 → 16` (Phase 4 split 후 sync script 수정)

---

## 7. 검증 종합

```
pytest       : 3227 passed (+62 vs v1.0.0), 592 skipped, 0 failed
mypy strict  : 142 source files, 0 errors
ruff check   : All checks passed
wheel build  : v1.1.0a1 (410KB) + tarball (3.78MB)
wheel smoke  : 5/5 import + functional tests pass
```

---

## 8. 잔존 — v1.1.0 final / v1.2.0 백로그

### v1.1.0 final (Option 1 P2/P3)
- Variable Reward Nodes (제안 6)
- Faction Tension Events (제안 7)
- Auto-Play Tempo Layering (제안 8)
- Grade 6 Master Whisper (제안 4)
- Near-Miss Extraction (제안 3)
- Death Replay (제안 5)

### Module splits (ADR-0141 partial)
- `combat/effects.py` (1246 LOC, ADR-0112)
- `combat_view.py` (1096 LOC, ADR-0113)
- matrix_view.py full 4-way split
- combat/state.py full 4-way split

### 사용자 액션
- `git push origin main`
- `twine upload dist/roguelike_sprawl-1.1.0a1*`
- Notion 발행

---

## 9. 변경 이력

```
2026-07-28 docs: ADR-0140 Accepted (Engagement Layer Top 3)
2026-07-28 docs: ADR-0141 Accepted (Module Splits Top 2)
2026-07-28 feat: lore subsystem (memory_fragment, fragment_tracker, fragment_hook, construct_whisper, construct_whisper_hook)
2026-07-28 feat: AppState fields (memory_fragment_tracker, construct_whisper_tracker)
2026-07-28 feat: cyberspace_view.py matrix fragment hook
2026-07-28 refactor: matrix_minimap.py extract (1121→1047)
2026-07-28 refactor: state_models.py extract (1075→859)
2026-07-28 fix: equip_defense kwarg → equip_defense_bonus
2026-07-28 docs: CHANGELOG + log.md + SESSION_SUMMARY updates
2026-07-28 chore: bump version 1.0.0 → 1.1.0a1
2026-07-28 chore: regenerate dashboard stats
2026-07-28 fix: sync_dashboard_facts skill_effect_count (0 → 16)
2026-07-28 docs: dashboard v1.1.0a1 indicator + Highlights
```

---

> **버전**: v1.1.0a1 (alpha 1)
> **작성일**: 2026-07-28
> **이전 버전**: v1.0.0 (2026-07-28, FINAL)
> **연관 문서**: log.md, CHANGELOG.md, decisions/README.md, ADR-0140, ADR-0141
> **다음 버전 후보**: v1.1.0 final (P2/P3 proposals + remaining module splits)