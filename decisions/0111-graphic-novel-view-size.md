# ADR-0111: graphic_novel_view.py (1,510 LOC) — 정당화 or 분할

**상태**: Draft
**날짜**: 2026-07-12
**결정자**: 사용자
**우선순위**: P3 (The Build)
**관련**: ADR-0110 (모듈 사이즈 정책), ADR-0032 (Graphic Novel Mode)

## 컨텍스트 (Context)

ADR-0110 채택 후, 1000+ LOC 모듈 중 매트릭스 view 가 runtime 미사용인 matrix_view (ADR-0103) 는 보존 결정. 나머지 3 모듈 중 가장 큰 `engine/graphic_novel_view.py` (1,510 LOC) 의 처리:

**현황**:
- 42 functions, 4 classes, 7 imports
- docstring 2/42 (95% 누락) — 가독성 심각
- ADR-0032 / 0041 / 0042 / 0043 / 0044 / 0046 / 0048 / 0049 통합 영향
- 게임 진입점 (메인메뉴 "GRAPHIC NOVEL" 옵션) 의 자동재생 시스템

**인접 의존성**:
- `engine/app.py` — main loop 통합
- `engine/menu.py` — 메인메뉴 진입
- `engine/graphic_novel_audio.py` — 사운드 큐 (별도 모듈, ADR-0043)
- `engine/graphic_novel_save.py` — save/restore (별도 모듈, ADR-0044)
- `data/scenes/{case,sil,kas}/` JSON — 데이터
- `data/art/{portraits,backgrounds}/*.json` — 자산

**현 file 구조 (간략)**:
- `GraphicNovelPlayer` 클래스 (~600 LOC)
  - `play()`, `pause()`, `resume()`, `skip_scene()`, `skip_dialogue()`
  - `_render_frame()`, `_apply_fx()`, `_transition()`
- `Scene` / `Dialogue` / `Ending` 데이터 클래스 (~200 LOC)
- 헬퍼 함수 ~30개 (~700 LOC): 키 입력, 타이밍, transition, save/restore

## 고려한 옵션

### Option 1: 정당화 (Keep) — Split 없이 유지

- **설명**: 본 모듈은 게임플레이적 코히어런스 (씬 진행 + 입력 + 렌더 + transition + sound + save) 가 본질적으로 한 곳에 있어야 자연스러움. 분리 시 import 사이클 + 상태 공유 부담.
- **장점**:
  - 즉시 작업 0, 위험 0
  - 6개 ADR (0032+0041~0044+0046+0048+0049) 가 한 곳에 있다는 점은 코드 추적에 유리
- **단점**:
  - docstring 95% 누락인 채로 유지
  - 향후 확장 시 모듈 import 부담
- **Pillar 정합**:
  - P4 (The Build): 가독성 ↓

### Option 2: 분할 (3-way: view / input / state)

- **설명**: 단일 클래스를 3 모듈로:
  - `graphic_novel_view.py` (render + transition) ~500 LOC
  - `graphic_novel_input.py` (key bindings) ~300 LOC
  - `graphic_novel_state.py` (scene progression + save/restore) ~700 LOC
- **장점**:
  - 사이즈 정책 충족 (모두 700 미만)
  - 책임 분리
- **단점**:
  - 6개 ADR 영향 — 통합 테스트 회귀 위험
  - import 사이클 가능성
  - 분할 작업 ~2-4 시간

### Option 3: 분할 (5-way) — 더 세분화

- **설명**:
  - `view/render.py` — 화면 렌더 (~400)
  - `view/transition.py` — fade/flash (~150)
  - `view/input.py` — 키 (~200)
  - `view/save.py` — save/restore (~250)
  - `view/scene.py` — 진행 (~500)
- **장점**:
  - 더 깔끔한 분리
- **단점**:
  - 분할 작업 ~4-6 시간, 테스트 회귀 위험 큼
  - import 그래프 복잡화

### Option 4: Action — docstring 보강만 (Keep + Doc)

- **설명**: 분할하지 않고 docstring 만 채우기 (90%+ 누락 해소)
- **장점**:
  - 사이즈 그대로, 가독성 ↑
  - 작업 부담 낮음 (~2-4 시간)
- **단점**:
  - 사이즈 정책 미충족

## 추천 (Recommendation)

**Option 4** (Keep + docstring 보강) **또는 Option 1** (정당화) — 사용자가 분할을 원하지 않는 경우.

이유:
- 본 모듈은 게임플레이 흐름의 본질적 단일 책임 (씬 진행 + 표시 + 입력 + save)
- 6 ADR 의 통합 테스트가 이미 있음 (분할 시 모든 테스트 재실행 + 회귀 추적 부담)
- docstring 보강만으로 가독성 문제 해소 가능

사용자가 코드 클린업 우선순위라면 Option 4. 도메인 분리 가치 있다면 Option 2 또는 3.

## 사용자 결정 (Decision)

[ ] Option 1 (정당화 Keep)
[ ] Option 2 (3-way 분할)
[ ] Option 3 (5-way 분할)
[ ] Option 4 (Keep + docstring 보강)
[ ] 기타: ___
[ ] Defer (다음 단계로 미룸)

## 결과 (Consequences)

(결정 후 작성)

## 영향 받는 항목

- `prototype/src/roguelike_sprawl/engine/graphic_novel_view.py` (1,510 LOC)
- 영향 테스트: `tests/unit/test_graphic_novel_view.py` (8 files, 40+ tests)
- 영향 ADR: 0032 / 0041 / 0042 / 0043 / 0044 / 0046 / 0048 / 0049 (8건)

## 관련 결정

- ADR-0032 (Graphic Novel Mode Accepted 2026-06-20)
- ADR-0110 (모듈 사이즈 정책 Accepted 2026-07-12)

## 변경 이력

- 2026-07-12: Draft 작성 (ADR-0110 후속)
