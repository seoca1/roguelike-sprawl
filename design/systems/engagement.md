# Engagement Layer (ADR-0140)

> **Status**: v1.0.0 polish complete (Top 3: Memory Fragments + Construct Whisper + Module split scaffolding)
> **Cycle**: v1.1.0 (P2 proposals)
> **Owner**: variable reward nodes implemented 2026-08-03

## Overview

ADR-0140은 8개 engagement proposal 중 Top 3 (Memory Fragments + Construct Whisper +
module split scaffolding) 만 v1.0.0 cycle에서 구현. v1.1.0 cycle에서 P2/P3 의 나머지
5개 proposal (Variable Reward Nodes, Faction Tension, Auto-Play Tempo, Near-Miss,
Death Replay) + ADR-0140 P3 (Grade 6 Master Whisper) 가 defer 됨.

이 문서는 v1.1.0 P2/P3 의 Variable Reward Nodes (제안 6) + Near-Miss Extraction (제안 3)
디자인 스펙 + 구현 노트.

## Variable Reward Nodes (ADR-0140 §Proposal 6)

### 골재

Matrix 안의 DATA node 일부가 **anomaly variant** 로 표시된다. Jack-in 시 시각적으로
구분되며 (◆ glyph, magenta color), first entry 시 one-shot bonus reward 부여.

### 게임 디자인

- **Probabilities**: 30% of DATA nodes are anomalies (per ADR-0140)
- **Visual distinction**:
  - Glyph: `◆` (대비: regular DATA = `$`)
  - Color: `(255, 100, 255)` magenta (대비: regular DATA = `(255, 215, 0)` gold)
  - Label: "Anomaly" (대비: "Data")
- **Trigger**: player enters the anomaly node (first entry only)
- **One-shot**: `state.anomaly_triggered` set 으로 중복 트리거 방지

### Reward 종류 (Pillar 4 safe — no cross-run inheritance)

| Reward | Amount | Description | Pillar 4 Check |
|---|---|---|---|
| **CREDITS** | +50 | in-run currency (flat) | ✅ No inheritance |
| **SALVAGE** | +1 | in-run crafting material | ✅ Consumed in-run |
| **INFO** | +1 | narrative data fragment | ✅ Ephemeral |

**Weighted uniform**: 모든 reward 33% 확률. Tier scaling (later grade = bigger reward)
은 v1.1.0+ deferred.

### Pillar 정합 검증

- **Pillar 1 (The Run)**: anomaly 는 run-scoped. 새 런 = 새 anomaly detection.
- **Pillar 2 (The Matrix)**: anomaly 는 cyberspace 안 phenomenon.
- **Pillar 3 (The Flatline)**: anomaly reward 는 flat bonus, death 시 잃음.
- **Pillar 4 (The Build)**: rewards 는 *unlock-only* 형태로 cross-run inheritance 없음.
  - credits: in-run currency (사망 시 손실)
  - salvage: in-run crafting (사망 시 손실)
  - info: narrative piece (일회성)
- **Pillar 5 (The Style)**: anomaly 는 깁슨 코퍼스 톤 ("이 코드는 뭔가 다르다") 정합.

### Flow

```
[Player navigates matrix with arrow keys]
    |
    v
[_handle_cyberspace_movement() called]
    |
    v
[best_neighbor determined]
    |
    v
[state.current_node_id = best_neighbor.id]
    |
    v
[check_memory_fragment_on_node_entry() — ADR-0140 §2]
    |
    v
[NEW: check_anomaly_reward_on_node_entry() — ADR-0140 §6]
    |
    +-- if best_neighbor.is_anomaly AND not in triggered set:
    |   +-- pick random reward from anomaly_reward table
    |   +-- apply reward to state (credits / salvage_fragments / info_pieces)
    |   +-- append status message: ">>> Anomaly recovered: ..."
    |   +-- add best_neighbor.id to state.anomaly_triggered
    |
    +-- else: no-op
```

### 구현 노트

**파일**:
- `matrix/node.py` — `is_anomaly: bool = False` field 추가 (with `__post_init__` validation: DATA only)
- `matrix/generator.py` — `ANOMALY_PROBABILITY = 0.30` constant + 30% check per DATA node
- `matrix/anomaly_reward.py` (NEW) — `AnomalyRewardKind`, `AnomalyReward`, `AnomalyResult`, `roll_anomaly_reward`, `apply_anomaly_reward`, `check_anomaly_reward_on_node_entry`
- `engine/cyberspace_view.py` — `_ANOMALY_GLYPH` + `_ANOMALY_COLOR` constants + `_draw_node()` override + on_node_enter hook
- `engine/state.py` — `AppState.anomaly_triggered: set[str]` field
- `tests/unit/test_variable_reward.py` (NEW) — 22 tests across 5 classes

**Quality gates**:
- ruff: ✅ All checks passed
- mypy: ✅ 0 errors (143 source files)
- pytest: ✅ 3300 passed (22 new), 664 skipped, 0 failed

**Test coverage**:
- `TestNodeAnomalyField`: 5 tests (default false, DATA allowed, non-DATA rejected)
- `TestAnomalyProbability`: 4 tests (constant=0.30, empirical 0.20-0.40, label)
- `TestAnomalyReward`: 7 tests (roll, distribution, apply each kind, missing fields, message)
- `TestAnomalyTriggerOneShot`: 4 tests (non-anomaly, first entry, re-entry, multiple)
- `TestAnomalyIsPillar4Safe`: 2 tests (no meta_state, flat rewards)

### 향후 작업 (v1.1.0 ADR-0140 P2/P3 Deferred)

- **Faction Tension Events** (제안 7): 15-25% mission 에서 faction conflict trigger
- **Auto-Play Tempo Layering** (제안 8): graphic novel pacing variations
- **Near-Miss Extraction** (제안 3): 80%+ HP jack-out bonus
- **Death Replay** (제안 5): Hall of Dead echo
- **Grade 6 Master Whisper** (제안 4): master tier voice differentiation
- **Tier scaling** for anomaly rewards (grade 5+ = bigger bonuses)

### Cross-Reference

- `decisions/0140-engagement-layer.md` — proposal status (Phase 1+2 done, Phase 3 deferred)
- `decisions/0060-project-improvement-plans.md` — workspace-level improvement tracker
- `IMPROVEMENTS.md` — historical 2026-07-01 cycle (Phase 5→6)
- `log.md` — 2026-08-03 entry for this commit cycle

---

## Near-Miss Extraction (ADR-0140 §Proposal 3)

### 골재

Player 가 exit node 도달 시 HP 가 threshold (default 80%) 이상으로 남아있으면, bonus reward.
**Death-avoidance payoff** — careful play 가 보상받음.

### 게임 디자인

- **Threshold**: 80% HP (default, configurable via `DEFAULT_NEAR_MISS_HP_THRESHOLD`)
- **Trigger**: player enters an EXIT node (`NodeKind.EXIT`)
- **One-shot per run**: `state.near_miss_triggered: bool` flag
- **Reward**:
  - +75 credits (in-run currency)
  - +1 salvage fragment (in-run crafting material)

### Pillar 정합 검증

- **Pillar 1 (The Run)**: one-shot per run, 새 런 = 새 기회.
- **Pillar 3 (The Flatline)**: HP > 80% 를 유지하는 것이 death avoidance 와 직접 연결.
- **Pillar 4 (The Build)**: rewards 는 in-run, no cross-run inheritance.
- **Pillar 5 (The Style)**: 깁슨 코퍼스 — "good contractor walks away with the prize" 톤.

### 흐름

```
[Player navigates matrix with arrow keys]
    |
    v
[Player enters EXIT node]
    |
    v
[best_neighbor.kind == NodeKind.EXIT]
    |
    v
[check_near_miss_extraction()]
    |
    +-- if state.player_hp / state.player_max_hp >= 0.80 AND not already_triggered:
    |   +-- apply +75 credits + +1 salvage fragment
    |   +-- append status message: ">>> Near-miss extraction (80% HP): ..."
    |   +-- set state.near_miss_triggered = True
    |
    +-- else: no-op
```

### 구현 노트

**파일**:
- `matrix/near_miss.py` (NEW) — `NearMissRewardKind`, `NearMissReward`, `NearMissResult`,
  `compute_hp_ratio`, `check_near_miss_extraction`
- `engine/cyberspace_view.py` — `check_near_miss_extraction` hook on EXIT node entry
- `engine/state.py` — `AppState.near_miss_triggered: bool = False` field
- `tests/unit/test_near_miss.py` (NEW) — 24 tests across 6 classes

**Quality gates**:
- ruff: ✅ All checks passed
- mypy: ✅ 0 errors (144 source files)
- pytest: ✅ 3324 passed (24 new), 664 skipped, 0 failed

**Test coverage**:
- `TestComputeHpRatio` (6): clamping, edge cases (zero max_hp, overheal, negative HP)
- `TestNearMissThreshold` (5): 80% boundary, custom threshold, full HP, zero HP
- `TestNearMissRewards` (5): credits, salvage, missing fields, status message
- `TestNearMissOneShot` (2): no double-reward, single status message
- `TestNearMissIsPillar4Safe` (2): no meta_state write, death-reset behavior
- `TestNearMissRewardIntegrity` (3): positive amounts, flat rewards

### 향후 작업 (v1.1.0 ADR-0140 P2/P3 Deferred)

- **Faction Tension Events** (제안 7): 15-25% mission 에서 faction conflict trigger
- **Auto-Play Tempo Layering** (제안 8): graphic novel pacing variations
- **Death Replay** (제안 5): Hall of Dead echo
- **Tier scaling** for anomaly + near-miss rewards (grade 5+ = bigger bonuses)

### Cross-Reference (Near-Miss)

- `decisions/0140-engagement-layer.md` — proposal status
- `prototype/src/roguelike_sprawl/engine/state.py` — `AppState.near_miss_triggered`
- `prototype/src/roguelike_sprawl/engine/cyberspace_view.py` — EXIT node hook
- `prototype/src/roguelike_sprawl/matrix/near_miss.py` — implementation
