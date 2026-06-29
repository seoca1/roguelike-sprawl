---
title: 세션 인계 문서 - Session Handover
date: 2026-06-25
tags: [handover, project, phase-5]
---

# Session Handover — 다른 세션에서 이어서 진행하기

> 작성일: 2026-06-25
> 작성 시점 상태: Phase 5 완료, 2970 tests pass, CHARACTER_PATHS 문서화 완료
> 대상: 다음 세션의 AI 에이전트 또는 개발자

---

## 0. 5초 요약 (다음 에이전트용)

이 프로젝트는 깁슨 스프롤 로그라이크 게임 (Python 3.11+ / tcod / uv).
**현재 상태: 모든 핵심 시스템 + 그래픽 노블 + 이어서 읽기 + 매트릭스 이동 UX 완성.**
**2970 tests pass, ruff/format/mypy 모두 green.**

방향 잡기:
1. `design/CHARACTER_PATHS.md` 읽기 (3캐릭터 × 15미션 경로)
2. `log.md` 마지막 섹션 (최근 작업 흐름)
3. `prototype/scripts/README.md` (데모 가이드)
4. 작업 선택 후 "이어서 진행"

---

## 1. 프로젝트 한 줄 설명

**깁슨 스프롤 3부작 세계관의 사이버펑크 로그라이크.**
플레이어는 console cowboy가 되어 cyberspace에서 ICE를 뚫고 데이터 탈취.
깁슨 톤 (cold, detached, cinematic) — 한 줄, 단편, atmospheric.

---

## 2. 현재 완료 상태 (2026-06-25)

### Phase 5 (Vertical Slice) — 완료

| 시스템 | 상태 | ADR | 핵심 파일 |
|---|---|---|---|
| 매트릭스 진입/이탈 (Hub ↔ Matrix) | ✅ | 0005 | `engine/matrix_view.py` |
| 노드 그래프 절차적 생성 | ✅ | 0005 | `matrix/generator.py` |
| PPL & ZDR (난이도 시스템) | ✅ | 0012 | `matrix/ppl.py`, `matrix/zdr.py` |
| Fog of War / Exploration | ✅ | 0020 | `matrix/exploration.py` |
| 전투 (RT-MS, 5 ICE 타입, 5-Layer VFX) | ✅ | 0003, 0018 | `combat/state.py`, `combat/effects.py` |
| Combat HUD + 콤보 (5-stage) | ✅ | 0003 | `combat/hud.py`, `combat/combo.py` |
| Death & Restart Cycle | ✅ | 0040 | `engine/death.py`, `engine/jockey_history.py` |
| 오리지널 시나리오 (단편 → 챕터) | ✅ | 0031 | `engine/chapter_view.py` |
| 그래픽 노블 모드 (12 씬, 5 옵션) | ✅ | 0032 | `engine/graphic_novel_view.py` |
| 그래픽 노블 소설 페이지 (30줄, chapter cards, fade) | ✅ | 0041, 0042 | `graphic_novel_view.py` |
| 사운드 큐 연결 (15 cue → file) | ✅ | 0043 | `engine/graphic_novel_audio.py` |
| GN 이어서 읽기 (CONTINUE READING) | ✅ | 0044 | `engine/graphic_novel_save.py` |
| 매트릭스 이동 UX (15 키, 시각 힌트) | ✅ | 0045 | `engine/matrix_view.py` |
| 30+ 설정, 28 업적, 10 대시보드 | ✅ | — | `dashboard/*.html` |
| SaveManager (5 슬롯) | ✅ | — | `engine/save_manager.py` |

---

## 3. 핵심 명령어 (자주 씀)

### 검증

```bash
cd ~/projects/Projects/Game/roguelike_sprawl/prototype

uv run pytest                  # 2970 tests
uv run ruff check src tests    # lint
uv run ruff format src tests   # format
uv run mypy src/              # typecheck
```

### 데모 실행

```bash
# 전체 게임 플로우 (15개 화면 모두)
uv run python scripts/demo_full_flow.py

# 그래픽 노블
uv run python scripts/graphic_novel.py --mode novice --continue

# 전투 시뮬레이터
uv run python scripts/combat_simulator.py --ppl 24 --enemy standard

# Death 사이클
uv run python scripts/death_in_action_demo.py

# 풀 게임 (GUI)
uv run python scripts/play.py
```

전체 데모 가이드: `prototype/scripts/README.md`

---

## 4. 디렉토리 구조 (핵심만)

```
Game/roguelike_sprawl/
├── AGENTS.md                          # AI 에이전트 가이드
├── ROADMAP.md                         # 단계별 계획 (Phase 5 완료)
├── README.md                          # 프로젝트 개요
├── index.md                           # Wiki 인덱스
├── log.md                             # 활동 로그
├── decisions/                          # ADR (11개 Accepted)
├── design/
│   ├── CHARACTER_PATHS.md            # 3캐릭터 × 15미션 경로
│   ├── systems/
│   │   └── stage_structure.json       # 9 stages, 15 missions
│   └── story/
│       └── prologue_data.json         # 3 캐릭터, 프롤로그 씬
├── prototype/
│   ├── src/roguelike_sprawl/         # 게임 엔진
│   │   ├── combat/                   # RT-MS 전투
│   │   ├── engine/                   # 화면 렌더링
│   │   ├── matrix/                   # 매트릭스 생성
│   │   └── run/                      # Run 상태 관리
│   ├── scripts/
│   │   ├── demo_full_flow.py         # 전체 게임 플로우 (신규)
│   │   └── *.py                      # 기타 데모
│   └── tests/                        # 2970 unit tests
├── dashboard/                         # HTML 대시보드
└── scripts/                          # 검증 스크립트
```

---

## 5. 파일 참조

| 파일 | 설명 |
|------|------|
| `design/CHARACTER_PATHS.md` | 3캐릭터 × 15미션 진행 경로 |
| `design/systems/stage_structure.json` | 9 stages, 15 missions |
| `prototype/scripts/README.md` | 모든 데모 스크립트 가이드 |
| `prototype/scripts/demo_full_flow.py` | 전체 게임 플로우 종합 데모 (2026-06-25 신규) |
| `log.md` | 활동 로그 (2600+ 줄) |
| `SESSION_HANDOVER.md` | 이 문서 |

---

## 6. 다음 세션이 가장 먼저 할 일

1. `git status` — 어떤 파일이 수정되었는지
2. `uv run pytest` — 현재 상태 확인 (2970 pass)
3. `tail -300 log.md` — 최근 흐름 파악
4. 사용자에게 "이어서 진행" 받기

---

## 7. 빠른 참조 — 1줄 명령어

```bash
cd prototype/

# 전체 검증
uv run pytest && uv run ruff check src tests && uv run mypy src/ --ignore-missing-imports

# 캐릭터 경로 문서
cat design/CHARACTER_PATHS.md

# 데모 실행
uv run python scripts/demo_full_flow.py
uv run python scripts/demo.py --duration 10
```

---

## 8. 연락 / 컨텍스트

- **GitHub**: `seoca1/roguelike-sprawl` (Pages: https://seoca1.github.io/roguelike-sprawl/)
- **로컬 경로**: `~/projects/Projects/Game/roguelike_sprawl/`
- **Python**: 3.11+ (uv로 관리)
- **테스트**: 2970 passing
- **마지막 ADR**: 0045 (matrix movement UX)

---

**이 문서를 다른 세션의 첫 번째 참고 자료로 사용하세요.**
**모든 컨텍스트는 log.md, decisions/, 그리고 위 디렉토리 구조에 있습니다.**
