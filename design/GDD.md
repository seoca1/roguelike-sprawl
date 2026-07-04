# Game Design Document (GDD)

## 1. Concept

**One-liner**: 사이버스페이스에서 콘솔 카우보이로 플레이하는 로그라이크.

**Hook**: 죽으면 끝. 그러나 더 좋은 데크, 프로그램, construct로 돌아와서 더 어려운 시스템에 침투한다.

**Setting**: 윌리엄 깁슨 스프롤 3부작. 보스턴-애틀랜타 메트로폴리스와 L5 궤도 식민지.

**Tone**: 거칠고, 어둡고, 명료한 사이버펑크.

**주인공 (Player Character)**: 소설에 출현하지 않은 새로운 decker. 핸들(별명)만 플레이어가 선택. meatspace는 절대 시각화되지 않음 — 게임의 *유일한* 시각적 공간은 cyberspace (ADR-0009).

**meatspace 전달 방식**: 뉴스 / 이야기 (Story Archive). 의뢰 briefing, 의뢰 결과, 월드 뉴스, faction 움직임, construct 대화가 텍스트로 전달되며 메인 메뉴에서 다시 볼 수 있음.

**언어 (i18n)**: 영어 1차 (Gibson 톤 직접 보존) + 한글 보조 번역/자막. 표시 모드: Off (영어만) / Subtitle (영어+한글) / Replace (한글만). 모든 in-game 텍스트는 `data/i18n/en.json` (1차) + `data/i18n/ko.json` (보조)에서 로드 (ADR-0010).

**Reference**:
- Neuromancer / Count Zero / Mona Lisa Overdrive (world, lore)
- Caves of Qud / Cogmind (mechanics reference — 사이버 + 로그라이크)
- Hacknet / Bitburner (해킹 + 게임)
- Netrunner TCG (해킹 미학)
- (반대) Cyberpunk 2077 / Shadowrun (톤 회피)

## 2. Player Experience

플레이어가 게임 중 느끼는 것:

- **데이터가 흐르는 매트릭스 안에서 항해** — 시각적으로 강렬
- **ICE의 압박** — 시간이 지날수록 위험 증가
- **도구의 진화** — 매 런 새로운 프로그램을 손에 넣음
- **의뢰의 결과** — 죽음 또는 보상, 둘 다 명확
- **거친 미래** — 깁슨 톤의 비관적 매력

## 3. Game Structure

### 한 런의 구조
- **Job Board**: 3~7개 의뢰 중 선택
- **Prep**: 데크/프로그램/웨웨어 로드
- **Infiltration**: 메트스페이스 → 매트릭스 진입
- **Matrix Run**: 미션 수행
- **Extraction**: 매트릭스 이탈
- **Reward**: 보상 획득 또는 death

### 메타 진행
- 새 데크 unlock (Ono-Sendai Cyberspace 7, SAMSARA 등)
- 새 프로그램 unlock (Goliath, Kraken, Wisp, Wardrone 등)
- 새 construct unlock (Dixie 류, 픽스처 AI)
- 의뢰 라인 / 클라이언트 진행 (light, optional)

## 4. Core Systems

자세한 명세는 `systems/` 참조.

| 시스템 | 문서 | 상태 |
| --- | --- | --- |
| 전투 | `systems/combat.md` | **작성됨 (ADR-0003 + ADR-0014)** |
| 사이버스페이스 / 해킹 | `systems/hacking.md` | 미작성 |
| 미션 | `systems/missions.md` | 미작성 |
| 진행 | `systems/progression.md` | 미작성 |
| 경제 | `systems/economy.md` | 미작성 |
| 인벤토리 | `systems/inventory.md` | 미작성 |
| 대화 | `systems/dialogue.md` | 미작성 |
| 절차적 생성 | `systems/procgen.md` | 미작성 |
| **Story Archive** | `systems/story-archive.md` | 미작성 (ADR-0009) |
| **i18n** | `systems/i18n.md` | 미작성 (ADR-0010) |
| **Combat** | `systems/combat.md` | **작성됨 (ADR-0003 + ADR-0014)** |
| **Crafting** | `systems/crafting.md` | **작성됨 (ADR-0015)** |
| **Jockey Avatar** | `systems/avatar.md` | **작성됨 (ADR-0016)** |
| **Missions** | `systems/missions.md` | **작성됨 (ADR-0017)** |
| **Animations** | `systems/animations.md` | **작성됨 (ADR-0018)** |
| **Aftermath & Subtitles** | `systems/aftermath.md` | **작성됨 (ADR-0019)** |
| **ASCII Portraits** | `systems/ascii-portraits.md` | **작성됨** (ADR-0011) |
| **Difficulty Rating (PPL & ZDR)** | `systems/difficulty-rating.md` | **작성됨** (ADR-0012) |
| **Story Events** | `systems/story-events.md` | **작성됨** (ADR-0013) |
| **Plot Skeleton** | `story_skeleton.md` | **작성됨** (5 arcs + 4+ endings + 이벤트) |

## 5. Content Pillars

### 의뢰 유형 (예정)

- **Data Extraction** — 파일 탈취 (가장 흔함)
- **ICE Bypass** — 특정 시스템의 방어선 뚫기
- **Black Ops** — 다른 자키 해킹 / 제거
- **Construct Retrieval** — AI construct 추출
- **Sabotage** — 시스템 파괴
- **Surveillance** — 정보 수집
- **Counter-Intelligence** — 다른 자키의 흔적 지우기

### 적 유형 (예정)

- **ICE** — 다양한 종류 (예: probe, watchdog, bulldog, asp)
- **Black ICE** — 치명적
- **Worms / Viruses** — 감염
- **Hostile Deckers** — 다른 자키
- **AIs / Constructs** — 알 수 없는 construct (보스급)

### 의뢰인 (예정)

- **Fixer** (The Finn 류) — 중개인
- **Corporate** (T-A, Hosaka, Maas) — 기업
- **Yakuza** — 일본 마피아
- **Panther Moderns** — 자키 게릴라
- **Lo Teks** — 궤도 난민
- **Construct** — AI 의뢰 (드물게)

## 6. 결정된 사항 (Decided)

### 모든 핵심 결정 완료 (10/10)
- **ADR-0001**: libtcod + Python ✓
- **ADR-0002**: Pure ASCII ✓
- **ADR-0003**: AP 턴 전투 ✓
- **ADR-0004**: ECS-lite + 데이터 주도 ✓
- **ADR-0005**: 노드 그래프 ✓
- **ADR-0006**: 하이브리드 (unlock만 메타) ✓
- **ADR-0007**: macOS + Windows ✓
- **ADR-0008**: 런 내 스탯 고정 + 자키 등급 (메타) ✓
- **ADR-0009**: Story/News 시스템 ✓ — meatspace 미표시, Story Archive
- **ADR-0010**: i18n + Content Pipeline ✓ — en 1차 + ko 보조, 데이터 주도, plot bones 사전 정의
- **ADR-0011**: ASCII Portraits ✓ — Pure ASCII 보강, 인물/객체 시각 식별, cyberspace only
- **ADR-0012**: Difficulty Rating (PPL & ZDR) ✓ — 명시적 숫자, soft difficulty, 회피 가능
- **ADR-0013**: Story Events ✓ — 소설 스토리 부가 콘텐츠, 아이템/program/construct 보상
- **ADR-0014**: Data Salvage ✓ — 전투 승리 보상 (HEAL 20%, FRAG/CRED Phase 6+)
- **ADR-0015**: Material & Crafting ✓ — 5 raw → 4 components → program/item/construct (3-tier)
- **ADR-0016**: Jockey Avatar ✓ — 스틱 피규어, 부위별 stat 표현
- **ADR-0017**: Mission-Material Integration ✓ — 6 미션 타입, Hub 4-패널, Recipe 트리 뷰
- **ADR-0018**: Combat Animation ✓ — Normal 240ms gray vs Skill 600ms color, 깁슨 톤 글리치
- **ADR-0019**: Combat Aftermath & Subtitles ✓ — 후일담 4 importance + 소설 인물 7명 반응 + 한글 자막

자세한 것은 `decisions/README.md` 참조.

### Plot Skeleton (주요 줄기 뼈대)

상세: `design/story_skeleton.md`

- **5 arcs**: First Run → The Sprawl → Corporate Ice → The AIs → The Choice
- **4+ endings**: Sprawl Returns, AI Awakens, Lo Tek, Flatline
- **초반 우선**: Arc 1 (1-3 jobs) — Phase 5에서 우선 구현
- **반복 보강**: 무한 side content, faction 뉴스, world events

### 디자인 영향 (Accepted 결정으로 제약)
- **Pillar 2 (The Matrix)**: ASCII 노드 그래프 + *유일한* 시각적 공간
- **Pillar 3 (The Flatline)**: 스탯 고정 = 한 자키의 무게
- **Pillar 4 (The Build)**: 자키 등급 + unlock + Story Archive로 표현
- **Pillar 5 (The Style)**: 깁슨 톤 + ASCII + mediated world + 다국어
- **콘텐츠**: 데이터 주도, 초반 우선, plot bones 사전 정의

### 추가 미해결 디자인 질문 (Phase 4 이후 결정)
- 매트릭스의 노드 그래프 깊이 / 구조 (구체적 수치)
- 알람 / trace 메카닉의 구체적 수치
- 한 런의 길이: 30분, 60분, 90분?
- 의뢰 난이도 시스템
- 자키 등급 상승 조건 (정확한 수치)
- unlock 트리 디자인
- 노드 그래프 절차적 생성 알고리즘
- **Story Archive**: 카테고리, 검색, 시간 이벤트 시스템
- **Hub 표현**: 텍스트 메뉴 vs 작은 노드 그래프
- **Construct 대화**: Dixie 류 동료 시스템
- **한국어 톤 가이드**: 깁슨 톤의 한국어 차용
- **엔딩 발동 조건**: 정확한 world state 트리거
- **Arc trigger**: 자키 등급 / unlock / 선택

## 7. Living Spec

이 문서는 살아있는 스펙이다. 매 디자인 결정은 `decisions/`에 ADR로 기록되고, 본 문서와 `systems/`가 그에 따라 갱신된다.

### 동기화 규칙
- 새 시스템 추가 시 `systems/`에 명세 작성
- 명세 변경 시 `testcases/`에 시나리오 추가
- 의뢰 유형 추가 시 `missions.md`에 명세
- 적 추가 시 `combat.md`에 명세

## 8. 비-기둥 (회피)

`pillars.md` 참조. 명시적으로 만들지 않을 것들:

- Loot grind, Multiplayer, Skins, Daily login, Infinite scaling, Prestige, Mobile/F2P
