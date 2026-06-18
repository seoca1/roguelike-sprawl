# Roguelike Sprawl - AI Agent Guide

이 문서는 `Game/roguelike_sprawl/`에서 작업하는 모든 AI 에이전트를 위한 작업 규약이다. 루트 `AGENTS.md`를 보완한다.

## 1. 프로젝트 개요

윌리엄 깁슨의 스프롤 3부작 세계관을 배경으로 한 로그라이크. 플레이어는 데커(console cowboy)가 되어 사이버스페이스에서 ICE를 뚫고 임무를 수행한다. 자세한 내용은 `README.md`와 `ROADMAP.md`를 참조.

## 2. 디렉토리별 규칙

| 디렉토리 | 에이전트의 역할 | 절대 규칙 |
| --- | --- | --- |
| `raw/` | **읽기 전용** | 절대 수정 금지. 원본 자료의 무결성 유지. |
| `wiki/` | 자유롭게 편집, 인덱스/로그 갱신 필수 | LLM Wiki 계층. 인용이 가능한 모든 페이지에 원문 인용 포함. |
| `design/` | 자유롭게 편집, 사용자 검토 영역 | 활성 스펙. 사용자가 직접 수정할 수 있음을 인지. |
| `testcases/` | 자유롭게 편집, 템플릿 사용 | 디자인 변경 시 동기화 필요. |
| `decisions/` | Draft 상태는 자유, Accepted는 immutable | 결정된 사항 임의 변경 금지, 새 결정은 신규 ADR로. |
| `prototype/` | 미정 | 엔진 결정 후 생성. |
| 루트 메타 파일 | 신중히 수정 | README, AGENTS.md, index, log, ROADMAP, SETUP_LOG |

## 3. 작업 워크플로우

### 3.1 새 원본 자료 추가 (예: 소설 챕터 발췌)
1. `raw/` 에 원본 추가 (절대 수정하지 말 것)
2. `AGENTS.md` 의 "LLM Wiki Operations" 절차 수행:
   - 원문 읽기 → 핵심 추출 → 기존 위키 페이지 갱신
   - 신규 페이지 필요 시 생성
   - `index.md` 갱신
   - `log.md` 에 `[YYYY-MM-DD] ingest | 제목` 형식으로 기록
3. 위키 페이지에 원문 인용 추가 (가능하면)

### 3.2 게임 디자인 변경
1. `decisions/` 에 새 ADR 작성 또는 기존 ADR Status 변경
2. 영향 받는 `design/systems/*.md` 갱신
3. `testcases/` 에 회귀 테스트 추가/갱신
4. `design/GDD.md` 의 본문 또는 Open Questions 갱신
5. `log.md` 에 기록

### 3.3 결정 요청
- `decisions/template.md` 사용
- 옵션 비교표 + 추천안 + 열린 질문 포함 필수
- 사용자가 결정하면 Status를 "Accepted"로 변경하고 결과(Consequences) 섹션 채우기

## 4. Sprawl 세계관 정확성 규칙

깁슨 원작의 톤과 용어를 정확히 살리는 것은 디자인의 일부다.

- 깁슨이 만든 용어(ICE, deck, program, construct, wetware, console cowboy 등) 사용
- 1980년대 깁슨이 상상한 미래의 톤 — 너무 깔끔하거나 유토피아적이지 않음
- "Sprawl" = 보스턴-애틀랜타 메트로폴리스의 속칭
- "Freeside" = L5 궤도 식민지
- 인종차별, 빈곤, 중독, 신체 훼손 같은 어두운 주제를 회피하지 말 것
- 21세기 인터넷 memes, Cyberpunk 2077, D&D 등 다른 작품의 용어로 대체 금지
- 사실 단언 시 원문 인용 첨부 ("깁슨에 따르면..." → 인용 필수)

### 4.1 World Source: Fiction wiki

게임의 세계관은 **`../../../Fiction/wiki/`** (깁슨 분석 wiki)을 *Primary source*로 참조한다.

- 게임 wiki (`Game/roguelike_sprawl/wiki/world/`)는 게임용 요약/적응
- 깊은 분석/원문 인용/캐릭터 디테일은 Fiction wiki 참조
- Fiction wiki 페이지 예시:
  - `../../../Fiction/wiki/authors/william-gibson.md`
  - `../../../Fiction/wiki/works/neuromancer.md` (1984)
  - `../../../Fiction/wiki/works/count-zero.md` (1986)
  - `../../../Fiction/wiki/works/mona-lisa-overdrive.md` (1988)
  - `../../../Fiction/wiki/characters/case.md`
  - `../../../Fiction/wiki/characters/molly-millions.md`
  - `../../../Fiction/wiki/settings/cyberspace.md`
  - `../../../Fiction/wiki/index.md`

게임 내 텍스트 작성 시:
1. Fiction wiki에서 원문 톤 확인
2. 게임 컨텍스트에 맞게 적응
3. 원문에 없는 요소를 만들지 말 것
4. 새 요소가 필요하면 Fiction wiki의 *이전 작품* (Bridge, Blue Ant, Jackpot)에서 차용 가능 — 단 명시

## 5. LLM Wiki Operations (raw / wiki / schema)

이 프로젝트는 표준 LLM Wiki 패턴을 따른다.

- **Ingest**: raw에 새 자료 → 관련 wiki 페이지 작성/갱신 → index 갱신 → log 기록
- **Query**: 사용자가 질문 → index로 관련 페이지 찾기 → 인용과 함께 답변 → 가치가 있으면 결과를 새 wiki 페이지로 file-back
- **Lint**: 주기적으로 wiki 건강 점검
  - orphan 페이지 (인바운드 링크 없음)
  - 모순 (여러 페이지의 동일 주제 다름)
  - 인용 누락 (사실 단언인데 출처 없음)
  - 갱신 필요한 페이지 (오래된 정보)

## 6. 코딩 규칙 (Accepted 결정 반영)

### 언어 및 의존성
- **언어**: Python 3.11+ (3.12, 3.14 호환 확인)
- **렌더링 / 게임 루프**: python-tcod (>= 16.0, 21+ 검증)
- **테스트**: pytest
- **린트 / 포맷**: ruff
- **타입 체크**: mypy (strict)
- **의존성 관리**: pyproject.toml + uv (또는 pip)
- **빌드 백엔드**: hatchling

### 디렉토리 구조 (Phase 4 확정)

코드 프로젝트는 `prototype/` 하위. 디자인 문서와 분리.

```
prototype/
├── pyproject.toml          # uv / pip 프로젝트 설정
├── README.md               # 코드 프로젝트 README
├── Makefile                # 편의 명령
├── .gitignore, .editorconfig, .python-version
├── src/
│   └── roguelike_sprawl/   # Python 패키지
│       ├── __init__.py
│       ├── __main__.py     # python -m roguelike_sprawl
│       ├── engine/         # tcod 통합 (app, render, input, config)
│       ├── ecs/            # ECS-lite (entity, world)
│       ├── i18n/           # 번역 (translator)
│       ├── portraits/      # ASCII Portraits (manager)
│       ├── data/           # 데이터 로더
│       ├── matrix/         # (Phase 5) 사이버스페이스
│       ├── combat/         # (Phase 5) RT-MS 전투
│       ├── programs/       # (Phase 5) 프로그램
│       └── jobs/           # (Phase 5) 의뢰
├── tests/
│   ├── conftest.py
│   └── unit/               # 단위 테스트
├── data/
│   ├── i18n/               # en.json, ko.json
│   ├── portraits/          # portraits.json
│   ├── programs/           # programs.json
│   └── fonts/              # libtcod terminal font
├── scripts/
│   └── download_font.py    # 폰트 다운로드
└── .github/workflows/
    └── ci.yml              # GitHub Actions CI
```

### 스타일
- PEP 8 + ruff 기본
- 모든 public 함수 / 클래스에 타입 힌트 + docstring
- `from __future__ import annotations` 사용
- 한 줄 100자 (ruff)
- 모듈 / 클래스 / 함수 모두 docstring
- `__slots__` 사용 (메모리 효율)

### 명령 (Makefile)

```bash
make sync         # uv sync --all-extras
make download-font  # 폰트 다운로드 (최초 1회)
make run          # 게임 실행 (hello-world)
make test         # pytest
make lint         # ruff check
make format       # ruff format
make typecheck    # mypy
make build        # uv build
make clean        # 캐시 정리
make all          # format + lint + typecheck + test
```

### 빠른 데모 (Phase 5)

```bash
# 30초 자동 플레이 (Menu → Hub → Matrix 사이클, Fog 표시)
uv run python scripts/play.py

# 짧은 데모
uv run python scripts/play.py --duration 8 --step-delay 0.3

# 화면 누적 (스크롤)
uv run python scripts/play.py --no-clear

# 한글
uv run python scripts/play.py --lang ko
```

추가 도구:
- `scripts/combat_simulator.py` — 단일 전투 검증
- `scripts/combat_grades.py` — 5등급 진행 비교
- `scripts/demo.py` — 2분 전체 플레이

### 코드 변경 시 워크플로우
1. 관련 `design/systems/*.md` 와 `testcases/*.md` 확인
2. 자동 테스트 추가 (단위/통합)
3. `make format && make lint && make typecheck && make test`
4. `log.md` 에 기록
5. 영향 받는 ADR / 결정이 있으면 ADR 갱신

### i18n (번역) 가이드라인 (ADR-0010)

- **1차**: 영어 (en) — 깁슨 원문 톤 직접 보존
- **보조**: 한글 (ko) — 번역/자막 추가
- **고유명사**: 영어 원문 그대로 사용 가능 (Case, Tessier-Ashpool, Ono-Sendai, ICE, construct 등)
- **일반 명사/서술/대사**: 한국어 의역
- **표시 모드**: Off (영어만) / Subtitle (영어+한글) / Replace (한글만)
- 자세한 내용: `decisions/0010-i18n-content-pipeline.md`, `design/glossary.md` 의 "고유명사 번역 원칙"

### CI / CD
- GitHub Actions: macOS + Windows 매트릭스
- PR마다 lint + format + typecheck + test 자동 실행
- python-tcod 21+ 검증

## 7. 절대 하지 말 것

- `raw/` 수정
- 결정된 사항(`decisions/`의 Accepted 상태) 임의 변경
- 한 세션에 너무 많은 문서/파일 변경 (사용자 검토 부담)
- 원작에 없는 사실의 무성한 단언
- 다른 사이버펑크 작품의 톤/용어 차용 (Cyberpunk 2077, Shadowrun, D&D 등)
- Fiction wiki (`../../../Fiction/wiki/`) 수정 — 깁슨 분석은 Fiction 프로젝트 영역

## 8. 작업 시작 체크리스트

- [ ] `ROADMAP.md` 의 "Current Phase" 확인
- [ ] `decisions/README.md` 에서 미해결 결정 확인
- [ ] `index.md` 에서 관련 위키 페이지 찾기
- [ ] 작업 완료 후 `log.md` 갱신

## 9. 작업 종료 체크리스트

- [ ] `index.md` 가 새 페이지를 모두 가리키는가
- [ ] `log.md` 에 이번 세션 작업이 기록되었는가
- [ ] 영향 받는 `design/`/`testcases/`/`decisions/`가 동기화되었는가
- [ ] raw에서 읽은 자료는 모두 인용되었는가
