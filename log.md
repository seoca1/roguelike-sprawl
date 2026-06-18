# Roguelike Sprawl - Activity Log

LLM Wiki 패턴의 활동 기록. 시간 순으로 추가. 각 항목은 `## [YYYY-MM-DD] {kind} | {title}` 형식.

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
