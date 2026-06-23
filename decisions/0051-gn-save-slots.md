# ADR-0051: GN Save Slot 확장 (3 슬롯)

**상태**: Draft
**날짜**: 2026-06-21
**결정자**: 사용자
**우선순위**: P2

## 컨텍스트 (Context)

현재 GN save 시스템은 **단일 슬롯** (`data/saves/gn_progress.json`):
- 한 번 저장 = 이전 저장 덮어쓰기
- 여러 캐릭터/엔딩 시도 시 비교 불가
- "다른 결말 보기 위해 시도하다가 기존 진행도 잃음" 문제

GN은 자동 플레이 (자동 진행) 이므로 사용자가 여러 결말을 시도해볼 여지가 큼.
**3 슬롯 = (A/B/C) × (3 chars) = 9 결말 조합 시도** 의 자연스러운 인프라.

## 고려한 옵션

### Option 1: 3 슬롯 (고정) ✓ 선택

- **설명**: `slot_1.json`, `slot_2.json`, `slot_3.json` (3개 고정).
- **장점**:
  - 단순, 빠른 구현
  - 3 chars × 3 endings = 9 매칭 가능
- **단점**: 슬롯 추가 시 코드 변경.

### Option 2: 동적 슬롯 (N개)

- **설명**: 사용자가 슬롯 추가/삭제.
- **장점**: 무한 확장.
- **단점**:
  - UI 복잡 (생성/삭제 메뉴)
  - 인덱스 관리 어려움
  - 게임 끝까지 9개면 충분

### Option 3: 단일 슬롯 + 세이브 이름

- **설명**: 사용자가 슬롯에 이름 부여 (예: "case-ending-A-final").
- **장점**: 자유도.
- **단점**:
  - 입력 받는 UI 필요
  - 한글 입력 = 복잡

## 추천 (Recommendation)

**Option 1**. 3 슬롯 충분, 단순, 빠른 구현.

## 사용자 결정 (Decision)

[x] Option 1 (사용자 선택 "Save slot 확장")

## 결과 (Consequences)

### Save 파일 구조

- `data/saves/gn_progress_slot_1.json` (기본, ADR-0044 마이그레이션)
- `data/saves/gn_progress_slot_2.json`
- `data/saves/gn_progress_slot_3.json`

### 신규 API (graphic_novel_save.py)

- `GN_SAVE_SLOTS = 3` 상수
- `slot_path(slot_id: int) -> Path` — 슬롯 → 경로
- `save_gn_progress_slot(progress, slot_id) -> Path`
- `load_gn_progress_slot(slot_id) -> GNProgress`
- `delete_gn_progress_slot(slot_id) -> bool`
- `list_save_slots() -> list[tuple[int, GNProgress | None, str]]` — `(slot_id, progress_or_none, mtime_str)`
- `has_gn_save_slot(slot_id) -> bool`

### Backward Compatibility

- 기존 `data/saves/gn_progress.json` (단일 슬롯, ADR-0044 era)
- 첫 실행 시 자동 migration:
  - `gn_progress.json` → `gn_progress_slot_1.json`로 rename
  - 원본 삭제 (또는 보존)
- 이후 모든 새 save는 슬롯 기반

### 신규 Screen + State

- `ScreenKind.SAVE_SLOT_SELECT` — 슬롯 선택 화면
- `AppState.gn_save_slot_selected: int = 0` (1-3)
- 입력 핸들러: N1/N2/N3 → 슬롯 1/2/3, ESC → 이전 메뉴

### Render

- 3 슬롯 카드 형식:
  ```
  ┌─ SLOT 1 ─────────────────┐  ┌─ SLOT 2 ─────────────────┐
  │ CHARACTER:  novice       │  │ EMPTY                     │
  │ ENDING:     B            │  │                           │
  │ SCENE:      5/8          │  │                           │
  │ SAVED:      2026-06-21   │  │                           │
  │ [Space] load  [Del] del  │  │ [Space] start new         │
  └──────────────────────────┘  └──────────────────────────┘
  ```
- 빈 슬롯: "EMPTY — press to start new save"
- 사용된 슬롯: 메타데이터 + DEL 키로 삭제

### 영향 받는 항목

- `decisions/0044-graphic-novel-save.md` — 다중 슬롯 추가
- `design/scenario/graphic-novel.md` — 슬롯 UI 명세
- `tests/unit/test_graphic_novel_save.py` — 슬롯 API + 마이그레이션
- 신규: `tests/unit/test_save_slots.py`

### Scripts

- `scripts/save_slot_demo.py` — 3 슬롯 시각 데모 (fill / list / switch / delete)

## 신규 테스트

- `tests/unit/test_save_slots.py` (~30 tests):
  - `slot_path(1/2/3)` 정확한 경로
  - `save_gn_progress_slot` / `load_gn_progress_slot` round-trip
  - `has_gn_save_slot` (empty / filled)
  - `delete_gn_progress_slot`
  - `list_save_slots()` returns 3 entries (some empty, some filled)
  - Backward compat: `gn_progress.json` → `gn_progress_slot_1.json` migration
  - ScreenKind.SAVE_SLOT_SELECT exists
  - Slot rendering shows metadata

## 변경 이력

- 2026-06-21: Draft 작성