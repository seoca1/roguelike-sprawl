# Session Handover — 다른 세션에서 이어서 진행하기

> 작성일: 2026-07-01
> 작성 시점 상태: Phase 5+6 완료, 3894 tests pass (3962 collected), ADR-0060/0061 Accepted + 4 통합 작업 + 콘텐츠 확장 5 미션 추가
> 대상: 다음 세션의 AI 에이전트 또는 개발자

---

## 0. 5초 요약 (다음 에이전트용)

이 프로젝트는 깁슨 스프롤 로그라이크 게임 (Python 3.11+ / tcod / uv).
**현재 상태: 38 missions, 41 단편 (en+ko), 13 stages (BRIEFING/TRAVEL/BYPASS_SECURITY 추가), Novel Hook Dispatch 미션 완료 시 자동 호출.**
**3894 tests pass, ruff/format/mypy 모두 green.**

방향 잡기:
1. `design/CHARACTER_PATHS.md` 읽기 (3캐릭터 × 15미션 경로)
2. `log.md` 마지막 섹션 (P1~P4 + B 통합 작업)
3. `prototype/scripts/README.md` (데모 가이드)
4. 작업 선택 후 "이어서 진행"

---

## 1. 프로젝트 한 줄 설명

**깁슨 스프롤 3부작 세계관의 사이버펑크 로그라이크.**
플레이어는 console cowboy가 되어 cyberspace에서 ICE를 뚫고 데이터 탈취.
깁슨 톤 (cold, detached, cinematic) — 한 줄, 단편, atmospheric.

---

## 2. 현재 완료 상태 (2026-07-01)

### Phase 5+6 (Vertical Slice + Expansion) — 완료

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
| Boss ICE (Wintermute + T-A Prime 3-phase) | ✅ | 0050 | `combat/bosses.py` |
| Graphic Novel Ending B / C / 메뉴 | ✅ | 0046, 0048, 0049 | `engine/graphic_novel_view.py` |
| **Dungeon BSP + NetHack + VFX Overlay** | ✅ | 0060 | `matrix/dungeon_generator.py`, `engine/dungeon_view.py` |
| **Novel Hook Dispatch (4-layer)** | ✅ | 0061 | `novel/{catalog,manifest,hooks,dispatcher}.py` |
| **Novel Integration (런타임 연동)** | ✅ | 0061 | `engine/novel_integration.py` (신규) |
| **Stage BRIEFING / TRAVEL / BYPASS_SECURITY** | ✅ | — | `run/state.py` (Phase B) |
| **신규 미션 5개 (Arc 2-3)** | ✅ | — | `data/missions/missions.json` (33→38) |
| 30+ 설정, 28 업적, 10 대시보드 | ✅ | — | `dashboard/*.html` |
| SaveManager (5 슬롯) | ✅ | — | `engine/save_manager.py` |

### 테스트 통계 (2026-07-01)
- **3894 tests passing** (3962 collected, 24 xfailed)
- 24 xfailed (의도적 — INDEX 갱신 대기 단편)
- 44 skipped (의도적 — 통합 테스트 환경 의존)
- **이전 3254 → 3894 (+640, 통합 작업 + 콘텐츠 확장 모두 반영)**
- **ruff check / format / mypy strict**: 모두 green
- **테스트 분포**: 90+ unit + integration test files

### 콘텐츠 카운트 (2026-07-01)
- 미션: 33 → **38** (+15%)
- 단편 (EN/KO 페어): 32 → **41** (+28%)
- Stage enum: 10 → **13** (+30%, BRIEFING/TRAVEL/BYPASS)
- 캐릭터: 3 (Case/Sil/Kas) + 1 (suit) = **4**

---

## 3. 핵심 명령어 (자주 씀)

```bash
cd ~/projects/Projects/Game/roguelike_sprawl/prototype

# 검증 (3-in-1)
uv run pytest                  # 2284 tests
uv run ruff check .            # lint
uv run ruff format --check .   # format

# 데모
uv run python scripts/graphic_novel.py --mode novice --continue  # 이어서 읽기
uv run python scripts/combat_simulator.py --ppl 24 --enemy standard
uv run python scripts/combat_grades.py  # 5등급 표
uv run python scripts/death_in_action_demo.py  # Combat → Death 5-Phase
uv run python scripts/play.py  # 풀 게임 (MENU → HUB → MATRIX)
```

전체 데모 가이드: `prototype/scripts/README.md` (477줄, 추천 순서 + 비교표)

---

## 4. 디렉토리 구조 (핵심만)

```
Game/roguelike_sprawl/
├── AGENTS.md                          # AI 에이전트 가이드 (이 문서보다 우선)
├── ROADMAP.md                         # 단계별 계획 (Phase 5 완료, Phase 6 진입 가능)
├── README.md                          # 프로젝트 개요
├── index.md                           # Wiki 인덱스
├── log.md                             # 활동 로그 (90KB+, 36개 섹션)
├── decisions/                         # ADR (모두 Accepted 또는 Draft)
│   ├── README.md                      # ADR 인덱스 (11개 Accepted)
│   ├── 0031-original-scenario-integration.md  (Accepted)
│   ├── 0032-graphic-novel-mode.md            (Accepted)
│   ├── 0040-death-restart-cycle.md           (Accepted)
│   ├── 0041-graphic-novel-content-expansion.md (Accepted)
│   ├── 0042-chapter-title-cards.md            (Accepted)
│   ├── 0043-sound-cue-integration.md          (Accepted)
│   ├── 0044-graphic-novel-save.md             (Accepted)
│   └── 0045-matrix-movement.md               (Accepted, 이번 세션)
├── design/scenario/                   # 디자인 명세
│   ├── graphic-novel.md               # GN 디자인 (톤 가이드라인 §10 포함)
│   ├── death-restart.md               # Death cycle 디자인
│   └── chapter-{1,2,3}.md             # 캐릭터별 챕터
├── docs/
│   ├── DEPLOYMENT_GUIDE.md            # GitHub Pages 자동 배포
│   └── REMOTE_DEV_SETUP.md            # 원격 개발 환경 (이전 세션)
└── prototype/
    ├── pyproject.toml                  # uv 의존성
    ├── Makefile                        # make test / lint / typecheck
    ├── src/roguelike_sprawl/
    │   ├── engine/                     # 화면 렌더링 (matrix, hub, menu, ...)
    │   │   ├── matrix_view.py          # 매트릭스 (방금 업데이트)
    │   │   ├── graphic_novel_view.py   # GN (방금 업데이트)
    │   │   ├── graphic_novel_audio.py  # 사운드 (방금 업데이트)
    │   │   ├── graphic_novel_save.py   # GN 저장 (방금 업데이트)
    │   │   ├── death.py                # Death cycle
    │   │   ├── jockey_history.py       # Hall of Dead
    │   │   └── ...
    │   ├── matrix/                     # 노드 그래프 데이터
    │   ├── combat/                     # 전투 시스템
    │   ├── audio/                      # 사운드 매니저 (afplay/aplay)
    │   └── i18n/                       # en/ko 번역
    ├── tests/unit/                     # 80+ 테스트 파일
    ├── data/
    │   ├── scenes/{case,sil,kas}/      # 12 GN 씬 (4× 확장됨)
    │   ├── sounds_test/                # 46개 자동 생성 WAV
    │   ├── saves/gn_progress.json      # GN 이어서 읽기
    │   └── i18n/{en,ko}.json           # 1000+ 키
    └── scripts/
        ├── README.md                   # 27+ 데모 가이드
        ├── graphic_novel.py            # 메인 GN 데모 (--continue)
        ├── combat_simulator.py         # 단일 전투
        ├── death_in_action_demo.py     # Combat → Death 5-Phase
        └── ...
```

---

## 5. 최근 작업 (이번 세션의 핵심 흐름)

### 5.1 매트릭스 이동 UX 개선 (ADR-0045) — 가장 최근
- **문제**: 사용자 피드백 "직관적이지 않고, 상하좌우 이동이 자유스럽지 않다"
- **원인**: 엄격한 축 필터링, 시각 단서 없음, 대각선 불가
- **해결**:
  - `graphic_novel_view.py` (X) → `matrix_view.py` (O) — _handle_movement가 Euclidian dot-product 알고리즘
  - 15개 키 지원 (←→↑↓ + Numpad 7/9/1/3 + vim H/L/J/K + Y/U/B/N)
  - 현재 노드 박스에 ◄►▲▼ 시각 힌트
- **테스트**: `tests/unit/test_matrix_movement.py` (27 tests)
- **테스트 카운트**: 2257 → **2284** (+27)

### 5.2 그래픽 노블 폴리시 4작업 (ADR-0041~0044)
- **0041**: 12 씬 dialogue 4× 확장 (110자 → 443자)
- **0042**: 챕터 카드 I-XII + fade transition
- **0043**: 15개 scene cue → file 매핑 (path 버그 fix)
- **0044**: GNProgress atomic save + CONTINUE READING 메뉴
- **테스트**: +190 across 4 ADRs

### 5.3 이전 세션의 핵심 (참고용)
- Phase 5 전반부: 매트릭스/전투/Death/사이드 콘텐츠 완성
- ADR-0031, 0032, 0040

---

## 6. 다음 작업 후보 (다음 세션이 선택)

> 사용자가 "이어서 진행" 명령 시 이 옵션들을 제시하세요. 각 옵션은
> 다른 작업 카테고리라 보통 1개씩 진행됩니다.

### 6.1 콘텐츠 확장 (안전 / 큰 작업)

- **추가 캐릭터 (4번째 자키)** — 기존 3명 외 새로운 자키 + 4 씬
  - 디자인: `design/scenario/` 에 chapter-4-newchar.md 추가
  - 장면: `data/scenes/<newchar>/` 에 4 JSON
  - 영향: character_id 추가, graphic_novel_view.py 옵션 추가
- **추가 ICE 타입 (보스)** — 5종 외 6-7번째 보스급 ICE
- **미션 확장** — 미션 2개 → 10개 (현재 미션 JSON은 6개 정의됨)
- **시나리오 확장** — 단편 4편 추가 (현재 3편)
- **엔딩 확장** — 엔딩 B 추가 (현재 A만 다뤄짐)

### 6.2 폴리시 / UX (중간 작업)

- **드롭 캡 / 타이포그래피** — 첫 문단 첫 글자 크게, narrator 진한 테두리
- **한글 폰트 최적화** — 자간, fallback 폰트, 폭
- **그래픽 노블 한글 자막 자동 동기화 도구** — `script_en.json` → `script_ko.json`
- **SaveManager 슬롯 확장** — 현재 5슬롯, 10슬롯 + 자동저장 슬롯
- **전투 이펙트 강화** — 화면 흔들림, hit-stop, 카메라 줌

### 6.3 시스템 신규 (큰 작업)

- **매트릭스 미니맵 인터랙티브** — 현재 정적 → 클릭으로 노드 점프
- **Faction 평판 시스템** — Hosaka/Maas/T-A 별 평판, 미션 영향
- **데크 커스터마이제이션** — 프로그램 슬롯 관리
- **멀티 엔딩** — 선택지 기반 엔딩 A/B/C/D

### 6.4 인프라 (안전 / 작은 작업)

- **CI 강화** — 현재 ruff+pytest만, mypy 추가 + Pages deploy 검증
- **테스트 커버리지 30% → 80%** — `prototype/src/` 미커버 영역 많음
- **문서 자동 생성** — ADR → index.md 자동 동기화
- **데모 자동 빌드** — GitHub Actions로 데모 비디오 생성

---

## 7. 작업 시작 체크리스트 (다음 세션이 봐야 할 것)

```bash
# 1. 환경 확인 (5분)
cd ~/projects/Projects/Game/roguelike_sprawl/prototype
uv run pytest --collect-only -q 2>&1 | tail -1  # 2284 collected
git status   # 수정된 파일 확인

# 2. 최근 작업 흐름 파악 (10분)
tail -300 log.md  # 마지막 4-5개 섹션
cat decisions/0041-graphic-novel-content-expansion.md  # ADR 양식
cat decisions/0045-matrix-movement.md  # 가장 최근 ADR

# 3. 작업 선택 (사용자에게 "이어서 진행" 받으면 옵션 제시)
# 위 6.1~6.4 중 하나 선택

# 4. 작업 중 규칙
- 코드 변경 시 ADR 패턴 준수: decisions/0046-*.md (Draft → Accepted)
- 디자인 변경 시 design/ 동기화
- 테스트 추가 후 uv run pytest
- 작업 끝에 log.md 한 섹션 추가
```

---

## 8. 자주 발생하는 함정 / 주의사항

### 8.1 환경 / 명령어
- **`uv run` 빼먹기** — 시스템 Python 의존성과 격리됨, 항상 `uv run` 사용
- **bash `cd` 절대경로 문제** — `Game/` (대문자 G) vs `game/` 흔동
- **bash 따옴표** — 공백 포함 경로는 반드시 `"..."`

### 8.2 코드 스타일
- **frozen dataclass** — `assign to field` 에러 (예: `state.player_loadout.deck_tier = 2` ❌)
- **`from __future__ import annotations`** — 모든 파일 첫 줄
- **타입 힌트 + docstring** — public 함수/클래스 필수
- **`__slots__`** — 메모리 효율, frozen dataclass와 함께

### 8.3 테스트
- **pytest fixture 순서** — `tmp_path`, `monkeypatch` 활용
- **mypy strict** — 타입 누락 시 CI 실패
- **PT011** 등 ruff 규칙 자주 업데이트됨

### 8.4 게임 시스템
- **전투 TICK_MS = 100, AUTO_ATTACK_INTERVAL_MS = 2000** — 20+ 틱 = 1 attack
- **매트릭스 DAG** — 이동은 양방향이지만 `_handle_movement`는 in/out 모두 처리 (방금 업데이트)
- **사운드 `afplay`** — macOS 전용, 원격 SSH에서 출력 안 됨
- **GN 이어서 읽기** — 단일 슬롯 (`data/saves/gn_progress.json`), chain_length 변경 시 sanity check

### 8.5 디버깅 팁
```bash
# 단일 테스트 디버그
uv run pytest tests/unit/test_X.py::test_y -v --tb=short -s

# Demo headless (no TUI)
uv run python scripts/X.py --duration 5 --step-delay 0.3 --no-clear 2>&1 | head -50

# 매트릭스 상태 dump
uv run python -c "
import sys; sys.path.insert(0, 'src')
from roguelike_sprawl.engine.state import AppState
s = AppState()
print(s.matrix, s.current_node_id)
"
```

---

## 9. 현재 uncommitted 변경사항

`git status` 기준:
- **메타 문서**: AGENTS.md, ROADMAP.md, README.md, index.md, log.md, decisions/README.md
- **워크플로우**: .github/workflows/pages.yml
- **대시보드**: 9개 HTML 파일
- **i18n**: en.json, ko.json
- **코드**: audio/, engine/death.py, scripts/demo.py, scripts/play.py 등
- **테스트**: 10+ 신규 test 파일 (jockey_history, graphic_novel_*, matrix_movement 등)
- **신규 모듈**: graphic_novel_save.py (190 lines)
- **신규 문서**: docs/REMOTE_DEV_SETUP*.md

**커밋하지 않은 이유**: 사용자 검토 대기 (ADR-0031~0045 모두 Draft 상태인 채 통합). 다음 세션 시작 시 일괄 커밋 가능.

---

## 10. 다음 세션이 가장 먼저 할 일 (제안)

1. **`git status`** — 어떤 파일이 수정되었는지
2. **`uv run pytest`** — 현재 상태 확인 (2284 pass)
3. **`tail -300 log.md`** — 최근 흐름 파악
4. **사용자에게 "이어서 진행" 받기** — 옵션 제시 후 선택
5. **작업 선택** — 위 6.1~6.4 중 하나
6. **작업 시작** — ADR 패턴으로 문서화 → 코드 → 테스트 → log.md

---

## 11. 빠른 참조 — 1줄 명령어

```bash
cd prototype/

# 전체 검증
uv run pytest && uv run ruff check src tests && uv run mypy src/ --ignore-missing-imports

# 캐릭터 경로 문서
cat design/CHARACTER_PATHS.md

# 데모 실행
uv run python scripts/demo.py --duration 10
uv run python scripts/play.py --duration 5
```

---

## 12. 연락 / 컨텍스트

- **GitHub**: `seoca1/roguelike-sprawl` (Pages: https://seoca1.github.io/roguelike-sprawl/)
- **로컬 경로**: `~/projects/Projects/Game/roguelike_sprawl/`
- **Python**: 3.11+ (uv로 관리)
- **테스트**: 3254 passing
- **마지막 ADR**: 0061 (novel hook dispatch)
- **신규 문서**: `design/CHARACTER_PATHS.md` (390줄, 3캐릭터 × 15미션 경로)

---

**이 문서를 다른 세션의 첫 번째 참고 자료로 사용하세요.**
**모든 컨텍스트는 log.md, decisions/, 그리고 위 디렉토리 구조에 있습니다.**

다음 세션이 시작되면 사용자에게 "이어서 진행"을 요청해 옵션을 제시하면 됩니다.