# ADR-0112: combat/effects.py (1,246 LOC) — 5-Layer VFX 시스템

**상태**: Draft
**날짜**: 2026-07-12
**결정자**: 사용자
**우선순위**: P3 (The Build)
**관련**: ADR-0110 (모듈 사이즈 정책), ADR-0018 (Combat Animation 5-Layer VFX)

## 컨텍스트 (Context)

`prototype/src/roguelike_sprawl/combat/effects.py` (1,246 LOC) 는 전투의 시각 효과 시스템:

**현황**:
- 28 functions, 12 classes, 8 imports
- docstring 2/28 (93% 누락)
- VFX 5-Layer 시스템: particles / shake / flash / transitions / cinematic
- 12 신규 spawn 함수 (Phase 1.5: spawn_jackin_glitch, spawn_room_flash 등)

**의존성**:
- `combat/state.py` (6 LOC) — 전투 상태
- `engine/combat_view.py` (1,053 LOC) — combat_view 호출
- `engine/dungeon_view.py` (678 LOC) — dungeon_view spawn
- python-tcod 컬러 처리

**Layer 구조**:
- Layer 1: base particle (small dots, lines)
- Layer 2: shake effect (screen offset)
- Layer 3: flash overlay (color flood)
- Layer 4: transitions (fade, wipe)
- Layer 5: cinematic (multi-phase scripted)

## 고려한 옵션

### Option 1: 정당화 (Keep) — VFX 시스템 단일 책임

- **설명**: 5-Layer 가 본질적으로 한 시스템. 분리 시 레이어 간 타이밍 동기화 부담.
- **장점**:
  - 즉시 작업 0, 위험 0
  - 12 spawn 함수와 12 helper 가 한 곳에 (참조 추적 용이)
- **단점**:
  - docstring 93% 누락 유지
  - 사이즈 정책 미충족

### Option 2: Layer 5-way 분할

- **설명**:
  - `effects/particles.py` (Layer 1) — particle drawing (~250)
  - `effects/shake.py` (Layer 2) — screen shake (~150)
  - `effects/flash.py` (Layer 3) — color overlay (~100)
  - `effects/transition.py` (Layer 4) — fade/wipe (~200)
  - `effects/cinematic.py` (Layer 5) — multi-phase (~250)
  - `effects/spawners.py` — 12 spawn 함수 (~300)
  - 합계: ~1,250
- **장점**:
  - Layer 구조 명확화
  - 1000+ 정책 충족
- **단점**:
  - Layer 간 의존성 (timing sync) — import 복잡
  - 분할 작업 ~3-5 시간

### Option 3: 2-way 분할 — spawners / renderers

- **설명**:
  - `effects/spawners.py` — spawn_* 12 함수 + 데이터 (~600)
  - `effects/renderers.py` — 레이어별 렌더링 (~600)
- **장점**:
  - 2-way 단순, 정책 충족
  - spawner 와 renderer 책임 분리
- **단점**:
  - Layer 간 의존성 여전히

### Option 4: Keep + docstring 보강

- **설명**: 분할 없이 docstring 만 추가 (12 spawn + 28 helper 설명)
- **장점**:
  - 정책 회피 (ADR-0112 정당화 섹션으로)
  - 작업 부담 낮음 (~2-3 시간)
- **단점**:
  - 사이즈 그대로

## 추천 (Recommendation)

**Option 2** (Layer 5-way) — Layer 구조가 이미 자명, 분할의 의의 명확.

또는 **Option 1** (정당화) — Layer 간 타이밍 동기화가 시각 효과의 본질.

Option 4 는 작업 부담 낮지만 사이즈 정책 미충족.

## 사용자 결정 (Decision)

[ ] Option 1 (정당화 Keep)
[ ] Option 2 (5-way Layer 분할)
[ ] Option 3 (2-way spawner/renderer 분할)
[ ] Option 4 (Keep + docstring)
[ ] 기타: ___
[ ] Defer (다음 단계로 미룸)

## 결과 (Consequences)

(결정 후 작성)

## 영향 받는 항목

- `combat/effects.py` (1,246 LOC)
- `combat/state.py` (6 LOC) — 분할 시 import 업데이트
- `engine/combat_view.py` — spawner 호출 경로
- `engine/dungeon_view.py` — spawner 호출 경로
- 영향 테스트: `tests/unit/test_combat_vfx.py` (12+ tests), `test_combat_effects_demo.py`

## 관련 결정

- ADR-0018 (Combat Animation 5-Layer VFX) — 본 모듈 기반
- ADR-0110 (모듈 사이즈 정책)

## 변경 이력

- 2026-07-12: Draft 작성 (ADR-0110 후속)
