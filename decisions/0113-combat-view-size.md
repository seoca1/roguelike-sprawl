# ADR-0113: combat_view.py (1,053 LOC) — 전투 화면 렌더링

**상태**: Draft
**날짜**: 2026-07-12
**결정자**: 사용자
**우선순위**: P3 (The Build)
**관련**: ADR-0110 (모듈 사이즈 정책), ADR-0003 (전투 시스템)

## 컨텍스트 (Context)

`prototype/src/roguelike_sprawl/engine/combat_view.py` (1,053 LOC) — 전투 화면 렌더링 + 입력 핸들러:

**현황**:
- 24 functions, 0 classes, 18 imports
- docstring 2/24 (92% 누락)
- python-tcod 의존성 큼 (combat rendering wrapper)
- 최다 import (18) — 다른 모듈와의 결합도 가장 높음

**주요 기능**:
- 전투 HUD 렌더 (체력/페이즈/콤보)
- 입력 핸들러 (공격/방어/스킬 선택)
- 이펙트 트리거 (combat/effects.py 호출)
- VFX 통합 (5-Layer)
- 메뉴 / 액션 처리

**의존성** (18 import):
- `combat/state.py`, `combat/effects.py`, `combat/combo.py`
- `engine/` 다수 모듈
- python-tcod

## 고려한 옵션

### Option 1: 정당화 (Keep) — combat_view 단일 책임

- **설명**: combat 화면 렌더링 + 입력 + 이펙트 트리거 + 메뉴가 본질적으로 한 곳. tcod wrapper.
- **장점**:
  - 즉시 작업 0
  - 18 import 가 한 곳에 = 다른 모듈 변경 시 추적 용이
- **단점**:
  - docstring 92% 누락
  - import 의존성 그래프가 가장 복잡

### Option 2: 2-way — render / input

- **설명**:
  - `combat_view_render.py` (~600) — 화면 + 이펙트 호출
  - `combat_view_input.py` (~450) — 입력 + 메뉴 + 액션
- **장점**:
  - 정책 충족
  - 책임 분리 (render vs input)
- **단점**:
  - render/input 사이 의존성 — 키 → 액션 → 이펙트 → 화면 업데이트 흐름

### Option 3: 3-way — render / input / hud

- **설명**:
  - `combat_view_render.py` (~400)
  - `combat_view_input.py` (~350)
  - `combat_view_hud.py` (~300) — 체력/콤보/페이즈 표시
- **장점**:
  - 더 깔끔한 분리
- **단점**:
  - 3-way 분할 작업 ~3-4 시간

### Option 4: Keep + docstring 보강

- **설명**: 분할 없이 docstring 만 추가
- **장점**:
  - 정책 회피 (ADR-0113 정당화)
  - 작업 부담 낮음 (~2-3 시간)
- **단점**:
  - 사이즈 정책 미충족

## 추천 (Recommendation)

**Option 2** (render/input 2-way) — combat 화면의 입출력 분리는 자연스러움.

또는 **Option 4** (Keep + docstring) — 시각 효과 + HUD + 입력이 한 곳에 있는 편이 게임 일관성 유지에 유리할 수 있음.

## 사용자 결정 (Decision)

[ ] Option 1 (정당화 Keep)
[ ] Option 2 (2-way render/input 분할)
[ ] Option 3 (3-way render/input/hud 분할)
[ ] Option 4 (Keep + docstring)
[ ] 기타: ___
[ ] Defer (다음 단계로 미룸)

## 결과 (Consequences)

(결정 후 작성)

## 영향 받는 항목

- `engine/combat_view.py` (1,053 LOC)
- `engine/app.py` (845 LOC) — combat 호출 라우팅
- `engine/dungeon_view.py` — combat 연동
- `combat/state.py`, `combat/effects.py`, `combat/combo.py`
- 영향 테스트: `tests/unit/test_combat.py` + `test_dungeon_view.py`

## 관련 결정

- ADR-0003 (전투 시스템)
- ADR-0110 (모듈 사이즈 정책)

## 변경 이력

- 2026-07-12: Draft 작성 (ADR-0110 후속)
