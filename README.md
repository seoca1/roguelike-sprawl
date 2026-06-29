# Roguelike Sprawl

[![CI](https://github.com/seoca1/roguelike-sprawl/actions/workflows/ci.yml/badge.svg)](https://github.com/seoca1/roguelike-sprawl/actions)
[![Pages](https://github.com/seoca1/roguelike-sprawl/actions/workflows/pages.yml/badge.svg)](https://seoca1.github.io/roguelike-sprawl/)
[![Tests](https://img.shields.io/badge/tests-2257%20passing-brightgreen)]()
[![Lint](https://img.shields.io/badge/lint-ruff-blue)]()
[![Typecheck](https://img.shields.io/badge/typecheck-mypy%20strict-blue)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()

윌리엄 깁슨의 스프롤 3부작(《뉴로맨서》, 《카운트 제로》, 《모나리자 오버드라이브》) 세계관을 기반으로 한 로그라이크 게임 개발 프로젝트.

플레이어는 **콘솔 카우보이(console cowboy)**가 되어 사이버스페이스에 진입, ICE를 뚫고 데이터를 탈취하며 임무를 수행한다. 죽으면 끝. 그러나 더 좋은 데크(cyberdeck), 프로그램, 웨웨어(wetware), construct로 돌아와 더 깊이 들어간다.

🌆 **Live Dashboard**: https://seoca1.github.io/roguelike-sprawl/

## 핵심 컨셉
- 매 런은 "잡(job)" — 의뢰인의 의뢰, 타겟 시스템, 보상
- 사이버스페이스에서의 해킹, 전투, 데이터 탈취
- 사이버펑크 톤 — 네온, 크롬, 거대 기업, 인공 지능
- "flatline" = 게임 오버

## 디렉토리 구조

| 경로 | 목적 | 비고 |
| --- | --- | --- |
| `raw/` | 원본 자료 (Gibson 소설, 레퍼런스) | 읽기 전용 |
| `wiki/` | LLM이 유지하는 지식 베이스 (세계관, 메카닉) | LLM Wiki |
| `design/` | 활성 게임 디자인 명세 | 사용자/AI가 함께 편집 |
| `testcases/` | 게임플레이 테스트 케이스 / 시나리오 | 디자인과 동기화 |
| `decisions/` | 결정 기록 (ADR) | 결정은 immutable, draft는 mutable |
| `prototype/` | 프로토타입 코드 (엔진 결정 후) | 미정 |
| `ROADMAP.md` | 단계별 계획 | 본 디렉토리 루트 |
| `AGENTS.md` | AI 에이전트 작업 가이드 | 본 디렉토리 루트 |

## 빠른 시작

1. `ROADMAP.md` — 현재 단계와 다음 단계 확인
2. `decisions/README.md` — 미해결 결정 사항 확인
3. `wiki/world/sprawl_universe.md` — 세계관 컨셉 참조
4. `design/pillars.md` → `design/GDD.md` — 현재 게임 디자인 확인
5. `design/CHARACTER_PATHS.md` — 캐릭터별 진행 경로 (3인 × 15미션)

## 주요 문서

- 모든 문서는 마크다운, Git으로 버전 관리
- LLM Wiki 패턴: `raw/` → `wiki/` (원본 → 정리)
- 결정 사항은 `decisions/`에 ADR 형식으로 기록 (결정 후 immutable)
- 디자인 변경 시 `testcases/`도 동기화

## 최근 작업 (2026-06-21)

Phase 5 (Vertical Slice) 완료. 핵심 시스템 + 콘텐츠 통합 + 그래픽 노블 모드:

- **전투 (RT-MS)** — 5 ICE 타입 (Standard/Watchdog/Black/Goliath/Construct), 5-Layer VFX, 5-Stage Combo
- **자키 사이클** — Death → DEATH_SUMMARY → HALL_OF_DEAD → 새 자키 (3 옵션)
- **오리지널 시나리오** — 단편 3편 소설 레벨 (12 씬, 38 dialogues, 16,862 chars)
- **그래픽 노블** — 메인메뉴 5 옵션 + 자동재생 + 30줄 소설 페이지 + 챕터 카드 I-XII + fade
- **사운드** — 15개 scene cue → file 매핑 (theme/movement 카테고리)
- **이어서 읽기** — GNProgress atomic save + CONTINUE READING 메뉴

상세: [`ROADMAP.md`](./ROADMAP.md), [`decisions/`](./decisions/), [`log.md`](./log.md).

## 핵심 데모 명령

```bash
cd prototype
make test      # 2257 tests
make all       # format + lint + typecheck + test

# 그래픽 노블 자동재생
uv run python scripts/graphic_novel.py --mode novice --lang ko

# 전투 시뮬레이터
uv run python scripts/combat_simulator.py --ppl 24 --enemy standard
uv run python scripts/combat_grades.py  # 5등급 비교
uv run python scripts/death_in_action_demo.py  # Combat → Death 5-Phase

# 풀 게임 자동플레이
uv run python scripts/play.py --duration 30
```
