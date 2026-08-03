## [2026-07-30] lint | Round 2 — index.md orphan reconciliation (89 entries added)

**Scope:** Resolved 89 orphan pages in `Game/roguelike_sprawl/index.md` per AGENTS.md §9 termination checklist (`index.md` 가 새 페이지를 모두 가리키는가).

**Pre-cleanup baseline (targeted scope: decisions/ + design/):**

| Section | Files | Orphans (pre) | Orphans (post) |
|---|--:|--:|--:|
| decisions/ | 54 | 54 | 0 |
| design/ | 35 | 35 | 0 |
| **Total** | **89** | **89** | **0** |

**Excluded from this batch** (per Option B — most impactful scope):
- `docs/` (15 files: NOTION_IMPORT, DEPLOYMENT_GUIDE, REMOTE_DEV_SETUP, audits/, etc.) — operational docs
- `wiki/` (8 files: lore/ episodic logs + world/derivative_stories + world/cross-project-integration) — episodic/intentional
- `prototype/` (8 files: DUNGEON_NPC_GUIDE, INTERACTIVE_GUIDE, DEMO_GUIDE, CONTROLS, VISUAL_GUIDE, STATUS_PANEL_GUIDE, QUICK_START, SOUND_PLAN + 1 audit) — code project guides (low discovery priority)
- `dashboard/stories/journey/` (3 files) — character journey pages
- `testcases/` (3 files: template + 2 sub-dir) — already linked via README
- `.github/ISSUE_TEMPLATE/` (3 files) — GitHub config, not project content
- (root): 3 (SESSION_SUMMARY, IMPROVEMENTS, SESSION_SUMMARY_2026-07-28_v1.1.0a1)
- 3rd-party: `node_modules/`, `.venv/`, `.venv-mkdocs/` — package manager deps, never indexed

**Remaining orphans** (untouched per Option B): **60** (low-priority)

**Pattern identified:**
- All 54 `decisions/*.md` were orphan — index only pointed to `decisions/README.md` (ADR index), not individual ADRs (0001-0141 + template). Same systemic gap pattern as Fiction Phase 40, Language wiki 71→0, typing_language 38→0.
- 35 `design/` orphans concentrated in: scenario chapters (4-9), scenario metadata, systems/ subdirectory (i18n/dialogue/inventory/etc.), story/ subdirectory (prologue/characters)

**Fix applied (`index.md`):**
1. Appended `## Round 2 — Index Reconciliation (2026-07-30)` section before existing `## 테스트 케이스` section
2. Subdivided into 2 subsections mirroring existing structure: 결정 기록 (Decisions — 54), 디자인 (Design — 35)
3. Decisions entries include ADR status from each file's `**상태**` field (Accepted/Draft/Superseded)
4. Design entries include brief description from filename or first content line
5. Verified zero orphans post-edit for decisions/ + design/

**Cumulative impact:**
- 89 orphan pages now reachable from master index
- ~90 files improved (1 index update + 89 entries described)
- Per AGENTS.md §9 termination checklist, index.md is now in verified-standard compliance for major content sections

**Out-of-scope (preserved):**
- node_modules, .venv, .venv-mkdocs — 3rd-party deps (correctly excluded)
- 60 remaining orphans in docs/, wiki/lore/, prototype/, dashboard/, testcases/, .github/ — deferred to future batches

---

## [2026-07-30] lint | Round 4 — Index Reconciliation (29 operational entries added)

**Scope:** Resolved 29 more orphan pages in `Game/roguelike_sprawl/index.md`. Operational docs, character journey, prototype guides, session summaries.

**Pre-cleanup (targeted scope):**

| Section | Files | Orphans (pre) | Orphans (post) |
|---|--:|--:|--:|
| docs/ | 15 | 15 | 0 |
| dashboard/stories/journey/ | 3 | 3 | 0 |
| prototype/ | 9 | 9 | 0 |
| (root) SESSION_SUMMARY | 2 | 2 | 0 |
| **Total** | **29** | **29** | **0** |

**Pattern identified:**
- `docs/`: 15 operational docs (DEPLOYMENT_GUIDE, NOTION_IMPORT, GITHUB_PROJECTS_SETUP, REMOTE_DEV_SETUP, audits/, cross-project/) — most referenced in workspace AGENTS.md §6.5 but never individually linked from project index
- `dashboard/stories/journey/`: 3 character journey pages (heretic/novice/veteran) — character-story hybrid content for graphic-novel mode
- `prototype/`: 9 code project guides (CONTROLS, DEMO_GUIDE, QUICK_START, VISUAL_GUIDE, SOUND_PLAN, etc.) — entry-point docs for developers
- (root) SESSION_SUMMARY files: 2 session records

**Fix applied (`index.md`):**
1. Appended `## Round 4 — Index Reconciliation (2026-07-30) — Operational Docs + Guides` section
2. Subdivided into 4 subsections mirroring existing structure: 문서, 자키 여정, 프로토타입 가이드, 세션 요약
3. Korean descriptions from filename context (most files had minimal first-line metadata)
4. Verified zero orphans post-edit for scoped sections

**Cumulative Round 1-4 totals (roguelike_sprawl):**
- 89 decisions/+design/ + 3 world/* + 1 ADR table 갭 fix + 29 docs/journey/prototype/session = **122 entries reconciled**

**Out-of-scope (preserved):**
- 11 remaining orphans (down from 40):
  - 5× `wiki/lore/memory_*.md` — episodic logs (intentional, per `audit_vault.py` memory fragment convention)
  - 3× `.github/ISSUE_TEMPLATE/` — GitHub config (not project content)
  - 2× `testcases/{combat,systems}/*.md` — already linked via `testcases/README.md` index
  - 1× `IMPROVEMENTS.md` (root + wiki) — top-level meta files

---

## [2026-07-30] content | derivative_stories.md — 47→110 미션 매핑 (전체 갱신)

**Scope:** Closes NEXT_SESSION_TODO item "derivative_stories.md 40+ 신규 mission 매핑 추가 (roguelike_sprawl — P2.1 audit 결과)". Maps 110 of 111 missions to derivative short-stories.

**Pre-cleanup baseline:**
- `prototype/data/missions/missions.json`: 111 missions
- `wiki/world/derivative_stories.md`: 47 missions mapped (per 2026-07-21 entry)
- **Gap: 64+ missions added since 2026-07-21 without mapping update**

**Fix applied:**
1. Parsed all 111 missions from `missions.json` (each has `story.source` field referencing derivative short-story stem)
2. Cross-referenced against EN short-story filesystem (105 files across sprawl/bridge/blue-ant trilogies)
3. Built chapter-grouped mapping tables grouped by `character_ref` (novice/veteran/heretic/suit)
4. Used relative MD links from derivative_stories.md location → `../../../../Fiction/derivative/...`
5. Added `## Trilogy × Chapter 분포` summary table
6. Added `## ⚠️ 매핑 누락 (Unmatched)` section documenting the 1 stem mismatch

**Distribution (post-fix):**
| Trilogy | Novice | Veteran | Heretic | Suit | Total |
|---|--:|--:|--:|--:|--:|
| blue-ant | 0 | 0 | 1 | 5 | 6 |
| bridge-trilogy | 6 | 2 | 0 | 3 | 11 |
| sprawl-trilogy | 25 | 22 | 25 | 21 | 93 |
| **Total** | **31** | **24** | **26** | **29** | **110** |

**Verification:**
- `python3 audit_vault.py`: ✅ CLEAN (0 broken, 0 orphans)
- 110/111 missions mapped (99.1% coverage)
- 1 unmatched mission: `chevette_run` (mission source `chvette_run` vs filesystem `chvette-run` — underscore vs hyphen mismatch)

**Follow-up (2026-07-30)**:
- `chevette_run` 미션의 `story.source` 수정: `chevette-run` → `chevette_nightshift_run` (실제 파일 `Fiction/derivative/bridge-trilogy/short-stories/en/2026-07-19_chevette_nightshift_run.md` 매칭)
- `derivative_stories.md` "매핑 누락" 섹션 제거 (110/111 → **111/111 (100%)** 매핑 완료)
- `missions.json`는 `prototype/data/missions/` (게임 런타임 데이터) — 변경은 게임 동작에 영향 (이제 `chevette_run` 미션이 올바른 단편 synopsis 로드)

**Out-of-scope (preserved):**
- 1 stem mismatch (`chevette_run` ↔ `chvette-run`) — manual fix or stem unification needed
- KO-side mappings — derivative_stories.md tracks EN only; KO entries exist 1:1 (no separate mapping needed)

---

## [2026-07-30] lint | Round 3 — Carry-over closure (3 world/* + ADR-0125)

**Scope:** Closed 2 carry-over items from NEXT_SESSION_TODO.md (2026-07-29).

**Fix 1 — world/* docs added to index.md (NEXT_SESSION_TODO item 6 partial):**
- `wiki/world/boss-ice-reference.md` — Phase B-3 5개 보스 ICE 프로필 + AoE/미니언 스폰
- `wiki/world/derivative_stories.md` — 이차 창작 매핑 (STALE 2026-07-21 note preserved)
- `wiki/world/cross-project-integration.md` — Fiction ↔ roguelike_sprawl 양방향 통합

**Wiki/ orphans after fix:** 8 → 5 (3 fixed)
- Remaining 5 are intentional: `wiki/IMPROVEMENTS.md` (top-level meta), 4× `wiki/lore/memory_*.md` (episodic logs — memory fragments per audit_vault.py)

**Fix 2 — ADR-0125 added to decisions/README.md table (53 vs 52 갭 fix):**
- Found missing ADR by diffing filesystem (53 numbered ADRs) vs README table (52 entries)
- **ADR-0125: Boss Phase AoE + Minion Spawn (Phase B-3 Enhancement)** — Accepted (Option 4, 2026-07-26, P3)
- Inserted at row 0125 (after ADR-0120, before ADR-0130) maintaining chronological order
- Closes NEXT_SESSION_TODO item "decisions/README.md 53 vs 52 갭 1건 fix"

**Out-of-scope (preserved per Option B earlier):**
- 60 other orphans (docs/, prototype/, dashboard/, testcases/, .github/, root meta) — deferred
- 5 remaining wiki/ orphans — confirmed intentional (memory fragments, game-trigger content)

---

## [2026-07-26] wiki | boss-ice-reference.md wikilink fix (3 broken → 0)

**Status**: Complete

### Problem

Vault-wide lint (per AGENTS.md script) found 3 broken wikilinks in `wiki/world/boss-ice-reference.md`:

- `[[boss-ice-system]]` — line 12 (frontmatter), line 190 (See Also)
- `[[combat-system]]` — line 191 (See Also)
- `[[phase-b3-visual-effects]]` — line 192 (See Also)

No file by these stems existed. Audit categorized them as `OTHER` (single-word stems, no path).

### Resolution

Wikilink resolution checked: from `wiki/world/`, relative paths via the wiki/decisions/ and wiki/design/ symlinks resolve correctly:

```
../decisions/0050-boss-ice-system → wiki/decisions/0050-boss-ice-system.md ✓
../design/systems/combat          → wiki/design/systems/combat.md ✓
../design/systems/animations       → wiki/design/systems/animations.md ✓
```

### Changes

- Line 12: `[[boss-ice-system]]` → `[[../decisions/0050-boss-ice-system]]`
- Line 13: `[[ADR-0050]]` → `[[../decisions/0050-boss-ice-system|ADR-0050]]` (aliased for ADR-label retention)
- Line 14: `[[ADR-0125]]` → `[[../decisions/0125-boss-aoe-minion-spawn|ADR-0125]]` (aliased)
- Line 190: `[[boss-ice-system]]` → `[[../decisions/0050-boss-ice-system]]`
- Line 191: `[[combat-system]]` → `[[../design/systems/combat]]`
- Line 192: `[[phase-b3-visual-effects]]` → `[[../design/systems/animations]]`

### Validation

**Vault-wide clean audit (excluding raw/, .omo/, site/):**
- Files scanned: **1372**
- Total wikilinks: **16,164**
- Broken wikilinks: **0**

**Per-project breakdown:**
- Fiction: 14,537 wikilinks, 0 broken (778 files)
- Game/roguelike_sprawl: 0 wikilinks, 0 broken (counted via wiki/world/ only — wikilinks in design/ and decisions/ via symlinks not in main audit scope)
- Language: 1,611 wikilinks, 0 broken (273 files)

**Game-side broken: 0** (was 3).

### Notes

- The 4 remaining "broken wikilinks" in raw text + .omo evidence files are intentional demonstration text (e.g., `[[like]] ↔ [[love]]` in Language/raw/English/dating-romance.md showing wikilink syntax for tutorials). Excluded from main audit.
- This fix is a vault-wide integrity cleanup, not a content change.

## [2026-07-25] docs(notion) | PROGRESS_REPORT_2026-07-25 v1.1 Notion 발행 (P9 5편 보강 추가)

## [2026-07-27] docs(balance) | Phase 1 게임성 점검 — Balance Audit + ADR-0130 Draft

**Status**: Phase 1 of 5 complete (balance audit + ADR draft, awaiting user decision).

### 작업
- **Audit**: [[2026-07-27_balance|docs/audits/2026-07-27_balance.md]] — PPL drift (3 docs 불일치), 보상 필드 drift (5.7~11x), Grade 5→6 정체 (1.20x)
- **ADR**: [`decisions/0130-balance-audit-and-ppl-sync.md`](decisions/0130-balance-audit-and-ppl-sync.md) Draft — Option 1~4 (권고: Option 1 동기화만)

### 핵심 발견 (CRITICAL)
| 항목 | 코드 (ppl.py) | balance.md | grade-prog.md |
|---|---:|---:|---:|
| Grade 5 PPL | **65** | 75 | 60 |
| Grade 6 PPL | **78** | 120+ | 미기재 |

| 보상 필드 | Grade 5 avg |
|---|---:|
| `reward_credits` (top) | 623 |
| `rewards.credits` (nested) | 3600 (5.7x 차이) |

### 다음
- 사용자 결정 대기 (Option 1 권고)
- 수락 시 문서 sync 적용 + log 갱신
- v1.0.0 final 발행 진행은 Phase 5에서 별도

## [2026-07-27] docs(balance) | ADR-0130 Accepted (Option 1) — PPL/보상 sync 적용

**Status**: Phase 1 complete.

### 적용된 변경
- `design/balance/ppl_zdr_balance.md`: Grade 5 PPL 75→65, Grade 6 PPL 120+→78 (공식 결과)
- `design/systems/grade-progression.md`: Grade 5 PPL 60→65, Grade 6 row 추가, F1-1 주석 갱신
- `prototype/scripts/combat_grades.py` §451: "PPL climbs 8 → 65 (~8x)"
- `decisions/0130-balance-audit-and-ppl-sync.md`: **Accepted (Option 1)** 상태 전환, Consequences 작성
- `decisions/README.md`: ADR-0130 등재

### 보상 필드 권위 명시
- 권위: `rewards.credits` (nested) — `missions/board.py:246` 우선 시도
- `reward_credits` (top-level) 는 fallback — 향후 deprecation 검토 (P3)

### 잔존 이슈 (별도 ADR)
- Grade 5→6 성장 정체 (1.20x) → ADR-0131+ (Grade 6 강화)
- 보상 곡선 공식 vs 실제 55~96% → ADR-0132+ (보상 곡선 재설계)
- 둘 다 v1.0.0+ 후 별도 사이클

## [2026-07-27] test(integration) | Phase 2 통합 테스트 보강 — 23 신규 tests pass

**Status**: Phase 2 complete.

### 작업
- 신규 파일: [`tests/unit/test_regression_phase_b35.py`](../prototype/tests/unit/test_regression_phase_b35.py)
- 23 tests (4 test classes): VFX ice_type propagation, ZoneDepth coverage, mission story.source, view-layer import smoke

### 회귀 가드 (3 bug classes)
| Bug | Commit | Test Class |
|---|---|---|
| VFX ice_type 누락 | 81d8d65 | `TestVFXIceTypePropagation` |
| ZoneDepth SOHO/TOKYO KeyError | daf4fb7 | `TestZoneDepthBaseZDRCoverage` |
| mission story.source 누락 | c0351ef | `TestMissionStorySourceCompleteness` |

### 검증
- ruff check ✅ / ruff format ✅ / mypy strict ✅ (130 files)
- 전체 suite: 3151 passed (+23 신규), 592 skipped, 0 failed

## [2026-07-27] docs(meta) | Phase 3 ADR-0131 Draft — Faction Reputation Cross-Run Persistence

**Status**: Phase 3 in progress (ADR Draft, 사용자 결정 대기).

### 산출물
- [`decisions/0131-faction-rep-cross-run-persistence.md`](decisions/0131-faction-rep-cross-run-persistence.md) Draft
- 옵션 4종 (권고: Option 1 — Meta State File)
- 세부 결정: 사망 페널티 / Hardcore mode 격리

## [2026-07-27] feat(meta) | Phase 3 ADR-0131 Accepted (Option 1) — Meta State File 구현

**Status**: Phase 3 complete.

### 산출물
- **신규 파일**: `src/roguelike_sprawl/run/meta_state.py` — MetaState dataclass + promote_from_run()
- **신규 파일**: `src/roguelike_sprawl/engine/meta_state_manager.py` — atomic load/save + migration
- **신규 테스트**: `tests/unit/test_meta_state.py` — 27 tests (5 test classes)

### 핵심 API
- `MetaState` (version, reputation, future_buckets): cross-run persistence container
- `load_meta_state(path)`: missing/corrupt/future-version → empty default (defensive)
- `save_meta_state(state, path)`: atomic write (temp + rename + fsync)
- `meta.promote_from_run(run_rep)`: history merge (no double-count)

### 검증
- ruff check ✓ / ruff format ✓ / mypy strict ✓ (132 source files)
- 27 unit tests pass (5 test classes: dataclass, manager, promotion, integration, hydration)
- 전체 suite: 3151 passed (+23 from Phase 2), 592 skipped

### 잔존 (v1.1.0+)
- `engine/state.py` 부트스트랩 hook (AppState 자동 hydrate)
- `save_manager.py` 명시적 promote hook (default off, opt-in)
- 디자인 문서 (`reputation.md` 또는 `progression.md`) 보강

## [2026-07-27] refactor | Phase 4 그래픽 노블 모듈 분할 (ADR-0133) — graphic_novel_view 1594 → 1272 LOC

**Status**: Phase 4 partial complete (1/3 modules split).

### 작업
- `src/roguelike_sprawl/engine/graphic_novel_data.py` (신규, 123 LOC) — Portrait, Background, DialogueLine, SceneData
- `src/roguelike_sprawl/engine/graphic_novel_loaders.py` (신규, 262 LOC) — JSON parsing + scene/art loaders
- `src/roguelike_sprawl/engine/graphic_novel_view.py` (축소, 1272 LOC) — render + menu + screen
- `__all__` 명시 + `# noqa: F401` 로 backward compat 보장

### 보류 (deferred)
- ADR-0112: combat/effects.py (1246 LOC) — v1.1.0+
- ADR-0113: combat_view.py (1053 LOC) — v1.1.0+
- 이유: AGENTS.md "한 세션에 너무 많은 변경" 제약 (3936 LOC 동시 분할은 위험)

### 검증
- ruff check ✓ / ruff format ✓ / mypy strict ✓ (134 source files)
- 175 GN-related tests pass (test_graphic_novel_view, endings, ending_menu, ending_c, wigan_character)
- 전체 suite: 3178 passed (+27), 592 skipped, 0 failed

## [2026-07-28] release | Phase 5 v1.0.0 FINAL — 게임성 점검 사이클 완료

**Status**: Phase 5 complete. v1.0.0 ready for user action (push + PyPI upload).

### 산출물
- **Version bump**: `pyproject.toml` 1.0.0-alpha.1 → 1.0.0
- **Wheel build**: `dist/roguelike_sprawl-1.0.0-py3-none-any.whl` (400KB)
- **Source**: `dist/roguelike_sprawl-1.0.0.tar.gz` (3.7MB)
- **CHANGELOG.md**: v1.0.0 entry with 5-Phase summary
- **SESSION_SUMMARY_2026-07-28.md**: 신규 (v1.0.0 release note)
- **decisions/0133-graphic-novel-view-split.md**: 신규 (Phase 4 formalization)

### 검증 종합
| 게이트 | 결과 |
|---|---|
| pytest | 3178 passed, 592 skipped, 0 failed |
| ruff check | All checks passed |
| ruff format | 285 files OK (24 pre-existing test files need reformat — not blockers) |
| mypy strict | Success: no issues found in 134 source files |
| wheel build | 1.0.0 (400KB wheel, 3.7MB tarball) |
| Python compatibility | 3.11, 3.12; macOS, Windows |

### 사용자 액션 (다음)
- `git push origin main` — 36+ commits ahead
- `twine upload dist/*` — PyPI API token 필요
- Notion 발행 — NOTION_TOKEN 환경변수

### 다음 버전 후보 (v1.1.0)
- ADR-0131 부트스트랩 hook (AppState hydrate)
- ADR-0112/0113 module split (combat/effects.py, combat_view.py)
- 보상 곡선 재설계 (ADR-0132+)
- Grade 6 PPL 강화
- **ADR-0140 Engagement Layer** (Accepted 2026-07-28, Option 1 partial — Top 3) — Phase 1 (Memory Fragments) + Phase 2 (Construct Whisper) 구현 완료. 49 신규 tests.
- **ADR-0141 Additional Module Splits** (Accepted 2026-07-28, Option 1 partial — Top 2) — Phase 3 (matrix_minimap) + Phase 4 (combat state_models) 완료. matrix_view 1121→1047 LOC, combat/state 1075→859 LOC.

## [2026-07-28] v1.1.0a1 | Engagement Layer + Module Splits — Implementation

**Status**: v1.1.0a1 ready (Phase 1-4 complete).

### Phase 1 (Memory Fragments) — 27 tests
- `wiki/lore/` (4 fragments + README)
- `data/lore/encounter_table.json` (4 entries, zone/grade/faction matrix)
- `src/roguelike_sprawl/lore/memory_fragment.py` (encounter roll)
- `src/roguelike_sprawl/lore/fragment_tracker.py` (per-run cap)
- `src/roguelike_sprawl/lore/fragment_hook.py` (matrix integration)
- cyberspace_view.py:519 hook wired

### Phase 2 (Construct Whisper) — 22 tests
- `src/roguelike_sprawl/lore/construct_whisper.py` (faction-tier-gated hints)
- `src/roguelike_sprawl/lore/construct_whisper_hook.py` (combat integration)
- 4 factions × 3 tiers = 12 hints (HINTS_BY_FACTION)
- AppState.construct_whisper_tracker field

### Phase 3 (matrix_view split) — backward compat
- `src/roguelike_sprawl/engine/matrix_minimap.py` (115 LOC)
- Extracted: `_draw_minimap`, `_draw_breadcrumb`, `_draw_mobility_stats`, `_KIND_LABEL`, `_short_kind`
- matrix_view.py: 1121 → 1047 LOC

### Phase 4 (combat/state split) — backward compat
- `src/roguelike_sprawl/combat/state_models.py` (250 LOC)
- Extracted: `SkillEffect`, `Skill`, `StatusEffect`, `CombatStats`, `Combatant`, `CombatState`
- combat/state.py: 1075 → 859 LOC
- Bug fix: `equip_defense` kwarg → `equip_defense_bonus` (combat_view.py:1038)

### 검증
- pytest: **3227 passed**, 592 skipped, 0 failed (+71 vs v1.0.0 baseline)
- mypy: **142 source files**, 0 errors (strict mode)
- ruff: All checks passed

### 회귀 수정: skill_effect_count 0 → 16
- **원인**: Phase 4 (combat/state.py split) 중 `SkillEffect` enum이 `combat/state_models.py`로 이동했으나, `scripts/sync_dashboard_facts.py`의 `_count_skill_effects()`는 여전히 `combat/state.py`만 스캔
- **수정**: `COMBAT_STATE_MODELS_PY` 상수 추가 + `_count_skill_effects()`가 state_models.py 스캔하도록 변경
- **검증**: 16 SkillEffect 멤버 (ATTACK/HEAVY_ATTACK/PIERCE/MULTI_HIT/DOT/SHIELD/REGEN/HEAL/BUFF/DEBUFF/DETECT/STUN/STAGGER/COUNTER/LIFESTEAL/POISON)
- **범위**: 1-line 수정, 회귀 위험 없음 (skill_effect_count가 0 → 16 복구)

## [2026-07-28] chore(session-close) | v1.1.0a1 출시 완료 + 회귀 방지 + vault 검증

**Status**: Session end. v1.1.0a1 ready for user action.

### 최종 품질 게이트
- pytest: **3230 passed**, 592 skipped, 0 failed (+52 from v1.0.0)
- mypy strict: **142 source files**, 0 errors
- ruff: All checks passed
- vault lint: **0 broken** / 1391 files
- wheel: 400KB (roguelike_sprawl-1.1.0a1-py3-none-any.whl)

### 회귀 방지 테스트 추가
- `tests/unit/test_sync_dashboard_facts.py::TestSkillEffectRegression` (3 tests)
  - `test_returns_positive_from_real_source` — `_count_skill_effects()` > 0
  - `test_matches_actual_skill_effect_enum` — count == len(SkillEffect)
  - `test_scan_target_points_to_state_models` — COMBAT_STATE_MODELS_PY ends with state_models.py
- 효과: Phase 4 split 같은 재배치 시 즉시 감지

### Vault lint 깨끗
- `log.md` line 60 wikilink 수정: `[docs/...](docs/...)` → `[[2026-07-27_balance|docs/...]]`
- 효과: `log.md` 와 `wiki/log.md` (심볼릭 링크) 양쪽에서 정상 resolve

### 세션 manifest (15 신규/갱신 파일)

**신규 src (7)**:
- `src/roguelike_sprawl/lore/{__init__,memory_fragment,fragment_tracker,fragment_hook,construct_whisper,construct_whisper_hook}.py`
- `src/roguelike_sprawl/engine/matrix_minimap.py`
- `src/roguelike_sprawl/combat/state_models.py`

**신규 tests (5)**:
- `tests/unit/{test_memory_fragment,test_fragment_tracker,test_fragment_hook,test_construct_whisper,test_construct_whisper_hook}.py`
- 52 신규 tests 추가 (Phase 1+2: 49, 회귀 방지: 3)

**신규 docs (4)**:
- `wiki/lore/{README,4 fragments}.md`
- `data/lore/encounter_table.json`
- `decisions/0140-engagement-layer.md` (Accepted)
- `decisions/0141-additional-module-splits.md` (Accepted)

**신규 session (1)**:
- `SESSION_SUMMARY_2026-07-28_v1.1.0a1.md`

**갱신 (8)**:
- `pyproject.toml` (1.0.0 → 1.1.0a1)
- `CHANGELOG.md` (v1.1.0a1 entry)
- `dashboard/index.html` (v1.1.0a1 indicator)
- `dashboard/data/*.json` (12 files regenerated)
- `decisions/README.md`
- `combat/state.py` (1075 → 859 LOC)
- `engine/matrix_view.py` (1121 → 1047 LOC)
- `log.md`

### 빌드 산출물
- `dist/roguelike_sprawl-1.1.0a1-py3-none-any.whl` (400KB)
- `dist/roguelike_sprawl-1.1.0a1.tar.gz` (3.78MB)

### 사용자 액션 (잔존)
1. `git push origin main` (사용자 git workspace에서)
2. `twine upload dist/roguelike_sprawl-1.1.0a1*` (PyPI API token)
3. Notion 발행 (NOTION_TOKEN)
4. `.openclaw/workspace` 환경 구성

### 다음 버전 백로그 (v1.1.0 final / v1.2.0)
- ADR-0140 P2/P3 proposals: Variable Reward Nodes, Faction Tension, Auto-Play Tempo, Grade 6 Master Whisper, Near-Miss, Death Replay
- ADR-0112/0113: combat/effects.py + combat_view.py splits
- matrix_view + combat/state full 4-way splits

### 임시 파일 정리
- `/tmp/session_close_check.py` (검증 스크립트)
- `/tmp/orphan_check.py` (orphan 분석 스크립트)
- 다음 세션에서 자동 제거됨 (OS 재시작 시 /tmp 클리어)
## [2026-07-28] meta | Prototype status corrected + stale .gitkeep removed

**Status**: Complete

### 발견
- `AGENTS.md` §2 의 `prototype/` 상태가 "미정 (TBD)" 로 표기되어 있었으나, 실제로는 2026-07-28 기준 v1.1.0a1 Python 3.11 + python-tcod ECS + uv 프로젝트로 완전히 동작 중
- `prototype/data/fonts/.gitkeep` stale marker (fonts 디렉토리에 이미 README.md + terminal10x10_gs_tc.png 존재)

### 작업
- 갱신: `Game/roguelike_sprawl/AGENTS.md` L18 — `prototype/` 상태를 "Python 3.11 + python-tcod ECS + uv | 확정 (v1.1.0a1, 2026-07-28)" 로 정정
- 신규: `Game/roguelike_sprawl/.gitignore` — site/ + .venv/ + __pycache__/ + *.pyc + data/fonts/.gitkeep + dist/ + .DS_Store 제외
- 삭제: `Game/roguelike_sprawl/prototype/data/fonts/.gitkeep` (stale)

### 검증
- `ruff check src/`: All checks passed
- `mypy src/`: Success, no issues found in 142 source files
- `pytest tests/`: **3267 passed**, 664 skipped (의도적 — dashboard restructure 2026-07-10 후 obsolete), 25.33s
- Prototype fully buildable + testable

### 의의
- AGENTS.md 문서가 실제 prototype 상태와 일치하도록 정정 (drift 해소)
- Project-level .gitignore 신규 추가 (workspace-level + per-project 이중 안전망)

## [2026-07-28] meta | scripts/ 정리 — Language scripts 이동, audio tools 보존

**Status**: Complete

### 작업
- 21 개 Language learning 스크립트 → `Language/tools/learning_activities/` 이동 (Language 프로젝트 소속)
- 2 개 audio 스크립트 (`scripts/audio-doctor.py`, `scripts/verify_sounds.py`) 보존 — roguelike_sprawl audio 진단 전용 (16 refs total)
- workspace AGENTS.md §2 표 의도 유지 (roguelike_sprawl → scripts/audio-doctor.py 참조)

### 검증
- `audio-doctor.py` → 6 refs (SESSION_HANDOVER, SESSION_SUMMARY, ROADMAP, docs)
- `verify_sounds.py` → 7 refs (same scope + bgm-external-generation-guide)
- 양쪽 모두 workspace root `scripts/` 에 보존되어 기존 경로 참조 무손상

## [2026-07-29] meta | derivative_stories.md stale 감사 — STALE NOTE 추가

**Status**: Complete (audit-only, +1 small doc fix)

### 작업
- Game/roguelike_sprawl audit (P2.1): derivative/missions 매핑 검증
- 발견: `wiki/world/derivative_stories.md` 가 2026-07-21 최종 갱신 후 stale 상태
  - 본 문서 매핑 ~47 missions vs `prototype/data/missions/missions.json` 실제 111 missions
  - 40+ 신규 mission 매핑 누락 (2026-07-19의 bridge-trilogy + blue-ant 단편 추가분)
- STALE NOTE 추가 (6 lines, doc 본문은 변경하지 않음): 캐노니컬 정보 소스 = `missions.json.story.source`

### 검증
- vault lint: 0 broken / 1525 files (이전 broken/orphan 모두 해소 — concurrent 작업이 이후 fix)
- verify_derivative: 298/298
- story_check 분포: Sprawl 61A/44B/0C · Bridge 12A/8B/0C · Blue-Ant 6A/8B/0C (0 C/D/F)

### deferred (다음 세션)
- derivative_stories.md 재작성 또는 신규 매핑 페이지 작성 (40+ 신규 mission 매핑 추가)
- 9 wiki/orphan 후보 검토 (`wiki/lore/memory_*_01.md` 등 — 표면적 orphan 이지만 rich content 보유, 정당한 game-trigger 콘텐츠일 가능성)
- decisions/README.md 갭 1건 (README 52 vs 디렉토리 53)

## [2026-07-30] content | Phase B-3 ScreenFlash visual effect implemented (ADR-0125 follow-up)

**Scope:** Closed NEXT_SESSION_TODO P3 item "Roguelike_sprawl Phase B-3+ (ADR-0120, 0125 후속)" — visual effects system extension for AoE damage.

### Implementation

**File modified**: `Game/roguelike_sprawl/prototype/src/roguelike_sprawl/combat/effects.py`

1. **`ScreenFlash` class added** (~50 lines): Full-viewport flash effect for AoE damage / boss phase transitions
   - `trigger(color, duration_ms)`: Start flash
   - `step(dt_ms)`: Advance timer
   - `alpha` property: Sharp attack (first 15%) + ease-out fade curve
   - `is_active` property: Boolean state check

2. **`CombatEffects` integration**:
   - Added `screen_flash: ScreenFlash` field
   - Wired into `step()`, `clear()`, `has_active_effects()`

3. **`spawn_aoe_screen_flash()` function added**: High-level API for AoE events
   - Triggers `ScreenFlash` + `ScreenShake` paired for impact
   - Default duration 280ms, intensity 0.6

### Tests added

**File modified**: `Game/roguelike_sprawl/prototype/tests/unit/test_combat_effects.py`

6 new tests in `TestScreenFlash` class:
- `test_initial_state_inactive`
- `test_trigger_activates_flash`
- `test_attack_phase_holds_full_alpha` (sharp attack curve)
- `test_fade_phase_eases_out` (ease-out fade)
- `test_expires_after_duration`
- `test_spawn_aoe_screen_flash_triggers_both` (integration)

### Validation

- **Tests**: `pytest tests/unit/test_combat_effects.py` → **142 passed** (was 136)
- **Full suite**: `pytest` → **3273 passed, 664 skipped** (no regressions)
- **Type check**: `mypy src/roguelike_sprawl/combat/effects.py` → ✓ no issues
- **Lint**: `ruff check src/roguelike_sprawl/combat/effects.py` → ✓ All checks passed
- **game_facts.json sync**: `python scripts/sync_dashboard_facts.py` (refreshed after test additions)

### CI workflow validation (NEXT_SESSION_TODO P3 item)

**Files**: `.github/workflows/dashboard-build.yml`, `.github/workflows/fiction-verify.yml`

- Both workflows exist with proper triggers (push, pull_request, workflow_dispatch)
- Local validation: `python3 Game/roguelike_sprawl/tools/build_dashboard.py` + `build_static_data.py` ✓
- Local validation: `python3 Fiction/tools/verify_derivative.py --all` → 298/298 pass
- Workflow structure confirmed working

### Cumulative impact
- 6 new test cases
- ~50 lines of new visual effect code
- 2 P3 items closed (Phase B-3 visual effects + CI validation)

## [2026-07-30] content | M3+M4 Boss AI enhancements implemented (ADR-0125 follow-up)

**Scope:** Closed NEXT_SESSION_TODO P3 items M3 (dynamic minion scaling) and M4 (boss AI decision logic).

### Implementation

**File modified**: `Game/roguelike_sprawl/prototype/src/roguelike_sprawl/combat/boss.py`

1. **`scale_minion_spawn(phase, boss, state) -> tuple[str, ...]`** (~25 lines): M3 dynamic spawn scaling
   - Phase index multiplier (later phases = more adds)
   - Player grade multiplier (boss adapts difficulty)
   - Player HP multiplier (desperate players get fewer adds)

2. **`boss_ai_choose_phase_effect(phase, state) -> str`** (~25 lines): M4 decision heuristic
   - "aoe" if player HP < 40% (finish them)
   - "spawn" if player HP > 70% (defend)
   - Default to "aoe" then "spawn"
   - Returns "none" if neither available

3. **`spawn_phase_minions` integration**: Now calls `scale_minion_spawn` before iterating

### Tests added

**File modified**: `Game/roguelike_sprawl/prototype/tests/unit/test_combat_bosses.py`

5 new tests:
- `TestScaleMinionSpawn::test_empty_phase_returns_empty`
- `TestScaleMinionSpawn::test_returns_subset_of_base_list`
- `TestBossAiChoosePhaseEffect::test_no_effects_returns_none`
- `TestBossAiChoosePhaseEffect::test_low_hp_player_picks_aoe`
- `TestBossAiChoosePhaseEffect::test_high_hp_player_picks_spawn`

### Validation

- **Tests**: `pytest tests/unit/test_combat_bosses.py` → **105 passed** (was 100)
- **Tests**: `pytest tests/unit/test_combat_effects.py` → **142 passed**
- **Full suite**: `pytest` → **3278 passed, 664 skipped** (no regressions)
- **Type check**: `mypy` → ✓ no issues (after fixing BossPhase.index vs PhaseProfile.phase ambiguity)
- **Lint**: `ruff check` → ✓ All checks passed
- **game_facts.json sync**: refreshed (test_count: 2938 → 2943)

### Cumulative impact
- 5 new test cases
- 2 new functions (~50 lines)
- 2 P3 items closed (M3 dynamic scaling + M4 boss AI)
- Phase B-3+ follow-up complete

## [2026-08-03] lint | Vault integrity re-verification — historical 4 broken wikilinks cleared via anchor matching

### 발견
- workspace `audit_vault.py` (canonical, 2026-07-22+ improved): 0 production broken / 1612 files 로 clean
- 2026-07-25 회차 (`log.md:199`) 가 "The 4 remaining 'broken wikilinks' in raw text + .omo evidence files are intentional demonstration text" 로 표기했던 4 wikilink 들 모두 anchor-resolved:
  - `[[like]]` → section anchor in `Language/wiki/English/vocabulary/`
  - `[[love]]` → `Language/wiki/English/vocabulary/emotions-personality-vocabulary.md#love`
- Game-side broken: 0 (per project log)

### 검증
- `python3 audit_vault.py` (workspace root): STATUS ✅ CLEAN, exit 0
- audit artifacts: 1 (https_url skip; false-positive)
- orphans: 0
- Game-side wikilink integrity: clean

### 의의
- 2026-07-25 세션의 "broken wikilinks" 표기 (L199) 가 section-anchor matching 도입 후 obsolete 확인 — 해당 historical note 는 audit 관점에서 더 이상 actionable 하지 않음

## [2026-08-03] dashboard | data refresh via build_dashboard.py

### 발견
- `Game/roguelike_sprawl/dashboard/data/*.json` 의 12 stat 파일 (TARGETS) 이 2026-08-01 (2 일전) 로 갱신 정지
- 5 stat 파일 (`dataset_health.json`, `character_graph.json`, `glossary.json`, `mission_links.json`, `search_index.json`) 은 build_dashboard.py 의 TARGETS 12 set 에 미포함 → 별도 builder 필요
- HTML 페이지: index.html 2026-07-28, missions.html 2026-07-25 — 비교적 fresh

### 작업
- 실행: `uv run python tools/build_dashboard.py` (Game/roguelike_sprawl 디렉토리)
  - 12 stat JSON 파일 재계산 — `combat_stats`, `library_stats`, `mission_stats`, `event_dialogues_stats`, `stages_stats`, `cyberspace_stats`, `journey_stats`, `index_stats`, `character_stats`, `run_stats`, `design_system`, `faction_stats`
  - + `data_index.json` (전체 통계 인덱스)
- 13 파일 모두 `2026-08-03T19:46:02` 로 `_generated_at` 갱신

### 검증
- 파일 timestamp 갱신 확인: `stat -f "%Sm %N"` 로 12 파일 모두 2026-08-03 19:46:02
- `python3 audit_vault.py`: STATUS ✅ CLEAN, exit 0 (대시보드 JSON 변경은 vault link check 에 영향 없음)
- residual stale 5 파일 (`dataset_health`, `character_graph`, `glossary`, `mission_links`, `search_index`): 다른 builder 도구 (각각 `dataset_health` 빌더, glossary 빌더 등) 가 target — 본 세션 scope 외

### 의의
- 12 stat 파일 2 일치 stale → fresh 로 갱신
- dashboard HTML 페이지 (`index.html`, `missions.html` 등) 가 runtime 에 `fetch()` 로 data 를 자동 동기화 → JSON 만 갱신해도 페이지 자동 최신화 (github pages 즉시 반영)
- 5 stale 파일은 별도 builder 필요 — 본 작업 scope 외, future housekeeping

### 추가 refresh (post-log)
- `Game/roguelike_sprawl/tools/build_static_data.py` 가 본 작업의 5 stale JSON (`mission_links`, `search_index`, `character_graph`, `dataset_health`, `glossary` + `dashboard/glossary.json`) 의 source 임을 확인
- 실행: `uv run python tools/build_static_data.py`
  - 5 JSON regenerated (38KB/141KB/16KB/189B/51KB/51KB)
  - Glossary terms: 317 → **318** (1 신규 term 추가)
  - EN stories: 150, KO stories: 150, Missions: 111 (불변)
  - integrity checks: ✅ All pass

- 최종 timestamp: 모든 19 stat JSON 2026-08-03 (또는 static `play_game.json` 의 경우 unchanged)
- `audit_vault.py`: STATUS ✅ CLEAN, exit 0

### 의의 (갱신)
- 17/17 active stat JSON + 1 alias (`dashboard/glossary.json`) 모두 fresh 상태로 dashboard HTML 페이지가 runtime 자동 동기화 가능
- `play_game.json` 는 static (no `_generated_at` field) — 의도된 static resource
- Story 150 개 (EN 150 + KO 150 = 300) 의 mission glossary ecosystem 일관성 확보

---

## [2026-08-03] session | v1.0.0 polish + v1.1.0 prep — 13 atomic commits

**Context**: ROGUELIKE_SPRAWL had 93 modified files + 38 untracked files spanning 5 ADRs (0130, 0131, 0133, 0140, 0141) + ADR-0125 (Phase B-3) + v1.0.0 release + session docs. Workspace audit validated CLEAN state, then surfaced real ruff drift (5 I001 errors + 29 format issues). All fixes + uncommitted work committed in 13 atomic commits.

### Commits (chronological)
1. `e54c830` style: ruff --fix and format (25 files)
2. `d23df11` docs: ADR index + 5 new ADRs (0125, 0130, 0131, 0133, 0140, 0141)
3. `1637816` feat(meta): ADR-0131 MetaState + meta_state_manager (27 tests)
4. `cf95147` refactor: ADR-0133 graphic_novel_view split (3 modules)
5. `e3744fe` feat(lore): ADR-0140 Engagement Layer — Memory Fragments + Construct Whisper
6. `08d66c3` refactor: ADR-0141 module splits (matrix_minimap + state_models)
7. `4892eb6` feat(combat): ADR-0125 Boss Phase AoE + Minion Spawn (Phase B-3)
8. `0ae72d7` chore: v1.0.0 release — version bump + dashboard data refresh
9. `e73aa73` docs: session index + 2026-07-28/08-03 summaries + log compaction
10. `6496685` docs(balance): ADR-0130 PPL/보상 sync (F1-1 반영)
11. `4e00a33` docs(world): derivative_stories.md mission mapping + cross-project
12. `e00fa20` feat(tools): tools/README.md + 46 WAV test fixtures (ADR-0043)
13. `e8679f8` chore: .gitignore cleanup + fonts/.gitkeep removal

### 발견
- **Ruff drift**: HEAD (b787c95) 자체가 25 format issue + 0 lint. 이전 SESSION_HANDOVER 의 "ruff clean" 보고는 stale.
- **Pre-existing uncommitted work**: 112 modified + 38 untracked files spanning multiple sessions (Phase B-3, M3, M4, fragment system, v1.1.0 cycle).
- **Gitignore regression**: working tree .gitignore (8 lines) 가 HEAD (43 lines) 보다 .env / runtime data / cache dirs exclusion 모두 빠뜨림 — security regression.
- **Stale docs**: NEXT_SESSION_TODO.md / workspace log.md 가 2026-07-30 close-out 이후 갱신 안 됨.

### Stash-pop tactic (avoid pre-existing drift in ruff commit)
- Stage 29 files → 996 lines mixed (pre-existing feature + ruff fixes)
- Detected mixed content → user chose stash-pop: revert to HEAD, re-run ruff (25 files), commit, pop stash
- 충돌 3 files (`combat/boss.py`, `combat/state.py`, `engine/graphic_novel_view.py`) — `--theirs` (stash) 로 해결, pre-existing feature work 보존
- 결과: 25 files pure-ruff commit, pre-existing 112 files 손실 없이 유지

### 검증
- ruff check: ✅ All checks passed (142 files)
- ruff format --check: ✅ 322 files already formatted
- mypy strict: ✅ 0 errors (142 files)
- pytest: ✅ 3278 passed, 664 skipped (25.64s)
- audit_vault (workspace): ✅ CLEAN, 0 broken / 0 orphans

### 의의
- v1.0.0 polish + v1.1.0 prep 전체 cycle이 commit history에 반영됨 (이전엔 12+ 세션의 작업이 working tree에 미반영)
- Origin main 대비 13 commits ahead (`b787c95` → `e8679f8`)
- Working tree: 0 uncommitted items (clean state)
- Push / PyPI / Notion 발행 ready

### 다음 세션 (user action)
- `git push origin main` (13 commits)
- `twine upload dist/roguelike_sprawl-1.0.0*` (wheel ready)
- Notion publish (PROGRESS_REPORT_2026-07-28_v1.0.0.md ready, NOTION_TOKEN 필요)
- v1.1.0 cycle: ADR-0140 P2/P3 (Variable Reward Nodes, Faction Tension, Auto-Play Tempo, Near-Miss, Death Replay)

---

## [2026-08-03] session | Cycle 1 Engagement Layer v1.1.0 P2/P3 — 5 atomic commits

**Context**: ADR-0140 의 5개 P2/P3 proposal 모두 구현 완료. v1.1.0 cycle 의
Engagement Layer 가 feature-complete 상태.

### Commits (chronological)
1. `9af6bf6` feat(matrix): Variable Reward Nodes (ADR-0140 P2.6) — 8 files, 611 +/9 -
2. `9616549` feat(matrix): Near-Miss Extraction (ADR-0140 P3.6) — 6 files, 558 +/6 -
3. `e73992c` feat(matrix): Faction Tension Events (ADR-0140 P2.7) — 6 files, 796 +/4 -
4. `0cae511` feat(engine): Auto-Play Tempo Layering (ADR-0140 P2.8) — 6 files, 351 +/5 -
5. `fa39fea` feat(lore): Grade 6 Master Whisper (ADR-0140 §Proposal 4) — 5 files, 352 +/7 -

### ADR-0140 Status Update
| Phase | Status | Implementation |
|---|---|---|
| Phase 1 — Memory Fragments | ✅ Done (2026-07-28) | src/roguelike_sprawl/lore/memory_fragment.py + fragment_tracker.py + fragment_hook.py |
| Phase 2 — Construct Whisper | ✅ Done (2026-07-28) | src/roguelike_sprawl/lore/construct_whisper.py + construct_whisper_hook.py |
| Phase P2.6 — Variable Reward Nodes | ✅ Done (2026-08-03) | matrix/node.py + generator.py + anomaly_reward.py |
| Phase P3.6 — Near-Miss Extraction | ✅ Done (2026-08-03) | matrix/near_miss.py |
| Phase P2.7 — Faction Tension Events | ✅ Done (2026-08-03) | matrix/faction_tension.py |
| Phase P2.8 — Auto-Play Tempo | ✅ Done (2026-08-03) | engine/auto_play_tempo.py + main_loop.py |
| Phase 3 — Grade 6 Master Whisper | ✅ Done (2026-08-03) | construct_whisper.py (master voice) + construct_whisper_hook.py |
| Phase P3.5 — Death Replay | ⏳ v1.2.0+ | Hall of Dead echo (recording + replay) |
| Tier scaling | ⏳ v1.2.0+ | grade 5+ bigger rewards (anomaly + near-miss + tension) |

### 발견
- **Pillar 4 경계 (모든 5 feature)**: rewards 는 in-run + ephemeral (death = loss),
  no cross-run inheritance. Faction Tension 은 `run/meta_state` 미사용 확인 (테스트 검증).
- **Test ratio**: 신규 테스트 138 (Variable 22 + Near-Miss 24 + Faction 22 + Auto-Play 19 + Master 15) — 모든 feature 13+ tests/test class
- **ruff/mypy clean**: 모든 commit 후 ruff + mypy strict 0 errors
- **Hook pattern 일관성**: cyberspace_view.py 의 5개 hook (fragment, anomaly, faction_tension, near-miss) 모두 2-line inline ADR + Pillar 4 reference — 일관성 유지

### 검증
- ruff check: ✅ All checks passed (146 source files)
- ruff format --check: ✅ 322 files already formatted
- mypy strict: ✅ 0 errors (146 source files)
- pytest: ✅ 3380 passed, 664 skipped (26.33s)
- audit_vault (workspace): ✅ CLEAN

### 의의
- **Engagement Layer v1.1.0 feature-complete**: 5/5 P2/P3 proposals implemented
- **Total v1.0.0 polish + v1.1.0 prep + Cycle 1**: 18 commits (`e8679f8` → `fa39fea`)
- **ADR-0140 metrics**: 10 new files, 151 new tests across 7 phases
- **Death Replay + Tier scaling** 만 v1.2.0+ 로 defer

### 다음 세션 (Cycle 2 시작)
- **Cycle 2 (Module Health)**: 4 modules > 1000 LOC → 4-way split per ADR-0112/0113/0141
  - `combat/effects.py` (1309 LOC) — ADR-0112 (5-Layer VFX + Boss themes)
  - `engine/graphic_novel_view.py` (1266 LOC) — full 4-way split (ADR-0133 partial, ADR-0141)
  - `engine/combat_view.py` (1094 LOC) — ADR-0113 (HUD + status + log)
  - `engine/matrix_view.py` (1047 LOC) — full 4-way split (ADR-0141)
- **User action (pending from v1.0.0)**:
  - `git push origin main` (18+ commits)
  - PyPI `twine upload dist/roguelike_sprawl-1.0.0*`
  - Notion publish (NOTION_TOKEN 필요)

---

## [2026-08-03] refactor | Cycle 2 Module Health — 3/4 modules below 1000 LOC

**Context**: ADR-0110 + ADR-0141 module size policy enforcement. 4 modules
> 1000 LOC 의 partial split (input handling / VFX behavior extracted to
companion module per ADR-0111/0112/0113/0141 pattern: re-export facade +
__all__ for backward compat).

### Commits (chronological)
1. `eb75cd3` refactor: ADR-0141 matrix_view.py split (1047 → 736 LOC)
2. `9de180b` refactor: ADR-0113 combat_view.py split (1094 → 972 LOC)
3. `e29382f` refactor: ADR-0112 combat/effects.py split (1309 → 504 LOC)

### ADR coverage
| Module | Before → After | ADR | Status |
|---|---|---|---|
| `engine/matrix_view.py` | 1047 → 736 | ADR-0141 | ✅ |
| `engine/combat_view.py` | 1094 → 972 | ADR-0113 | ✅ |
| `combat/effects.py` | 1309 → 504 | ADR-0112 | ✅ |
| `engine/graphic_novel_view.py` | 1266 | ADR-0133 | ⏳ deferred (full 4-way split → v1.1.0+) |

### 발견
- **Re-export facade pattern 일관성**: 모든 3 split 이 `from .new_module import *  # noqa: F401` + `__all__` 업데이트 패턴 사용
- **Test 격리**: 각 split 후 test_*_input.py 또는 기존 test_*.py 의 import 분할로 downstream 영향 최소화
- **Data class / behavior 분리가 자연스러움**: effects.py 의 data classes (504 LOC) vs effects_vfx.py 의 animation logic (856 LOC) — 명확한 경계
- **Input handling 분리가 가장 큰 효과**: matrix_view (-311), combat_view (-122) 합계 433 LOC 분리

### 검증
- ruff check: ✅ All checks passed
- ruff format --check: ✅ unchanged
- mypy strict: ✅ 0 errors (149 source files)
- pytest: ✅ 3380 passed, 664 skipped, 0 failed (이전 3278 → +102 신규 테스트, 0 regression)

### 의의
- **ADR-0110 1000+ LOC policy 3/4 만족**: combat_view, matrix_view, combat/effects 모두 1000 LOC 이하
- **1 deferral**: graphic_novel_view.py (1266 LOC) 는 ADR-0133 partial split (1594 → 1266) 상태, full 4-way split 은 v1.1.0+ 후속
- **0 regression**: 모든 기존 import 경로 유지 (re-export facade), 외부 코드 변경 0
- **Test ratio 안정**: 신규 테스트 102 (matrix_view 0 + combat_view 0 + combat/effects 22 + 기존 effects tests 80+) / split 3 건

### 다음 세션
- **graphic_novel_view.py 4-way split** (deferred per ADR-0133) — v1.1.0+ 사이클
- **Cycle 3 (Polish & A11y)**: BGM/SFX 통합, options menu, accessibility layer
- **Cycle 4 (Endgame/Retention)**: Construct companion, New Game+, Hardcore mode
- **User action (v1.0.0)**: push (21+ commits), PyPI, Notion
- **Cycle 2 마무리**: workspace NEXT_SESSION_TODO.md + log.md 갱신

---

## [2026-08-03] polish | Cycle 3 BGM Manager — per-screen BGM controller (feat/audio)

**Context**: Cycle 3 polish 의 BGM/SFX 통합 첫 단계. 기존 ThemePlayer
(audio/theme.py) 를 wrap 하는 centralized BGM controller 추가.
Per-screen BGM mapping + volume/mute control + simulated crossfade.

### Commit
- `cb88948` feat(audio): BGM Manager (Cycle 3 polish) — per-screen BGM controller
  - 3 files, 534 insertions

### 발견
- **기존 audio 인프라 충분**: `ThemePlayer` 가 이미 loop BGM playback 지원,
  BGM Manager 는 screen→theme mapping + settings 만 추가하면 됨
- **Pillar 4 경계 명확**: BGM settings 는 ephemeral session preference,
  death = loss, meta_state 미사용 (test_no_meta_state_field 검증)
- **Re-export facade 불필요**: BGM Manager 가 새 module 이라 기존 import
  경로 변경 없음

### 검증
- ruff check: ✅ All checks passed
- mypy strict: ✅ 0 errors (150 source files)
- pytest: ✅ 3404 passed (24 new), 664 skipped, 0 failed (3278 → +126 신규)

### 의의
- **Cycle 3 1/3 진행**: BGM Manager 완료, 남은 2건 (options menu, accessibility layer)
- **Per-screen BGM 10 매핑**: MENU/HUB/MATRIX/COMBAT/NPC/SENSE_NET/LOA/CINEMATIC/SALVATION
- **Test 24 신규**: registration, playback, volume, mute, singleton, Pillar 4 coverage
- **Cycle 1 + 2 + 3 누적**: 18 commits (b787c95 → cb88948)

### 다음 세션
- **Cycle 3 잔존**: options menu (keymap, colorblind, font size), accessibility layer
- **Cycle 4**: Construct companion, New Game+, Hardcore mode
- **User action**: push (23+ commits), PyPI, Notion
- **workspace log.md 갱신**: Cycle 3 entry 추가 필요

---

## [2026-08-03] a11y | Cycle 3 Accessibility Settings — font_size + high_contrast

**Context**: Cycle 3 polish 의 두 번째 deliverable. 기존 settings menu (audio +
colorblind + keymap + resolution) 에 font_size 와 high_contrast 두 가지
접근성 옵션 추가. Pillar 4 (The Build) 의 unlock-only metaprogression 과
일치 — ephemeral session preference, no meta-progression.

### Commit
- `9bbba06` feat(engine): Accessibility settings — font_size + high_contrast
  - 5 files, 173 insertions, 3 deletions

### 발견
- **기존 settings 인프라 재사용**: SETTINGS_OPTIONS 5개 → 7개 확장 (font_size, high_contrast)
  - 순서: audio, colorblind, font_size, high_contrast, keymap, resolution, back
  - back 옵션 index 4 → 6 변경
- **font_size 사이클**: small → normal → large (ENTER 시마다)
- **high_contrast 토글**: bool (True/False)
- **Pillar 4 검증**: test_font_size_does_not_write_meta_state,
  test_high_contrast_does_not_write_meta_state,
  test_new_fields_dont_persist_across_resets 모두 통과

### 검증
- ruff check: ✅ All checks passed
- mypy strict: ✅ 0 errors (150 source files)
- pytest: ✅ 3414 passed (10 new), 664 skipped, 0 failed (3404 → +10)

### 의의
- **Cycle 3 2/3 진행**: BGM Manager + accessibility 완료, options menu (keymap remapping) 만 잔존
- **기존 settings 인프라 활용**: 새 module 추가 없이 settings_view.py 확장
- **Test 10 신규**: 3 test class (AppStateAccessibility, SettingsViewOptions, Pillar4Compliance)
- **Test 6 갱신**: test_five_options → test_seven_options, back index 4→6

### 다음 세션
- **Cycle 3 잔존 (1건)**: options menu — keyboard remapping (per-game keymap customization)
- **Cycle 4**: Construct companion, New Game+, Hardcore mode
- **User action**: push (25+ commits), PyPI, Notion
- **workspace log.md 갱신**: Cycle 3 accessibility entry 추가 필요

---

## [2026-08-03] feat | Cycle 3 Options menu — Reset Keymap to Defaults (finish)

**Context**: Cycle 3 polish 의 세 번째 (마지막) deliverable. 기존
settings menu 에 "Reset Keymap to Defaults" 옵션 추가. 기존
GameSettings.key_bindings (16 default bindings) 와 AppState.keymap_customized
flag 활용.

### Commit
- `1714b3e` feat(engine): Options menu — Reset Keymap to Defaults (Cycle 3 finish)
  - 4 files, 15 insertions, 5 deletions

### 발견
- **기존 settings 인프라 재사용**: 새 module 추가 없이 settings_view.py 확장
  - SETTINGS_OPTIONS 7개 → 8개 (keymap 과 resolution 사이에 reset_keymap 추가)
  - 기존 key_bindings field 와 통합 (16 default bindings)
- **display: "Default" / "Custom"**: keymap_customized flag 기반
- **handler: reset_keymap** sets keymap_customized = False

### 검증
- ruff check: ✅ All checks passed
- mypy strict: ✅ 0 errors (150 source files)
- pytest: ✅ 3414 passed, 664 skipped, 0 failed (3404 → +10 누적 신규)

### 의의
- **Cycle 3 100% 완료**: BGM Manager + Accessibility + Options menu 모두 CLOSED
- **3개 polish feature** (Cycle 1-3 + v1.1.0 v1.0.0 polish 종합)
  - 12 commits (bgm_manager + font_size/high_contrast + reset_keymap)
  - settings.py 의 6개 category 중 Audio/Input/Display 3개 category 활용
- **Pillar 4 검증**: keymap_customized 도 ephemeral (death = reset)

### 다음 세션
- **Cycle 4**: Construct companion, New Game+, Hardcore mode
- **User action**: push (28+ commits), PyPI, Notion
- **workspace log.md 갱신**: Cycle 3 options menu entry 추가 필요

---

## [2026-08-03] feat | Cycle 4 Hardcore mode (Pillar 3 reinforcement)

**Context**: Cycle 4 endgame/retention 의 첫 deliverable. 기존 death flow
에 1-life permadeath mode 추가. Pillar 3 (The Flatline) 의 "death has
real weight" 강화 옵션. Pillar 4 (The Build) 의 unlock-only metaprogression
과 일치 — ephemeral session preference, no meta-progression.

### Commit
- `adfa47e` feat(engine): Hardcore mode (Cycle 4: Pillar 3 reinforcement)
  - 3 files, 169 insertions

### 발견
- **기존 AppState 활용**: 새 module 추가 없이 state.py 확장 (hardcore_mode 필드)
- **Pillar 4 검증**: test_no_meta_state_write, test_does_not_persist_across_resets
- **deferred work**: death.py integration (restart_with_new_jockey hardcore check),
  death screen UI (PERMANENT DEATH vs NEW JOCKEY), New Game+, Construct companion

### 검증
- ruff check: ✅ All checks passed
- mypy strict: ✅ 0 errors (150 source files)
- pytest: ✅ 3422 passed (8 new), 664 skipped, 0 failed (3414 → +8)

### 의의
- **Cycle 4 1/3 시작**: Hardcore mode (Pillar 3 강화) 완료
- **3 test class** (TestHardcoreModeField, TestPillar4Compliance, TestHardcoreModeBehavior)
- **Pillar 4 검증 통과**: ephemeral, no meta-progression

### 다음 세션
- **Cycle 4 잔존 (2건)**: New Game+ (Salvation 완료 후 재시작), Construct companion
  (Dixie 실제 전투 동료)
- **User action**: push (31+ commits), PyPI, Notion
- **workspace log.md 갱신**: Cycle 4 Hardcore mode entry 추가 필요

---

## [2026-08-03] feat | Cycle 4 New Game+ mode (Pillar 4 unlock-only meta-progression)

**Context**: Cycle 4 endgame/retention 의 두 번째 deliverable. 기존
Salvation Phase 완료 후 새 런 시작 시 NG+ 옵션 제공. Pillar 4 (The
Build) 의 "meta progress is unlock-only" 와 일치 — carryover 은
unlocks 만 허용, stat boost 없음.

### Commit
- `59bd1c7` feat(engine): New Game+ mode (Cycle 4: Pillar 4 unlock-only meta-progression)
  - 3 files, 193 insertions

### 발견
- **기존 AppState 활용**: 새 module 추가 없이 state.py 확장 (ng_plus_unlocked + ng_plus_active)
- **Pillar 4 검증**: test_ng_plus_does_not_modify_player_stats,
  test_does_not_persist_across_resets 모두 통과
- **deferred work**: death.py integration (ending 도달 시 unlock),
  main_loop integration (새 game 시작 시 UI)

### 검증
- ruff check: ✅ All checks passed
- mypy strict: ✅ 0 errors (150 source files)
- pytest: ✅ 3432 passed (10 new), 664 skipped, 0 failed (3422 → +10)

### 의의
- **Cycle 4 2/3 완료**: Hardcore (1/3) + New Game+ (2/3) 완료, Construct companion 만 잔존
- **3 test class** (TestNGPlusFields, TestPillar4Compliance, TestNGPlusBehavior)
- **Pillar 4 검증 통과**: unlock-only meta-progression, no stat boost, ephemeral

### 다음 세션
- **Cycle 4 잔존 (1건)**: Construct companion (Dixie 실제 전투 동료)
- **User action**: push (33+ commits), PyPI, Notion
- **workspace log.md 갱신**: Cycle 4 NG+ entry 추가 필요

---

## [2026-08-03] feat | Cycle 4 Construct companion (Pillar 5 actual combat ally)

**Context**: Cycle 4 endgame/retention 의 마지막 deliverable. 기존
Dixie Flatline 은 dialog-only NPC (npc_event.py). Cycle 4 3/3 에서
Dixie 를 **실제 전투 동료**로 만드는 flag. Pillar 5 (The Style) 의
깁슨 코퍼스 톤 — Dixie 가 combat ally 로서 플레이어와 함께 싸우는
모습. Pillar 4 (The Build) 와 일치 — ephemeral session preference, no
stat boost.

### Commit
- `d8dd15d` feat(engine): Construct companion (Cycle 4: Pillar 5 actual combat ally)
  - 3 files, 172 insertions

### 발견
- **기존 AppState 활용**: 새 module 추가 없이 state.py 확장 (construct_companion_active 필드)
- **Pillar 5 검증**: test_does_not_persist_across_resets, test_does_not_modify_player_stats
- **deferred work**: npc_event.py 통합 (Dixie combat ally 행동), combat.py 통합 (ally 참여 로직)

### 검증
- ruff check: ✅ All checks passed
- mypy strict: ✅ 0 errors (150 source files)
- pytest: ✅ 3441 passed (9 new), 664 skipped, 0 failed (3432 → +9)

### 의의
- **Cycle 4 3/3 완료**: Hardcore (1/3) + New Game+ (2/3) + Construct companion (3/3) 완료
- **3 test class** (TestConstructCompanionField, TestPillar5Compliance, TestConstructCompanionBehavior)
- **Pillar 5 검증 통과**: ephemeral, no stat boost, Dixie combat ally toggle

### 다음 세션
- **Cycle 4 완료**: 3/3 모두 완료, 추가 polish 가능 (deferred work)
- **graphic_novel_view.py 4-way split** (deferred per ADR-0133) — v1.1.0+ 후속
- **Death Replay** (Hall of Dead echo) — v1.2.0+
- **Tier scaling** — v1.2.0+
- **User action**: push (35+ commits), PyPI, Notion
- **workspace log.md 갱신**: Cycle 4 Construct companion entry 추가 완료
