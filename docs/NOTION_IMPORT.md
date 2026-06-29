---
title: Roguelike Sprawl - 프로젝트 가이드
date: 2026-06-25
tags: [game, gibson, cyberpunk, python]
---

# Roguelike Sprawl - 프로젝트 가이드

## 프로젝트 개요

**깁슨 스프롤 3부작 세계관의 사이버펑크 로그라이크**

플레이어는 콘솔 카우보이(console cowboy)가 되어 사이버스페이스에서 ICE를 뚫고 데이터 탈취하는 게임입니다.

### 기술 스택

- Python 3.11+
- python-tcod 21+
- pytest (2970 tests)
- ruff (linter)
- mypy (type checker)
- uv (package manager)

---

## 1. 캐릭터별 진행 경로

### 1.1 캐릭터 구성

| ID | 이름 | 아키타입 | Deck Tier | 무기 | 동기 |
|---|---|---|---|---|---|
| novice | 케이 (K) | Novice | T1 | Wisp (T1) | 빚 갚기 (생존) |
| veteran | 실 (Sil) | Veteran | T2 | Hammer (T2) | 복수 (T-Aへの) |
| heretic | 카스 (Kas) | Heretic | T3 (bio) | Viral Sermon | 시스템 폭로 |

### 1.2 Stage Flow (9 stages)

```
PENDING → MEET_NPC → EXTRACT_DATA → DEFEAT_ICE → JACK_OUT → REWARD → COMPLETE
                 ↓                      ↓
              (DEATH)              FAILED → DEATH_RESTART → PENDING
```

### 1.3 미션 Grade 분포

| Arc | Grade 범위 | 미션 수 | 대표 미션 |
|-----|-----------|--------|----------|
| 1 | 1-2 | 4개 | first_jack, watchdog_patrol |
| 2 | 1-5 | 4개 | first_trace, craft_job |
| 3 | 3-4 | 3개 | mollys_razor, black_ice_dream |
| 4 | 4-5 | 3개 | dixies_offer, aleph_fragment |
| 5 | 5 | 1개 | final_choice |

### 1.4 보상 공식

```
credits = arc × 800 + (grade - 1) × 300
```

---

## 2. 실행 가능한 데모

### 2.1 전체 게임 플로우 데모 (최신)

모든 주요 화면과 상태 전이를 보여주는 종합 데모입니다.

```bash
cd prototype/
uv run python scripts/demo_full_flow.py
```

**보이는 화면 (15개)**

1. MENU (5 options)
2. CHARACTER_SELECT (Finn's briefing)
3. HUB (mission board, NPC)
4. MATRIX (node exploration)
5. NPC_DIALOGUE (Dixie Flatline)
6. DATA_EXTRACT (data node)
7. COMBAT (RT-MS battle)
8. JACK_OUT (disconnection)
9. REWARD (mission complete)
10. DEBRIEF (post-mission narrative)
11. COMPLETE (return to Hub)
12. DEATH (flatline screen)
13. HALL_OF_DEAD (archived jockeys)
14. SAVE/LOAD (browser)
15. CREDITS

**옵션**

- `--skip-combat` — Combat 스킵, 자동 승리
- `--skip-animation` — 애니메이션 스킵
- `--character novice|veteran|heretic` — 캐릭터 선택
- `--lang en|ko` — 언어 선택

### 2.2 기타 데모

```bash
# 풀 게임 자동플레이 (GUI)
uv run python scripts/play.py --duration 30

# 그래픽 노블
uv run python scripts/graphic_novel.py --mode prologue

# 전투 시뮬레이터
uv run python scripts/combat_simulator.py --ppl 24 --enemy standard

# Death 사이클
uv run python scripts/death_in_action_demo.py

# 5등급 전투 비교
uv run python scripts/combat_grades.py
```

---

## 3. 검증 명령어

### 3.1 전체 테스트

```bash
cd prototype/

# 전체 테스트 (2970개)
uv run pytest

# Lint + Format
uv run ruff check src tests
uv run ruff format src tests

# Type check
uv run mypy src/ --ignore-missing-imports
```

### 3.2 데이터 검증

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

---

## 4. 현재 상태 (2026-06-25)

| 항목 | 상태 |
|------|------|
| Unit Tests | ✅ 2970 passed |
| mypy | ✅ No errors |
| ruff | ✅ All passed |
| validate_stage_structure | ✅ PASS (9 stages, 15 missions) |
| validate_stories | ✅ 29 PASS, 0 FAIL, 8 WARN |

---

## 5. 주요 문서

| 문서 | 설명 |
|------|------|
| `design/CHARACTER_PATHS.md` | 3캐릭터 × 15미션 진행 경로 |
| `design/systems/stage_structure.json` | 9 stages, 15 missions |
| `design/story/prologue_data.json` | 3 캐릭터, 프롤로그 씬 |
| `prototype/scripts/README.md` | 모든 데모 스크립트 가이드 |
| `log.md` | 활동 로그 |
| `SESSION_HANDOVER.md` | 세션 인계 문서 |

---

## 6. 게임 시스템 개요

### 6.1 Stage Types

| Stage | Type | Description |
|-------|------|-------------|
| PENDING | hub | Run 미시작, Hub에서 미션 수락 대기 |
| MEET_NPC | matrix | NPC 구성체와 대화 |
| EXTRACT_DATA | matrix | 데이터 노드에서 페이로드 추출 |
| DEFEAT_ICE | combat | ICE와 교전하여 격파 |
| JACK_OUT | animation | 매트릭스 연결 해제 |
| REWARD | hub | 미션 보상 표시 |
| COMPLETE | hub | Run 완료 |
| FAILED | death | 플레이어 HP = 0 |
| DEATH_RESTART | death | 재시작 또는 종료 선택 |

### 6.2 Screen Kinds

- MENU
- CHARACTER_SELECT
- CHAPTER
- HUB
- MATRIX
- COMBAT
- JACK_OUT
- REWARD
- DEBRIEF
- DEATH
- HALL_OF_DEAD
- SAVE/LOAD
- CREDITS

---

## 7. 파일 구조

```
roguelike_sprawl/
├── design/
│   ├── CHARACTER_PATHS.md      # 캐릭터별 진행 경로
│   ├── systems/
│   │   └── stage_structure.json  # 9 stages, 15 missions
│   └── story/
│       └── prologue_data.json   # 3 캐릭터, 프롤로그
├── prototype/
│   ├── src/
│   │   └── roguelike_sprawl/   # 게임 엔진
│   │       ├── combat/         # RT-MS 전투
│   │       ├── engine/         # 화면 렌더링
│   │       ├── matrix/         # 매트릭스 생성
│   │       └── run/            # Run 상태 관리
│   ├── scripts/
│   │   ├── demo_full_flow.py  # 전체 게임 플로우
│   │   ├── play.py            # GUI 자동플레이
│   │   └── *.py               # 기타 데모
│   └── tests/                 # 2970 unit tests
├── dashboard/
│   ├── stories/               # HTML story files
│   └── *.html                 # 대시보드
└── scripts/                   # 검증 스크립트
```

---

## 8. Notion 임포트 가이드

### Markdown → Notion 변환

1. 이 파일을 `.md`로 저장
2. Notion에서 **Import** → **Markdown** 선택
3. 저장한 파일 선택

또는 `publish_to_notion.py` 스크립트 사용:

```bash
export NOTION_TOKEN="secret_xxx..."
export NOTION_PARENT_PAGE_ID="page-id"

python Language/_publish/scripts/publish_to_notion.py this-file.md
```

---

> **작성일**: 2026-06-25
> **작성자**: AI Agent
> **연관 문서**: CHARACTER_PATHS.md, scripts/README.md, log.md
