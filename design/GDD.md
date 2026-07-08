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

자세한 명세는 `systems/` 참조. 모든 시스템이 문서화됨 (2026-07-08 기준).

| 시스템 | 문서 | 상태 | ADR |
| --- | --- | --- | --- |
| 전투 (RT-MS) | `systems/combat.md` | **완료** | ADR-0003, ADR-0014 |
| 사이버스페이스 / 해킹 | `systems/hacking.md` | **완료** | ADR-0005 |
| 미션 | `systems/missions.md` | **완료** | ADR-0017 |
| 진행 (메타) | `systems/progression.md` | **완료** | ADR-0008 |
| 경제 (재화) | `systems/economy.md` | **완료** | — |
| 인벤토리 / 장비 | `systems/inventory.md` | **완료** | — |
| 대화 / NPC | `systems/dialogue.md` | **완료** | — |
| 절차적 생성 | `systems/procgen.md` | **완료** | ADR-0005 |
| Story Archive | `systems/story-archive.md` | **완료** | ADR-0009 |
| i18n | `systems/i18n.md` | **완료** | ADR-0010 |
| Crafting | `systems/crafting.md` | **완료** | ADR-0015 |
| Jockey Avatar | `systems/avatar.md` | **완료** | ADR-0016 |
| Animations | `systems/animations.md` | **완료** | ADR-0018 |
| Aftermath & Subtitles | `systems/aftermath.md` | **완료** | ADR-0019 |
| ASCII Portraits | `systems/ascii-portraits.md` | **완료** | ADR-0011 |
| Difficulty Rating (PPL & ZDR) | `systems/difficulty-rating.md` | **완료** | ADR-0012 |
| Story Events | `systems/story-events.md` | **완료** | ADR-0013 |
| 탐험 / Fog of War | `systems/exploration.md` | **완료** | ADR-0020 |
| Grade Progression | `systems/grade-progression.md` | **완료** | — |
| Plot Skeleton | `story_skeleton.md` | **완료** | ADR-0031 |

## 5. Content Pillars

### 의뢰 유형 (구현됨)

| 유형 | 설명 | 구현 |
|------|------|------|
| **Data Extraction** | 파일/데이터 탈취 (가장 흔함) | ✅ |
| **Sabotage** | 시스템 파괴 | ✅ |
| **Construct Retrieval** | AI construct 추출 | ✅ |
| **Surveillance** | 정보 수집 | ✅ |
| **Black Ops** | 다른 자키 해킹/제거 | ✅ (limited) |
| **ICE Bypass** | 방어선 뚫기 | ✅ |
| **Counter-Intelligence** | 흔적 지우기 | ✅ |

실제 미션 예시: `missions.json` (47 missions, 5 zones 균형)

### 적 유형 (구현됨)

| 유형 | 설명 | 구현 |
|------|------|------|
| **ICE** | probe, watchdog, bulldog, asp, hellhound 등 41 types | ✅ |
| **Black ICE** | 치명적, trace 진행 | ✅ |
| **Boss ICE** | Wintermute, T-A Prime 3-phase | ✅ (ADR-0050) |
| **Hostile Deckers** | NPC 자키 (limited) | ✅ |
| **AIs / Constructs** | 보스급 (Dixie, Loa) | ✅ |

### 의뢰인/세력 (구현됨)

| 세력 | 설명 | 구현 |
|------|------|------|
| **The Finn** | Fixer — 주요 중개인 | ✅ |
| **Tessier-Ashpool (T-A)** | corporate, Deep zone | ✅ |
| **Hosaka** | corporate, Core zone | ✅ |
| **Sense/Net** | corporate, Surface/Mid zone | ✅ |
| **Yakuza** | 일본 마피아, Mid zone | ✅ |
| **Lo Teks** | 궤도 난민 | ✅ |
| **Panther Moderns** | 자키 게릴라 | ✅ (limited) |

## 6. 결정된 사항 (Decided)

### 핵심 결정 (ADR-0001 ~ ADR-0020)

| ADR | 제목 | 상태 |
|-----|------|------|
| ADR-0001 | 엔진/프레임워크 (libtcod + Python) | **Accepted** |
| ADR-0002 | 비주얼 스타일 (Pure ASCII) | **Accepted** |
| ADR-0003 | 전투 시스템 (RT-MS) | **Accepted** |
| ADR-0004 | 코드 아키텍처 (ECS-lite) | **Accepted** |
| ADR-0005 | 사이버스페이스 표현 (노드 그래프) | **Accepted** |
| ADR-0006 | 런 구조 (로그라이크 vs 로그라이트) | **Accepted** |
| ADR-0007 | 플랫폼 타겟 (macOS + Windows) | **Accepted** |
| ADR-0008 | 진행 / 레벨업 시스템 | **Accepted** |
| ADR-0009 | Story / News 전달 시스템 | **Accepted** |
| ADR-0010 | i18n + Content Pipeline | **Accepted** |
| ADR-0011 | ASCII Portraits | **Accepted** |
| ADR-0012 | Combat Difficulty (PPL & ZDR) | **Accepted** |
| ADR-0013 | Story Events System | **Accepted** |
| ADR-0014 | Data Salvage (전투 보상) | **Accepted** |
| ADR-0015 | Material & Crafting System | **Accepted** |
| ADR-0016 | Jockey Avatar | **Accepted** |
| ADR-0017 | Mission-Material Integration | **Accepted** |
| ADR-0018 | Combat Animation | **Accepted** |
| ADR-0019 | Combat Aftermath & Subtitles | **Accepted** |
| ADR-0020 | Fog of War + Exploration | **Accepted** |

### Phase 6~7 결정 (ADR-0030 ~ ADR-0061)

| ADR | 제목 | 상태 |
|-----|------|------|
| ADR-0030 | GitHub Utilization Plan | **Accepted** |
| ADR-0031 | Original Scenario Integration | **Accepted** |
| ADR-0032 | Graphic Novel Auto-Play Mode | **Accepted** |
| ADR-0040 | Death & Restart Cycle | **Accepted** |
| ADR-0041~0044 | Graphic Novel Content Expansion | **Accepted** |
| ADR-0046~0049 | Graphic Novel Endings + Saves | **Accepted** |
| ADR-0050 | Boss ICE System (Wintermute + T-A) | **Accepted** |
| ADR-0051 | Mission Story Metadata | **Accepted** |
| ADR-0052 | Short Story Expansion Plan | **Accepted** |
| ADR-0060 | Dungeon Exploration Redesign | **Accepted** |
| ADR-0061 | Novel Integration Architecture | **Accepted** |

### Phase 8~10 결정 (ADR-0090 ~ ADR-0102)

| ADR | 제목 | 상태 |
|-----|------|------|
| ADR-0090 | Salvation Phase Integration | **Accepted** |
| ADR-0101 | Fiction Metadata Backfill | **Accepted** |
| ADR-0102 | v1.0.0-beta.1 Release | **Accepted** |

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

### 미해결 / 열린 질문 (2026-07-08 기준)

| 질문 | 상태 | 비고 |
|------|------|------|
| 한 런의 목표 길이 (30/60/90분) | ⏳ 열린 질문 | 플레이어 피드백 필요 |
| 한국어 톤 가이드 (깁슨 한국어 차용) | ⏳ 열린 질문 | ADR-0010 참조 |
| Arc trigger 조건 (등급/unlock/선택) | ✅ 해결 (ADR-0031) | 챕터 JSON + arc 데이터로 구현 |
| Hub 표현 | ✅ 해결 | 텍스트 메뉴 + cyberspace construct |
| Story Archive 카테고리/검색 | ✅ 해결 (ADR-0009) | 4 카테고리 + StoryEvents로 확장 |
| Construct 동료 시스템 | ✅ 해결 (limited) | Dixie Flatline dialogue만 구현 |

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
