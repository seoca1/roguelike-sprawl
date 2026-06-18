# Roguelike Sprawl - 단계별 계획 (Roadmap)

## 전체 흐름

```
Phase 0: 문서 시스템 기반       [완료]
    ↓
Phase 1: 세계관 정리 (World Bible)
    ↓
Phase 2: 디자인 명세 작성
    ↓
Phase 3: 핵심 기술 결정         [현재 대기]
    ↓
Phase 4: 개발 환경 구축 (코드 스켈레톤)
    ↓
Phase 5: 핵심 시스템 프로토타입 (Vertical Slice)
    ↓
Phase 6: 콘텐츠 제작
    ↓
Phase 7: 알파 빌드
```

각 단계는 직전 단계의 결과에 의존하지만, **사용자 결정**(Phase 3)은 어느 시점에서든 끼워넣을 수 있다. 디자인 명세(Phase 2)와 결정(Phase 3)은 병행 가능하다.

---

## Phase 0: 문서 시스템 기반

**목표**: 지속 가능한 문서 체계 구축. LLM과 사용자가 함께 진화시킬 수 있는 구조.

**완료 조건**:
- [x] 디렉토리 구조 (raw / wiki / design / testcases / decisions)
- [x] 메타 문서 (README, AGENTS, index, log, ROADMAP, SETUP_LOG)
- [x] 디자인 문서 골격 (GDD, 시스템 명세, 디자인 기둥)
- [x] 결정 기록 템플릿 (ADR)
- [x] 테스트 케이스 템플릿

**상태**: 완료

---

## Phase 1: 세계관 정리 (World Bible)

**목표**: 깁슨 스프롤 3부작의 핵심 세계관을 위키에 정리. 디자인의 일관성 reference. **Fiction wiki를 Primary source로 통합 (2026-06-17 완료)**.

**완료 조건**:
- [x] `wiki/world/sprawl_universe.md` — Fiction cross-ref, 소설 등장인물 활용
- [x] `wiki/world/cyberspace.md` — Fiction 상세 (사회 구조, 톤, 상징)
- [x] `wiki/world/factions.md` — Loa/Vodou, Biosoft, Simstim 추가
- [x] `wiki/world/glossary.md` — meat, biosoft, simstim, loa, microsofts, trode 등
- [x] `wiki/world/style_guide.md` — Fiction source 명시
- [x] `AGENTS.md` — "World Source: Fiction wiki" 규칙
- [ ] `raw/` 에 원본 자료 (스프롤 3부작 텍스트) 추가 (선택)
- [ ] Fiction wiki에서 더 깊은 인용 보강 (필요시)
- [ ] 게임용 추가 세계관 확장 (corporations, zones, 의뢰 라인)

---

## Phase 2: 디자인 명세 작성 (Game Design Spec)

**목표**: 게임의 디자인을 명문화. 사용자가 직접 수정 가능한 "활성 스펙".

**완료 조건**:
- [x] `design/pillars.md` - 디자인 기둥 (5개, Pillar 2 강화됨)
- [x] `design/core_loop.md` - 매크로/미시 루프 (Hub도 cyberspace 안)
- [x] `design/GDD.md` - GDD 골격
- [x] `design/glossary.md` - 게임 용어 (Story / i18n / portrait 용어 추가)
- [x] `design/story_skeleton.md` - **메인 줄기 뼈대 (5 arcs + 4+ endings)** (ADR-0010)
- [x] `design/systems/ascii-portraits.md` - **ASCII Portrait 시스템** (ADR-0011)
- [x] `design/systems/difficulty-rating.md` - **PPL & ZDR 난이도 가시화** (ADR-0012)
- [x] `design/systems/story-events.md` - **Story Events (소설 스토리 부가 이벤트)** (ADR-0013)
- [x] `design/systems/combat.md` - **전투 시스템 명세 (RT-MS + PPL/ZDR + Data Salvage, ADR-0003 + ADR-0014)**
- [x] `design/systems/story-events.md` ✓ (이벤트 시스템은 작성됨) → **event data 작성** 필요
- [x] `design/systems/hacking.md` - **사이버스페이스 해킹 명세 (ADR-0005)**
- [x] `design/systems/missions.md` - **미션 시스템 + 재료 통합 (ADR-0017)**
- [x] `design/systems/animations.md` (신규, ADR-0018)
- [x] `design/systems/aftermath.md` (신규, ADR-0019)
- [x] `design/systems/exploration.md` (신규, ADR-0020)
- [ ] `design/systems/progression.md` - 진행/레벨업 명세 (Item Tier T1~T5 + PPL)
- [ ] `design/systems/economy.md` - 재화/거래 명세
- [x] `design/systems/crafting.md` - **3-tier 재료 & 조합 시스템 (ADR-0015)**
- [x] `design/systems/avatar.md` - **자키 아바타 — 스탯 시각화 (ADR-0016)**
- [ ] `design/systems/inventory.md` - 인벤토리/장비 명세 (티어 시스템 + PPL 계산)
- [ ] `design/systems/dialogue.md` - NPC/대화 명세
- [ ] `design/systems/procgen.md` - 절차적 생성 명세 (ZDR 매핑)
- [ ] `design/systems/story-archive.md` - Story/News 시스템 명세 (ADR-0009)
- [ ] `design/systems/i18n.md` - i18n 시스템 명세 (ADR-0010)
- [ ] `design/balance/` - 밸런스 노트 (PPL 공식, ZDR 공식, 티어별 stat)
- [ ] `testcases/` 에 시스템별 시나리오 작성

### Phase 2 콘텐츠 우선순위 (ADR-0010)
1. **Plot bones** (필수) — `story_skeleton.md` ✓
2. **초반 미션** (Phase 5 우선) — Arc 1의 1-3개 의뢰
3. **Side content** (반복 추가) — 무한

---

## Phase 3: 핵심 기술 결정 (Tech Stack)

**목표**: 엔진/프레임워크/아키텍처 결정. `decisions/`의 ADR을 Accepted 상태로.

**결정 항목** (모두 결정됨):
- [x] `0001-engine-framework.md` - libtcod + Python
- [x] `0002-rendering-style.md` - Pure ASCII
- [x] `0003-combat-system.md` - AP 턴
- [x] `0004-code-architecture.md` - ECS-lite + 데이터 주도
- [x] `0005-cyberspace-representation.md` - 노드 그래프
- [x] `0006-run-structure.md` - 하이브리드 (unlock만 메타)
- [x] `0007-platform-target.md` - macOS + Windows
- [x] `0008-progression-system.md` - 런 내 스탯 고정 + 자키 등급

**완료 조건**:
- [x] 모든 ADR Accepted
- [x] 선택된 기술 스택이 디자인 명세의 제약을 충족
- [x] 8/8 결정 일관성 확인 (decisions/README.md)

**상태**: 완료 (2026-06-17)

---

## Phase 4: 개발 환경 구축 (Dev Environment)

**목표**: 실제 코드를 작성할 수 있는 환경 셋업.

**완료 조건**:
- [x] `prototype/` 에 프로젝트 스켈레톤 생성 (uv + pyproject.toml)
- [x] `src/roguelike_sprawl/` 디렉토리 구조 확정 (engine, ecs, i18n, portraits, data)
- [x] 빌드 시스템 셋업 (hatchling + uv)
- [x] 테스트 프레임워크 셋업 (pytest, 27 tests passing)
- [x] 린트/포맷터 셋업 (ruff check + format)
- [x] 타입 체커 셋업 (mypy strict)
- [x] CI 셋업 (GitHub Actions, macOS + Windows)
- [x] 에디터 설정 (.editorconfig, .vscode/)
- [x] 첫 hello-world 실행 — "You jack in. The world goes gray." 표시
- [x] 폰트 다운로드 (libtcod terminal font)
- [x] `AGENTS.md` 갱신 (코딩 규칙)

**상태**: 완료 (2026-06-18)

---

## Phase 5: 핵심 시스템 프로토타입 (Vertical Slice)

**목표**: 게임의 핵심 한 사이클이 동작하는 상태.

**프로토타입 범위**:
- [x] 매트릭스 진입/이탈 — Hub → Jack-in → Matrix → Jack-out
- [x] 노드 그래프 절차적 생성 — `MatrixGenerator` (deterministic, Surface 한정)
- [x] 미션 1~2개 — `JobBoard` + `data/missions/missions.json` (first_jack, watchdog_patrol)
- [x] PPL & ZDR 표시 — HUD + 노드별 status 색상
- [x] 화면 상태 머신 — Menu / Hub / Matrix
- [x] Data Salvage 디자인 (ADR-0014) — HEAL 20%, FRAG/CRED Phase 6+
- [x] Crafting 시스템 디자인 (ADR-0015) — 3-tier, 5 raw → 4 components → final, Info Market
- [x] Jockey Avatar 디자인 (ADR-0016) — 스틱 피규어, 부위별 stat 표현
- [x] Mission-Material 통합 디자인 (ADR-0017) — 6 미션 타입, Hub 4-패널, Recipe 트리
- [x] Combat Animation 디자인 (ADR-0018) — Normal vs Skill ASCII 애니메이션
- [x] Aftermath & Subtitles 디자인 (ADR-0019) — 후일담 4-importance + 소설 인물 7명 + 한글 자막
- [ ] 전투 한 판 — 플레이어 vs ICE 한 종 (RT-MS, 다음 세션) + Salvage 통합
- [ ] 데크/프로그램 1~2개 작동 — programs.json 데이터는 있음, 인벤토리 미구현
- [ ] 죽음 → 재시작 → 메타 진행 사이클 (combat 의존)
- [x] ASCII 렌더링 1프레임 — 노드 박스 + 연결선

**완료 조건**:
- "Play a run" 가능 (미션 선택 → 잭인 → 노드 이동 → 잭아웃)
- 모든 핵심 시스템이 최소한 동작
- 밸런스는 placeholder 값 OK

**예상 소요**: 5~10 세션 (1 완료)

**세션 진행 (2026-06-18)**:
- [x] 매트릭스 진입 + 노드 그래프
  - matrix 모듈 (node, zdr, ppl, graph, generator, labels)
  - missions 모듈 + data
  - 엔진 state machine (menu/hub/matrix)
  - 80 tests passing
  - `make all` green
- [x] Data Salvage 결정 (ADR-0014)
  - design/systems/combat.md (신규)
  - testcases/combat/salvage.md (신규)
  - core_loop.md, glossary.md, GDD.md 갱신
- [x] Crafting 결정 (ADR-0015) + data/crafting JSON (materials, recipes, market)
- [x] Jockey Avatar 결정 (ADR-0016)
- [x] Mission-Material 통합 결정 (ADR-0017) + data/missions/missions.json 확장
- [x] Combat Animation 결정 (ADR-0018) + data/animations/frames.json
- [x] Aftermath 결정 (ADR-0019) + data/story/{aftermath,reactions}.json + i18n 확장
- [x] Fog of War 결정 (ADR-0020) + matrix/exploration.py + matrix_view.py Fog 렌더링 + 미니맵 + breadcrumb
- [x] **Quick Demo 스크립트 (`scripts/play.py`)**
  - 단일 명령 자동 진행: `uv run python scripts/play.py`
  - Menu → Hub → Matrix (Fog) → Hub 사이클
  - 기본 30s, 옵션: --duration, --step-delay, --no-clear, --lang, --seed, --mission
- [x] **Combat Simulator (developer/QA tool)**
  - `combat/` 모듈: state.py (Combatant, Skill, CombatState, step_combat, use_skill), registry.py (ProgramRegistry, IceRegistry)
  - `data/combat/ice_types.json` (5 ICE 타입)
  - `scripts/combat_simulator.py` (CLI)
  - `tests/unit/test_combat.py` (17 tests)
  - 97 tests passing
  - `make all` green
- [x] **Grade Progression (5단계 전투 검증)**
  - 5등급 (1-up to 5-up) 전투 + 결과 이벤트 검증
  - `scripts/combat_grades.py` — 5등급 자동 실행 + 비교표
  - `data/programs/programs.json` 확장 (strike, hammer, wardrone, virus)
  - `tests/unit/test_grade_progression.py` (13 tests)
  - `design/systems/grade-progression.md` (신규)
  - 110 tests passing
  - `make all` green
  - design/systems/combat.md (신규)
  - testcases/combat/salvage.md (신규)
  - core_loop.md, glossary.md, GDD.md 갱신

**다음 세션 (Vertical Slice 계속)**:
- 전투 (RT-MS): ICE 진입 시 실시간 자동 공격 + 메뉴 스킬
- Action menu: 노드 진입 시 scan/extract/engage/communicate
- 데이터 추출 성공 → 미션 완료 → 보상 → Hub

---

## Phase 6: 콘텐츠 (Content Pipeline)

**목표**: 다양한 미션, 적, 도구를 추가하여 replayability 확보.

**작업**:
- [ ] ICE 타입 N개 (블랙 ICE, 와치독, 킬러 등)
- [ ] 프로그램 카탈로그
- [ ] 데크 카탈로그
- [ ] 웨웨어 카탈로그
- [ ] 미션 템플릿 N개
- [ ] 의뢰인/픽서 NPC 카탈로그
- [ ] 톤/문체 가이드 (대화, 로그 등)
- [ ] 절차적 생성 규칙

**완료 조건**:
- 한 런이 30~60분 분량
- 매 런이 의미 있게 다름
- 적어도 20개 이상의 미션이 생성 가능

---

## Phase 7: 알파 빌드

**목표**: 외부 테스트 가능한 빌드.

**작업**:
- [ ] 튜토리얼/온보딩
- [ ] 사운드/비주얼 폴리시 (placeholder → 의도된 자산)
- [ ] 세이브/로드
- [ ] 옵션 (해상도, 키맵, 색맹 모드)
- [ ] 크래시 리포팅
- [ ] 빌드/배포 파이프라인

---

## 현재 위치

**현재 Phase**: Phase 4 완료 → **Phase 5 진행 중 (1/5~10 세션)**
**완료된 세션**:
- [x] 매트릭스 진입 + 노드 그래프 (2026-06-18) — 80 tests, all checks green
- [x] Combat Simulator (developer/QA tool) (2026-06-18) — 97 tests, all checks green
- [x] Grade Progression (5단계 검증) (2026-06-18) — 110 tests, all checks green
- [x] Fog of War + Exploration (ADR-0020) (2026-06-18) — 124 tests, all checks green
- [x] Quick Demo 스크립트 (`scripts/play.py`) (2026-06-18)

**차순 작업**:
1. **전투 (RT-MS)** — `design/systems/combat.md` 작성 + ICE 진입 시 자동 공격 + 메뉴 스킬
2. **Action menu** — 노드 진입 시 행동 선택
3. **의뢰 완료 / 보상** — 데이터 추출 성공 시 미션 종료 + Hub 복귀
4. **죽음/재시작** — HP 0 → flatline 화면 → 새 자키
5. Phase 6: Mid / Core / TA zone 콘텐츠 보강
