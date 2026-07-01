---
title: Roguelike Sprawl - 프로젝트 가이드
date: 2026-07-01
tags: [game, gibson, cyberpunk, python]
version: 0.4.0
---

# Roguelike Sprawl - 프로젝트 가이드 (v0.4)

## 프로젝트 개요

**깁슨 스프롤 3부작 세계관의 사이버펑크 로그라이크**

플레이어는 콘솔 카우보이(console cowboy)가 되어 사이버스페이스에서 ICE를 뚫고 데이터를 탈취합니다. 깁슨 톤 (cold, detached, cinematic)을 게임 플레이 전반에 반영합니다.

### 기술 스택

- **언어**: Python 3.11+ (3.12, 3.14 호환)
- **엔진**: python-tcod 21+
- **아키텍처**: ECS-lite (Entity Component System)
- **테스트**: pytest (3894 passing, 3962 collected, 24 xfailed)
- **린트**: ruff check / format
- **타입 체크**: mypy strict
- **의존성**: pyproject.toml + uv

### 콘텐츠 카운트 (2026-07-01)

| 항목 | 수량 | 비고 |
|---|---|---|
| 미션 | 38 | Arc 1-5 + 4 suit-persona |
| 단편 (EN+KO 페어) | 41 | Fiction/derivative/sprawl-trilogy/short-stories/ |
| Stage enum | 13 | PENDING/BRIEFING/TRAVEL/MEET_NPC/EXTRACT_DATA/BYPASS_SECURITY/DEFEAT_ICE/JACK_OUT/REWARD/DEBRIEF/COMPLETE/DEATH_RESTART/FAILED |
| 캐릭터 아크 | 4 | Case (Novice) / Sil (Veteran) / Kas (Heretic) / Suit |
| 챕터 (playable) | 6/15 | 9 future |
| 엔딩 (A/B/C) | 3 | GN 메인 + 6 ending 씬 |
| 업적 | 28 | dashboard/achievements.html |
| 설정 | 30+ | dashboard/settings.html |
| 대시보드 | 11 | index/stages/novel/story/cyberspace/dungeon/combat/equipment/graphic-novel/player/sound |

---

## 1. 캐릭터별 진행 경로 (4 캐릭터 × 15 미션)

### 1.1 캐릭터 구성

| ID | 이름 | 아키타입 | Deck Tier | 무기 | 동기 | 단편 매핑 |
|---|---|---|---|---|---|---|
| `novice` | 케이 (K) | Novice | T1 | Wisp (T1) | 빚 갚기 (생존) | Case (Neuromancer) |
| `veteran` | 실 (Sil) | Veteran | T2 | Hammer (T2) | 복수 (T-A) | Marly (Count Zero) |
| `heretic` | 카스 (Kas) | Heretic | T3 (bio) | Viral Sermon | 시스템 폭로 | Kumiko (MLO) |
| `suit` | (4-persona) | Corporate | T1-T3 | Variable | 임무 수행 | Armitage / Hosaka / T-A / Wintermute |

### 1.2 Stage Flow (13 stages)

```
PENDING → BRIEFING → TRAVEL → MEET_NPC → EXTRACT_DATA
                                          ↓ (optional)
                                       BYPASS_SECURITY → DEFEAT_ICE
                                          ↓
                                       JACK_OUT → REWARD → DEBRIEF → COMPLETE
                                          ↓
                                       FAILED → DEATH_RESTART → PENDING
```

**Phase B 추가** (2026-07-01): `BRIEFING` / `TRAVEL` / `BYPASS_SECURITY` (10→13 stages)

### 1.3 미션 Grade 분포 (38 missions)

| Arc | Grade 범위 | 미션 수 | 대표 미션 |
|-----|-----------|--------|----------|
| 1 | 1-2 | 6 | first_jack, watchdog_patrol, tutorial_maze |
| 2 | 1-5 | 11 | sense_net_infiltration, wigan_call, first_trace, craft_job |
| 3 | 3-4 | 10 | hosaka_core, straylight_approach, maas_heist, black_ice_dream |
| 4 | 4-5 | 7 | aleph_fragment, dixies_offer, ta_defection |
| 5 | 5-6 | 4 | final_choice, neuromancer_merger, zion_express |

**신규 추가 (2026-07-01)**: `sense_net_infiltration`, `wigan_call`, `hosaka_core`, `straylight_approach`, `maas_heist`

### 1.4 보상 공식

```python
credits = arc × 800 + (grade - 1) × 300
materials = mission.rewards.materials  # per-mission JSON 정의
```

---

## 2. 소설 통합 (Novel Integration, ADR-0061)

### 2.1 4-Layer Hook Dispatch

```
Fiction/derivative/sprawl-trilogy/short-stories/*.md
         ↓ catalog.py (자동 스캔)
NovelCatalog (41 entries, en+ko 페어)
         ↓ manifest.py (단편→hook 추론)
NovelManifest (stem → HookKind 매핑)
         ↓ dispatcher.py (런타임)
HookAction (NARRATIVE/EXCERPT/EVENT/COMBAT/ITEM/CINEMATIC)
         ↓ engine/novel_integration.py (신규)
AppState.status_messages / active_event / inventory
```

### 2.2 런타임 자동 호출 (2026-07-01 신규)

`reward_view.return_to_hub_from_reward()` → `trigger_mission_completion_novel_hooks()` 자동 호출:

```python
# 미션 완료 시
state.completed_missions.add(mission_id)
trigger_mission_completion_novel_hooks(state, mission_id)
# → mission_to_stem(mission_id) → dispatch_for_state(runtime, stem, state)
```

### 2.3 Hook 종류 (6)

| Hook | 기본 효과 | 예시 |
|---|---|---|
| `NARRATIVE` | excerpt 표시 | 케이 잭아웃 |
| `EXCERPT` | 인라인 발췌 | T-A 사찰 |
| `EVENT` | EventState 트리거 | construct 등장 |
| `COMBAT` | ICE 종류 시드 | Hammer T2 |
| `ITEM` | 인벤토리 추가 | biochip |
| `CINEMATIC` | GN 큐 | cutscene |

---

## 3. 실행 가능한 데모 (27+ scripts)

### 3.1 핵심 데모

```bash
cd prototype/

# 풀 게임 자동플레이 (GUI, 모든 화면 순회)
uv run python scripts/play.py --duration 30

# 그래픽 노블 자동재생 (이어서 읽기)
uv run python scripts/graphic_novel.py --mode novice --continue

# 전투 시뮬레이터 (PPL/ZDR/적/전략)
uv run python scripts/combat_simulator.py --ppl 24 --enemy standard

# Death 사이클 (Combat → Death 5-Phase)
uv run python scripts/death_in_action_demo.py

# 5등급 전투 진행 비교
uv run python scripts/combat_grades.py

# Novel Hook Dispatch 검증
uv run python scripts/play_novel_runtime.py

# BSP 던전 + ECS
uv run python scripts/play_ecs_dungeon.py
```

### 3.2 신규 Phase 1-5 데모 (2026-06-30)

```bash
# D 키 dungeon_mode + BSP 미로
uv run python scripts/play_dungeon_mode.py

# CombatEffects + 4 VFX spawner
uv run python scripts/play_vfx_overlay.py

# 16 미션 → RoomType + MatrixGraph 매핑
uv run python scripts/play_mission_mapping.py

# Novel Hook 6종 dispatch
uv run python scripts/play_novel_runtime.py
```

전체 가이드: `prototype/scripts/README.md`

---

## 4. 시스템 아키텍처 (Phase 5+6)

```
prototype/src/roguelike_sprawl/
├── engine/         # 화면 렌더링 + 게임 루프
│   ├── matrix_view.py       # 매트릭스 (D키 던전 토글)
│   ├── graphic_novel_view.py  # GN 모드
│   ├── chapter_view.py      # 챕터 (단편 인용)
│   ├── reward_view.py       # 미션 완료 → novel_integration 트리거
│   ├── novel_integration.py # 미션→단편→hook dispatch (신규)
│   ├── death.py             # Death cycle
│   └── ...
├── matrix/         # 노드 그래프 + BSP 던전
├── combat/         # RT-MS 전투 + VFX + 보스
├── novel/          # 4-layer Hook Dispatch
│   ├── catalog.py / hooks.py / manifest.py / dispatcher.py / integrator.py
├── story/          # 보상, 아크
├── i18n/           # en/ko 번역
├── ecs/            # ECS-lite (Room entity)
├── run/            # Run state, Stage, ChapterState
├── missions/       # JobBoard, Mission
└── data/           # JSON 데이터 (i18n, scenes, missions, story)
```

---

## 5. 콘텐츠 확장 계획 (CONTENT_EXPANSION_PLAN.md)

### 5.1 Phase A: 미션 확장 (15→25, 달성: 33→38)

- ✅ Arc 1 미션 6개 (tutorial_maze, first_contact, data_retrieval, first_jack, watchdog_patrol, ice_run)
- ✅ Arc 2 미션 11개 (sense_net_infiltration, wigan_call 추가 2026-07-01)
- ✅ Arc 3 미션 10개 (hosaka_core, straylight_approach, maas_heist 추가 2026-07-01)
- ⏳ Arc 4-5 추가 가능

### 5.2 Phase B: Stage 확장 (9→13, 달성)

- ✅ BRIEFING (픽서 브리핑)
- ✅ TRAVEL (잭인 지점 이동)
- ✅ BYPASS_SECURITY (보안 우회)

### 5.3 Phase C: 단편 확장 (17→35+, 달성: 41+)

- ✅ 2026-06-22 단편 3편 (Armitage, Hosaka, T-A defection, Wintermute)
- ✅ 2026-07-01 단편 5편 (sense_net_infiltration, wigan_call, hosaka_core, straylight_approach, maas_heist)

### 5.4 Phase D: 밸런스 (진행 중)

- ⏳ 미션 보상 곡선 재계산
- ⏳ 플레이타임 측정

---

## 6. ADR 인덱스 (Active)

| 번호 | 제목 | 상태 | 날짜 |
|---|---|---|---|
| 0041-0044 | GN Content/Card/Audio/Save | Accepted | 2026-06-20/21 |
| 0046 | GN Ending B | Accepted | 2026-06-21 |
| 0048-0049 | GN Ending Menu + C | Accepted | 2026-06-21 |
| 0050 | Boss ICE (Wintermute + T-A Prime) | Accepted | 2026-06-21 |
| 0051 | Mission Story Metadata | Accepted | 2026-06-22 |
| 0052 | Short Story Expansion Plan | Accepted | 2026-06-22 |
| 0060 | Dungeon BSP + NetHack + VFX | Accepted | 2026-06-30 |
| 0061 | Novel Integration (4-layer + runtime) | Accepted | 2026-06-30 |
| (impl) | Stage BRIEFING/TRAVEL/BYPASS_SECURITY | Implemented | 2026-07-01 |
| (impl) | CONTENT_EXPANSION Phase A+ (5 신규 미션) | Implemented | 2026-07-01 |

---

## 7. 검증 명령어

### 7.1 전체 테스트

```bash
cd prototype/

# 전체 테스트 (3894 passing, 3962 collected)
uv run pytest

# Lint + Format
uv run ruff check src tests
uv run ruff format --check src tests

# Type check
uv run mypy src/ --ignore-missing-imports
```

### 7.2 데이터 검증

```bash
# Stage structure 검증
uv run python scripts/validate_stage_structure.py

# Story 검증 (Gibson 톤 contamination 체크)
uv run python scripts/validate_stories.py /path/to/short-stories

# Event dialogue 검증
uv run python scripts/validate_event_dialogues.py

# Prologue data 검증
uv run python scripts/validate_prologue_data.py
```

### 7.3 대시보드 빌드

```bash
cd /Users/emilio/projects/Projects/Game/roguelike_sprawl
python3 tools/build_dashboard.py
# 10 stats JSON 자동 갱신 → dashboard/data/*.json
```

---

## 8. 현재 상태 (2026-07-01)

| 항목 | 상태 |
|------|------|
| Unit Tests | ✅ **3894 passed** (3962 collected) |
| mypy | ✅ No errors (2 source files) |
| ruff | ✅ All passed |
| 미션 | ✅ **38개** (Arc 1-5 + 4 suit) |
| 단편 (EN+KO) | ✅ **41 pair** |
| Stage | ✅ **13개** (Phase B 확장) |
| Novel Integration | ✅ 런타임 자동 호출 연동 |

### 8.1 신규 통합 작업 (P1~P4 + B, 2026-07-01)

- **P1**: 테스트 10건 수정 (suit 단편 스텁 + 오타 + stale 정정)
- **P2**: Novel Dispatcher 미션 트리거 자동 호출 (215 lines)
- **P3**: KO 번역 한자 잔재 0건 (모든 JSON)
- **P4**: Stage BRIEFING/TRAVEL/BYPASS_SECURITY 추가
- **B**: 신규 미션 5개 (Arc 2-3) + 단편 5편 (깁슨 톤)

### 8.2 신규 테스트 (2026-07-01)

- `tests/unit/test_novel_integration.py` (11 tests)
- `tests/unit/test_stage_expansion.py` (16 tests)
- `tests/integration/test_expansion_missions.py` (59 tests)
- **합계: +86 신규**

---

## 9. 디자인 톤 가이드라인

### 9.1 깁슨 톤 (캐릭터 voice profile)

| 캐릭터 | 톤 | 어휘 |
|---|---|---|
| **Case (novice)** | Jaded, ironic, self-deprecating | deck, jack, flatline, ICE, wetware, cowboy |
| **Marly (veteran)** | Quiet, deliberate, gallery curator | data, matrix, T-A, Mara |
| **Kumiko (heretic)** | Ritualistic, formal, declarative | wheel, Loa, casting, Tessier-Ashpool |
| **narrator** | Cold camera, omnipresent | (시점 묘사) |

### 9.2 작성 규칙 (씬 dialogue, ADR-0041)

1. **첫 문장 hook**: "30초. Ono-Sendai 전극이 떨어진다."
2. **마지막 비트로 끝**: 완결하지 않고 호흡 넘김
3. **Sensory detail 1개 이상**: smell, sound, touch, sight
4. **산업 이름 1개 이상**: T-A, Sense/Net, Maas, Hosaka, Ono-Sendai, Neuromancer
5. **번역 동기화**: 영문 → 한글 자막 (ADR-0010)

### 9.3 안티패턴

- ❌ 설명적 monologue
- ❌ 직접 감정 표현
- ❌ 멜로드라마
- ❌ 현대 인터넷 meme, Cyberpunk 2077, D&D 용어
- ❌ 원문에 없는 사실 단언

---

## 10. Notion 임포트 가이드

### Markdown → Notion 변환

1. 이 파일을 `NOTION_IMPORT.md`로 저장
2. Notion에서 **Import** → **Markdown** 선택
3. 저장한 파일 선택

또는 `Language/_publish/scripts/publish_to_notion.py` 스크립트 사용:

```bash
export NOTION_TOKEN="secret_xxx..."
export NOTION_PARENT_PAGE_ID="page-id"

python Language/_publish/scripts/publish_to_notion.py this-file.md
```

### 동기화 체크리스트

- [x] 미션 카운트 38
- [x] 단편 카운트 41 pair
- [x] Stage 13개
- [x] Novel Integration 런타임 연동
- [x] 테스트 3894 passed
- [x] ADR 0041-0061 + 2026-07-01 구현 사항

---

> **버전**: 0.4.0
> **작성일**: 2026-07-01
> **이전 버전**: 0.3.0 (2026-06-25, 15 미션)
> **연관 문서**: `log.md`, `SESSION_HANDOVER.md`, `IMPROVEMENTS.md`, `decisions/README.md`