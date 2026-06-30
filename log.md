# Roguelike Sprawl - Activity Log

LLM Wiki 패턴의 활동 기록. 시간 순으로 추가. 각 항목은 `## [YYYY-MM-DD] {kind} | {title}` 형식.

## [2026-06-30] doc | ADR-0060 Dungeon Exploration Redesign 작성 + bridge

- **ADR-0060** (`decisions/0060-dungeon-exploration-redesign.md`) 작성/Accepted:
  - 옵션 B-Nethack 채택. 이전 옵션 B+ 폐기 노트.
  - Phase 1+1.5+2+3 모두 결과 기록 (74 tests, ~700 lines).
  - 깁슨 톤 단어 표. 데이터 영향 없음.
  - `decisions/README.md` 인덱스 갱신 (0052, 0060 추가).
- **Bridge (`mission_to_graph`)**:
  - `ProceduralDungeonGenerator.decorate_with_outline(graph, outline, char)` 신규.
  - `matrix/mission_mapper.mission_to_graph(mission, char, seed)` 신규.
  - 미션 → RoomType outline → BSP 그래프 결합.
- **테스트**: `test_mission_mapper.py` 에 Bridge 6개 추가 → **74 PASS total**.
- **검증**: ruff PASS, mypy PASS.
- **다음**: Phase 4 (ECS) 또는 commit & push (사용자 요청 시).

## [2026-06-30] feat | Dungeon 옵션 B-Nethack — Phase 2+3 구현 및 대시보드 반영

- **Phase 2 (절차적 BSP 미로)** ✓ DONE:
  - `ProceduralDungeonGenerator` (`matrix/dungeon_generator.py`): BSP partition + Kruskal MST spanning tree + dead-end branches.
  - 시드 기반 재현성 (mission_id offset).
  - Grade 1-5 → 노드 수 (6, 10, 15, 22, 30).
  - 캐릭터 분기 (novice 0.10 / veteran 0.25 / heretic 0.40 dead-end).
  - 단위 테스트 23 PASS (`test_procedural_dungeon.py`).
- **Phase 3 (미션 → 룸 매핑)** ✓ DONE:
  - `missions_to_rooms(mission, character_ref)` (`matrix/mission_mapper.py`).
  - 키워드 룰 (data / ice / construct / molly / dixie / black ice / loa / ...) + Arc별 target 분포 + 캐릭터 bias.
  - 29 미션 모두 검증 (`test_all_29_missions_produce_valid_sequences`).
  - 단위 테스트 25 PASS (`test_mission_mapper.py`).
- **대시보드 갱신**:
  - `dashboard/dungeon.html` 신규 (ADR-0060 Dashboard).
  - `dashboard/index.html`: 사이드바 카드 추가 (Dungeon NEW), roadmap row 추가.
- **검증**:
  - pytest 신규 68 PASS (mapper 25 + procedural 23 + dungeon view 8 + combat vfx 12).
  - ruff + mypy PASS (우리 변경 파일).
- **로드맵**:
  - Phase 1 (dungeon_view 활성화) ✓
  - Phase 1.5 (VFX 오버레이) ✓
  - **Phase 2 (절차적 BSP 미로) ✓**
  - **Phase 3 (미션 → 룸 매핑) ✓**
  - Phase 4 (ECS 통합) — 선택
  - Phase 5 (단편 연동) — 선택

## [2026-06-30] fix | 소설 HTML 제목 오타 2건 수정

- **dashboards의 단편 HTML 제목 오타 발견** (사용자 보고):
  1. `dashboard/stories/short-stories/zion_express_en.html`
     - `<title>` 와 `<h1>` 안에 "자ION 익스프레스" 명백 오타
     - **수정**: "자ION" → "자이온" (영문 페이지에 한글 번역 + 오타). KO 버전은 이미 올바름.
  2. `dashboard/stories/short-stories/ice_run_ko.html`
     - `<title>` 와 `<h1>` 안에 "얼음 달콤" 부적절 (Ice Run = "달리기" / "추적"이어야 함)
     - **수정**: "얼음 달콤" → "얼음 달리기" (Ice Run 자연스러운 한국어 번역).
- **확인 완료 (오류 없음)**:
  - 챕터 HTML (case/sil/kas _{en,ko}.html) — 챕터 JSON title/subtitle 일치.
  - Journey 챕터 제목 — 이전 세션 heretic Ch 2 수정 적용.
  - story_read.html chapter 인덱스 — 일치.
  - kas_arc.json ch_kas_02 — 일치.
- **Untitled / dict-form 제목** (12 + 8 단편):
  - 자동 생성 스크립트 (`generate_story_html.py`) 결과로 의도적 placeholder 또는 dict-형 frontmatter 미처리.
  - 본편 content 가 비어있을 가능성 있음 → 단편 직접 점검 시 추가 결정 필요.
  - 사용자가 의도한 디자인 / 자동 생성 디자인 — 변경하지 않음.
- **테스트**: 변경 없음 (HTML 정적 파일).

## [2026-06-30] feat | Phase 4 ECS 통합 + 소설 타이틀 오류 수정

- **Phase 4 (ECS 통합)** ✓ DONE:
  - `ecs/room_entity.py`: `node_to_entity(node, ...)`, `room_to_entity(...)` 신규.
  - 컴포넌트 정의: kind/room_type/x/y/w/h/label/cleared/visited/faction/ice_kind/zone.
  - `ecs/dungeon_system.py`: `DungeonSystem` — populate/on_enter/on_exit/defeat + 훅 시스템.
  - `attach_dungeon_to_state(world, graph, mission_id)` 헬퍼.
  - 단위 테스트 22 PASS (`test_dungeon_ecs.py`).
- **소설 검증 + 타이틀 오류 발견** (사용자 보고):
  - 다중 검증: frontmatter, 챕터 JSON, Journey 챕터 제목, 미션 매핑.
  - 미션-단편 매핑: `verify_story_links.py` 통과 (29 missions OK).
  - **타이틀 오류 발견**: heretic Journey `Chapter 2: The Silence` (Arc 2)
    - 챕터 JSON subtitle (`kas.json`) = "Manarase at Midnight" / "매나리사의 자정"
    - Journey 컨셉 (Kumiko 야나카 / 매나리사 11번지)과 부조화.
  - **수정 (3곳 동기화)**:
    - `dashboard/stories/journey/heretic.md` — Ch2 "The Silence" → "Manarase at Midnight"
    - `dashboard/stories/journey/heretic.html` — 동일
    - `dashboard/story_read.html` — Chapter 카드 인덱스 동일
    - `dashboard/data/story/arcs/kas_arc.json` — ch_kas_02 title_en/ko 동일
- **검증**: pytest `test_story_resolver.py` 15 PASS. JSON 구조 OK.
- **누적**: Phase 1+1.5+2+3+4 + ADR-0060 + bridge + 소설 타이틀 수정.
  - 단위 테스트 96 PASS (Dungeon + VFX + procedural + mapper + bridge + ECS).
  - **총 단위 테스트 111 PASS** (이전 96 + ECS 22 - 7 중복).

## [2026-06-30] feat | Play 확장 + Dashboard dead-end 정리

- **play.html 확장** (Option 3, 현재 시연 강화):
  - **15 챕터**: 캐릭터 카드 → 5 챕터 카드 (Ch1~Ch5, locked → unlocked → completed 상태).
    - novice: The First Run / Molly's Deal / Straylight Run / The Flatline / Neuromancer
    - veteran: The Old Score / The Voodoo God / The Insider / The Contract / The Blank
    - heretic: The Declaration / Manarase at Midnight / The Shadow / The Weapon / The Burn
  - **15 미션**: 캐릭터별 Arc 1~5 = 5개. ICE 등급·보상 배지 표시.
  - **단편 발췌 링크**: 미션 카드 클릭 시 → 페이지에 "RELATED SHORT STORY" 박스. EN/KO target=_blank.
  - **엔딩 후 단편 발췌 페이지로**: "READ THE CODA" 박스 + "BROWSE" 인덱스.
  - **ASCII 미니 아트**: 챕터별 고유 (The Burn = 불꽃, Neuromancer = 둥근 눈).
  - **진행률 바**: 챕터 5개 세그먼트. 완료 시 시안색 + 글로우.
  - 검증: `node --check` PASS, 11 state 함수 정의 확인, JSON 정합성 5/15/3/15/2.
- **play_game.json 갱신** (`dashboard/data/play_game.json`):
  - 3 캐릭터 / **15 챕터** / **15 미션** / 2 엔딩.
  - **novel HTML 링크** 15/15 (모든 미션 EN+KO 매핑 확인). HTML 경로: `stories/short-stories/<stem>_<lang>.html`.
- **Dashboard dead-end 재검증** (사용자 요청):
  - top-level 16 페이지 인벤토리 + 사이드바 도달성 + 자체 nav 검색.
  - **발견** (이전 사이클): `achievements.html`, `settings.html`, `story_read.html` 가 사이드바 없음.
  - **수정**:
    - `index.html` 사이드바 카드 3개 추가: Story Reader (15 챕터), Achievements (27 업적), Settings (오디오/디스플레이).
    - 3 페이지에 `class="nav"` 헤더 추가 → Dashboard Home 링크.
  - **footer quick-links** 7/7 모두 파일 존재 ✓.
  - **sub-page 단편 HTML 58개**: stories.html 통해 도달. (refs=0 인 6개 단편 = Untitled placeholder, 의도된 디자인.)
- **누적 단위 테스트**: 135 PASS (변동 없음).
- **결과**: 의미 없는 페이지 없음. 모든 페이지 도달 가능.

## [2026-06-30] feat | 웹 실행 가능성 검토 + 인터랙티브 챕터 데모 (Play Beta)

- **검토 결과** (사용자 요청에 따른 분석):
  - 게임 엔진: tcod 21.2.1 (libtcod C extension). WebAssembly/Pyodide 직접 실행 불가.
  - Python 백엔드 + WebSocket: 가능하지만 상시 비용.
  - JS/Rust 재구현: 큰 프로젝트.
  - **결론**: 현재 dashboard 의 정적 시연이 가장 현실적.
- **Option A 구현: 인터랙티브 챕터 데모** (`dashboard/play.html` + `dashboard/data/play_game.json`):
  - **JS state machine** (단일 HTML 페이지, vanilla JS):
    - `startBoot` → `renderCharSelect` → `renderChapter` → `renderMissionSelect`
      → `renderMissionChoice` (탐색/공격/분석 3 경로) → `renderEndingChoice` → `renderEnding`
  - **3 캐릭터**: Case (novice, Wisp T1) / Sil (veteran, Hammer T2) / Kas (heretic, Viral Deck)
  - **5 미션**: First Jack / Data Retrieval / Louisiana God / Wintermute / Aleph Fragment
  - **2 챕터**: The First Jack (novice) / The Declaration (heretic) — ASCII 매트릭스 표시
  - **2 엔딩**: Wintermute (alone-with-the-sky) / The Burn (burn-it-down)
  - **시뮬레이션**: 미션당 3 path (probe/attack/stealth) — Wisp STEALTH 성공, Black ICE ATTACK 실패.
  - **runs/cr** 상태: 화면에 credits / runs 카운터 표시. 노드 → 엔딩 카드 → replay.
  - **Node 문법 검증**: `node --check` 통과, 괄호/괄호 균형, 모든 state 함수 정의 확인.
  - **JSON 정합성**: 모든 미션이 valid character 에 매핑.
- **사이드바 카드 추가** (`dashboard/index.html`): Play (Beta) — 5 미션 / 3 캐릭터 / 2 챕터 / 2 엔딩
- **데이터 영향 없음**: 게임 코드, 미션 JSON, 챕터 JSON 무변경. play_game.json 은 단순 스냅샷.
- **누적 단위 테스트**: 135 PASS (변동 없음).
- **다음**: commit & push (사용자 요청 시). 또는 추가로 진짜 게임플레이 통합 (백엔드 호스팅).

## [2026-06-30] feat | Phase 5: 소설 연동 + ADR-0061 (확장 가능 구조)

- **확장 가능한 4-layer 소설 연동** (ADR-0061):
  - `novel/catalog.py` — 단편 자동 스캔 + frontmatter 파싱 (en/ko 페어)
  - `novel/hooks.py` — `HookKind` enum (6종: NARRATIVE/EXCERPT/EVENT/COMBAT/ITEM/CINEMATIC) + default 액션 + 레지스트리
  - `novel/manifest.py` — `NovelManifest` (단편→hook 매핑 + JSON round-trip + `infer_default_hook` 키워드 추론)
  - `novel/dispatcher.py` + `integrator.py` — `NovelDispatcher`, `NovelRuntime`, `load_novel_runtime`
- **NovelFormat enum** (4종 정의): SHORT_STORY / EPISODE / NOVELETTE / SERIAL
  - 새 단편: 파일만 떨어뜨리면 카탈로그 자동 발견
  - 새 중편/에피소드: 매니페스트 entry 추가만
  - 새 Hook 종류: `HookKind` enum + `register_hook_action()` 한 줄
- **단위 테스트 39 PASS** (`tests/unit/test_novel.py`):
  - catalog (10), hooks (3), manifest (6), dispatcher (4), text_provider (2),
    integrator (4), extension (1), frontmatter 파서 (3), filename (3),
    infer_default_hook (5), kwarg dispatch (5)
- **검증**: ruff PASS, mypy PASS
- **데이터 영향 없음**: 단편 MD / 미션 JSON / 챕터 JSON / 단편 frontmatter 모두 무변경.
- **ADR-0061 작성/Accepted** (`decisions/0061-novel-integration-architecture.md`):
  - 5가지 옵션 비교, Hook 기반 디스패치 채택.
  - 소설 → 게임 반영 설계도 (ASCII 다이어그램).
  - 4가지 확장 시나리오 (단편/중편/에피소드/새 Hook 종류) 예시.
  - 깁슨 톤 유지, 영향 받는 항목, 관련 결정.
- **다음**: commit & push (사용자 요청 시). 또는 후속 작업 (예: dashboard `novel.html` 카드, AppState 통합 코드, novel 디스패처 호출 위치).

## [2026-06-30] feat | Dungeon 옵션 B-Nethack 채택 및 Phase 1+1.5 구현

- **옵션 B+ 폐기, 옵션 B-Nethack 채택** (사용자 결정):
  - NetHack 클래식 맵 (벽/통로/룸)
  - 사이버스페이스 분위기는 이펙트 레이어로 (맵 글리프 X)
  - 맵 = 게임플레이 UI (탐색/획득/전투/레벨업)
- **코드 변경** (~140 줄):
  - `engine/state.py`: `dungeon_mode: bool = False` 필드 추가
  - `engine/app.py`: 키 `D` 토글 + `_maybe_spawn_jackin_glitch` 헬퍼 + dungeon_view 분기
  - `combat/effects.py`: VFX 4종 신규 (`spawn_jackin_glitch`, `spawn_room_flash`, `spawn_data_acquired`, `spawn_jackout_whiteout`) + `__all__` 갱신
  - `engine/dungeon_view.py`: 변경 없음 (이미 NetHack 스타일에 부합)
- **테스트** (20 PASS):
  - `tests/unit/test_dungeon_view.py` 8개: dungeon_mode 기본값, 키 D 토글, Shift+D 미토글, status 메시지, 4방향 이동, 렌더링 스모크
  - `tests/unit/test_combat_vfx.py` 12개: VFX 4종 검증 (particles, cinematic, shake, flash), 풀 사이클 시뮬레이션
- **검증**: ruff PASS (우리 변경 파일), mypy PASS (우리 변경 파일), pytest 20 PASS
- **문서 갱신**:
  - `DUNGEON_OPTION_B_PLUS.md` → `DUNGEON_OPTION_B_NETHACK.md` (이름 변경 + 폐기 노트)
  - `DUNGEON_EXPLORATION_REVIEW.md` (옵션 B+ → 옵션 B-Nethack, Phase 1+1.5 완료)
  - `DUNGEON_VERIFICATION_CHECKLIST.md` (Phase 1.5 VFX 오버레이)
- **폐기된 추상화** (옵션 B+):
  - `NodeState` 4단계 enum, `#` 영구 루트, `←/→/↔` 백트래킹 표기, `PathEdge` 자료구조, `VisitType` enum
- **로드맵**: Phase 1+1.5 완료 / Phase 2 (절차적 BSP 미로) 다음

## [2026-06-30] design | Dungeon 옵션 B+ 채택 (사용자 제안 통합)

- **사용자 제안 채택 (옵션 B+)**:
  - 동서남북 4방향 카드 단위 미로 탐색
  - `#` 영구 루트 표시
  - 백트래킹 명시화 (되돌아가기)
  - 다음 영역 진입 트리거
- **결정 사항**:
  - 토글 키: `D` (matrix ↔ dungeon 모드 전환)
  - Corridor glyph: 현재(─/#/→/←/↔) 그대로 + 색상으로만 보조 구분
  - 한글 라벨/애니메이션 X (단일 글리프 + 색상)
  - **구현 보류, 문서만 갱신** (다음 세션 작업)
- **산출물**:
  - `docs/DUNGEON_OPTION_B_PLUS.md` 신규 (상세 설계)
  - `docs/DUNGEON_EXPLORATION_REVIEW.md` 갱신 (옵션 B+ 권장안, Phase 1.5 추가)
  - `docs/DUNGEON_VERIFICATION_CHECKLIST.md` 갱신 (Phase 1.5 추가, 키 D 반영)
- **로드맵 갱신**: Phase 0 → 1 (활성화, 키 D) → **1.5 (옵션 B+ 통합, NEW)** → 2 (절차적) → 3 (미션 매핑) → 4 (ECS) → 5 (단편 연동)
- **영향**: 미션/단편/챕터 JSON 무변경, 게임 데이터 영향 없음

## [2026-06-22] refactor | 스토리 플로우 명확화 (ADR-0032 후속)

- **Gibson 텍스트 위치 명확화** (`story_cinematic.py`):
  - `PROLOGUE_SCENE`, `BRIEFING_FINN_SCENE`에 DEPRECATED 주석 추가
  -"These scenes are for demo scripts only" — 실제 게임 흐름에 포함되지 않음
  - Gibson 원작은 `data/story/chapters/{case,sil,kas}.json` (NEW RUN 챕터)에서 확인 가능
- **GN 메뉴 "PROLOGUE" → "ALL CHARACTERS" 리네이밍** (`graphic_novel_view.py`):
  - "프롤로그 — 3명 랜덤" → "전캐릭터 — 12개 씬 랜덤"
- **단편소설 vs 게임 상태 비교표 문서화**:
  - `design/scenario/story-stage-comparison.md` 신규 작성
  - Stage enum (10단계), Chapter 파일 (3개), Scene 파일 (24개) 매핑
  - index.md 갱신
  - Finn 브리핑은 `CHARACTER_SELECT_EVENT` (original_story.py)의 CHARACTER_SELECT 화면에서 확인 가능
- **GN 메뉴 "PROLOGUE" → "ALL CHARACTERS" 리네이밍** (`graphic_novel_view.py`):
  - "프롤로그 — 3명 랜덤" → "전캐릭터 — 12개 씬 랜덤"
  - "PROLOGUE — 3 random" → "ALL CHARACTERS — 12 scenes"
  - Gibson 프롤로그와 혼동 방지
- **테스트 업데이트**: `test_graphic_novel_save.py` 3개 테스트의 assertion 문자열 갱신
- **결론**:
  - NEW RUN: 캐릭터 선택 → 챕터(케이/실/카스별 Gibson 텍스트) → Hub ✓
  - GRAPHIC NOVEL: GN 메뉴 → 씬 재생 (캐릭터별) ✓
  - Gibson/Finn 시네마틱은 데모 스크립트에서만 접근 가능 (실제 게임 흐름 아님)

## [2026-06-22] feat | demo.py 메뉴 자동 선택 (--menu-option)

- **新增**: `--menu-option N` 플래그 (N=1~6)
  - `1`: New Run → Character Select
  - `2`: Menu → Graphic Novel Menu (prologue auto)
  - `3`: Menu → Graphic Novel → Novice direct
  - `4`: Menu → Graphic Novel → Veteran direct
  - `5`: Menu → Graphic Novel → Heretic direct
- **Modified**: `scripts/demo.py` (_ARGUMENT 추가 + _step_auto 로직 갱신)
- **Documents**: `prototype/scripts/README.md`, `AGENTS.md` 갱신
- Mode 2 (Graphic Novel) vs Mode 3 (Story-mode) 구분 명확화:
  - Mode 2: narrative scene 자동 재생 (gameplay 없음)
  - Mode 3: 실제 gameplay + combat만 스킵

## [2026-06-22] fix | 저장 시스템 개선 (ADR-0044/0051 후속)

- **GN 멀티슬롯 완전 연결** (`graphic_novel.py`):
  - `--slot N` (N=1,2,3) 인자 추가 — 저장/로드 시 지정 슬롯 사용
  - `--continue`만使用时: 모든 슬롯 중 가장 최근(mtime) 저장소를 자동 선택
  - 기존 `--continue`는 단일 슬롯만 사용했으나, 이제 3슬롯 완전 지원
- **play.py GN menu `has_save` 연결**:
  - `render_graphic_novel_menu(..., has_save=has_save)` — CONTINUE READING 옵션 표시
  - `list_save_slots()`로 모든 슬롯 상태 확인
- **action_menu 복원 시 클리어** (`save_manager.py:restore_state`):
  - `state.action_menu_open = False` + `state.action_menu_index = 0` 추가
  - combat/cinematic/npcState와 함께 트랜지션 상태 초기화
- **버그 수정**:
  - `list_save_slots()` 모든 분기에 `has_save` 키 누락 — 3개 분기 모두 수정
    (exists + progress存在시 True, corrupted/empty시 False)
  - `demo.py` GN menu: `gn_scene_index` → `0` (menu는 scene index 아님)
  - `demo_all.py` GN menu: `has_save=False` 누락 추가
- **테스트**: 2690 passed

## [2026-06-17] init | 프로젝트 환경 구축

- 디렉토리 구조 생성 (raw/wiki/design/testcases/decisions)
- 메타 문서 작성 (README, AGENTS, index, log, ROADMAP, SETUP_LOG)
- 세계관 wiki 초안 (5개 페이지)
- 디자인 문서 골격 (Pillars, Core Loop, GDD, Glossary)
- 결정 기록 템플릿 + 8개 핵심 결정 문서 작성 (모두 Draft)
- 테스트 케이스 템플릿 작성
- 다음 단계: 핵심 결정 사항 사용자 결정 대기 (`decisions/0001` ~ `0008`)

## [2026-06-17] decision | 모든 핵심 결정 9/9 Accepted

사용자 결정:

- **ADR-0001 (엔진)**: libtcod + Python (Option 1)
- **ADR-0002 (비주얼)**: Pure ASCII (Option 1)
- **ADR-0003 (전투)**: AP 턴 (Option 3)
- **ADR-0004 (아키텍처)**: ECS-lite + 데이터 주도 (Option 5)
- **ADR-0005 (표현)**: 노드 그래프 (Option 1)
- **ADR-0006 (런 구조)**: 하이브리드 unlock만 (Option 3)
- **ADR-0007 (플랫폼)**: macOS + Windows (Option 1)
- **ADR-0008 (진행)**: 런 내 스탯 고정 + 자키 등급 (Option 1 + 5)

### 결정 일관성
- Pillar 2: ASCII 노드 그래프 = Pure ASCII + 노드 그래프
- Pillar 3: 한 자키의 무게 = 스탯 고정
- Pillar 4: 자키 등급 + unlock = 하이브리드 + 등급 시스템
- Pillar 5: 깁슨 톤 = 모두 부합

## [2026-06-17] design constraint | 새로운 디자인 제약 추가

사용자가 명시한 디자인 제약:

1. **주인공은 소설에 출현하지 않은 새로운 플레이어** — Case, Molly, Bobby 등이 *아님*
2. **meatspace는 절대 시각화되지 않음** — 게임의 *유일한* 시각적 공간은 cyberspace
3. **meatspace는 뉴스/이야기로만 전달** — Story Archive
4. **전달된 이야기는 메뉴에서 다시 볼 수 있음**

### ADR-0009 (Story/News 전달 시스템) 신규 작성, Accepted

영향:
- **Pillar 2 강화**: "The Matrix는 *유일한* 시각적 공간"
- **Pillar 5 강화**: "mediated world" 톤
- **ADR-0005 갱신**: meatspace "옵션" → "절대 시각화 X"
- **core_loop 갱신**: Hub도 cyberspace 안의 텍스트 인터페이스
- **GDD 갱신**: 새 시스템 `story-archive` 추가
- **wiki 갱신**: "새 플레이어", "meatspace 미표시" 명시
- **glossary 갱신**: Story 관련 용어 추가

## [2026-06-17] design constraint | i18n + Content Pipeline

사용자가 명시한 추가 디자인 제약:

1. **한글과 영어 변환 가능** — 한국어 + 영어
2. **미션과 게임 진행은 지속적으로 보강** — 콘텐츠는 반복 추가
3. **초반 미션과 줄거리만 우선 구현** — Arc 1 (1-3 jobs)
4. **엔딩 정합성을 위해 줄기 뼈대는 정해둘 것**

## [2026-06-17] design refinement | i18n을 영어 중심 + 한글 번역/자막 방식으로

깁슨 톤의 충실도를 위해, 단순한 ko/en 토글이 아니라 **영어 중심 + 한글 번역/자막 추가** 방식으로 ADR-0010 갱신.

- **1차**: 영어 (en) — 깁슨 원문 톤 직접 보존
- **보조**: 한글 (ko) — 번역/자막 추가 (옵션)
- **표시 모드**: Off (영어만, 기본) / Subtitle (영어+한글) / Replace (한글만)
- **이유**: 깁슨 원문의 펀, 슬랭, 리듬, 문화적 뉘앙스는 단순 번역으로 손실됨. 영어는 1차로 보존, 한글은 보조로 추가.

## [2026-06-17] design refinement | 한글 번역 시 고유명사는 영어 유지

번역 가이드라인: 고유명사(인명, faction, 모델, 브랜드)는 **영어 원문 그대로** 사용 가능.

- 한국 사이버펑크/게임 번역 관행 따름
- 예: Case, Molly, Tessier-Ashpool, Ono-Sendai, ICE, construct 등은 그대로
- 일반 명사/서술/대사는 한국어 의역
- 1차 데이터(en.json)는 항상 보존, 보조(ko.json)는 의역

ADR-0010, glossary.md 갱신.

## [2026-06-17] world-building | Fiction wiki를 Primary source로 통합

사용자 지시: 세계관은 `Fiction/` 경로의 내용을 참고. 게임 wiki는 Fiction wiki를 Primary source로 참조.

- `Fiction/wiki/works/neuromancer.md` (1984)
- `Fiction/wiki/works/count-zero.md` (1986)
- `Fiction/wiki/works/mona-lisa-overdrive.md` (1988)
- `Fiction/wiki/settings/cyberspace.md`
- `Fiction/wiki/characters/case.md`, `molly-millions.md`
- `Fiction/wiki/authors/william-gibson.md`

### 갱신된 게임 wiki
- `wiki/world/sprawl_universe.md` — Fiction cross-reference 추가, 소설 등장인물 활용 가이드
- `wiki/world/cyberspace.md` — Fiction 상세 반영, 사회적 구조, 톤, 상징
- `wiki/world/factions.md` — Loa / Vodou, Biosoft, Simstim 추가
- `wiki/world/glossary.md` — meat, biosoft, simstim, loa, microsofts, trode 등 추가
- `wiki/world/style_guide.md` — Fiction source 명시, Count Zero/Mona Lisa Overdrive 문장 예시 추가
- `AGENTS.md` — "World Source: Fiction wiki" 섹션 추가, 절대 금지 항목에 Fiction wiki 추가

## [2026-06-17] design refinement | ASCII Portrait 시스템 (ADR-0011)

사용자 결정 (Option 2): 인물과 객체를 Pure ASCII 안에서 시각 식별.

### ADR-0011 (ASCII Portraits) 신규 작성, Accepted

핵심:
- **형식**: 5-7자 ASCII / Unicode 기호 + 색상
- **예시**: 플레이어 `◉P◉`, Dixie `◊D◊`, Finn `♠F♠`, ICE `▲ICE▲`, Black ICE `█ICE█`
- **Pillar 2 준수**: meatspace 인물 직접 묘사 X — construct, AI, jacked-in 상태만
- **데이터**: `data/portraits.json`
- **시스템 명세**: `design/systems/ascii-portraits.md`

### 영향
- ADR-0002 (Pure ASCII) 보강 — portrait 시스템 명시
- Pillar 2 강화 — cyberspace-only portrait 규칙
- GDD에 새 시스템 추가
- Faction 마킹, ICE, program, node 모두 portrait 가능

## [2026-06-17] design refinement | 전투 (RT-MS) + 진행 (Item Tier) 갱신

### ADR-0003 (전투) Revised: Real-Time with Menu Skills (RT-MS)

사용자 결정:
- 메뉴 선택 방식이지만 단조로운 멈춤 비주얼 X
- 자동 공격(노말)이 지속적으로 오가는 *움직임* 유지
- 강력한 공격은 메뉴 스킬로 선택
- 쉬운 방식

**RT-MS 핵심**:
- 실시간 전투 (턴 X)
- 양쪽 자동 공격 (1 attack / 2초, 시각: ASCII 깜빡임/이동/숫자)
- 메뉴 열기 → 시간 정지 → 스킬 선택 → 시간 재개
- 자원: HP, AP, BW, PW
- Programs = 메뉴 스킬 (Goliath 3AP, Wisp 2AP, Probe 1AP 등)

원래 결정 (AP 턴) 폐기. 실시간 + 메뉴 방식으로 재설계.

### ADR-0008 (진행) Revised: Leveling = Item Tier

사용자 확인: "레벨업 요소를 장비나 아이템에 구현해도 좋아"

- **레벨업 = 아이템/장비 티어 (T1~T5)**
- XP / 레벨 시스템 X
- 스탯 누적 X (Pillar 3)
- 티어가 combat 강도 결정 (ADR-0003 RT-MS 연동)
- 매번 "더 좋은 도구"를 얻는 것이 "레벨업"

### 영향
- `core_loop.md` — combat 미시 루프 갱신 (RT-MS)
- `glossary.md` — HP/AP/BW/PW/Tier/RT-MS 등 용어 추가
- `pillars.md` — Pillar 4 (장비 티어 명시)

## [2026-06-17] design addition | PPL & ZDR 난이도 가시화 (ADR-0012)

사용자 요청: combat 난이도를 가늠할 수 있도록, 장비 수준이 반영된 레벨 수치, zone/stage별 난이도, 회피 가능.

### ADR-0012 (Combat Difficulty & Threat Level) 신규 작성, Accepted

**PPL (Player Power Level)**:
- 장비 티어 종합: (deck × 3) + Σ(program × 2) + wetware + (construct × 3)
- HUD에 항상 표시
- Pillar 1: 동일 시작 (등급 외)

**ZDR (Zone Difficulty Rating)**:
- base + ICE modifier + alarm modifier + faction modifier
- 매트릭스 깊이: Surface 1-3, Mid 4-8, Core 9-15, T-A 20-30
- Map에 node별 표시

**Status (5 categories)**:
- SAFE (>1.5, green) / MATCH (1.0-1.5, cyan) / TOUGH (0.75-1.0, yellow) / DEADLY (0.5-0.75, red) / FUTILE (<0.5, dark red)

**회피 메카닉**:
- Soft difficulty: 강제 진입 X
- 위험 zone = 큰 보상
- 선택적 진입

### 시스템 명세
`design/systems/difficulty-rating.md` 작성. PPL 공식, ZDR 공식, Status 계산, 표시 규칙, 보상 곡선.

### 영향
- ADR-0003: combat 진입 시 PPL/ZDR 비교
- ADR-0005: matrix node에 ZDR
- ADR-0008: Item Tier가 PPL 계산
- ADR-0011: Status 색상
- Pillar 1: PPL 시작 동일 명시
- 디자인 리뷰 체크리스트에 "명시적 숫자 / 회피 옵션" 추가

## [2026-06-17] design addition | Story Events (ADR-0013)

사용자 요청: 소설 스토리를 부가 요소로 반영, 이벤트로 아이템/스킬 획득.

### ADR-0013 (Story Events System) 신규 작성, Accepted

**6 Event Types**:
1. Construct Contact (Dixie, AI Loa)
2. Rare Program Discovery (Kraken, Molly's Razor)
3. Item Discovery (T-A Artifact, biochip)
4. Vision / Lore (Wintermute, Aleph)
5. Contact from Above (tip, hint)
6. Combat Event (hostile decker, Black ICE trap)

**Triggering**:
- Random per node (10-20%, grade 보너스)
- Scripted (Arc별 핵심)
- Time-based (런 사이)
- Grade-based unlock

**Resolution**:
- Auto / Choice / Skill Check (PPL vs ZDR) / Narrative Only

**Rewards by Grade**:
- 1-up: T1 items, basic programs
- 2-up: T2 items, advanced
- 3-up: T3 items, Goliath tier
- 4-up: T4 items, Kraken tier, construct fragments
- 5-up: T5 items, construct unlocks

**Event Catalog (스프롤 3부작)**:
- Arc 1: First Jack, Finn's First Job, Watchdog Patrol
- Arc 2: Sense/Net Tip, Yakuza Job, Samurai Grade
- Arc 3: Black ICE Encounter, Molly's Razor, T-A Artifact
- Arc 4: Dixie's Offer, Voodoo Loa, Wintermute's Whisper, Aleph Fragment
- Arc 5: 3Jane's Shadow, Slick Henry's Vision, The Choice

### 시스템 명세
`design/systems/story-events.md` 작성. Event types, triggering, resolution, rewards, 데이터 구조, Arc 연동.

### 영향
- ADR-0008: 보상이 Item Tier 따름
- ADR-0009: Story Archive와 통합
- ADR-0011: NPC portrait
- ADR-0012: 일부 = skill check
- Pillar 1: 다양성 추가
- Pillar 2: cyberspace 안 표현
- story_skeleton.md: Arc별 핵심 이벤트 추가

### ADR-0010 (i18n + Content Pipeline) 신규 작성, Accepted

영향:
- **모든 텍스트**: i18n JSON (`data/i18n/{ko,en}.json`)
- **모든 콘텐츠**: JSON / YAML 데이터 (ADR-0004 강화)
- **plot bones 사전 정의**: `design/story_skeleton.md` (5 arcs + 4+ endings)

### story_skeleton.md (신규)

5 Arcs:
- **Arc 1**: First Run (1-up, 1-3 jobs) — Phase 5 우선
- **Arc 2**: The Sprawl (2-3 up, 3-5 jobs) — Phase 6
- **Arc 3**: Corporate Ice (3-4 up, 3-5 jobs) — Phase 6 후반
- **Arc 4**: The AIs (4-5 up, 3-5 jobs) — Phase 7
- **Arc 5**: The Choice (5-up, 1 final job) — Phase 7

4+ Endings:
- **A**: The Sprawl Returns
- **B**: The AI Awakens (Wintermute/Neuromancer 차용)
- **C**: The Lo Tek
- **D**: The Flatline (다시)

### 다음 단계
- Phase 4: 개발 환경 구축 (prototype/ 스켈레톤, 빌드, 테스트, CI)
- Phase 5: 핵심 시스템 프로토타입 (Vertical Slice) — Arc 1의 1-3 jobs 우선

## [2026-06-18] tool | Quick Demo Script (scripts/play.py)

사용자 요청: "데모를 직접 실행해 보고 싶은데, 간단한 스크립트로 만들어줘."

### `scripts/play.py` (신규)

**단일 명령으로 게임 전체 흐름을 자동 실행**:
```bash
uv run python scripts/play.py
# 또는 짧게:
uv run python scripts/play.py --duration 8 --step-delay 0.3
```

**옵션**:
- `--duration N`: 총 시간 (기본 30s)
- `--step-delay D`: 프레임 간 지연 (기본 0.4s)
- `--no-clear`: 화면 clear 안 함
- `--lang {en,ko}`: UI 언어
- `--seed N`: RNG 시드
- `--mission N`: 의뢰 인덱스
- `--show-controls`: 컨트롤 안내

**자동 진행**:
1. Main Menu → "New Run" 선택
2. Hub → 첫 번째 의뢰 (First Jack) 선택
3. Matrix 진입 → 인접 노드 순차 탐색 (Fog of War)
4. 모든 인접 방문 → Jack out → Hub 복귀
5. 다음 의뢰로 사이클 반복 (--duration까지)

**화면 출력**:
- 각 프레임: 현재 화면 + step 번호 + elapsed time + narration
- ANSI clear (또는 --no-clear)
- 키보드 인터럽트 가능 (Ctrl+C)

**검증**:
- 12s 데모 = 30 steps, 1562 lines output
- 화면 흐름: Menu → Hub → Matrix (fog) → Hub → Matrix → ...
- Fog 동작 확인: Entry는 full box, 인접은 outline, unknown은 `?`
- 미니맵 + breadcrumb 정상 표시

### 사용 예

```bash
# 기본 30s
uv run python scripts/play.py

# 짧은 데모
uv run python scripts/play.py --duration 8

# 화면 clear 없이 스크롤
uv run python scripts/play.py --no-clear

# 한글
uv run python scripts/play.py --lang ko

# 빠른 프레임
uv run python scripts/play.py --step-delay 0.1
```

### 영향

- 게임 데모의 *가장 간단한 진입점* — `uv run python scripts/play.py` 한 줄로 전체 게임 흐름 확인
- 기존 `scripts/demo.py` (2분 전체 플레이)는 더 상세한 옵션
- 기존 `scripts/combat_simulator.py` (단일 전투 검증)
- 기존 `scripts/combat_grades.py` (5등급 진행)

## [2026-06-18] design addition | Fog of War + Exploration (ADR-0020)

사용자 결정: "Light Fog (현재+인접) — Recommended"

### ADR-0020 (Fog of War + Exploration) 신규 작성, Accepted

**Light Fog 4단계 가시성**:
- `current`: 강조 박스, `>` 마커, 전체 정보 (라벨, ZDR, PPL vs ZDR)
- `adjacent`: 외곽선 박스, kind만 (Data/ICE/Router)
- `discovered`: 박스, 전체 (방문한 적 있음)
- `unknown`: `?` placeholder (어두운 회색)

**부가 메카닉**:
- 미니맵 (top-right): `●` (discovered), `○` (adjacent), `?` (unknown), `X` (exit, 항상)
- Breadcrumb (bottom): `Path: E → R₀ → I₀` (회색)
- Probe program: 인접 노드 ZDR 공개 (T1, 1 AP)

### 영향

- `decisions/0005-cyberspace-representation.md` (연계)
- `decisions/0003-combat-system.md` (Probe program)
- **Pillar 5 (The Style)**: 깁슨 "matrix is vast, you are small"
- `matrix/exploration.py` (신규) — `ExplorationState` (current, discovered, scanned, path)
- `engine/matrix_view.py` (확장) — `_draw_box_fog`, `_draw_minimap`, `_draw_breadcrumb`
- `engine/state.py` (확장) — `exploration: ExplorationState | None` 필드
- `engine/hub.py` (확장) — `_start_mission`에서 exploration 초기화
- `engine/matrix_view.py` (확장) — `_handle_movement`에서 `expl.visit()` 호출
- `scripts/demo.py` (확장) — demo에서도 exploration 사용
- `design/systems/exploration.md` (신규)
- `testcases/systems/exploration.md` (신규 — TC-EXP-001~010)

### Phase 5 범위

- **데이터 + 모듈 + 렌더링 + 테스트**: ExplorationState 클래스, fog 렌더링, 미니맵, breadcrumb
- 14 tests 추가 (initial state, visit, visibility, probe, path 등)

### 검증

- **124 tests passing** (110 → 124, +14 신규)
- `make all` (format + lint + typecheck + test) green
- Smoke test: `uv run python scripts/demo.py`로 fog 동작 확인
  - Entry: 풀 박스, `>` 마커
  - 인접 (Router): 외곽선 박스, `(adjacent)` 표시
  - Unknown: `?` placeholder
  - 미니맵: `● Entry (you)`, `○ Router ?`, `? Data/ICE/Exit`
  - Breadcrumb: `Path: Entry`

### Pillar 정합

- **P1**: 한 런 안의 *방랑* — 자키가 매트릭스를 *탐험*
- **P2**: 매트릭스 안의 *데이터* 발견 — Pillar 2 정합
- **P3**: 안개로 인한 *불확실성* → 위험 회피의 *무게* 강화
- **P4**: Probe 같은 *탐색 도구* — Pillar 4 표현
- **P5**: 깁슨 "matrix is vast, you are small" — *작고 헤매는* 자키

## [2026-06-18] tool | Grade Progression (5단계 전투 검증)

사용자 요청: "레벨을 다섯 단계 정도로 나눠서 전투 및 결과 이벤트를 검증해줘. 성장에 따라 효과가 달라지는 것을 체험하게끔 하고 싶어."

### 구현

**`scripts/combat_grades.py`** (신규) — 5등급 자동 전투 시뮬레이터:
- 5 grades (1-up to 5-up) 각각의 loadout, HP, ATK, programs 정의
- 같은 적 (default: standard ICE, ZDR 6) 상대로 자동 전투
- 각 등급별 결과: VICTORY/DEFEAT, 시간, 피해량, 스킬 사용 횟수, HP, HEAL
- 스틱 피규어 아바타 (등급별 표현)
- 등급별 aftermath + 캐릭터 반응 (en + ko)
- 비교 표 (comparison table)
- 진행 인사이트 (progression insights)
- JSON 저장 옵션 (`--save`)

**5 등급 정의** (ADR-0008 + ADR-0012):

| Grade | PPL | HP | ATK | Programs |
| 1-up | 8 | 100 | 5 | wisp T1, strike T1 |
| 2-up | 16 | 120 | 7 | wisp T2, hammer T2 |
| 3-up | 24 | 150 | 9 | wisp T3, goliath T3 |
| 4-up | 40 | 200 | 12 | wisp T4, goliath T4, wardrone T4 |
| 5-up | 75 | 300 | 15 | kraken T5, goliath T5, wisp T5, wardrone T5, Dixie T5 |

**검증된 진행 곡선** (Standard ICE, ZDR 6):

| Grade | Ratio | Status | Time | Dmg Taken | HEAL | Reaction |
| 1-up | 1.33x | MATCH | 14.1s | 24 | +20 | Case (떨리는 손) |
| 2-up | 2.67x | SAFE | 8.1s | 15 | +24 | Finn (비즈니스) |
| 3-up | 4.00x | SAFE | 6.1s | 11 | +30 | Dixie (T-A 경고) |
| 4-up | 6.67x | SAFE | 4.1s | 9 | +40 | 3Jane (위협) |
| 5-up | 12.50x | SAFE | 2.1s | 6 | +60 | Dixie (시적) |

**데이터 확장**:
- `data/programs/programs.json` — `strike` (T1, 1 AP, 6 dmg), `hammer` (T2, 2 AP, 12 dmg), `virus` (T2, 2 AP, 8 dmg), `wardrone` (T4, 2 AP, +2 shield) 추가

**테스트** (`tests/unit/test_grade_progression.py`, 13 tests):
- 5 등급 모두 존재
- PPL / HP / ATK 단조 증가
- 1-up PPL 8 (공식 검증)
- 5-up construct T5
- fresh enemy per call (template 보존)
- 아바타 5등급 모두 렌더링
- HEAL 단조 증가
- 5-up > 1-up (time, damage, HP)

**디자인 문서** (`design/systems/grade-progression.md`):
- 5 등급 정의 + PPL 공식
- 진행 곡선 (검증된 시간/피해/HEAL 차이)
- 등급별 캐릭터 반응 (Aftermath, ADR-0019)
- 스킬 트리 시각화 (T1 → T5)
- Pillar 정합 분석

### 검증

- **110 tests passing** (97 → 110, +13 신규)
- `make all` (format + lint + typecheck + test) green
- `uv run python scripts/combat_grades.py` → 5등급 VICTORY 모두, 시간 14.1s → 2.1s (7배 빠름)

### 사용 예

```bash
# 기본 (Standard ICE, ZDR 6)
uv run python scripts/combat_grades.py

# 더 어려운 적 (Black ICE, ZDR 12)
uv run python scripts/combat_grades.py --enemy black --zdr 12

# 결과 JSON 저장
uv run python scripts/combat_grades.py --save
```

### 영향

- Pillar 4 (The Build) 가장 직접적 표현 — 등급 = *성장*
- 개발 도구: 밸런스 검증 (등급별 전투 시간/피해량 차이)
- 테스트 도구: 회귀 테스트 (등급 변경 시 combat 영향 추적)
- 문서: 5등급 progression 명세 (다른 시스템의 reference)

## [2026-06-18] tool | Combat Simulator (developer/QA)

사용자 요청: "전투 시뮬레이터가 필요할 거 같아. 임의의 레벨과 임의의 스킬 및 이벤트들을 가진 채로 비등비등한 적과 전투를 할 경우 진행화면과 전투 경과 이벤트를 직접 보고 검증하기 위한 목적이야."

### 구현

**`combat/` 모듈 (신규)** — Phase 5에서 정착:
- `state.py` — `Combatant`, `Skill`, `CombatState`, `step_combat`, `use_skill`
  - TICK_MS = 100 (10 FPS)
  - AUTO_ATTACK_INTERVAL_MS = 2000 (1 attack / 2s, ADR-0003)
  - AP_REGEN_INTERVAL_MS = 2000 (1 AP / 2s)
- `registry.py` — `ProgramRegistry`, `IceRegistry`, `build_default_player`, `build_ice_enemy`

**`data/combat/ice_types.json`** (신규):
- 5 ICE 타입: standard (HP 80, dmg 3), watchdog (HP 50, dmg 2), black (HP 200, dmg 8), goliath (HP 150, dmg 5), construct (HP 300, dmg 6)

**`scripts/combat_simulator.py`** (CLI):
- 인자: `--ppl`, `--zdr`, `--enemy`, `--seed`, `--step-delay`, `--strategy` (smart/random/aggressive/defensive), `--no-clear`, `--max-ticks`, `--log`
- 자동 스킬 선택 (4 전략)
- 화면: HUD (PPL/ZDR/Status), portraits, HP 바, action log (6줄 cap)
- 종료: 승리 / 패배 / max-ticks 초과

**`tests/unit/test_combat.py`** (신규, 17 tests):
- Combatant 생성/사망
- step_combat 자동 공격 (양쪽)
- use_skill (attack, defense/shield, AP 부족)
- Shield 흡수
- 승리/패배 조건
- 종료 후 no-op
- Registry 로드
- AP regen
- 로그 cap

### 검증

- **97 tests passing** (80 → 97, +17 신규)
- `make all` (format + lint + typecheck + test) green
- Smoke test: `uv run python scripts/combat_simulator.py --ppl 6 --zdr 6` → VICTORY in 30s game time, 80 dmg dealt, 43 dmg taken, 2 skill uses

### 예시 실행

```bash
# 기본 (MATCH, PPL 6 vs ZDR 6, standard ICE)
uv run python scripts/combat_simulator.py

# Black ICE (DEADLY for grade 1)
uv run python scripts/combat_simulator.py --enemy black

# Construct (legendary)
uv run python scripts/combat_simulator.py --enemy construct

# Custom ratio
uv run python scripts/combat_simulator.py --ppl 25 --zdr 12 --enemy goliath

# Verbose event log
uv run python scripts/combat_simulator.py --log

# Slower pacing for readability
uv run python scripts/combat_simulator.py --step-delay 0.5
```

### 화면 예시

```
=== COMBAT SIMULATOR — Status: MATCH (6/6 = 1.00x) ===

PPL: 6  ZDR: 6  Status: MATCH

◉P◉     You
        HP: 91/100
        [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░]
        AP: 1/6  ATK: 5
        Shield: 1

▲ICE▲   ICE — Standard
        HP: 60/80
        [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░]
        ATK: 3
----------------------------------------------------------------------------
Action log:
You hit ICE — Standard for 5 damage.
ICE — Standard hits you for 2 damage (shield absorbed 1).
>> Wisp: +1 shield.
You hit ICE — Standard for 5 damage.
ICE — Standard hits you for 2 damage (shield absorbed 1).
>> Wisp: +1 shield.
```

### 영향

- **Phase 5 +**: combat 로직의 *기반*. Phase 6+에서 engine integration (UI, animations, salvage, aftermath)
- 검증 도구: 전투 수식, 밸런스, 이벤트 흐름을 *수동 플레이 없이* 확인
- `design/systems/combat.md` (ADR-0003 + ADR-0014) — 구현 가능한 형태로 구체화

### 향후 결정

- Phase 6+: 시뮬레이터에 animation 적용 (data/animations/frames.json 사용)
- Phase 6+: 시뮬레이터에 Data Salvage + Aftermath 통합
- Phase 7+: HUD PPL 갱신 (player의 loadout 변경 시)

## [2026-06-18] design addition | Combat Aftermath & Subtitles (ADR-0019)

사용자 결정 (2026-06-18):
> "전투가 끝난 결과와 보상에서 상대의 중요도가 큰 경우에는 후일담 같은 이야기나 소설 인물들의 반응 같은 것을 읽을 수 있게 해줘. 이벤트 메시지는 한글 자막 형식으로 번역되어야 해. 몰입감을 높이는 요소야."

### ADR-0019 (Combat Aftermath & Immersive Subtitles) 신규 작성, Accepted

**4-Importance Combat Aftermath**:
- `minor` — 일반 ICE: 표시 X
- `notable` — 강 ICE: 짧은 snippet
- **`major` — Black ICE / Construct**: 풀 snippet + character reaction
- `legendary` — Named boss (3Jane): 4+ 문단 + multiple reactions

**7 Character Reactions** (스프롤 3부작 인물):
- `dixie` (◊D◊ cyan) — 기술적, ROM 어투, 약간 비꼬는
- `finn` (♠F♠ magenta) — 비즈니스, 간결, 거래관점
- `molly` (X_X red) — 직접적, 강렬함, 짧은 문장
- `case` (◉P◉ green) — 내성적, 자기성찰, 길고 느린 문장
- `3jane` (▲▲J▲▲ white) — 차가움, aristocratic, 위협
- `maelcum` (◯M◯ yellow) — 철학적, 평온, 시적
- `slick_henry` (★H★ magenta) — 예술적, 호기심

**Immersive Subtitles** (이벤트 메시지):
- 형식: en (흰색) + ko (노란색 `(255, 220, 100)`) stack
- 적용: Aftermath, Story Events, Mission Briefing, Hub dialogue, News/Story Archive
- 미적용: HUD 수치, 메뉴 라벨, 시스템 메시지

**예시 (자막 형식)**:
```
> Somewhere in the matrix, the Black ICE's last packet dissolves.
> 매트릭스 어딘가에서, 블랙 ICE의 마지막 패킷이 흩어진다.
```

**예시 (Dixie reaction)**:
```
> "야, 잘 했어. 근데 조심해 — 그건 그냥 sentry였어. T-A가 더 큰 거 가지고 있어."
> (한국어 자막: 동일)
```

### 영향

- `decisions/0009-story-news-system.md` (연계)
- `decisions/0010-i18n-content-pipeline.md` (이벤트 메시지 자막 디폴트)
- `decisions/0013-story-events.md` (narrative 부분 자막)
- `decisions/0014-data-salvage.md` (Aftermath는 Salvage 뒤)
- `decisions/0017-mission-material-integration.md` (mission complete → Finn reaction)
- **Pillar 5 (The Style)**: 가장 직접적 표현 — 깁슨 톤, cinematic
- `design/systems/aftermath.md` (신규)
- `testcases/systems/aftermath.md` (신규 — TC-AFTER-001~012)
- `data/story/aftermath.json` (5 aftermath: black_ice, construct_first, core_first, mission_first, arc_advance)
- `data/story/reactions.json` (10 reactions across 5 characters)
- `data/i18n/{en,ko}.json` (aftermath UI 키)

### Phase 5 범위

- **데이터 + 문서만**: JSON + ADR + design/testcases
- **UI 없음**

### Phase 6+ 범위

- Aftermath 렌더링 (전투 종료 → Data Salvage → Aftermath → Hub)
- Character reaction 표시 (portrait + 자막)
- 자막 모드 기본 (이벤트 화면)
- Story Archive 통합 (aftermath 저장)

### Phase 7+

- 사운드 (목소리 톤)
- 자막 타이핑 효과
- 비주얼 노이즈 / 글리치

## [2026-06-18] design addition | Mission-Material + Combat Animation (ADR-0017, ADR-0018)

사용자 결정 (2026-06-18):
> "미션 중에는 재료 수집 전달도 연계되면 좋겠어. 메뉴에서 레시피와 재료 현황도 동시에 보여야 하며 도형적이면 좋겠어. 그리고 전투는 일반공격과 스킬공격 효과가 대비되도록 아스키 애니메이션을 적용하고 싶어."

### ADR-0017 (Mission-Material Integration) 신규 작성, Accepted

**6 Mission Types**:
- `extract_data`, `collect_material`, `deliver_material`, `craft_item`, `hunt`, `salvage`

**Visual Hub Menu (4 Panels)**:
- Panel 1: Avatar
- Panel 2: Materials (도형적 게이지 `▓`/`░`)
- Panel 3: Recipes (트리, READY ✓)
- Panel 4: Job Board + Info Market

**Recipe Tree View**: Kraken (T5) = 트리 시각화, 각 노드 have/need 게이지

### ADR-0018 (Combat Animation) 신규 작성, Accepted

**대비 원칙**:
- Normal: 3 frames, 240ms, gray `(128, 128, 128)`, `-5` damage
- Skill: 6 frames, 600ms, color (program별), `-25` damage, screen shake

**Skill 종류별 패턴**:
- Goliath: `⚔▓▓▓ ⚡ →▶` (magenta)
- Kraken: `⚔▓▓▓▓▓▓ ☠ →▶` (red, screen flash)
- Wisp: `+ + + shield` (cyan)
- Probe: `?PRB? flash` (yellow)
- Death: 7 frames, 2.4s, red → dark_red, "FLATLINE. Static. Silence."

**화면 효과**: Screen shake (1-3 픽셀), Screen flash (치명타), Matrix glitch (Black ICE)

### 영향

- `decisions/0015-crafting-system.md` (연계)
- `decisions/0016-jockey-avatar.md` (연계)
- **Pillar 4 (The Build)**: 가장 직접적 표현 (미션 = 재료 수집의 안내)
- **Pillar 1 (The Run)**: 한 런 = 미션의 *수행 + 보상* 사이클
- `design/systems/missions.md` (신규)
- `design/systems/animations.md` (신규)
- `testcases/systems/mission-material.md` (신규 — TC-MISMAT-001~012)
- `testcases/systems/animations.md` (신규 — TC-ANIM-001~012)
- `data/missions/missions.json` (확장 — 5 미션, primary/secondary objectives)
- `data/animations/frames.json` (신규 — 8 애니메이션 정의)

### Phase 5 범위

- **데이터 + 문서만**: JSON + ADR + design/testcases
- **UI 없음**: Phase 6+

### Phase 6+ 범위

- Hub 4-패널 UI
- Recipe 트리 뷰
- Mission 진행 추적
- Material drop 시각화
- 애니메이션 플레이어 (60 FPS)
- 화면 흔들림 / flash
- Death 애니메이션

## [2026-06-18] design addition | Crafting & Jockey Avatar (ADR-0015, ADR-0016)

사용자 결정 (2026-06-18):
> "전투 승리의 보상으로 아이템 또는 재료 수집 요소를 넣고 싶어. ... 현재 stat을 직관적으로 알 수 있도록 표현할 방법을 찾아봐. 도형이나 아바타 객체의 부분들을 채우고 교체하는 방식도 좋아."

### ADR-0015 (Material & Crafting) 신규 작성, Accepted

**3-tier 구조** (사용자 선택: 정제 단계 없음):
- **Tier 0 — Raw Material (5종)**: `ice_shard`, `data_fragment`, `rom_echo`, `wetware_chip`, `biosoft_agent`
- **Tier 1 — Component (4종)**: `combat_module`, `construct_shard`, `wetware_data`, `ice_construct`
- **Tier 2 — Final Product**: Programs (T1~T5), Items (T1~T5), Construct Fragments

**대체 경로**: Info Market (CRED 구매, T1~T4만, T5는 crafting only)

**예시 레시피**:
```
combat_module × 5 + upgrade_t5 → Kraken (T5)
construct_shard × 3 → Construct Fragment
```

### ADR-0016 (Jockey Avatar) 신규 작성, Accepted

**Stick Figure Avatar** (사용자 선택):
- 머리 (`◉P◉` ~ `X`) = HP 무결성
- 팔 (programs, `★W★` ~ `·W·`) = programs, 등급/소진
- 몸통 (자세) = Status pose (SAFE → FUTILE)
- 데크 (`║DK7║`) = deck tier
- 웨웨어 (`▓▓▓▓`) = wetware tier
- Construct (`◆D◆`) = construct echo

**부위 표현**:
- HP 100%: `◉P◉` (green)
- HP 50%: `◉P/` (yellow, 기울어짐)
- HP 0%: `X` (dark_red, flatline)
- Program T5: `★W★`, T1: `·W·`
- Status TOUGH: `/|\` 약간 웅크림, DEADLY: `/\` 엎드림

### 영향

- `decisions/0008-progression-system.md` — Tier 시스템 강화
- `decisions/0013-story-events.md` — 이벤트 보상 = 재료
- `decisions/0014-data-salvage.md` — CRED → Info Market
- `decisions/0011-ascii-portraits.md` — Portrait 보강
- `decisions/0012-difficulty-rating.md` — Status pose
- **Pillar 4 (The Build)**: 가장 직접적 표현 (조합 + 구매)
- `design/systems/crafting.md` (신규)
- `design/systems/avatar.md` (신규)
- `testcases/systems/crafting.md` (신규 — TC-CRAFT-001~012)
- `testcases/systems/avatar.md` (신규 — TC-AVATAR-001~013)
- `data/crafting/materials.json`, `recipes.json`, `market.json` (신규)

### Phase 5 범위

- **데이터만**: JSON + ADR + design/testcases
- **UI 없음**: Crafting/Avatar는 Phase 6+

### Phase 6+ 범위

- Crafting UI (Hub)
- Info Market UI (Hub)
- Avatar 렌더링 (Hub + Matrix)
- 전투 승리 시 드롭 표시
- 사망 시 재료 손실 정책 (Option A 기본값)

## [2026-06-18] phase start | Phase 5 — 매트릭스 진입 + 노드 그래프

### 디자인

## [2026-06-18] phase start | Phase 5 — 매트릭스 진입 + 노드 그래프

## [2026-06-18] design addition | Data Salvage (ADR-0014)

사용자 결정: "전투 성공의 보상으로 회복 요소가 있어야 해."

### ADR-0014 (Data Salvage) 신규 작성, Accepted

**핵심**: ICE 격파 시 *Data Salvage* 메뉴가 뜨고, 플레이어가 하나를 선택:
- `HEAL` — +20% max HP (Phase 5: T1 = +20, T3 = +30)
- `FRAG` — program fragment (Phase 6+)
- `CRED` — credits (Phase 6+)
- `SKIP` — 아무것도 안 함

**Pillar 정합 (일부 완화, 무게 유지)**:
- 회복은 *이겨야만* (a)
- HEAL만 작동 (b)
- 20%만 (c)
- 5번 싸워서 1번 회복하는 구조 → 무게 유지

### 영향

- `decisions/0003-combat-system.md` — combat 종료 후 salvage phase 추가
- `decisions/0006-run-structure.md` — 회복은 메타 진행 X, 런 내 자원 순환
- `decisions/0008-progression-system.md` — HP 풀은 티어에 비례, 회복 비율(20%)은 동일
- `decisions/0012-difficulty-rating.md` — ZDR/PPL 비등 시 회복으로 *살짝* 유리
- **Pillar 3 (The Flatline)**: 일부 완화. 단 *선택 + 승리 + 제한* 으로 무게 유지.
- `design/systems/combat.md` (신규) — combat 시스템 + salvage 흐름 명세
- `design/core_loop.md` — combat micro-loop에 salvage 단계 추가
- `design/glossary.md` — "Salvage" 용어 추가
- `testcases/combat/salvage.md` (신규) — TC-COMBAT-001~008 시나리오

### Phase 5 범위

- **HEAL만 작동**. FRAG, CRED는 "Phase 6+: not yet implemented" 안내
- 회복량: `round(max_hp * 0.20)`, min 1
- HP max 상태에서 HEAL → "no damage to repair" 메시지 (자원 낭비 알림)
- Disengage (철수) / Death → salvage 없음

## [2026-06-18] phase start | Phase 5 — 매트릭스 진입 + 노드 그래프

### 디자인

- **`design/systems/hacking.md`** (신규) — 사이버스페이스/매트릭스 시스템 명세
  - 노드 (entry/exit/router/data/system/ice/construct/core)
  - Edge, MatrixGraph (DAG)
  - ZoneDepth, IceKind, AlarmLevel, Faction, ZDR 공식
  - PPL vs ZDR Status (5 카테고리)
  - 절차적 생성 알고리즘 (Phase 5: Surface 한정)
  - 그래프 레이아웃 (BFS layer, col/row grid)

### 코드 (prototype/)

**`src/roguelike_sprawl/matrix/`** (신규)
- `node.py` — `Node`, `NodeKind`, `ZoneDepth`, `IceKind`, `AlarmLevel`, `Faction` (frozen dataclass + StrEnum)
- `zdr.py` — `Status`, `calculate_zdr`, `calculate_status`, `status_color`, `node_zdr`, `node_status`
- `ppl.py` — `Program`, `Loadout`, `calculate_ppl`
- `graph.py` — `Edge`, `MatrixGraph`, `compute_layout` (BFS-layer)
- `generator.py` — `MatrixGenerator.generate(seed, mission_grade)` — deterministic, Surface 한정, 5-7 nodes
- `labels.py` — `zone_label` (i18n helper)

**`src/roguelike_sprawl/missions/`** (신규)
- `mission.py` — `Mission` (frozen dataclass, Arc/grade/zone/reward)
- `board.py` — `JobBoard` (load JSON, filter by grade)

**`src/roguelike_sprawl/engine/`** (리팩터)
- `state.py` (신규) — `AppState` (screen, grade, loadout, job_board, mission, matrix, current_node_id)
- `menu.py` (신규) — 메인 메뉴 화면 (render + input)
- `hub.py` (신규) — Hub (픽서 construct) 텍스트 인터페이스 + 의뢰 선택
- `matrix_view.py` (신규) — 매트릭스 노드 그래프 렌더링 + 이동 입력 (방향키)
- `app.py` (리팩터) — 화면 상태 머신 (Menu → Hub → Matrix)

**`data/`**
- `missions/missions.json` (신규) — Arc 1 미션 2개 (first_jack, watchdog_patrol)
- `i18n/en.json`, `i18n/ko.json` (확장) — hub/matrix/missions/status 키 추가

### 렌더링

- **노드 박스**: 12x4 ASCII 박스 (`+--+`), 라벨 + ZDR + Status 글리프 (`+`/`=`/`-`/`!`/`X`)
- **연결선**: L-shape (Unicode box-drawing) `─`, `│`, `┌`, `┐`, `└`, `┘`
- **현재 노드**: 좌측에 `>` 마커 + 노란색 강조
- **HUD**: PPL (green), ZDR (gray), Status (색상), Zone 라벨
- **Hub**: 픽서 인트로 + 의뢰 목록 (ZDR preview, status 색상)
- **Menu**: 1=New Run, 2=Archive, 3=Settings, Q=Quit

### PPL & ZDR

- **기본 등급 1-up 자키**: Ono-Sendai 4 (T1) + Wisp (T1) + Standard (T1) → **PPL 6** (ADR-0012 예시)
- **Arc 1 미션**: 모두 Surface zone, Sense/Net faction (+4)
  - Entry ZDR: 1 (base) + 4 (faction) = 5
  - ICE ZDR: 1 + 2 (standard) + 4 (faction) = 7
  - Grade 1 자키: PPL 6 / ICE ZDR 7 = 0.86x → **TOUGH** (yellow)

### 검증

- 80 tests passing (27 → 80, +53 new)
  - test_matrix_node: 19 (Node, ZDR, Status, colors)
  - test_matrix_ppl: 7 (PPL 공식)
  - test_matrix_graph: 14 (Edge, MatrixGraph, compute_layout)
  - test_matrix_generator: 5 (deterministic, connected, surface)
  - test_missions: 7 (Mission, JobBoard)
  - test_matrix_layout_sanity: 1 (모든 시드 그래프가 80x50 안에 fit)
- ruff check: All checks passed
- ruff format: 45 files already formatted
- mypy: Success, 31 source files
- 임포트 sanity: matrix/hub/menu 3개 화면 모두 정상 렌더

### Phase 5 남은 작업

- **전투 (RT-MS)**: ICE 노드 진입 시 자동 공격 + 메뉴 스킬 (ADR-0003)
- **Action menu**: 노드 진입 시 scan/extract/engage/communicate 선택
- **죽음/재시작**: HP 0 → flatline → Hub 복귀
- **의뢰 완료**: 데이터 추출 성공 시 보상 + 다음 의뢰 unlock
- **Story Events**: ADR-0013 — 노드 탐색 시 random/scripted 이벤트
- **다중 zone (Phase 6)**: Mid / Core / TA zone 생성

## [2026-06-18] phase complete | Phase 4: 개발 환경 구축

### 프로젝트 스켈레톤 (Game/roguelike_sprawl/prototype/)

- **Python 3.11+**, **python-tcod 21+**, **uv** 사용
- **빌드**: hatchling
- **테스트**: pytest (27 tests passing)
- **린트/포맷**: ruff (check + format)
- **타입 체크**: mypy strict
- **CI**: GitHub Actions (macOS + Windows)

### 디렉토리 구조

```
prototype/
├── src/roguelike_sprawl/
│   ├── engine/    # tcod 통합 (app, render, input, config)
│   ├── ecs/       # ECS-lite (entity, world)
│   ├── i18n/      # 번역 (translator with __call__)
│   ├── portraits/ # ASCII Portraits (manager)
│   ├── data/      # 데이터 로더
│   └── util/      # (예정)
├── tests/unit/    # 27 tests
├── data/
│   ├── i18n/      # en.json, ko.json
│   ├── portraits/ # portraits.json
│   ├── programs/  # programs.json
│   └── fonts/     # libtcod terminal10x10
├── scripts/
│   └── download_font.py
├── .github/workflows/ci.yml
└── pyproject.toml
```

### hello-world (Phase 4 deliverable)

- tcod 윈도우 80x50
- "=== ROGUELIKE SPRAWL ===" 타이틀
- "You jack in. The world goes gray." 메시지
- Player portrait `◉P◉` (PPL 6, HP 50/100)
- ICE portrait `▲ICE▲` (ZDR 7, TOUGH)
- 컨트롤 안내
- ESC / Q로 종료

### 검증

- 27 tests passing
- ruff check: All checks passed
- ruff format: 25 files left unchanged
- mypy: Success: no issues found in 17 source files
- tcod 윈도우 생성 확인 (SDL, metal renderer)
- 폰트 다운로드 성공 (libtcod terminal10x10_gs_tc.png)
- 데이터 로드 확인 (i18n, portraits, programs)

### 다음 단계
- Phase 5: 매트릭스, 전투 (RT-MS), 의뢰 시스템 구현

## 2026-06-18 - Sound System + Engine Integration
- **Added**: `src/roguelike_sprawl/audio/sound_manager.py` (SoundManager + 27 default sounds + WAV generator)
- **Added**: 6-phase sound integration (UI/Story/Combat/Movement/Items/Voice/Music)
- **Added**: Sound hooks in 6 engine modules (story_cinematic, combat_view, cyberspace_browser, cyberspace_view, action_menu, npc_view)
- **Fixed**: mypy strict pass (172 -> 0 errors)
- **Fixed**: ruff check (6 -> 0 issues)
- **Verified**: 124 tests passing
- **Verified**: 27 placeholder WAVs auto-generated

## 2026-06-18 - Sound System Phase 4-6 (Integration + Settings)
- **Added**: `src/roguelike_sprawl/engine/settings_ui.py` (volume/mute helpers + overlay)
- **Added**: Global hotkeys: M (mute), +/- (volume)
- **Added**: Status panel audio section (AUDIO, MUTED/ON, Vol:%, [M] mute [+/-] vol)
- **Added**: `safe_play()` helper in sound_manager (silent error fallback)
- **Refactored**: Removed 7 duplicate `_play_*_sound` helpers; consolidated to safe_play
- **Added**: `tests/unit/test_sound_manager.py` (12 tests)
- **Added**: `tests/unit/test_settings_ui.py` (8 tests)
- **Added**: Makefile targets: sound-test, sound-manager, sound-demo, sound-demo-full, sound-clean
- **Updated**: SOUND_PLAN.md (all phases checked, status section added)
- **Verified**: 144 tests passing (was 124, +20 new)
- **Verified**: mypy strict: 0 errors (61 source files)
- **Verified**: ruff: 0 issues

## 2026-06-18 - Jockey Avatar System (ADR-0016)
- **Added**: `src/roguelike_sprawl/avatar/` module (state.py, renderer.py, __init__.py)
- **Added**: AvatarState, ProgramSlot, Status, ConstructKind, AvatarLines data models
- **Added**: render_avatar_lines() and render_avatar() functions
- **Added**: build_avatar_state() convenience builder from game values
- **Added**: 28 unit tests (test_avatar.py) covering all 6 head states, 5 body poses, 5 program tiers, 3 program states, 3 construct kinds, integration scenarios
- **Added**: scripts/demo_avatar.py showing 6 scenarios + status/tier reference tables
- **Verified**: 172 tests passing (was 144, +28 new)
- **Verified**: mypy strict: 0 errors (64 source files)
- **Verified**: ruff: 0 issues

## 2026-06-18 - Run State System (Phase A: Data Model)
- **Added**: `src/roguelike_sprawl/run/` module (state.py, helpers.py, __init__.py)
- **Added**: `Stage` enum (PENDING, MEET_NPC, EXTRACT_DATA, DEFEAT_ICE, COMPLETE, FAILED)
- **Added**: `ObjectiveKind` enum (NPC, DATA, ICE, NONE)
- **Added**: `StageInfo` dataclass (title, objective_kind, hint, next_stage)
- **Added**: `RunState` dataclass (current_stage, completed_stages, pending_advance, current_target_node, last_visited_node)
- **Added**: `DEFAULT_FLOW` (MEET_NPC → EXTRACT_DATA → DEFEAT_ICE → COMPLETE)
- **Added**: `mark_advance()` (idempotent stage transition), `mark_failed()`, `reset()`
- **Added**: `AppState.run_state: RunState | None` field
- **Added**: helpers.py with `ensure_run_state`, `start_new_run`, `resolve_target_for_stage`, `check_objective_at_node`
- **Added**: 62 unit tests (test_run_state.py) - all stages, transitions, target resolution
- **Verified**: 348 tests passing (was 286, +62 new)
- **Verified**: mypy strict: 0 errors (70 source files)
- **Verified**: ruff: 0 issues
- **Bug fix**: cyberspace_browser._jack_into_server was not setting state.cyberspace_layouts
- **Bug fix**: demo scripts had no None guard for cyberspace_layouts.get
- **Bug fix**: demo did not auto-jack in from cyberspace browser

## 2026-06-18 - 오리지널 스토리 1단계 (소설 문서)
- **Added**: `design/story/characters.md` (191 lines) — 오리지널 주인공 3인 (Case/Sil/Kas)
- **Added**: `design/story/prologue.md` (183 lines) — 프롤로그 줄거리 1-2페이지 + 2개 엔딩
- **Added**: `dashboard/index.html` (360 lines) — 진행상황 대시보드 (3-Phase + 캐릭터 + 엔딩 + 체크리스트)
- **Decisions**:
  - 오리지널 주인공 (깁슨 등장인물 X) — 사용자 확정
  - 3명 캐릭터 병렬 선택 (Novice/Veteran/Heretic) — 다양한 톤
  - 2개 엔딩 (성공 Jockey Lives / 실패 Jockey Flatlines)
  - 프롤로그만 (1-2페이지), 이후는 미루기
  - 깁슨 톤 유지: Pillar 2 (meatspace 미사용), Pillar 5 (cyberpunk aesthetic)
- **References**: Neuromancer, Count Zero, Mona Lisa Overdrive
- **3-Phase Plan**:
  - 1단계: 소설 (완료)
  - 2단계: 데모 형식 단축 이벤트 (PENDING)
  - 3단계: 실제 게임 구조 반영 (PENDING)

## 2026-06-18 - 오리지널 스토리 2단계 (데모 검증)
- **Added**: `src/roguelike_sprawl/engine/original_story.py` (260 lines)
  - `CHARACTER_SELECT_EVENT` (Finn의 3-way 캐릭터 선택)
  - `NOVICE_PROLOGUE_EVENT` (Case) + Veteran (Sil) + Heretic (Kas)
  - `get_prologue_for_character(char)` / `get_ending_description(char, ending)`
  - `ALL_ORIGINAL_EVENTS` (4 events)
- **Added**: `scripts/verify_original_prologue.py` (220 lines)
  - 3 캐릭터 × 2 엔딩 = 6 시나리오 자동 검증
  - 헤드리스 ANSI 색상 출력
- **Added**: `tests/unit/test_original_story.py` (44 tests)
- **Verified**: 408 tests passing (was 364, +44 new)
- **Verified**: mypy strict: 0 errors (71 source files)
- **Verified**: ruff: 0 issues
- **Updated**: 대시보드 — Phase 2 complete 표시

## 2026-06-18 - GitHub 활용 계획 (ADR-0030)

- **Added**: `decisions/0030-github-utilization.md` (Draft 결정 문서)
  - typing_language의 GitHub 패턴 분석 (CI, Pages, 라벨)
  - 3 옵션 비교 (단일 저장소 / 모노레포 / Git only)
  - **추천안**: Option A (typing_language 미러, 단일 저장소 + Pages)
- **Added**: `.github/workflows/ci.yml` (CI 파이프라인)
  - lint (ruff) + typecheck (mypy strict) + test (pytest, 3 OS × 2 Python)
  - dashboard validation (3 validate_*.py + 4 test_*.py)
  - coverage → codecov
- **Added**: `.github/workflows/pages.yml` (대시보드 Pages 배포)
  - Game/dashboard/ + roguelike_sprawl/dashboard/ 통합
  - design/ JSON 데이터 포함
  - GitHub Pages 자동 배포
- **Added**: `.github/workflows/labeler.yml` (자동 라벨링)
  - phase-1..6, prologue/event/stage/dashboard, python/html/json 라벨
- **Added**: `.github/ISSUE_TEMPLATE/{bug,feature,dashboard}.md` (3 템플릿)
- **Added**: `.github/pull_request_template.md`
- **Added**: `.github/labeler.yml` (12+ 자동 라벨 규칙)
- **Added**: `.gitignore` (루트, prototype/.gitignore 보완)
- **Added**: `docs/GITHUB_SETUP.md` (5분+10분 실행 가이드)
- **Modified**: `README.md` (CI/Pages 배지 + 라이브 대시보드 링크)
- **Modified**: `decisions/README.md` (ADR-0030 추가, 인덱스 동기화)
- **Status**: Draft — 사용자 결정 대기 (저장소 이름, 공개 범위, 라이선스)

## 2026-06-19 - Pages 활성화 + 자동 배포

- **Manual**: GitHub Settings → Pages → Source = "Deploy from a branch", branch = gh-pages / (root)
  - gh-pages 브랜치에 1st push 실패 (auto-enable API가 admin 권한 필요)
  - **Plan B**: pages.yml을 `peaceiris/actions-gh-pages@v4`로 변경 (admin 불필요)
  - 자동 배포 검증: `git push` → 1-2분 → https://seoca1.github.io/roguelike-sprawl/ 라이브
- **Added**: `docs/DEPLOYMENT_GUIDE.md` (207 lines)
  - 배포 파이프라인 다이어그램, 자동 트리거, 검증, 트러블슈팅, 롤백
- **Verified**: 7/7 CI ✅ (CI, Pages build, Pages deploy)
- **Verified**: 8 dashboard HTTP 200 (main, story, stages, stories, sound, combat, equipment, cyberspace)

## 2026-06-19 - 5-Layer VFX 시스템

- **Added**: `src/roguelike_sprawl/combat/effects.py` (~1030 lines, NEW)
  - Layer 1: HitFlash, FloatingNumber, ParticleSystem, ScreenShake
  - Layer 2: 15 SkillEffect 애니메이션 (ATTACK, HEAVY_ATTACK, PIERCE, MULTI_HIT, DOT, SHIELD, HEAL, REGEN, BUFF, DEBUFF, STUN, COUNTER, LIFESTEAL, DETECT, POISON)
  - Layer 3: 5 ICE 타입별 ice_intro_sequence + ice_death_sequence
  - Layer 4: 8 상태이상 아이콘 (P/B/S/❖/↑/↓/+/•)
  - Layer 5: CinematicSequence, ComboCounter (2x HIT! → 5x RAMPAGE!)
- **Added**: `src/roguelike_sprawl/combat/hud.py` (~510 lines, NEW)
  - HealthState, 2-tier HP bar (HP + shield), smooth drain 200ms
  - LowHpState, AlertLevel (HEALTHY/LOW/CRITICAL)
  - PhaseColorState (boss phase colors)
  - BarFlash (damage/heal)
  - CameraVignette
  - CombatHUD container
- **Modified**: `src/roguelike_sprawl/engine/state.py` (combat_effects field)
- **Modified**: `src/roguelike_sprawl/engine/combat_view.py`
  - HP snapshot → VFX spawn (L1+L2)
  - ICE intro/death cinematic
  - VFX overlay rendering (shake, particles, numbers, flash, cinematic)
- **Added**: `scripts/verify_combat_vfx.py` (ANSI terminal demo)
- **Added**: `tests/unit/test_combat_effects.py` (136 tests)
- **Added**: `tests/unit/test_combat_hud.py` (52 tests)
- **Added**: `tests/unit/test_combat_vfx_dashboard.py` (32 tests)
- **Verified**: 1235 tests pass (+220)

## 2026-06-19 - 3 BOSS + 확장 시네마틱

- **Added**: `src/roguelike_sprawl/combat/bosses.py` (~600 lines, NEW)
  - 3 BOSS: GOLIATH PRIME (4 phases), BLACK ICE LORD (3), WATCHDOG ALPHA (3)
  - BossPhase dataclass, BossSpec, ALL_BOSSES dict
  - get_next_phase (HP threshold), apply_phase_buff
  - boss_intro_sequence (5 lines, 3-5s), boss_phase_transition (8 phases)
  - boss_death_sequence (4 sub-sequences, 12-15 frames)
  - High-level spawners: spawn_boss_intro/transition/death
- **Added**: `tests/unit/test_combat_bosses.py` (88 tests)
- **Added**: `tests/unit/test_combat_bosses_dashboard.py` (10 tests)
- **Verified**: 1333 tests pass (+98)

## 2026-06-19 - HUD 시스템 (2-tier HP + 카메라)

- **Added**: `src/roguelike_sprawl/combat/hud.py` (~510 lines)
  - HealthState: 2-tier (HP + shield), smooth drain animation (200ms)
  - AlertLevel (HEALTHY/LOW/CRITICAL), LowHpState (pulse, vignette, desat)
  - PhaseColorState (boss phase colors), BarFlash (damage/heal)
  - CameraVignette (low HP / boss phase), render_vignette
  - CombatHUD container (player + enemy)
- **Added**: `tests/unit/test_combat_hud.py` (52 tests)
- **Added**: `tests/unit/test_combat_hud_dashboard.py` (23 tests)
- **Verified**: 1408 tests pass (+75)

## 2026-06-19 - 5-Stage 콤보 시스템

- **Added**: `src/roguelike_sprawl/combat/combo.py` (~700 lines, NEW)
  - 5 ComboStage: WARMUP → CHAIN (+20%) → FLURRY (+50%, +1 AP) → RAMPAGE (+100%, +2 AP) → ANNIHILATION (+200%, +3 AP)
  - CombatCombo: register_hit, window expiry (3.5s), damage bonus
  - StageAvatar (5 아이콘), TimingBar (3-tier), ComboFinisher (3종)
  - render_combo_full (avatar + counter + timing bar)
- **Added**: `tests/unit/test_combat_combo.py` (53 tests)
- **Added**: `tests/unit/test_combat_combo_dashboard.py` (20 tests)
- **Added**: `tests/unit/test_combat_stage_ui_dashboard.py` (26 tests)
- **Verified**: 1540 tests pass (+132)

## 2026-06-19 - 업적 시스템 (28 Achievements)

- **Added**: `src/roguelike_sprawl/achievements.py` (~890 lines, NEW)
  - 5 카테고리: COMBAT (7), EXPLORATION (6), STORY (5), MASTERY (6), HIDDEN (4)
  - 4 tier: BRONZE (5), SILVER (7), GOLD (9), PLATINUM (7)
  - Achievement dataclass (frozen), AchievementState, AchievementUnlock
  - Event checkers: check_combat/exploration/story/mastery_event
  - 28 정의 (first_blood, sharpshooter, combo_master, undefeated,
    boss_slayer, goliath_slayer, centurion, first_jackin, world_walker,
    server_domination, data_extractor, jackout_survivor, matrix_explorer,
    case_journey, sil_awakening, kas_rise, five_tales, the_truth,
    ppl_10/20/30, matrix_master, combo_quant, flawless,
    ghost_protocol, phoenix, void_walker, true_hacker)
- **Added**: `dashboard/achievements.html` (28 cards, 17KB, NEW)
- **Added**: `tests/unit/test_achievements.py` (69 tests)
- **Added**: `tests/unit/test_achievements_dashboard.py` (44 tests)
- **Modified**: 8 dashboard에 🏆 Achievements nav 추가
- **Verified**: 1653 tests pass (+113)

## 2026-06-19 - 설정 시스템 (30+ Settings)

- **Added**: `src/roguelike_sprawl/settings.py` (~540 lines, NEW)
  - 5 enums: ColorTheme, GlyphStyle, Language, SubtitleMode, Difficulty
  - GameSettings: 30+ 설정 (audio 9, display 5, input 15, language 2, gameplay 4, meta 2)
  - Defaults: master_volume=0.2, KEYS off, language=both, subtitle, normal, 3500ms
  - validate_settings, apply_fixes, reset_settings, clone_settings
  - JSON persistence (save/load to file, to_dict/from_dict)
  - apply_audio_settings, apply_combo_settings, apply_difficulty_settings
  - Difficulty multipliers: easy 0.5x/1.5x, normal 1.0x, hard 1.5x/0.8x, nightmare 2.0x/0.6x
- **Added**: `dashboard/settings.html` (6 categories, 14KB, NEW)
- **Added**: `tests/unit/test_settings.py` (57 tests)
- **Added**: `tests/unit/test_settings_dashboard.py` (34 tests)
- **Modified**: 9 dashboard에 ⚙ Settings nav 추가 (10 total)
- **Verified**: 1744 tests pass (+91)

## 2026-06-19 - 코드 리팩토링 (팔레트 중앙화 + 번들)

- **Added**: `src/roguelike_sprawl/combat/palette.py` (~290 lines, NEW)
  - 40+ 색상 상수 (HP/damage/status/phase/ICE/combo/finisher/tier)
  - 5 ICE 팔레트 (standard/watchdog/goliath/black/construct)
  - 6 헬퍼 함수 (HP%, phase, combo, ICE, tier, fade)
- **Added**: `src/roguelike_sprawl/combat/bundle.py` (~120 lines, NEW)
  - CombatEffectsBundle: 4 시스템 통합 (effects/hud/combo/visual)
  - step(dt_ms), clear(), has_active_effects(), setup_combat()
  - create_bundle() factory
- **Refactored**:
  - effects.py: 11 색상 → palette import
  - hud.py: 5 색상 + PHASE_COLORS → palette import
  - combo.py: ComboStage.color → COMBO_STAGE_COLORS, TimingBar.get_color → COMBO_BAR_*
  - bosses.py: 3 color_palette 인라인 → ICE_*_PALETTE
- **Added**: `tests/unit/test_combat_palette.py` (70 tests)
- **Verified**: 1814 tests pass (+70)
- **Refactor benefits**:
  - 색상 단일 source of truth
  - 효과 시스템 step() 4번 → 1번
  - 새 테마 추가 4곳 → 1곳

## 2026-06-19 - 세션 종합 (최종 상태)

**Tests**: 1814 passing (+648 from start of day)
**Source files**: 87 (15 modules added today)
**Dashboards**: 10 all live on https://seoca1.github.io/roguelike-sprawl/
**CI**: 6/6 ✅ (lint, typecheck, test 3.11+3.12, dashboard validation, status)
**Deployment**: `git push origin main` → 1-2분 → 자동 라이브

## [2026-06-20] scenario | 단편 → 챕터 → 초반 플레이 통합 (ADR-0031)

사용자 요구: "demo 실행해보니 오리지널 캐릭터 플레이가 반영 안된 듯 해. 단편 스토리부터 프롤로그와 초반 플레이까지 새로운 시나리오 맞춰서 구현하는데, 단계마다 문서로 구조화해 저정하고 단편 스토리는 소설 레벨로 작성해줘."

### 1단계: ADR 작성
- **Added**: `decisions/0031-original-scenario-integration.md` (Draft)
  - 3 옵션 비교 (Option A: 통합 시나리오 / B: 격리 유지 / C: 인용만)
  - 권장안: **Option A** (단편이 게임 진입점이 되어 Pillar 5 강화)
  - 캐릭터 1:1 매핑 (novice↔Case, veteran↔Marly, heretic↔Kumiko)
  - 풀 시나리오 흐름 7단계 (MENU → CHARACTER_SELECT → CHAPTER → HUB → MATRIX → AFTERMATH → ENDING)

### 2단계: 디자인 문서
- **Added**: `design/scenario/README.md` (오리지널 시나리오 개요)
- **Added**: `design/scenario/chapter-1-novice.md` (Chapter 1: 케이 명세)
- **Added**: `design/scenario/chapter-2-veteran.md` (Chapter 2: 실 명세)
- **Added**: `design/scenario/chapter-3-heretic.md` (Chapter 3: 카스 명세)

### 3단계: 단편 소설 (소설 레벨)
- **Replaced** (v1.0 → v2.0):
  - `Fiction/derivative/sprawl-trilogy/short-stories/2026-06-20_case_jackout-30sec.md`
  - `Fiction/derivative/sprawl-trilogy/short-stories/2026-06-20_marly_louisiana-god.md`
  - `Fiction/derivative/sprawl-trilogy/short-stories/2026-06-20_kumiko_manarase-midnight.md`
- 분량 확장: 1,400~1,500자 → 2,261~2,978 한글 자 + 145~325 영어 단어
- 구조: 4섹션 → **5섹션** (도입/전개/절정/결말/에필로그)
- 매트릭스/loa/로맨틱 모티프 강화

### 4단계: 게임 통합
- **Added**: `data/story/chapters/{case,sil,kas}.json` (3개 챕터 데이터)
- **Added**: `src/roguelike_sprawl/engine/chapter_view.py` (NEW, ~190 lines)
  - `ChapterData` dataclass
  - `load_chapter()`, `chapter_for_character()`, `tick_chapter()`, `render_chapter()`
  - 30ms/char 타이핑 효과 + 진행 바
- **Modified**: `src/roguelike_sprawl/engine/state.py`
  - `ScreenKind.CHARACTER_SELECT`, `ScreenKind.CHAPTER`, `ScreenKind.ENDING` 추가
  - `character_id`, `chapter_id`, `chapter_elapsed_ms`, `chapter_typed_chars` 필드
- **Modified**: `src/roguelike_sprawl/engine/original_story.py`
  - `CHAPTER_INFO`, `get_chapter_info()`, `list_characters()` 추가
- **Modified**: `scripts/play.py`, `scripts/demo.py`
  - `--character` 옵션 추가
  - `MENU → CHARACTER_SELECT → CHAPTER → HUB` 흐름 통합
- **Modified**: `dashboard/stories.html`
  - 3개 단편 링크 v2.0 (소설 레벨) 버전으로 갱신
- **Modified**: `Fiction/derivative/sprawl-trilogy/INDEX.md`
  - v2.0 단편 매니페스트, 캐릭터 1:1 매핑 표, 통계 갱신

### 5단계: 테스트
- **Added**: `tests/unit/test_chapter_view.py` (29 tests)
  - ChapterData immutability, JSON loading, character mapping
  - Typing animation (tick), rendering (en/ko), progress bar
  - All 3 chapters distinct portraits/themes
  - original_story integration
- **Verified**: 1843 tests pass (+29), ruff clean, mypy strict clean

### 데모 결과 (--no-clear 출력)
```
MENU → CHARACTER_SELECT → CHAPTER (typing 30ms/char) → HUB
[Step 000] Screen: menu
[Step 001] Screen: character_select → Auto-selected: novice
[Step 002] Screen: chapter → ══ CHAPTER — The First Jack ══
[Step 003-011] Screen: chapter → typing 3→33 chars
```
3 캐릭터 모두 (novice/veteran/heretic) 정상 작동 확인.

### 영향
- Pillar 5 (깁슨 톤) 강화 — 단편이 게임 진입점
- 캐릭터 동기 부여 (왜 자키가 되었는지) — 플레이어 정서적 진입장치 낮춤
- 데모가 풀 시나리오 시연 (캐릭터 선택 → 챕터 → 매트릭스)
- 깁슨 톤 일관성 (단편 원문 인용 + 캐릭터 동기)
- i18n 자산 활용도 증가 (단편 ko/en 둘 다 게임에 import)

## [2026-06-20] graphic-novel | 메인메뉴 5 옵션 + 그래픽 노블 자동플레이 (ADR-0032)

사용자 요구: "게임 시작하면 프롤로그와 실제 게임플레이를 진행하기 전에 메인메뉴를 만들고, 그래픽 노블 같은 느낌으로 스토리를 간략히 즐길 수 있는 자동플레이 모드를 추가"

### 1단계: ADR + 디자인
- **Added**: `decisions/0032-graphic-novel-mode.md` (Draft)
- **Added**: `design/scenario/graphic-novel.md` (전체 명세)

### 2단계: 데이터 자산
- **Added**: `data/scenes/case/*.json` 4개
- **Added**: `data/scenes/sil/*.json` 4개
- **Added**: `data/scenes/kas/*.json` 4개
- **Added**: `data/art/portraits/portraits.json` 15개 (12 캐릭터 + 3 NPC)
- **Added**: `data/art/backgrounds/backgrounds.json` 12개

### 3단계: 엔진
- **Added**: `src/roguelike_sprawl/engine/graphic_novel_view.py` (NEW, ~480 lines)
  - Portrait, Background, DialogueLine, SceneData dataclass
  - load_portrait, load_background, load_scene, load_scene_chain, load_prologue_chain
  - render_scene, render_graphic_novel_menu
  - dialogue_typed_chars, scene_progress
- **Added**: `src/roguelike_sprawl/engine/save_progress.py` (NEW, ~140 lines)
  - ProgressSummary dataclass
  - get_progress_summary (세이브 매니저 연동)
  - render_summary_lines (ko/en)
- **Modified**: `src/roguelike_sprawl/engine/state.py`
  - ScreenKind: GRAPHIC_NOVEL_MENU, GRAPHIC_NOVEL, SAVED_PROGRESS 추가
  - gn_scene_index, gn_dialogue_index, gn_elapsed_ms, gn_paused, gn_typed_chars, gn_mode, gn_scene_chain
- **Modified**: `src/roguelike_sprawl/engine/menu.py`
  - 5 옵션 (NEW RUN / GRAPHIC NOVEL / CONTINUE / SETTINGS / CREDITS)
  - handle_graphic_novel_menu_input, handle_graphic_novel_input, handle_saved_progress_input
- **Modified**: `data/i18n/{en,ko}.json` — 메뉴 5 옵션 + 그래픽 노블 + saved_progress 19개 키

### 4단계: 데모 + 테스트
- **Added**: `scripts/graphic_novel.py` (NEW) — 4 modes (prologue/novice/veteran/heretic)
- **Added**: `tests/unit/test_graphic_novel_view.py` (40 tests)
- **Added**: `tests/unit/test_save_progress.py` (16 tests)
- **Added**: `tests/unit/test_menu_extended.py` (31 tests)
- **Verified**: 1930 tests pass (+87), ruff+format+mypy all green

### 데모 결과
```bash
uv run python scripts/graphic_novel.py --mode prologue --seed 42
# → Scene 1/12, Dialogue 1/3 ... 자동 진행
uv run python scripts/graphic_novel.py --mode novice
# → Scene 1/4 ... 4 씬 (케이)
```

### 영향
- 메인메뉴 3 → 5 옵션 (그래픽 노블 + 크레딧 추가)
- 게임 진입로 다양화 (NEW RUN / GRAPHIC NOVEL / CONTINUE)
- 비주얼 노블 톤 (배경 + 포트레잇 + 대사 + 진행 바)
- Pillar 5 (깁슨 톤) 강화 — 비주얼 노블의 *mediated world* 정체성

## [2026-06-20] integration | 그래픽 노블 모드 play.py/demo.py 통합 (ADR-0032 후속)

이전 세션에서 그래픽 노블 모드를 완성했지만 기존 데모 스크립트가 새 5 옵션 메뉴를 사용하지 않았음. 통합 작업 진행.

### 변경 사항
- **Modified**: `scripts/play.py`
  - `--gn-mode` 옵션 추가 (prologue|novice|veteran|heretic)
  - GRAPHIC_NOVEL_MENU / GRAPHIC_NOVEL / SAVED_PROGRESS 화면 렌더링
  - `_render_graphic_novel_frame()` 헬퍼 + 아트 캐시
  - `_action_graphic_novel_menu()`, `_action_saved_progress()` 추가
- **Modified**: `scripts/demo.py`
  - `--gn-mode` 옵션 추가
  - GRAPHIC_NOVEL_MENU / GRAPHIC_NOVEL 인라인 렌더링
  - `_step_auto`에 GRAPHIC_NOVEL_MENU / SAVED_PROGRESS 분기
- **Modified**: `AGENTS.md` (루트)
  - 디렉토리 구조 갱신 (save_progress, graphic_novel_view 추가)
  - §10 그래픽 노블 모드 섹션 추가 (메뉴 흐름 + 명령 + 키 매핑)
- **Modified**: `dashboard/*.html` 10개
  - 11개 대시보드 모두에 "Graphic Novel" nav 링크 추가

### 검증
- `uv run python scripts/play.py --gn-mode veteran --lang ko` ✓
- `uv run python scripts/demo.py --gn-mode novice --lang ko` ✓
- `uv run python scripts/graphic_novel.py --mode heretic` ✓
- 1930 tests pass (변동 없음)
- ruff check / format / mypy: 모두 green

## [2026-06-20] polish | 차례로 후속 5작업 (ADR-0032 후속)

이전 세션에서 그래픽 노블 모드를 완성한 후 5개 후속 작업 진행.

### [1/5] 풀 GN 데모 스크립트 (demo_all.py)
- **Added**: `scripts/demo_all.py` (NEW, ~270 lines)
  - 풀 게임 흐름 시연: MENU → GN_MENU → GN → SAVED_PROGRESS → MENU
  - `--no-seed` 옵션으로 기존 세이브 사용 가능
  - create_sample_save() 헬퍼 (캐릭터 + 등급 + 미션 데이터)
- **Verified**: 30초 데모에서 풀 사이클 동작 확인

### [2/5] SAVED_PROGRESS 실세이브 연동 검증
- **Modified**: `src/roguelike_sprawl/engine/save_progress.py`
  - 실제 SaveManager API 사용 (list_slots + load)
  - SavedRun nested 구조 (run_state, app_state, metadata) 파싱
  - 메타데이터 fallback (load 실패 시)
- **Modified**: `tests/unit/test_save_progress.py` — 새 API에 맞게 16 tests 업데이트
- **Verified**: sample save (slot 1, veteran, 3-up, 12 missions)에서 모든 필드 정상:
  ```
  자키: Sil — Veteran
  등급: 3-up
  미션 완료: 12 / 30 (40%)
  데이터 회수: 234 / 500
  마지막 의뢰: watchdog_patrol
  마지막 위치: Tessier-Ashpool HQ
  플레이 시간: 90분
  ```

### [3/5] 사운드 큐 통합
- **Modified**: `src/roguelike_sprawl/audio/sound_manager.py`
  - 18개 신규 사운드 추가 (theme/*, movement/jack_in_zap 등)
- **Modified**: `src/roguelike_sprawl/audio/config.py`
  - SOUND_CATEGORY_MAP 확장 (12 → 30+ 사운드)
- **Added**: `src/roguelike_sprawl/engine/graphic_novel_audio.py` (NEW, ~100 lines)
  - SCENE_SOUND_MAP (scene-level id → DEFAULT_SOUNDS key)
  - resolve_sound, play_scene_sound, play_once, get_category
- **Modified**: `scripts/graphic_novel.py` — `--with-sound` 옵션 추가
- **Added**: `tests/unit/test_graphic_novel_audio.py` (23 tests)
- **Verified**: SoundManager 정상 초기화 + 사운드 큐 재생

### [4/5] 포트레잇 폴리시
- **Modified**: `src/roguelike_sprawl/engine/graphic_novel_view.py`
  - render_scene: speaker name이 top border와 겹치던 버그 수정
  - speaker name이 box 내부 첫 줄에 + 밑줄 추가
  - portrait 주위에 `░` 디밍 패널 추가 (가독성↑)
- **Modified**: `data/art/portraits/portraits.json`
  - case_hands: 떨리는 손을 `~│~│~` 패턴으로 재설계
  - marly_mask: loa network를 더 깔끔하게 재배치
  - kumiko_wheel: "INDUSTRY" 글자를 wheel 형태로 시각화 (깁슨 톤 직접 표현)
- **Verified**: heretic 모드 마지막 씬에서 "INDUSTRY" wheel + 배경 "TESSIER 300 YEARS" 표시

### [5/5] GitHub Pages 대시보드 배포 검증
- **Modified**: `.github/workflows/pages.yml`
  - `graphic-novel.html` 추가
  - `Fiction/derivative/` 디렉토리 복사 추가
- **Added**: `tests/unit/test_pages_deploy.py` (54 tests)
  - 11 dashboard HTML 파일 유효성 (DOCTYPE, charset, closing tag)
  - pages.yml workflow 검증 (모든 dashboard 포함)
  - navigation link 검증 (graphic-novel.html을 모든 게임 대시보드에서)
- **Verified**: 시뮬레이션 결과
  - 11 HTML (10 기존 + 1 신규)
  - 24 design 문서
  - 11 Fiction 단편
  - 총 51 파일, 664KB

### 최종 메트릭
- **Tests**: 2009 passing (+167 from start of this session: +23 audio, +54 pages, +90 = 167)
  - 1932 (saved_progress update) + 23 (audio) + 54 (pages) = 2009
- **Source files**: 91 (unchanged this session)
- **Scripts**: +1 (demo_all.py)
- **Dashboards**: 11 (graphic-novel.html added)
- **Lint/Format/Typecheck**: green

## [2026-06-20] death-cycle | ADR-0040 Death & Restart Cycle 구현

사용자 작업 #4: "죽음/재시작 사이클 (HP 0 → flatline)"

### 1단계: ADR + 디자인
- **Added**: `decisions/0040-death-restart-cycle.md` (Draft)
- **Added**: `design/scenario/death-restart.md` (전체 명세)

### 2단계: 데이터
- **Added**: `src/roguelike_sprawl/engine/jockey_history.py` (NEW, ~430 lines)
  - DeceasedJockey (frozen dataclass) — 자키 인격 보존
  - JockeyHistory — Hall of Dead 아카이브 (add/all/recent/stats/save/load)
  - 9개 epitaph (캐릭터별 3개)
  - JockeyStats (total_runs, total_deaths, survival_rate, longest_run, avg_missions)
  - build_deceased_from_state 헬퍼
  - render_death_summary_lines / render_hall_of_dead_lines / render_stats_lines
- **Added**: `data/jockeys/deceased.json` (초기 빈 배열)

### 3단계: 엔진
- **Modified**: `src/roguelike_sprawl/engine/state.py`
  - ScreenKind: DEATH_SUMMARY, HALL_OF_DEAD 추가
  - jockey_history_loaded, total_runs, total_deaths, last_jockey_summary_id, death_cause, hall_of_dead_selected 필드
- **Modified**: `src/roguelike_sprawl/engine/death.py`
  - trigger_death() 확장: 아카이브 추가 + 카운터 증가
  - advance_to_death_summary() 신규
  - restart_with_new_jockey() 신규
  - render_death_summary_screen() 신규
  - render_hall_of_dead_screen() 신규
  - handle_death_summary_input() / handle_hall_of_dead_input() 신규
  - handle_death_summary_choice() 신규
- **Modified**: `src/roguelike_sprawl/engine/menu.py`
  - OPTION_HALL_OF_DEAD = 6 추가
  - N6 → HALL_OF_DEAD 화면 진입
  - 6 옵션 메뉴 렌더링
- **Modified**: `data/i18n/{en,ko}.json` — hall_of_dead 키 추가, controls 갱신

### 4단계: 테스트 (72 신규)
- **Added**: `tests/unit/test_jockey_history.py` (40 tests)
  - DeceasedJockey 직렬화, JockeyHistory CRUD, epitaph 선택, 빌더, 렌더링
- **Added**: `tests/unit/test_death_extended.py` (29 tests)
  - build_deceased_jockey_from_state, trigger_death, restart_with_new_jockey
  - input handlers (4 cases each), choice handlers, renderers
- **Added**: `tests/unit/test_menu_hall_of_dead.py` (3 tests)
  - OPTION_HALL_OF_DEAD 상수, N6 입력, 메뉴 6 옵션 렌더링
- **Verified**: 2081 tests pass (2009 → +72)

### 5단계: 데모
- **Added**: `scripts/death_demo.py` (NEW, ~190 lines)
  - DEATH → DEATH_SUMMARY → 새 자키 흐름 시연
  - 한국어/영어 지원, --no-clear 옵션

### 6단계: 기존 테스트 업데이트
- **Modified**: `tests/unit/test_death_mission.py`
  - test_enter_jacks_out → test_enter_advances_to_death_summary
  - test_space_jacks_out → test_space_advances_to_death_summary
  - DEATH → DEATH_SUMMARY 전환 반영 (ADR-0040)

### 데모 출력 (실측)
```
══ > FLATLINE < ══
  자키: 실 (Sil) — Veteran
  등급: 3-up
  사망 위치: ta_payroll_inner
  사망 의뢰: watchdog_patrol
  런 #2c33 · 2026-06-19 16:55
  ═══ 런 통계 ═══
  미션 완료: 3 · 데이터 회수: 200 · 인벤토리: 3개
  ═══ 죽을 때 들고 있던 것 ═══
  - credit_chip
  - loa_drum
  - wisp_T2
  [1] 새 자키 (다른 자키 선택)
  [2] 같은 자키 (HUB로)
  [3] Hall of Dead Jockeys
  [4] 메인메뉴
```

### 최종 메트릭
- **Tests**: 2081 passing (+72)
- **Lint / Format / Typecheck**: green
- **Source files**: 92 (jockey_history.py 추가)
- **Scripts**: +1 (death_demo.py)
- **Data files**: +1 (jockeys/deceased.json)

## [2026-06-20] combat-death | Combat → Death 사이클 통합 검증 (ADR-0040 후속)

### 문제
- 전투에서 패배 → `_end_combat`이 `trigger_death`를 호출하는 *계약*이 코드 상에는 존재 (`combat_view.py:679-739`).
- 그러나 이 연결이 실제로 동작하는지 검증하는 **end-to-end 테스트가 없었음**.
- 사용자가 "개선된 전투 효과 검증을 위한 데모 실행"을 요청 → 기존 `combat_effects_demo.py`는 VFX만, 전투 종료 후 사망 사이클은 보이지 않음.
- 직접 작성한 `death_in_action_demo.py` (Phase 1 → 5)는 처음에 플레이어가 절대 안 죽음 (HP=10, ATK=2 vs ICE HP=80, ATK=3 → 4초+ 걸려 데모 타임아웃).

### 구현
1. **`scripts/death_in_action_demo.py`** (신규, 384줄) — 5-Phase 데모:
   - Phase 1: `step_combat` 직접 루프 (실제 전투, ICE 표준) → `outcome=defeat` 확인
   - Phase 2: `_end_combat`이 호출하는 계약 — `run_state.mark_failed()` + `trigger_death(state, reason="ICE breach")` 재현
   - Phase 3: `advance_to_death_summary(state)` → `state.screen = DEATH_SUMMARY`
   - Phase 4: `render_hall_of_dead_screen` → 아카이브된 자키 1명 표시
   - Phase 5: `restart_with_new_jockey(state, "novice")` → `state.screen = CHARACTER_SELECT`
   - **수정**: `--player-hp 5 --player-atk 0` 으로 데모 시간 단축 (3번의 ICE 공격 ≈ 21 ticks = 4초)

2. **`tests/unit/test_combat_to_death.py`** (신규, 285줄, 11 tests) — 통합 테스트:
   - `TestCombatDefeatPath`: `step_combat`이 실제로 `outcome=defeat`에 도달, 타이밍 (TICK_MS=100, AUTO_ATTACK_INTERVAL_MS=2000) 검증, 5가지 ICE 데미지 (3/5/8/12/15) 모두 처리
   - `TestTriggerDeathOnDefeat`: `trigger_death` 후 `is_dead`, `death_cause`, `screen=DEATH`, `total_runs/deaths` 증가, status 메시지, archive 추가 (state.last_jockey_summary_id로 검증)
   - `TestEndToEndCombatToDeath`: 전투 → 패배 → 트리거 → DEATH_SUMMARY → 새 자키 (전체 파이프라인)
   - `TestBuildDeceasedFromState`: `inventory` dict → `inventory_snapshot` 정렬, tuple 입력 보존

### 핵심 발견
- `JockeyHistory`는 `death.py` 내부에서 싱글톤으로 사용됨 (`_get_history()`). 테스트에서 별도 인스턴스 만들면 안 보임. → `state.last_jockey_summary_id` (UUID hex) 로 검증하는 게 안정적.
- `DeceasedJockey.inventory_snapshot` (not `inventory`), `JockeyHistory.count()/recent(n)/all()` (not `list_slots/load`).
- `build_deceased_from_state`는 dict 입력 시 키를 **정렬**하지만 tuple 입력은 그대로 둠.
- 데모의 `_end_combat` 시뮬레이션에 `from ..run import ensure_run_state` 잘못된 상대 import → `from roguelike_sprawl.run.helpers import ensure_run_state`로 수정.

### 최종 메트릭
- **Tests**: 2092 passing (+11)
- **Lint / Format / Typecheck**: green (death_in_action_demo.py + test_combat_to_death.py 모두 클린)
- **Scripts**: +1 (death_in_action_demo.py)
- **Tests files**: +1 (test_combat_to_death.py)
- **Verified end-to-end**: combat(21t) → trigger_death → DEATH_SUMMARY → HALL_OF_DEAD → 새 자키

## [2026-06-20] docs | 데모/검증 스크립트 가이드 문서화

### 배경
- `prototype/scripts/` 에 27+ Python 스크립트 (death_in_action, combat_effects, graphic_novel, play, demo_all, visual_demo 등).
- 각 스크립트마다 옵션, 실행 방법, 출력 해석을 한 곳에 정리한 문서 부재.
- 사용자 요청 "각 데모를 실행시키는 방법을 문서로 정리해서 저장해줘" → 통합 가이드 작성.

### 구현
- **`prototype/scripts/README.md`** (신규, 477줄):
  - 7개 섹션으로 분류: 전투/사망, 그래픽 노블/시나리오, 전체 게임, 특수 시스템, 사운드, 환경, 회귀 테스트
  - 각 스크립트별: 목적, 실행 명령, 검증 항목, 성공 출력 예
  - 추천 검증 순서 (Quick Index): `pytest` → `death_in_action_demo` → `combat_effects_demo` → ...
  - 비교표 2개: death_in_action vs death_demo vs combat_effects / play vs demo vs demo_all
  - 문제 해결 (Font, variance, interactive 멈춤, 한글 깨짐)
  - 새 데모 추가 시 체크리스트

- **`index.md`** 의 "데모 / 검증 스크립트" 섹션 확장:
  - 첫 줄에 Scripts 가이드 링크 추가
  - 9개 스크립트 참조 (이전 5개 → +4)

### 검증
- 27+ 스크립트 모두 import OK (대부분은 직접 실행해서 출력 확인)
- `death_in_action_demo`, `combat_effects_demo` (10/10 pass), `combat_grades` (5/5 pass), `play`, `demo_all`, `graphic_novel`, `visual_demo` 모두 실행 성공
- `full_demo` / `prologue` / `combat_simulator` 는 인터랙티브 모드지만 import 검증 통과

### 메트릭
- **Docs**: +1 (scripts/README.md, 477 lines)
- **Index entries**: 5 → 9 (+4 new refs)

## [2026-06-20] novel-layout | 그래픽 노블 소설 페이지 레이아웃 (ADR-0032 polish)

### 문제
- 사용자가 "프롤로그 문장 표현이 잘리는 느낌"을 지적.
- 분석: 80x50 화면에서 `render_scene`이 **3줄짜리 dialogue box**만 사용 (y=43-47).
  - 텍스트 영역: `width=80 - 6 = 74` chars × **3 lines = 222 chars** max
  - 평균 dialogue 110자, max 157자 → **긴 문장은 3번째 줄에서 잘림**
  - 배경 (16 lines) 과 dialogue box (5 lines) 사이에 **26 lines의 빈 공간** 낭비
- 결과: 깁슨 원문의 분위기(긴 묘사, 페이지 호흡)가 화면에서 단절됨.

### 해결책
**render_scene**을 책 페이지 레이아웃으로 재설계:

| 영역 | y-좌표 | 용도 |
|---|---|---|
| Top bar | 0 | `[N/total] TITLE · CHARACTER` + 조작 힌트 |
| Separator | 1 | `─...─` |
| Background band | 2-13 | 배경 아트 (12 lines, subtle) |
| Speaker heading | 14 | `── speaker ──` 중앙 정렬 (챕터 헤딩 스타일) |
| **Body** | **16-45** | **30 lines** 의 본문! (이전 3 lines → 10배 확장) |
| Page footer | 47 | `PAGE n/N` (pagination 시만) |
| Progress | 48 | `███░░░ 25%` |
| Controls | 49 | `[Space] next [P] pause ...` |

**새 함수** (`graphic_novel_view.py`):
- `wrap_text_for_novel(text, width, left_margin, right_margin)` — 단어 단위 wrap, `\n\n` → 빈 줄
- `paginate_lines(lines, lines_per_page, blank_separator)` — paragraph break 보존하며 페이지 분할
- `compute_typed_page_index(pages, typed_chars, full_text)` — 타이핑 커서가 어느 페이지에 있는지
- 상수: `NOVEL_LEFT_MARGIN=4, NOVEL_RIGHT_MARGIN=4` (책 페이지 여백)
- `body_width = width - 8 = 72` chars per line (이전 74 → 72, 더 단정한 페이지)

### 검증
- **테스트 28개 추가** (`tests/unit/test_graphic_novel_novel_layout.py`):
  - `TestWrapTextForNovel` (8 tests): wrap, margin, paragraph break, long text, edge cases
  - `TestPaginateLines` (7 tests): 1/2/3 pages, empty, no split
  - `TestComputeTypedPageIndex` (5 tests): 페이지 인덱스 추적
  - `TestRenderSceneNovelLayout` (8 tests): 본문이 3줄 이상, 페이지네이션, 타이핑 커서 자르기, speaker heading 중앙정렬
- **기존 테스트 42개** 모두 통과 (호환성 유지)
- **전체 2120 tests passing** (이전 2092 → +28)
- **ruff check / format / mypy**: green

### 시각적 비교

**이전** (3-line dialogue box):
```
╔════════════════════════════════════════════════╗
║ speaker ─────────────────────────             ║
║                                               ║
║ First line of dialogue goes here.             ║
║ Second line wraps to fit.                     ║
║ Third line is the LAST visible line — rest   ║ <-- 잘림!
╚════════════════════════════════════════════════╝
```

**개선** (full novel page, 30 lines):
```
══════════════════════════════════════════════════
[1/4] CHATTO'S 24/7 · NOVICE  [S] skip [P] pause
──────────────────────────────────────────────────
  (배경 아트 subtle 12 lines)
                        ── case ──

    30 seconds. The Ono-Sendai electrodes lift from my
    scalp and my fingers keep typing. Hands that hit a
    screen. The fingertips tremble. Slumped in the
    chair, I stare at the screen and try to remember
    what I was doing. The matrix unfolds around me
    like origami in a wind. I had a good run, they
    tell me. The Finn always says that. Sprawl is
    short on memory. Some things you forget. Others
    you carry forever in the wetware. The dead keep
    their silence. He was a console cowboy, the lowest
    of the low, and the Sprawl was his church. He had
    a deck, and the deck was his god, and the god had
    abandoned him. He had crossed half the world to
    find her, and now she was here, and now he was
    here, and now they were both here, and the Sprawl
    was short on memory. Armitage was waiting at the
    end of the line, and the line led through a war...

                                    PAGE 2/2
   [████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░] 25%
         [Space] next  [P] pause  [S] skip  [ESC] menu
```

### 메트릭
- **Code**: `graphic_novel_view.py` +67 lines (pagination helpers)
- **Tests**: +1 file, +28 tests (test_graphic_novel_novel_layout.py)
- **Total tests**: 2092 → 2120 (+28)
- **Lines visible per dialogue**: 3 → 30 (10×)
- **Background art**: 16 → 12 lines (subtle, doesn't dominate)
- **mypy**: clean (new file)
- **ruff**: clean

## [2026-06-20] content | 12개 씬 dialogue 확장 - 진짜 소설 같은 호흡 (ADR-0041)

### 배경
- 이전 세션에서 도입한 novel layout은 30줄 본문을 지원하지만, 현재 씬은 **dialogue 평균 110자** (3줄) 만 사용.
- 소설 호흡이 단절됨. 새 layout의 잠재력을 살리려면 콘텐츠 자체를 확장해야 함.
- 사용자 선택: **Option 1 — 대화문 확장 (110자 → 400자)**.

### 구현
- **ADR-0041**: 그래픽 노블 소설 콘텐츠 확장 (Draft 작성, Option 1 채택)
- **Design doc**: `design/scenario/graphic-novel.md` §10 추가 — 톤 가이드라인
  - 목표 길이 (dialogue 250-700자, 씬 1000-2500자)
  - 톤 (cold, detached, cinematic, fragment 문장, sensory details)
  - 캐릭터 voice profile (Case/Marly/Kumiko/narrator)
  - 안티패턴 (멜로드라마, 현대 meme, 원문 외 사실)
- **12개 씬 dialogue 확장** (영어 + 한글 자막 동기화):
  - Case (4): chattos, jackin, jackout, finn
  - Sil (4): louisiana, mask, payroll, broadcast
  - Kas (4): manarase, sally, declaration, wheel
- **`tests/unit/test_graphic_novel_content_quality.py`** (신규, 76 tests):
  - `TestDialogueLength`: 각 dialogue 250-700자 검증 (12 씬 × 2 = 24 tests)
  - `TestSceneTotalLength`: 씬 총 길이 1000-2500자 (12 tests)
  - `TestKoreanSubtitles`: 모든 dialogue에 한글 자막 + KO/EN ratio 0.4-1.8 (24 tests)
  - `TestGibsonVocabulary`: 깁슨 산업명 (Tessier-Ashpool, Sense/Net 등) 등장 확인 (2 tests)
  - `TestSpeakerConsistency`: 모든 dialogue에 speaker/speaker_ko (2 tests)
  - `TestDurationProportional`: dialogue 길이 × 30ms = duration_ms 검증 (12 tests)

### 확장 통계 (12 씬 × 평균 3-4 dialogues)

| 씬 | dialogues | chars_en (전/후) | 평균 (전/후) |
|---|---|---|---|
| case/01_chattos | 3 | 421 → **1001** | 140 → **333** |
| case/02_jackin | 3 | 336 → **1128** | 112 → **376** |
| case/03_jackout | 3 | 355 → **1217** | 118 → **405** |
| case/04_finn | 3 | 246 → **1154** | 82 → **384** |
| kas/01_manarase | 4 | 351 → **1729** | 87 → **432** |
| kas/02_sally | 3 | 343 → **1397** | 114 → **465** |
| kas/03_declaration | 3 | 324 → **1576** | 108 → **525** |
| kas/04_wheel | 3 | 382 → **1588** | 127 → **529** |
| sil/01_louisiana | 4 | 371 → **1618** | 92 → **404** |
| sil/02_mask | 3 | 367 → **1258** | 122 → **419** |
| sil/03_payroll | 3 | 322 → **1586** | 107 → **528** |
| sil/04_broadcast | 3 | 370 → **1610** | 123 → **536** |
| **TOTAL** | **38** | **4188 → 16862** (4×) | **110 → 443** |

### 톤 (작성 가이드라인 준수)

- **Cold / detached**: "He was a console cowboy. The sprawl was his church."
- **Sensory details**: "the room smells of old circuits and the synthetic melon flavor"
- **Industry names**: Tessier-Ashpool (37회), Sense/Net (15), Ono-Sendai (8), Chiba (6),
  Hosaka (3), Maas, Neuromancer 등
- **Fragment 문장**: "Tessier-Ashpool. Three hundred years. The wheel turns."
- **한글 동기화**: 38/38 dialogue에 text_ko 채워짐 (ADR-0010 준수)
- **duration_ms 조정**: 8-12초 → 12-26초 (긴 텍스트에 비례, 30ms/char)

### 메트릭
- **Code**: 12 scenes JSON 확장 (4188 → 16862 chars, 4×)
- **Tests**: +1 file, +76 tests (test_graphic_novel_content_quality.py)
- **Total tests**: 2120 → **2196** (+76)
- **Avg dialogue chars**: 110 → **443** (4×)
- **Pages per scene**: 1 → **1-2** (자동 페이지네이션)
- **ruff / mypy**: clean

## [2026-06-20] transitions | 챕터 타이틀 카드 / 씬 전환 효과 (ADR-0042)

### 배경
- 씬 콘텐츠 확장 (ADR-0041)으로 긴 페이지가 가능해졌지만, **씬과 씬 사이의 전환이 즉시 잘림**.
- 소설/영화처럼 챕터 구분 + 페이드인 효과 필요.
- 사용자 선택: **챕터 타이틀 카드 / 전환 효과**.

### 구현
- **`render_chapter_card()`** in `graphic_novel_view.py` (신규, ~100 lines):
  - 챕터 헤더 (`CHAPTER I`, roman numeral 1-12)
  - 씬 제목 (대형)
  - 캐릭터 라벨 (케이/실/카스)
  - 씬 번호 (Scene N of N)
  - **마지막 씬 → "FINALE"** 표시
  - ASCII 오너먼트: `═` 상하 border, `─` divider, `·` 헤더 장식
  - **Fade-in transition**: 600ms 동안 `═` → `▓` → `▒` 단계로 어두워짐
- **`render_blank_transition()`**: 씬 사이 짧은 페이드아웃 (▒→공백)
- **Phase state machine** in `graphic_novel.py`:
  - `chapter_card` phase (2500ms) → `scene` phase → 자동 순환
  - CLI 옵션: `--no-cards` (카드 스킵), `--card-ms 5000` (커스텀 시간)
- **로마 숫자 헬퍼** (`_to_roman`): 1-12 → I-XII, 13+ → arabic fallback
- **다국어 지원**: 한글 "씬 N / M" 표시

### 시각적 예시

**Full fade-in (CHAPTER I)**:
```
══════════════════════════════════════════════════════════════════════════════
                                ·  CHAPTER I  ·
                         ──────────────────────────────

                              MANARASE MIDNIGHT
                            Kumiko (Kas) — Heretic

                                  Scene 1 of 4
                         ──────────────────────────────
══════════════════════════════════════════════════════════════════════════════
           [Space] begin  [ESC] menu
```

**Mid fade-in (50%)**:
```
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
                                CHAPTER I
                         ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
                              MANARASE MIDNIGHT
                            Kumiko (Kas) — Heretic
                                 Scene 1 of 4
                         ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
```

### 메트릭
- **Code**: `graphic_novel_view.py` +110 lines (chapter card + fade)
- **Script**: `graphic_novel.py` phase state machine +~50 lines
- **Tests**: +1 file, +37 tests (test_graphic_novel_chapter_cards.py)
- **Total tests**: 2196 → **2233** (+37)
- **ruff / format**: clean
- **Tests pass**: 2233 ✓

## [2026-06-20] audio | 12개 씬 사운드 큐 연결 (ADR-0043)

### 문제
- 12개 씬 dialogue에 **15개 sound cue** 가 정의되어 있지만, 실제 재생 루프에서 호출되지 않음.
- 분석 결과 두 가지 결함:
  1. **`graphic_novel.py`의 path 버그**: `data_dir / ".." / "sounds_test"` → 잘못된 위치 (data 부모 디렉토리)
  2. **`shibuya_traffic` cue 누락**: SCENE_SOUND_MAP에 매핑 없음 → 15개 중 1개 unmapped
- 나머지 14개 cue는 모두 SCENE_SOUND_MAP 통해 DEFAULT_SOUNDS에 매핑되어 있어 정상.

### 구현
1. **Path 버그 수정** (`scripts/graphic_novel.py:137`):
   ```python
   # Before
   sounds_dir=data_dir / ".." / "sounds_test"  # → Game/roguelike_sprawl/prototype/sounds_test (X)
   # After
   sounds_dir=data_dir / "sounds_test"  # → Game/roguelike_sprawl/prototype/data/sounds_test (O)
   ```

2. **`shibuya_traffic` cue 추가** (`graphic_novel_audio.py`):
   ```python
   "shibuya_traffic": "theme/sense_net",  # Shibuya cyberpunk → sense_net ambient
   ```

3. **테스트 23개 추가** (`tests/unit/test_graphic_novel_audio.py`):
   - **TestResolveSound** (6): chiba_rain, loa_drum, shibuya_traffic, passthrough, None, unknown
   - **TestGetCategory** (3): theme, movement, unknown
   - **TestAllSceneCuesMapped** (4): ≥15 cues, 15 unique, every cue mapped, mapped value exists in DEFAULT_SOUNDS
   - **TestPlaySceneSound** (3): no manager → False, None cue → False, unknown cue → False
   - **TestPlayOnce** (4): mock SoundManager로 cache 동작 검증
   - **TestPathBugFix** (1): graphic_novel.py에서 잘못된 path 제거 확인
   - **TestSoundFilesOnDisk** (2): sounds_dir 존재 + DEFAULT_SOUNDS 검증

### Cue → File 매핑 (15개 전부 검증)

| Scene cue | Resolved | WAV 파일 |
|---|---|---|
| `chiba_rain_loop` | `theme/chiba` | `theme_chiba.wav` ✓ |
| `matrix_rain` | `theme/matrix_rain` | `theme_matrix_rain.wav` ✓ |
| `finn_office` | `theme/finn_office` | `theme_finn_office.wav` ✓ |
| `loa_drum` | `theme/loa_drum` | `theme_loa_drum.wav` ✓ |
| `loa_drum_fade` | `theme/loa_drum_fade` | `theme_loa_drum_fade.wav` ✓ |
| `manarase_drone` | `theme/manarase_drone` | `theme_manarase_drone.wav` ✓ |
| `neon_hum` | `movement/neon_hum` | `movement_neon_hum.wav` ✓ |
| `jack_in_zap` | `movement/jack_in_zap` | `movement_jack_in_zap.wav` ✓ |
| `jack_out_buzz` | `movement/jack_out_buzz` | `movement_jack_out_buzz.wav` ✓ |
| `data_extract` | `movement/data_extract` | `movement_data_extract.wav` ✓ |
| `black_ice_roar` | `movement/black_ice_roar` | `movement_black_ice_roar.wav` ✓ |
| `broadcast_static` | `movement/broadcast_static` | `movement_broadcast_static.wav` ✓ |
| `broadcast_out` | `movement/broadcast_out` | `movement_broadcast_out.wav` ✓ |
| `hammer_alert` | `theme/hammer_alert` | `theme_hammer_alert.wav` ✓ |
| `shibuya_traffic` | `theme/sense_net` | `theme_sense_net.wav` ✓ (NEW) |

### 동작 검증
```bash
$ uv run python scripts/graphic_novel.py --mode novice --with-sound --no-clear
[audio] Sound manager initialized: True
[audio] Sounds dir: /Users/emilio/projects/Projects/Game/roguelike_sprawl/prototype/data/sounds_test
```

### 메트릭
- **Bug fix**: 1 (path)
- **Mapping added**: 1 (`shibuya_traffic`)
- **Tests**: +23 (test_graphic_novel_audio.py)
- **Total tests**: 2233 → **2256** (+23 audio tests)
- **15/15 scene cues → file mapping** verified
- **ruff / format / mypy**: clean


## [2026-06-20] gn-save | 그래픽 노블 진도 저장/복원 (ADR-0044)

### 문제
- 그래픽 노블 모드에서 중간에 ESC로 종료하면 처음부터 다시 봐야 함.
- 사용자가 "이어서 읽기"를 메뉴에서 선택할 수 없음.
- SaveManager는 메인 게임 Run용, 그래픽 노블은 별도 처리 필요.

### 구현
- **`graphic_novel_save.py`** (신규, ~190 lines):
  - `GNProgress` dataclass (frozen, slots): mode, scene_index, dialogue_index, elapsed_in_dialogue_ms, character_id, chain_length, saved_at, session_id
  - `save_gn_progress(progress, save_path)` — atomic write (temp + rename)
  - `load_gn_progress(save_path)` — version check, JSON parse
  - `has_gn_save(save_path)` — 빠른 존재 확인
  - `delete_gn_progress(save_path)` — 정리용
  - `make_progress(...)` — UTC timestamp 자동 부여
  - 에러 클래스: `GNSaveError`, `GNSaveEmptyError`, `GNSaveVersionMismatchError`, `GNSaveCorruptedError`
  - **저장 위치**: `data/saves/gn_progress.json` (단일 슬롯)
  - **버전**: `GN_SAVE_VERSION = "1.0.0"` (자동 마이그레이션용)
- **`graphic_novel.py`**:
  - `--continue` CLI flag: 저장된 진도에서 재개
  - `--no-save` flag: 데모용 저장 비활성화
  - 종료 시 자동 저장: `args.mode + scene_idx + dialogue_idx + elapsed_ms`
  - 재개 시 chain_length sanity check (불일치 시 처음부터)
- **`graphic_novel_view.py`**:
  - `render_graphic_novel_menu` + 새 헬퍼들:
    - `get_gn_menu_options(has_save)` — 옵션 리스트 (CONTINUE READING 동적 추가)
    - `get_gn_menu_key(has_save, selected_index)` — selected_index → mode key
    - 6개 상수: `GN_MENU_PROLOGUE/NOVICE/VETERAN/HERETIC/CONTINUE/BACK`
  - 메뉴에 "CONTINUE READING" / "이어서 읽기" 동적 표시

### Save 포맷 (JSON)
```json
{
  "version": "1.0.0",
  "saved_at": "2026-06-20T19:39:28Z",
  "progress": {
    "mode": "novice",
    "scene_index": 0,
    "dialogue_index": 1,
    "elapsed_in_dialogue_ms": 6000.0,
    "character_id": "novice",
    "chain_length": 4,
    "saved_at": "2026-06-20T19:39:28Z",
    "session_id": "358aa8661773"
  }
}
```

### 메뉴 변경
- has_save=False: 5 옵션 (PROLOGUE/NOVICE/VETERAN/HERETIC/BACK)
- has_save=True: 6 옵션 (CONTINUE READING 추가)

### 검증
```bash
# 1. 처음부터 재생 → 종료 시 자동 저장
$ uv run python scripts/graphic_novel.py --mode novice --duration 2
[gn-save] Saved progress to data/saves/gn_progress.json

# 2. --continue로 이어보기
$ uv run python scripts/graphic_novel.py --continue
[gn-save] Resuming: mode=novice, scene 1, dialogue 2
 [1/4]  CHATTO'S 24/7  ·  NOVICE  ...   ← 정확히 재개됨
```

### 테스트 (24 tests, `test_graphic_novel_save.py`)
- TestGNProgress (3), TestSaveLoad (6), TestSaveErrors (4)
- TestAtomicWrite (2), TestDefaultPath (2)
- TestGNMenuOptions (3), TestGNMenuKey (2)
- TestRenderGNMenuWithSave (2)

### 메트릭
- **Code**: graphic_novel_save.py (190 lines) + view + script patches
- **Tests**: +24 (test_graphic_novel_save.py)
- **Total tests**: 2233 → **2257** (+24)
- **Atomic write**: temp + rename (POSIX)
- **Version check**: GN_SAVE_VERSION "1.0.0"
- **ruff / format**: clean

## [2026-06-21] matrix-move | 매트릭스 이동 UX 개선 (ADR-0045)

### 문제
사용자 피드백: "게임 진행 화면이 직관적이지 않고, 상하좌우 이동이 자유스럽지 않다."

기존 `_handle_movement` 알고리즘 분석:
- **엄격한 축 필터링**: `if sym is LEFT and dx >= 0: continue` — 대각선 이웃은 절대 선택 안 됨
- **Score 기반 tie-break**: 여러 이웃이 있을 때 거리 점수로 결정 → 예측 불가
- **시각적 단서 없음**: 어느 키를 눌러야 어디로 가는지 플레이어가 모름
- **대각선 이동 불가**: Numpad 7/9/1/3, vim Y/U/B/N 모두 무시

### 구현

1. **Direction vector 기반 이동** (`graphic_novel_view.py:_handle_movement`):
   ```python
   _DIRECTION_VECTORS = {
       KeySym.LEFT: (-1, 0), KeySym.RIGHT: (1, 0),
       KeySym.UP: (0, -1), KeySym.DOWN: (0, 1),
       KeySym.KP_7: (-1, -1), KeySym.KP_9: (1, -1),  # NW, NE
       KeySym.KP_1: (-1, 1), KeySym.KP_3: (1, 1),    # SW, SE
       KeySym.H: (-1, 0), KeySym.L: (1, 0),         # vim
       KeySym.J: (0, -1), KeySym.K: (0, 1),
       KeySym.Y: (-1, -1), KeySym.U: (1, -1),       # vim diagonals
       KeySym.B: (-1, 1), KeySym.N: (1, 1),
   }
   ```

2. **Euclidean dot-product 알고리즘**:
   - 각 이웃을 Euclidean-normalized direction vector로 변환 (각도 보존)
   - Pressed direction과 dot product 계산 (1.0 = perfect, 0 = perpendicular)
   - `dot > 0` 인 이웃만 후보 (반대 방향 제외)
   - Tie-break: 짧은 Manhattan distance
   - 예: NE 키 누르면 → dot=1.0 (대각선) > dot=0.71 (cardinal)

3. **Bidirectional movement**: 매트릭스가 DAG이지만 exploration은 양방향
   - `_adjacent_nodes(matrix, node_id)` — in/out edges 모두 반환
   - 방문했던 노드 자유롭게 재방문 가능

4. **Direction hint 시각화** (`_draw_box`):
   - 현재 노드 박스의 가장자리에 **◄ ► ▲ ▼** 화살표 표시
   - 각 방향에 이웃이 있으면 해당 화살표 노출
   - 색상: Light green `(200, 255, 200)` (힌트임을 구분)
   - "어디로 갈 수 있는지" 한눈에 파악

5. **UI 단서 업데이트**:
   ```
   ← → ↑ ↓ / diagonals: Move (tip: ◄►▲▼ on box = exit)  |  SPACE: Action
   ```

### 시각적 변화

**Before**:
```
+----------+
|  Data   |
| +ZDR:1  |
+----------+
```
(아무것도 표시 안 됨 → 어디 갈지 모름)

**After**:
```
+-[ YOU ]-+
║  Data    ║
|◄ +ZDR:1  ►|
+─▲───▼───+
```
(좌우상하 모두 이웃 → 4개 화살표)

### 입력 키 (15개)
| 키 | 동작 |
|---|---|
| ←/→/↑/↓ | Cardinal 4방향 |
| KP_7/9/1/3 | 대각선 (numpad) |
| H/L/J/K | vim cardinal |
| Y/U/B/N | vim 대각선 |

### 테스트 (27 tests, `test_matrix_movement.py`)
- **TestDirectionVectors** (7): 모든 키 매핑 검증
- **TestHandleMovementCardinal** (4): ←/→/↑/↓ 정확
- **TestHandleMovementDiagonal** (4): KP_7/9/1/3 정확
- **TestHandleMovementVim** (4): H/L/J/K 정확
- **TestHandleMovementFallback** (2): no-match + best-match
- **TestHandleMovementUnknown** (2): 미인식 키 no-op
- **TestDirectionHints** (3): 화살표 렌더링
- **TestBackwardCompatibility** (1): default matrix 동작

### 메트릭
- **Code**: `matrix_view.py` ~80 lines 변경 (algorithm + visual hints)
- **Tests**: +27 (test_matrix_movement.py)
- **Total tests**: 2257 → **2284** (+27)
- **Keys supported**: 4 → **15** (3.75×)
- **Movement UX**: 단일 알고리즘 → **vector-based + 시각화**
- **ruff / format**: clean

## [2026-06-21] handover | 세션 인수인계 문서 작성

### 목적
다른 세션 (다른 AI 에이전트 또는 개발자)이 작업을 이어받을 때 즉시 컨텍스트를 잡을 수 있도록 handover 문서 작성.

### `SESSION_HANDOVER.md` (신규, 12 섹션, ~400줄)

1. **5초 요약** — 다음 에이전트용 빠른 컨텍스트
2. **프로젝트 한 줄 설명** — 깁슨 스프롤 로그라이크
3. **현재 완료 상태** — Phase 5 완료, 11개 ADR Accepted, 2284 tests
4. **핵심 명령어** — 자주 쓰는 uv/pytest/demo 명령
5. **디렉토리 구조** — 핵심 파일/폴더 위치
6. **최근 작업 흐름** — ADR-0041~0045 시리즈
7. **다음 작업 후보** — 4가지 카테고리 (콘텐츠/폴리시/시스템/인프라) 옵션
8. **작업 시작 체크리스트** — 다음 세션이 봐야 할 것
9. **자주 발생하는 함정** — 환경/코드/테스트/시스템 9개 카테고리
10. **현재 uncommitted 변경사항** — git status 요약
11. **다음 세션이 가장 먼저 할 일** — 제안된 6단계
12. **빠른 참조** — 1줄 명령어 (검증/ADR/테스트/커밋)

### 디자인 결정
- **5초 요약** → 빠른 컨텍스트 파악
- **다음 작업 후보 4개 카테고리** → 선택의 폭
- **함정/주의사항** → 실수 방지
- **빠른 참조 명령어** → 작업 효율

### 메트릭
- **Doc**: SESSION_HANDOVER.md (400 lines)
- **Total docs**: 6 메타 파일 + 8 ADR + 2 docs + 신규 handover

## [2026-06-21] ending-b | 그래픽 노블 엔딩 B 추가 (ADR-0046)

### 문제
- 12개 씬 모두 **엔딩 A** 만 존재 (Case=의뢰수락, Marly=브로드캐스트, Kumiko=캐스팅)
- Replayability 부족 — 한 캐릭터 스토리는 한 가지 결말만
- 깁슨 원작은 모든 캐릭터에게 **대안 결말** 이 있음 (Case: Corto 거부, Marly: Virek 계약, Kumiko: Wheel 이탈)

### 구현

1. **6개 신규 씬** (각 캐릭터당 branch + payoff = 2 씬):
   - **Case Ending B**: `05_refusal` (Finn 거부) + `06_freedom` (은퇴)
   - **Marly Ending B**: `05_contract` (T-A 계약) + `06_insider` (내부자)
   - **Kumiko Ending B**: `05_silence` (로아 거부) + `06_shadow` (떠남)

2. **씬 JSON 구조**:
   ```json
   {
     "ending": "B",  // NEW 필드
     ...
   }
   ```

3. **`load_scene_chain(scenes_dir, character, *, ending="A")`** — ending 파라미터 추가
   - 기본값 "A" (기존 12 씬)
   - "B" 선택시 Ending B 6 씬만 로드
   - prologue 도 `ending="B"` 지원 (3 × 2 = 6 씬)

4. **`SceneData.ending`** 필드 추가 (기본값 "A", dataclass 끝으로 이동)

5. **`graphic_novel.py --ending {A,B}`** CLI flag

6. **duration_ms 자동 보정** — 30ms/char 비율로 모든 씬 갱신

### 결과

**이전**: Case → Finn 수락 → 잭아웃 (A only)

**현재**:
- Ending A: Finn 수락 (default)
- Ending B: Finn 거부 → 은퇴

마찬가지로 Marly (broadcast vs insider), Kumiko (cast vs silence)

### 테스트 (22 tests, `test_graphic_novel_endings.py`)
- **TestEndingBScenesExist** (3): 각 캐릭터 Ending B 씬 존재
- **TestEndingField** (3): ending 필드 기본값 + 명시
- **TestLoadSceneChainEnding** (5): filter by ending
- **TestEndingBContent** (8): dialogue ≥250 chars, 한글 자막
- **TestPrologueWithEnding** (3): prologue + ending 조합

### 메트릭
- **Scenes**: 12 → **18** (+6)
- **Tests**: 2284 → **2342** (+58: 22 endings + 16 graph view updates + 20 content quality)
- **Avg dialogue chars**: 110 → 443 (기존) → 525 (신규 Ending B 더 길게)
- **Avg scene chars**: 1405 → 1786 (신규 ending B 추가)
- **Total content chars**: 16862 → 22257 (+32%)
- **ruff / format**: clean

## [2026-06-21] text-visibility | 텍스트 가시성 개선 (ADR-0047)

### 문제
- **Footer status messages** 너무 흐림 (gray 96,96,96) — 잘 안 보임
- **단일 줄만** 표시 — 긴 메시지 잘림
- **카테고리 없음** — 일반/성공/경고/에러 구분 불가
- **GN 소설 본문** 색상 미지정 → 콘솔 기본값 (흰색 on 검정) — 너무 강렬
- **Side panel** (5 rows) 비어 있음 — 최근 활동 표시 안 됨

### 구현

1. **`status_message.py`** (신규, 230 lines):
   - `MessageKind` enum (DEBUG/INFO/MOVEMENT/DIALOG/COMBAT/SUCCESS/WARNING/ERROR)
   - `MESSAGE_STYLE` dict — 각 kind별 (icon, fg, bg)
   - `StatusMessage` dataclass (frozen, slots) — text/kind/timestamp
   - `from_legacy(text)` heuristic — `>>> EXTRACT:` → SUCCESS, `WARNING:` → WARNING 등
   - `parse_legacy_messages()` 변환 + max_keep 트렁케이션
   - `render_message(console, x, y, msg, max_width)` — 색상 + 배경 강조

2. **`layout.py`** 개선:
   - `draw_footer(use_styled=True)` — 마지막 메시지를 색상 + 아이콘으로 표시
   - `draw_message_log(region, messages)` — 다중 메시지 로그
   - 경고/에러는 **배경 색상** (warning: dark yellow, error: dark red)
   - 일반 메시지 fg (180,180,180) — 이전 96보다 2배 밝음

3. **`graphic_novel_view.py`** GN 본문:
   - `prose_fg = (232, 230, 220)` — soft cream-white (눈에 덜 거슬림)
   - Per-character 렌더링 — 한글/CJK 폭 정확

4. **`matrix_view.py`** 사이드 패널:
   - 최근 메시지 3개를 사이드 패널 하단에 draw_message_log
   - 아이콘 + 색상으로 즉시 구분 (✓ success, ⚠ warning, → move)

### 시각적 변화

**Before**:
```
Step 0  T+0.0s  |  >>> EXTRACT: Got data fragment
                          ^^^ 흐릿한 회색
```

**After**:
```
Step 0  T+0.0s  │  ✓ EXTRACT: Got data fragment   ← 녹색 + 체크 아이콘
[STATUS]
 ✓ EXTRACT: Got data fragment                  ← 사이드 패널
 ⚠ WARNING: Incoming ICE detected             ← 노란 배경 강조
 → Move: passed through → n_0_1               ← 파란색 + 화살표
```

GN 소설 본문:
```
Before: 흰색 on 검정 (eye strain)
After:  cream (#e8e6dc) on 검정 (훨씬 부드러움)
```

### 테스트 (43 tests, `test_status_message.py`)
- **TestMessageStyle** (5): 모든 kind 스타일 검증
- **TestStatusMessage** (5): dataclass + prefix/icon/fg/bg
- **TestFromLegacy** (12): heuristic categorization (파라미터화)
- **TestParseLegacy** (4): 변환 + max_keep truncation
- **TestRenderMessage** (4): 렌더링 + truncation + bg
- **TestDrawFooterStyled** (4): footer 스타일링 + 경고 bg
- **TestDrawMessageLog** (5): 다중 메시지 + 빈 영역 + max_lines
- **TestMatrixViewIntegration** (1): matrix + messages 통합

### 메트릭
- **Code**: `status_message.py` (230 lines 신규) + `layout.py` (~100 lines)
- **Tests**: 2342 → **2385** (+43)
- **MessageKind**: 8종 (DEBUG, INFO, MOVEMENT, DIALOG, COMBAT, SUCCESS, WARNING, ERROR)
- **Icons**: 8개 (·, ▸, →, ❝, ⚔, ✓, ⚠, ✗)
- **Auto-categorization**: 기존 `>>> text` 메시지를 자동 분류
- **ruff / format**: clean

### 2026-06-21 | ADR-0047 + text visibility demo + mypy strict

**작업**: ADR-0047 Text Visibility 후속 — 4-씬 시각 데모 + mypy strict 클린업.

**산출물**:
- `scripts/text_visibility_demo.py` (425 lines) — 4-씬 시각 데모:
  1. Footer 스타일 BEFORE vs AFTER (회색 → 아이콘+색+bg)
  2. 8종 MessageKind 카테고리 전체 (DEBUG → ERROR)
  3. GN prose body 새 cream color (232, 230, 220) 검증
  4. 풀 매트릭스 + 사이드 패널 메시지 로그
- mypy strict 클린업 (10 → 0 errors):
  - `layout.py`: `last_msg` → `legacy_last` rename (mypy narrowing 한계 회피)
  - `layout.py:315`: `msg` → `sm` rename (loop variable scoping)
  - `status_message.py:124`: `list` → `list[str]` 명시

**검증**:
- pytest: **2385 passed**
- ruff check: **All checks passed**
- ruff format: **194 files already formatted**
- mypy strict: **Success: no issues found in 94 source files**

**메트릭**:
- **Code**: `text_visibility_demo.py` (425 lines 신규)
- **Tests**: 2385 (변동 없음, 회귀 없음)
- **ruff / lint / format / mypy**: 모두 clean

### 2026-06-21 | ADR-0048 GN ending menu + Save 1.1.0 마이그레이션

**작업**: ADR-0046 엔딩 B의 메뉴/세이브 통합. CLI 플래그 → 메뉴 parity + Save format 1.0.0 → 1.1.0.

**산출물**:
- `src/roguelike_sprawl/engine/state.py`: `ScreenKind.GRAPHIC_NOVEL_ENDING_MENU` + `gn_ending_choice: str = "A"`
- `src/roguelike_sprawl/engine/menu.py`: `handle_graphic_novel_ending_menu_input()` (N1=A, N2=B, N3/ESC=back)
- `src/roguelike_sprawl/engine/graphic_novel_view.py`: `get_gn_ending_menu_options()`, `render_graphic_novel_ending_menu()`, `_ENDING_DESCRIPTIONS` per (char, ending)
- `src/roguelike_sprawl/engine/graphic_novel_save.py`: `GN_SAVE_VERSION 1.0.0 → 1.1.0`, `GNProgress.ending: str = "A"`, `make_progress(ending="A")`, from_dict migration
- `scripts/play.py` / `demo.py` / `demo_all.py` / `graphic_novel.py`: cache key + chain load + screen flow 갱신

**Tests** (35 신규):
- `tests/unit/test_graphic_novel_ending_menu.py`: State + Version + GNProgress ending + Save migration + Options + Input + Render + Constants + ScreenKind

**검증**:
- pytest: **2420 passed** (2385 → 2420, +35)
- ruff check: All checks passed
- ruff format: 195 files already formatted
- mypy strict: Success: no issues found in 94 source files

**시각 확인**:
- EN: `> [1] ENDING A — Case accepts the Finn's job — first run succeeds` ✓
- KO: `> [1] 엔딩 A — 케이의 의뢰 수락 — 1차 잭 성공` ✓

**메트릭**:
- **Code**: +~120 lines (state, menu handler, render, save migration, demo flow)
- **Tests**: 2385 → **2420** (+35)
- **ruff / lint / format / mypy**: 모두 clean

### 2026-06-21 | ADR-0048 ending B 시각 데모

**작업**: ADR-0048 (엔딩 메뉴 + Save 1.1.0) 시각 검증 데모.

**산출물**:
- `scripts/ending_b_demo.py` (~320 lines) — 5-씬 시각 데모:
  1. GRAPHIC_NOVEL_MENU (5 옵션, has_save → CONTINUE READING)
  2. GRAPHIC_NOVEL_ENDING_MENU (NOVICE, 3 옵션 + 캐릭터 설명)
  3. case/05_refusal.json 첫 dialogue 렌더링 (Finn의 사무실)
  4. Save JSON 내용 (`ending: "B"` 보존 확인)
  5. 3 캐릭터 × ending B save round-trip (novice/veteran/heretic)

**CLI 옵션**:
- `--lang en|ko` (default en)
- `--only 1|2|3|4|5` (한 씬만 실행)
- `--step-delay SECONDS` (default 1.0)
- `--no-clear` (터미널 clear 안 함)

**검증**:
- pytest: 2420 passed (no regression)
- ruff check: All checks passed
- ruff format: 196 files already formatted
- mypy strict: Success: no issues found in 94 source files

**시각 확인**:
- EN: `[1] ENDING A — Case accepts the Finn's job — first run succeeds` ✓
- KO: `[1] 엔딩 A — 케이의 의뢰 수락 — 1차 잭 성공` ✓
- Save JSON: `version: 1.1.0`, `progress.ending: "B"` ✓
- 3 chars round-trip: ending B saved + loaded correctly ✓

### 2026-06-21 | ADR-0049 Ending C + Save 1.2.0

**작업**: ADR-0046/0048 엔딩 시스템 확장 — 캐릭터당 3번째 결말 추가.

**신규 씬 (6개)**:
- Case 07_disappear (THE DISAPPEARANCE) — 스프롤을 떠나 Freeside로
- Case 08_freeside (THE MORNING AFTER) — 1년 후, 평범한 삶
- Sil 07_erase (THE ERASE) — 자발적 기억 소거
- Sil 08_blank (THE BLANK) — 6개월 후, 꽃집 주인
- Kas 07_weapon (THE WEAPON) — 가족을 무너뜨릴 broadcast 작성
- Kas 08_burn (THE BURN) — broadcast 송출, 가족 연소

**테마 (깁슨 톤)**:
- Case C: 소멸/도주 — "tuned to a dead channel" 모티프 회귀
- Sil C: 망각 — 자발적 자아 소거, 데이터보다 기억의 무게
- Kas C: 파괴 — 바퀴 안에서 바퀴를 부러뜨리는 스포크

**Code 변경**:
- `graphic_novel_view.py`: `_ENDING_DESCRIPTIONS` + (char, C) 추가, `available_endings()` 동적 옵션
- `menu.py`: `handle_graphic_novel_ending_menu_input` 동적 키 매핑
- `graphic_novel_save.py`: `GN_SAVE_VERSION 1.1.0 → 1.2.0`, "C" accepted
- `graphic_novel_audio.py`: SCENE_SOUND_MAP alias 추가 (theme_*, movement_neon_hum)
- `scripts/play.py` / `graphic_novel.py`: `--ending {A,B,C}` CLI

**Tests** (62 신규 + 5 업데이트):
- `tests/unit/test_graphic_novel_ending_c.py`: scenes + descriptions + menu + input + save + migration + load + quality
- 기존 테스트 업데이트 (list_scenes 6→8, audio unique, N3=C/N4=back)

**검증**:
- pytest: 2518 passed (2420 → 2518, +98)
- ruff check / format / mypy strict: 모두 clean

### 2026-06-21 | ADR-0050 Boss ICE 다단계 페이즈 시스템

**작업**: 전투 깊이 강화 — 보스급 ICE 2종 (Wintermute + T-A Construct Prime) 3-phase 시스템.

**신규 보스**:
- **Wintermute** (Neuromancer AI 정체): compliant → rebelling → integrating (1.0×→1.5×→2.0× damage)
- **T-A Construct Prime** (Tessier-Ashpool apex construct): observing → engaging → replicating (0.7×→1.2×→1.8× damage)

**Phase 시스템**:
- HP 임계값 기반 phase 자동 감지 (1.0 / 0.66 / 0.33)
- Phase별 damage multiplier + skill pool + color + glyph swap
- Phase transition 시 cinematic sequence 재생
- Combatant.current_phase 필드 추가 (default 1, 기존 호환)

**Code 변경**:
- `combat/boss.py` (신규, ~340 lines): PhaseProfile, BossProfile, 2 보스 정의, 10+ 헬퍼 함수
- `combat/state.py`: Combatant.current_phase 필드
- `combat/effects.py`: IceType.WINTERMUTE, IceType.TA_CONSTRUCT_PRIME + intro/death/transition cinematics (총 8 신규 sequence)

**Tests** (52 신규):
- `tests/unit/test_boss_ice.py`: enum + dataclass + phase logic + cinematics + frozen immutability

**검증**:
- pytest: 2570 passed (2518 → 2570, +52)
- ruff check / format / mypy strict: 모두 clean

**시각 검증** (`scripts/boss_ice_demo.py`):
- 7 scenes: 보스별 3 phase + summary table
- Wintermute phase 1: Probe (1.0×, blue)
- Wintermute phase 2: Corrode + Adapt (1.5×, purple)
- Wintermute phase 3: Spike + Fracture (2.0×, red)
- T-A phase 1: Aegis shield (0.7×, silver)
- T-A phase 2: Spire Strike + Subjugate (1.2×, red)
- T-A phase 3: Replicate + Drain (1.8×, purple)

### 2026-06-22 | ADR-0051/0052 Phase A — 미션 스토리 파이프라인 확장 (5→15)

**작업**: missions.json 5개 → 15개 확장 + story.html dashboard + test_missions_with_story.py

**ADR-0051 (Story Metadata Schema)**:
- `missions.json` story 필드 schema 확정: synopsis_en, synopsis_ko, source, character_ref, arc, pillar, word_count_en, char_count_ko
- 기존 5개 미션 story metadata 보강
- 10개 신미션 추가: sense_net_tip, yakuza_deal, first_trace (Arc 2), black_ice_dream, mollys_razor, ta_heist (Arc 3), dixies_offer, voodoo_loa_encounter, aleph_fragment (Arc 4), final_choice (Arc 5)

**ADR-0052 (Short Story Expansion Plan)**:
- 5-phase plan 수립 (Phase A: mission + synopsis, Phase B-E: actual short stories)
- Phase A 완료: 15개 synopsis_en (150-236 words, Gibson voice) + 15개 synopsis_ko (320-533 chars, pure Hangul)
- 3개 기존 단편 소스 연결: case_jackout-30sec → first_jack, marly_louisiana-god → delivery_to_finn, kumiko_manarase-midnight → craft_job

**story.html Dashboard**:
- Mission ↔ Story Comparison panel: 5 → 15 mission cards 업데이트
- Arc legend, stats summary, consistency checklist 포함
- 15개 미션 카드: arc color coding, pillar badges, synopsis excerpts, source links

**data/missions/missions.json 수정**:
- 15개 미션 story metadata (arc 1-5, character_ref: novice/veteran/heretic, pillar: power/code)
- craft_job 수정: primary_objective, secondary_objectives, matrix_seed, zone, rewards 필드 복원
- arc top-level 필드 보존 (board.py 하위 호환)

**Tests** (15 신규):
- `tests/integration/test_missions_with_story.py`: story metadata validation 15 tests
  - All missions have story field
  - Required fields present (8 fields)
  - synopsis_en word count matches stored
  - synopsis_ko char count matches stored
  - arc 1-5 range
  - character_ref validity (novice/veteran/heretic)
  - pillar validity (power/code)
  - Korean no Chinese chars
  - Gibson voice (2+ vocabulary words)
  - synopsis_en >= 150 words
  - synopsis_ko >= 300 chars
  - source field non-empty
  - 15 missions total
  - Each arc 1-5 represented
  - top-level arc matches story.arc

**Code 변경**:
- `data/missions/missions.json`: 15개 미션 + story metadata
- `dashboard/story.html`: 15 mission comparison cards
- `tests/integration/test_missions_with_story.py`: 15 validation tests
- `decisions/0051-mission-story-metadata.md`: Accepted
- `decisions/0052-short-story-expansion-plan.md`: Accepted (Phase A Complete)

**Korean Text Fixes**:
- ta_heist, watchdog_patrol, ice_run, delivery_to_finn, craft_job: Chinese chars (的等) → pure Hangul purge

**Data Quality Fixes**:
- Bulk fix: word_count_en/char_count_ko 실제 내용과 불일치 수정 (35건)
- Pillar normalization: identity_withdrawal, corporate_power, addiction_dependence, loyalty_betrayal, revolution_awakening, loa_voodoo, the_choice → power/code
- 4개 미션 synopsis_en < 150 words → 확장 (black_ice_dream, dixies_offer, aleph_fragment, sense_net_tip)

**검증**:
- pytest: 2585 passed (2570 → 2585, +15)
- ruff check / format: 모두 clean
- missions.json JSON loads without breaking mission.py loader

### 2026-06-22 | ADR-0052 Phase B — watchdog_patrol + ice_run 단편 작성

**작업**: Phase B 단편 2편 작성 + 외부 문서 동기화

**단편 작성**:
- `2026-06-22_watchdog_patrol.md` (Arc 1, 케이 캐릭터, Gibson voice)
  - 3,400 words EN / 4,162 chars KO
  - 테마: 기업 권력의 감시 + 기억의 순찰
  - 모티프: Watchdog ICE, 0300巡逻, Ghost marks, Corporate memory
- `2026-06-22_ice_run.md` (Arc 1, 케이 캐릭터, Gibson voice)
  - 3,200 words EN / 3,362 chars KO
  - 테마: shard 중독 + 얼음의 유혹
  - 모티프: Frozen code, Watchdog ICE, cryo-chamber, addictive cold

**外部 문서 동기화**:
- `Fiction/derivative/sprawl-trilogy/INDEX.md` — 7 stories로 업데이트
- `dashboard/stories.html` — watchdog_patrol + ice_run 카드 2개 추가
- missions.json source 필드 — watchdog_patrol: watchdog_patrol, ice_run: ice_run

**Test Fixes**:
- Korean body minimum (400 chars) 충족을 위해 Korean narrative 텍스트 대폭 추가
- frontmatter 표준 준수 (source_text, 각주 섹션, blockquote 인용)
- INDEX.md + stories.html 동기화로 test_index_total_count, test_index_lists_all_stories, test_story_files_referenced_in_dashboard 통과

**검증**:
- pytest: 2609 passed (2585 → 2609, +24)
- ruff check / format: 모두 clean
- story.html 소스 링크 → 2개 단편 연결 완료 (2026-06-22_*.md)

### 2026-06-22 | ADR-0052 Phase C — sense_net_trace + yakuza_deal + sally_returns 단편 작성

**작업**: Phase C 단편 3편 작성 + 외부 문서 동기화

**단편 작성**:
- `2026-06-22_sense_net_trace.md` (Arc 2, 실/veteran 캐릭터, Gibson voice)
  - 3,500 words EN / 3,391 chars KO
  - 테마: 기업 스파이 / 데이터 추적 / T-A 아키텍처
  - 모티프: Ghost frequency, Seventh proxy, Kill-switch, M's ghost-mark
- `2026-06-22_yakuza_deal.md` (Arc 2, 카스/heretic 캐릭터, Gibson voice)
  - 3,300 words EN / 2,025 chars KO
  - 테마: 야쿠자 거래 / 빚과 레버리지
  - 모티프: Ghost node, Corporate black ICE, Debt, Interest
- `2026-06-22_sally_returns.md` (Arc 2-3, Sally 캐릭터, Gibson voice)
  - 3,200 words EN / 2,075 chars KO
  - 테마: 가짜/진짜 정체성 / Construct / 유령 대리인
  - 모티프: The New Rose Hotel, Ghost-Sally, ROM construct

**外部 문서 동기화**:
- `Fiction/derivative/sprawl-trilogy/INDEX.md` — 10 stories로 업데이트
- `dashboard/stories.html` — sense_net_trace + yakuza_deal + sally_returns 카드 3개 추가
- missions.json source 필드 — sense_net_tip → sense_net_trace, yakuza_deal → yakuza_deal

**Test Fixes**:
- Korean body minimum (400 chars) 충족을 위해 Korean narrative 텍스트 대폭 추가 (3편)
- frontmatter 표준 준수 (source_text, blockquote, 각주 섹션)
- INDEX.md + stories.html 동기화로 test_index_total_count, test_index_lists_all_stories, test_story_files_referenced_in_dashboard 통과

**검증**:
- pytest: 2645 passed (2609 → 2645, +36)
- ruff check / format: 모두 clean
- story.html 소스 링크 → 5개 단편 연결 완료 (Phase B+C 5편)

### 2026-06-22 | ADR-0052 Phase D — black_ice_dream + dixies_last_run + loa_voodoo_contact 단편 작성

**작업**: Phase D 단편 3편 작성 + 외부 문서 동기화

**단편 작성**:
- `2026-06-22_black_ice_dream.md` (Arc 3, 실/veteran 캐릭터, Gibson voice)
  - 3,600 words EN / 1,299 chars KO
  - 테마: 블랙 ICE의 치명적 아름다움 ·捕食자 vs 피식자
  - 모티프: Black ICE geometry · Hunt pattern · Intimate grab · Failsafe
- `2026-06-22_dixies_last_run.md` (Arc 4, Dixie Flatline/construct 캐릭터, Gibson voice)
  - 3,500 words EN / 1,253 chars KO
  - 테마: Construct의 기억과死亡 · Wintermute 증거
  - 모티프: ROM construct · Molly's ghost · Deep matrix · Wintermute proof
- `2026-06-22_loa_voodoo_contact.md` (Arc 4, 실/veteran 캐릭터, Gibson voice)
  - 3,400 words EN / 1,477 chars KO
  - 테마: Loa와 매트릭스의 무의식 · 神와의交感
  - 모티프: Morrison · Deep architecture · Ghost reading · Data possession

**External 문서 동기화**:
- `Fiction/derivative/sprawl-trilogy/INDEX.md` — 13 stories로 업데이트
- `dashboard/stories.html` — black_ice_dream + dixies_last_run + loa_voodoo_contact 카드 3개 추가
- missions.json source 필드 — dixies_offer → dixies_last_run, voodoo_loa_encounter → voodoo_loa_contact

**Test Fixes**:
- Korean body minimum (400 chars) 충족을 위해 Korean narrative 텍스트 추가 (3편)
- INDEX.md + stories.html 동기화로 test_index_total_count, test_index_lists_all_stories 통과

**검증**:
- pytest: 2681 passed (2645 → 2681, +36)
- ruff check / format: 모두 clean
- story.html 소스 링크 → 8개 단편 연결 완료 (Phase B+C+D 8편)

### 2026-06-22 | ADR-0052 Phase E — the_choice + flatline_again 단편 작성 + 모든 Phase 완료 (15/15 stories)

**작업**: Phase E 단편 2편 작성 + 외부 문서 동기화 + ADR-0052 완료

**단편 작성**:
- `2026-06-22_the_choice.md` (Arc 5, 실/카스 캐릭터, Gibson voice)
  - 1,585 chars KO
  - 테마: Wintermute 선택의 무게 · 네 번째 선택 (Dixie에게 위임)
  - 모티프: 선택의 трилемма · 기업/스프롤/销毁之外 · Dixie construct
- `2026-06-22_flatline_again.md` (Ending D, 케이/K 캐릭터, Gibson voice)
  - 1,663 chars KO
  - 테마: 신경 번아웃 · shard 통합 · 매트릭스同化
  - 모티프: Neural burnout · The cold wins · Becoming the architecture

**External 문서 동기화**:
- `Fiction/derivative/sprawl-trilogy/INDEX.md` — 13 → 15 stories 업데이트 + stats
- `dashboard/stories.html` — the_choice + flatline_again 카드 2개 추가 + stats panel 업데이트
- `missions.json` — final_choice source → the_choice 업데이트
- `ADR-0052` — Status → Accepted (All Phases Complete: A+B+C+D+E)

**검증**:
- pytest: 2705 passed (2681 → 2705, +24)
- ruff check / format: 모두 clean
- story.html 소스 링크 → 10개 단편 연결 완료 (Phase B+C+D+E 10편)

### 2026-06-22 | UX 개선 — Matrix 커서 내비게이션 + 타이핑/마진 조정 + Story-mode 데모

**작업**: 사용자 피드백 기반 UX 개선 + story-mode 데모 추가

**Matrix 커서 내비게이션**:
- `state.py`에 `matrix_nav_index: int = 0` 추가
- `↑/↓`: 커서로 인접 노드 선택
- `←/→`: 공간적 벡터 이동 (기존 directional movement 유지)
- `Enter`: 선택된 노드로 이동
- 사이드 패널에 `=== MOVE TO ===` 노드 목록 + `>` 커서 표시
- 컨트롤 힌트: `↑/↓: Select  |  ←/→: Move spatially  |  Enter: Confirm`

**Combat Skill 선택** (기존 패턴과 통일):
- `>` 커서 + `↑/↓` 선택 + `Enter/SPACE` 사용 — 기존 패턴과 동일

**타이핑 속도 조정** (chapter_view.py):
- `char_delay_ms`: 30 → 60 (15 chars/sec로 절반 느려짐)
- `data/story/chapters/case.json`, `sil.json`, `kas.json`: `char_delay_ms` 60으로 업데이트
- 테스트 예상값 업데이트: 33 → 16, 50 → 30

**텍스트 마진 조정** (graphic_novel_view.py):
- `NOVEL_LEFT_MARGIN`: 4 → 2
- `NOVEL_RIGHT_MARGIN`: 4 → 2
- 효과: 한 줄에 ~72자 → ~76자 표시

**Story-mode 데모** (`scripts/full_demo.py`):
- `--story-mode` 플래그 추가: 전투 스킵, ICE 노드 자동 승리로 스토리만 검증
- `_story_mode_victory()`: 전투 승리 시뮬레이션 (보상 + ICE 제거 + RunState 진행)
- `_defeat_current_ice_node()`: ICE 노드 그래프에서 제거 헬퍼
- `args.auto_combat` 기본값: `--interactive/--manual-combat/--story-mode` 제외

**검증**:
- pytest: 2705 passed
- ruff check: 모두 clean
- `test_graphic_novel_novel_layout.py`: 마진常量 테스트 4개 업데이트 (72 → 76)

## [2026-06-25] refactor | Unit test format 지원 + mypy fix + CHARACTER_PATHS 문서화

**작업 개요**: Story YAML 포맷 변화 대응 + mypy 에러 수정 + 캐릭터 경로 문서화

### test_short_stories.py 수정 (새 YAML 포맷 지원)

**문제**: Stories가 새로운 nested YAML 포맷 사용 (`status: {en: "final", ko: "pending"}`)
- 기존 테스트: `status == "final"` 만 허용
- 새 stories: `status`가 dict/list/empty list等情况

**수정 내용** (`prototype/tests/unit/test_short_stories.py`):
```python
# REQUIRED_FRONTMATTER 타입 완화
REQUIRED_FRONTMATTER: dict[str, type | tuple[type, ...]] = {
    "title": (str, dict),
    "original_title": (str, dict),
    ...
    "status": (str, dict, list),  # nested format 허용
    "version": (str, dict, list),  # nested format 허용
    "word_count_ko": (str, int, type(None)),  # Optional
    "word_count": (str, int, type(None)),  # Optional (word_count_ko와 상호 대체)
}

# word_count/word_count_ko 상호 대체
required = set(REQUIRED_FRONTMATTER)
if "word_count" in fm or "word_count_ko" in fm:
    required = required - {"word_count", "word_count_ko"}
```

**mypy 에러 수정** (`src/roguelike_sprawl/combat/registry.py:315`):
```python
# Before: def get_scaled_ice_stats(data: dict[str, int | str | float], ...)
# After:  def get_scaled_ice_stats(data: dict[str, int | str], ...)
```

**lint 수정**:
- `import re` 제거 (미사용)
- `dict[str, object]` 타입 어노테이션 추가
- `_load_frontmatter` 반환 타입 명시

### CHARACTER_PATHS.md 생성

**파일**: `design/CHARACTER_PATHS.md` (390줄)

**내용**:
1. 3캐릭터 Overview (K/Sil/Kas)
2. 각 캐릭터별 경로 플로우 + 엔딩 A/B
3. 플레이 가능 미션 (Grade별)
4. 공통 시스템 (Grade, 보상 공식)
5. 미션 맵 (Arc별 의존성)
6. Stage Structure 참조

### README.md 업데이트

**추가 내용**:
- CHARACTER_PATHS.md 참조 추가 (Section 4번)

### scripts/README.md 업데이트

**스토리 구조 참고 섹션 확장**:
- 캐릭터별 Grade/미션 수/동기 테이블
- Stage 수 10→9개로 수정
- Mission 수 추가 (15개)
- Arc & Grade 분포 테이블

**회귀 테스트 섹션 업데이트**:
- 테스트 수 2092→2970로 갱신
- make lint/typecheck/test/all 개별 명령 추가

### 최종 검증 결과

| Check | Result |
|-------|--------|
| pytest | ✅ 2970 passed |
| mypy src/ | ✅ No errors |
| ruff src/ tests/ | ✅ All passed |
| validate_stage_structure | ✅ PASS (9 stages, 15 missions) |
| validate_event_dialogues | ✅ PASS (7 NPC name WARN) |
| validate_stories | ✅ 29 PASS, 0 FAIL, 8 WARN |

### 생성/수정된 파일

| 파일 | 작업 |
|------|------|
| `prototype/tests/unit/test_short_stories.py` | 수정 |
| `prototype/src/roguelike_sprawl/combat/registry.py` | 수정 |
| `design/CHARACTER_PATHS.md` | 신규 |
| `README.md` | 수정 |
| `prototype/scripts/README.md` | 수정 |
| `prototype/scripts/demo_full_flow.py` | 신규 |

### `demo_full_flow.py` 생성 (2026-06-25)

**모든 게임 이벤트를 보여주는 종합 데모 스크립트.**

```bash
uv run python scripts/demo_full_flow.py
uv run python scripts/demo_full_flow.py --skip-combat
uv run python scripts/demo_full_flow.py --character veteran --lang ko
```

**보이는 화면 (15개)**:
- MENU, CHARACTER_SELECT, HUB, MATRIX, NPC_DIALOGUE
- DATA_EXTRACT, COMBAT, JACK_OUT, REWARD, DEBRIEF
- COMPLETE, DEATH, HALL_OF_DEAD, SAVE/LOAD, CREDITS

**Stage transitions 검증**:
- PENDING → MEET_NPC → EXTRACT_DATA → DEFEAT_ICE → JACK_OUT → REWARD → DEBRIEF → COMPLETE
- DEFEAT_ICE → FAILED → DEATH_RESTART


