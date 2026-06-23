# Scripts 가이드 — 데모 / 검증 스크립트 실행법

`prototype/scripts/` 하위의 모든 실행 스크립트를 목적별로 정리.
모든 명령은 `Game/roguelike_sprawl/prototype` 디렉토리에서 실행한다고 가정.

```bash
cd "/Users/emilio/projects/Projects/Game/roguelike_sprawl/prototype"
```

---

## 5분 퀵 가이드 (어떤 걸 실행할까?)

### 🤔 시나리오별로 고르기

| 하고 싶은 것 | 추천 명령 | 창필요 |
|---|---|---|
| **그래픽 노블 (캐릭터 대사) 보고 싶다** | `make gn` | ✅ |
| **터미널에서 그래픽 노블 보고 싶다** | `make gn-text` | ❌ |
| **게임 전체 플로우 보고 싶다** | `make demo` | ✅ |
| **전투 시스템 작동 확인** | `uv run python scripts/combat_effects_demo.py` | ❌ |
| **전투 → 사망 → 부활 사이클** | `make death-demo` | ❌ |
| **단위 테스트 실행** | `uv run pytest` | ❌ |

### ⚡ 가장 빠른 시작 (30초)

```bash
cd "/Users/emilio/projects/Projects/Game/roguelike_sprawl/prototype"

# 1. GUI 창에서 그래픽 노블 보기 (창 필요, 30초)
make gn

# 2. 터미널에서 그래픽 노블 보기 (창 불필요, 5초)
make gn-text

# 3. 풀 게임 데모 (Prologue → 전투, SDL 창)
make demo

# 4. GUI 없이 텍스트로 빠르게 (2분)
uv run python scripts/demo.py --duration 10
```

### 🎮 데모 스크립트 5종 비교

| 스크립트 | 창필요 | 출력 | 주용도 | 시간 |
|---|---|---|---|---|
| `play.py` | ✅ | GUI | 빠른 검증 / 시연 | 30초 |
| `demo.py` | ❌ | 텍스트 | 터미널headless | 2분 |
| `demo_all.py` | ❌ | 텍스트 | gameplay + GN 통합 | 20초 |
| `graphic_novel.py` | ❌ | 텍스트 | 스토리만 | 1분 |
| `full_demo.py` | ✅ | GUI | 풀 플로우 + 전투 | 1분 |

### 📐 용어 구분

| 용어 | 의미 | 환경 |
|------|------|------|
| **GUI** / **Windowed** / **Game screen** | 실제 SDL 창 렌더링 | 창 환경 필요 |
| **Text** / **Headless** / **Terminal** | 터미널에 텍스트 프레임 출력 | 어디서든 가능 |
| **Interactive** | 키보드 입력 대기 | 창 환경 필요 |

### ⚡ 빠른 시작

```bash
# GUI (창 필요) — 실제 게임 화면
make gn              # 그래픽 노블 (케이/novice) — SDL 창
make gn-veteran     # 그래픽 노블 (실/veteran)
make gn-heretic     # 그래픽 노블 (카스/heretic)
make gn-all         # 그래픽 노블 (전캐릭터 12 scenes 랜덤)
make demo           # 풀 게임 데모 (Prologue → 전투)
make play           # 인터랙티브 플레이

# Text (창 불필요) — 터미널 출력
make gn-text              # 그래픽 노블 (케이) — 터미널
make gn-text-all          # 그래픽 노블 (전캐릭터) — 터미널
make text-demo            # 시네마틱 텍스트 only
```

### 📖 데모 모드 설명

**Mode 1 — New Run (Gameplay)**
```
메인메뉴 → 캐릭터 선택 → 챕터 → Hub → Matrix → 전투 → Jack Out → Hub
```
`play.py` (GUI) 또는 `demo.py` (텍스트)로 실행.

**Mode 2 — Graphic Novel (스토리 자동재생)**
```
메인메뉴 → Graphic Novel 메뉴 → 씬 자동 재생 → SAVED_PROGRESS
```
스토리/대사만 있고 실제 gameplay 없음. `graphic_novel.py`로 실행.

**Mode 3 — Story-mode (전투 스킵 gameplay)**
```
New Run과 동일하지만 ICE 전투가 자동으로 승리
```
`full_demo.py --story-mode`로 실행.

**Mode 4 — Death Cycle (전투 → 사망 → 부활)**
```
전투 → 사망 → DEATH_SUMMARY → Hall of Dead → 새 자키
```
`death_in_action_demo.py`로 실행.

**Mode 5 — Combat Effects (VFX 검증)**
```
공격 / 콤보 / 버스트 어택 / 방어 / 스킬 15가지
```
`combat_effects_demo.py`로 실행.

---

## 빠른 인덱스 (추천 검증 순서)

| 우선순위 | 명령 | 무엇을 확인하나 |
|---|---|---|
| 1 | `uv run pytest` | **전 시스템 unit tests (2690개)** |
| 2 | `make gn-text` | **그래픽 노블 GUI 텍스트** (캐릭터 대사, 창 불필요) |
| 3 | `make gn` | **그래픽 노블 GUI 창** (실제 게임 화면, 창 필요) |
| 4 | `make demo` | 풀 게임 자동플레이 (Prologue → 전투) |
| 5 | `make play` | 인터랙티브 플레이 |
| 6 | `uv run python scripts/death_in_action_demo.py` | 전투 → 사망 → 재시작 end-to-end |
| 7 | `uv run python scripts/combat_effects_demo.py --no-color` | 5-Layer VFX 10-씬 |

### Make 명령 요약 (창 필요 여부)

| 명령 | 창필요 | 용도 |
|------|--------|------|
| `make gn` | ✅ | 그래픽 노블 — 케이 (SDL 창) |
| `make gn-veteran` | ✅ | 그래픽 노블 — 실 (SDL 창) |
| `make gn-heretic` | ✅ | 그래픽 노블 — 카스 (SDL 창) |
| `make gn-all` | ✅ | 그래픽 노블 — 전캐릭터 12 scenes (SDL 창) |
| `make gn-text` | ❌ | 그래픽 노블 — 케이 (터미널) |
| `make gn-text-all` | ❌ | 그래픽 노블 — 전캐릭터 (터미널) |
| `make demo` | ✅ | 풀 게임 데모 |
| `make play` | ✅ | 인터랙티브 플레이 |
| `make text-demo` | ❌ | 시네마틱 텍스트 |

---

## 1. 전투 / 사망 사이클 검증 (Combat + Death)

### `death_in_action_demo.py` ⭐ 가장 중요
**실제 전투(`step_combat`) → `trigger_death` → DEATH_SUMMARY → HALL_OF_DEAD → 새 자키** 의 end-to-end 데모.

```bash
# 기본 실행 (ICE 표준, HP=5, ATK=0, 약 4초)
uv run python scripts/death_in_action_demo.py

# 빠르게 (8초 안에 5-Phase 전부)
uv run python scripts/death_in_action_demo.py --duration 8 --step-delay 0.1

# 다른 ICE 타입
uv run python scripts/death_in_action_demo.py --ice black
uv run python scripts/death_in_action_demo.py --ice watchdog

# 한글 자막
uv run python scripts/death_in_action_demo.py --lang ko
```

**검증 항목**:
- `scripts/text_visibility_demo.py` — **텍스트 가시성 4-씬 데모 (footer/side panel/GN prose/풀 매트릭스, ADR-0047)**
- `scripts/ending_b_demo.py` — **엔딩 B 메뉴/세이브 5-씬 데모 (MENU → ENDING_MENU → 씬 + Save JSON, ADR-0048)**
- `scripts/ending_c_demo.py` — **엔딩 C 메뉴/세이브 7-씬 데모 (3 chars × ENDING_C + 2 scenes + Save 1.2.0 + v1.1.0 마이그레이션, ADR-0049)**
- `scripts/boss_ice_demo.py` — **보스 ICE 7-씬 데모 (Wintermute + T-A Prime × 3 phases + summary table, ADR-0050)**
- Phase 1: `step_combat` 21 ticks → `outcome=defeat` (실제 combat loop)
- Phase 2: `trigger_death(state, reason="ICE breach")` → `state.screen=DEATH, is_dead=True, total_runs++`
- Phase 3: `advance_to_death_summary` → DEATH_SUMMARY 렌더
- Phase 4: `render_hall_of_dead_screen` → 1명 archived
- Phase 5: `restart_with_new_jockey(state, "novice")` → CHARACTER_SELECT

**성공 출력 예**:
```
SUMMARY: Combat → Death → Death Summary → Hall of Dead → New Jockey
  ✓ Real combat: 21 ticks, outcome=defeat
  ✓ trigger_death: state.screen=character_select, is_dead=False
  ✓ Hall of Dead: 1 jockey(s) archived
  ✓ Restart with new jockey: character_id=veteran
```

### `combat_effects_demo.py` ⭐ VFX 검증
**5-Layer VFX 시스템** 10-씬 검증. palette, 애니메이션, 파티클, 크리티컬, 15 스킬, 5 ICE 인트로/사망, HUD, 5-단계 콤보, Bundle, 풀 파이트.

```bash
# 전체 10-씬
uv run python scripts/combat_effects_demo.py --no-color

# 특정 씬만
uv run python scripts/combat_effects_demo.py --only attack
uv run python scripts/combat_effects_demo.py --only combo
uv run python scripts/combat_effects_demo.py --only bundle
```

**성공 출력 예**:
```
  ✓ Palette Centralization
  ✓ Layer 1+2 Hit Feedback
  ✓ Critical Hit
  ✓ 15 Skill Effects — 15 effects
  ✓ ICE Intro Cinematics — 5/5 ICE types
  ...
  10/10 scenes passed
```

### `combat_grades.py`
**자키 등급 1~5** 의 전투 진행 비교 (PPL, 데미지, 생존 시간).

```bash
uv run python scripts/combat_grades.py
```

**성공 출력 예**:
```
Grade           PPL  Ratio Status   Outcome     Time  Dmg Out  Dmg In  Skills
1-up 신참           8   1.33 match    VICTORY    12.1s       80      22       2
2-up 일반          16   2.67 safe     VICTORY     6.1s       80      12       2
...
5-up 전설          75  12.50 safe     VICTORY     0.1s       80       2       1
```

### `death_demo.py`
**DEATH → DEATH_SUMMARY → CHARACTER_SELECT** 흐름만 빠르게 (전투 생략).

```bash
uv run python scripts/death_demo.py
uv run python scripts/death_demo.py --lang ko
```

---

## 2. 그래픽 노블 / 시나리오

### `graphic_novel.py` ⭐ ADR-0032
**12-씬 그래픽 노블 자동재생** (3 캐릭터 × 4 씬, 한글 자막, 3개 저장 슬롯).

```bash
# ─── 기본 실행 ───
# 프로로그: 12 씬 셔플 (60초)
uv run python scripts/graphic_novel.py --mode prologue --seed 42

# 특정 캐릭터 (4 씬)
uv run python scripts/graphic_novel.py --mode novice
uv run python scripts/graphic_novel.py --mode veteran
uv run python scripts/graphic_novel.py --mode heretic

# 한글 자막
uv run python scripts/graphic_novel.py --mode prologue --lang ko

# 빠르게 (10x 속도, 6초)
uv run python scripts/graphic_novel.py --mode prologue --speed 10

# 짧게 (5초만)
uv run python scripts/graphic_novel.py --mode novice --duration 5

# ─── 저장 / 이어서 읽기 (ADR-0044, ADR-0051) ───
# 종료 시 자동으로 현재 진행 상황 저장 (슬롯 1)
uv run python scripts/graphic_novel.py --mode novice --duration 10
# → [gn-save] Saved progress to slot 1: .../gn_progress_slot_1.json

# 특정 슬롯에 저장
uv run python scripts/graphic_novel.py --mode veteran --slot 2 --duration 5
# → [gn-save] Saved progress to slot 2: .../gn_progress_slot_2.json

# 이어서 읽기 (가장 최근 슬롯 자동 선택)
uv run python scripts/graphic_novel.py --continue
# → [gn-save] Resuming from slot 2 (most recent): mode=veteran, ending A, scene 3

# 특정 슬롯에서 이어서 읽기
uv run python scripts/graphic_novel.py --continue --slot 3

# 저장 없이 데모
uv run python scripts/graphic_novel.py --mode novice --no-save

# 저장 슬롯 확인 (어떤 슬롯에 뭐가 있나)
ls data/saves/gn_progress_slot_*.json
```

**모드**:
- `prologue` — 3명 × 4 씬 = 12 씬 (랜덤 셔플)
- `novice` / `veteran` / `heretic` — 한 캐릭터 4 씬
- **조작**: `Space/→` 즉시 완료, `S` 스킵, `P` 일시정지, `ESC/Q` 종료
- **저장 슬롯**: 3개 (slot 1, 2, 3) — `--slot N`으로 지정

### `prologue.py`
**깁슨 원문 프롤로그 + The Finn 미션 브리핑** (시네마틱).

```bash
# 프로로그 + 브리핑 (기본)
uv run python scripts/prologue.py

# 빠른 속도
uv run python scripts/prologue.py --speed fast

# 특정 씬만
uv run python scripts/prologue.py --scene prologue
uv run python scripts/prologue.py --scene briefing
```

### `verify_original_prologue.py`
**오리지널 시나리오 (ADR-0031)** 검증 — 3 캐릭터 × 엔딩 A/B.

```bash
# 전체
uv run python scripts/verify_original_prologue.py --character all --ending all

# 특정 캐릭터
uv run python scripts/verify_original_prologue.py --character veteran
uv run python scripts/verify_original_prologue.py --character heretic --ending B
```

### `verify_prologue.py`
**프롤로그 / 브리핑 씬** 의 메트릭 검증 (커버리지, 길이).

```bash
uv run python scripts/verify_prologue.py
uv run python scripts/verify_prologue.py --scene coverage
uv run python scripts/verify_prologue.py --scene transitions --speed instant
```

### `demo_cinematic_art.py`
**시네마틱 ASCII 아트** 시스템 데모 (Finn, Dixie, Molly, Armitage 등 10개 캐릭터).

```bash
# 사용 가능한 캐릭터 목록
uv run python scripts/demo_cinematic_art.py --list

# 특정 캐릭터 / 배경
uv run python scripts/demo_cinematic_art.py --character finn
uv run python scripts/demo_cinematic_art.py --character cyberspace
uv run python scripts/demo_cinematic_art.py --character matrix_rain --scene chill
```

---

## 3. 전체 게임 자동플레이

### `play.py` ⭐ GUI窗口 필요 (가장 빠른 검증)
**MENU → HUB → MATRIX → COMBAT** 자동플레이 (~5-10초). SDL 창이 필요하지만 가장 빠른 검증.

```bash
# 기본 (30초)
uv run python scripts/play.py

# 빠르게 (5초)
uv run python scripts/play.py --duration 5 --step-delay 0.3

# 특정 캐릭터
uv run python scripts/play.py --character veteran

# 한글
uv run python scripts/play.py --lang ko

# ─── Graphic Novel 모드 ───
uv run python scripts/play.py --gn-mode novice    # Novice 스토리
uv run python scripts/play.py --gn-mode veteran   # Veteran 스토리
uv run python scripts/play.py --gn-mode heretic  # Heretic 스토리
uv run python scripts/play.py --gn-mode prologue  # Prologue (12 씬 랜덤)

# 이어서 읽기 (GN 저장소에서 복원)
uv run python scripts/play.py --gn-mode novice --continue
```

### `demo.py`
**MENU → HUB → Matrix 사이클** + Fog 표시 (터미널 headless, 창 필요 없음).

```bash
# 기본 (2분)
uv run python scripts/demo.py

# 짧게 (10초)
uv run python scripts/demo.py --duration 10

# 빠르게 (0.3초 딜레이)
uv run python scripts/demo.py --duration 8 --step-delay 0.3

# 화면 누적 (스크롤)
uv run python scripts/demo.py --no-clear

# 한글
uv run python scripts/demo.py --lang ko

# ─── 진입점 선택 (--menu-option) ───
# Menu 옵션 1~6 중 자동 선택:
uv run python scripts/demo.py --menu-option 1  # 1=New Run (gameplay)
uv run python scripts/demo.py --menu-option 2  # 2=Graphic Novel → prologue 자동
uv run python scripts/demo.py --menu-option 3  # 3=Graphic Novel → Novice
uv run python scripts/demo.py --menu-option 4  # 4=Graphic Novel → Veteran
uv run python scripts/demo.py --menu-option 5  # 5=Graphic Novel → Heretic

# ─── Graphic Novel直接 진입 (--gn-mode) ───
# 메뉴를 스킵하고 바로 GN 시작:
uv run python scripts/demo.py --gn-mode prologue
uv run python scripts/demo.py --gn-mode novice --lang ko
```

### `demo_all.py` ⭐ 풀 게임 + 그래픽 노블
**ADR-0032 통합** 풀 게임 자동플레이. 메뉴 → 그래픽 노블 진입 → 자동재생.

```bash
# 기본 (20초)
uv run python scripts/demo_all.py

# 특정 캐릭터로
uv run python scripts/demo_all.py --character veteran
uv run python scripts/demo_all.py --character heretic

# 한글
uv run python scripts/demo_all.py --lang ko

# 화면 누적
uv run python scripts/demo_all.py --no-clear
```

### `full_demo.py` / `full_demo_sound.py`
**Prologue → Briefing → Matrix → Combat** 풀 플로우 (interactive 가능).

```bash
# 빠른 자동
uv run python scripts/full_demo.py --fast

# 사운드 포함
uv run python scripts/full_demo_sound.py --fast

# 인터랙티브 모드
uv run python scripts/full_demo.py --interactive
uv run python scripts/full_demo.py --manual-combat

# 사운드 끄기
uv run python scripts/full_demo_sound.py --no-sound --volume 0
```

### `headless_sound_demo.py`
**헤드리스 사운드 데모** (오디오 + 텍스트). 단계별 실행 가능.

```bash
# 전체
uv run python scripts/headless_sound_demo.py --stage all

# 전투만
uv run python scripts/headless_sound_demo.py --stage combat --fast

# 사운드 끄기
uv run python scripts/headless_sound_demo.py --no-sound
```

### `visual_demo.py` ⭐ 8개 시스템 한 번에
**완전 시각적 데모** — 스토리, NPC, 이벤트, 사이버스페이스, 전투, 장비, 한글 폰트 전부.

```bash
uv run python scripts/visual_demo.py
```

**검증 항목** (10+):
- Story (Prologue + Briefing) with Korean subtitles
- NPC dialogue (Dixie) with branching choices
- Event stories with character art
- Cyberspace browser (World/Sector/Server)
- Scrolling graph exploration
- Combat with 20+ skills, damage variance, crit
- Equipment system (15 items, 8 slots, 6 tiers)
- Equipment visualizer (ASCII character with gear)
- Persistent status panel
- Korean TTF font (AppleGothic)

---

## 4. 특수 시스템 데모

### `demo_avatar.py`
**자키 아바타** 시스템 (ADR-0016) — 부위별 stat 표현, HP/부상 시각화.

```bash
uv run python scripts/demo_avatar.py
```

### `verify_combat_vfx.py`
**전투 VFX** 시각 검증 (15 스킬 효과 × 5 ICE).

```bash
# 전체
uv run python scripts/verify_combat_vfx.py --mode all

# 특정 스킬
uv run python scripts/verify_combat_vfx.py --only stun
uv run python scripts/verify_combat_vfx.py --only lifesteal

# 특정 ICE
uv run python scripts/verify_combat_vfx.py --ice black
```

### `combat_simulator.py`
**전투 시뮬레이터** (개발자/QA 도구). 인터랙티브 모드 — 단일 전투 검증.

```bash
# 인터랙티브 모드
uv run python scripts/combat_simulator.py
```

### `text_demo.py`
**텍스트 전용** 데모 (tcod 없이 순수 터미널 출력).

```bash
uv run python scripts/text_demo.py
uv run python scripts/text_demo.py --fast
```

---

## 5. 사운드 시스템

### `demo_sounds.py`
**27개 기본 사운드** 순차 재생.

```bash
# 전체 (기본 카테고리)
uv run python scripts/demo_sounds.py

# 특정 카테고리
uv run python scripts/demo_sounds.py --category combat
uv run python scripts/demo_sounds.py --category story
uv run python scripts/demo_sounds.py --category ui

# 빠르게
uv run python scripts/demo_sounds.py --fast --delay 0.1
```

### `demo_sound_keys.py`
**사운드 설정 + 키 바인딩** 인터랙티브 데모.

```bash
# 입력 로그
uv run python scripts/demo_sound_keys.py --input keylog.txt

# 요약만
uv run python scripts/demo_sound_keys.py --summary
```

### `verify_sound_config.py`
**SoundConfig 시스템** 검증.

```bash
# 전체
uv run python scripts/verify_sound_config.py

# 특정 영역
uv run python scripts/verify_sound_config.py --toggle combat
uv run python scripts/verify_sound_config.py --toggle movement
```

### `test_sound_libraries.py`
**사운드 라이브러리** 비교 평가 (어떤 libtcod/sdl/portaudio 사용 가능하나).

```bash
uv run python scripts/test_sound_libraries.py
```

---

## 6. 환경 / 설정

### `download_font.py`
**libtcod 터미널 폰트** 다운로드 (최초 1회).

```bash
uv run python scripts/download_font.py
# → data/fonts/terminal10x10_gs_tc.png 저장
```

### `test_tcod.py`
**tcod 렌더링** 진단 (폰트, 화면 크기, 컬러).

```bash
uv run python scripts/test_tcod.py
# → Font path, Screen size, Color test 출력
```

---

## 7. 회귀 테스트 (자동)

```bash
# 전체 2092 unit tests
uv run pytest

# 특정 파일만
uv run pytest tests/unit/test_combat_to_death.py -v
uv run pytest tests/unit/test_death_extended.py -v
uv run pytest tests/unit/test_combat_effects.py -v

# Lint + Format + Typecheck
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests

# 또는 Makefile로 한 번에
make all  # format + lint + typecheck + test
```

---

## 일반적인 실행 패턴

### 데모 비교 (death_in_action vs death_demo vs combat_effects)

| 데모 | 전투 시뮬 | 사망 | 재시작 | VFX | 속도 |
|---|---|---|---|---|---|
| `death_in_action_demo.py` | ✓ 실제 | ✓ trigger | ✓ 새 자키 | ✗ | 4-8초 |
| `death_demo.py` | ✗ 수동 | ✓ trigger | ✓ 새 자키 | ✗ | 4-8초 |
| `combat_effects_demo.py` | ✗ | ✗ | ✗ | ✓ 10-씬 | 30초 |

### 데모 비교 (play vs demo vs demo_all)

| 데모 | 시작 | 그래픽 노블 | 풀 게임 | 사운드 |
|---|---|---|---|---|
| `play.py` | MENU | 옵션 | ✓ 자동 | ✗ |
| `demo.py` | MENU | ✗ | ✓ | ✗ |
| `demo_all.py` | MENU | ✓ 통합 | ✓ | ✗ |
| `full_demo.py` | 프롤로그 | ✗ | ✓ 인터랙티브 | ✗ |
| `full_demo_sound.py` | 프롤로그 | ✗ | ✓ | ✓ |
| `headless_sound_demo.py` | 단계별 | ✗ | ✓ | ✓ |

---

## 문제 해결

### "Font not found"
```bash
uv run python scripts/download_font.py
```

### "ICE damage variance 비결정적"
`step_combat`의 RNG는 `random.Random()` (글로벌). 결정적 테스트는 `combat.rng = random.Random(42)` 로 시드.

### "상대 import 에러"
스크립트는 `python -m` 또는 `sys.path`로 src를 추가해야 함. 항상 `cd prototype/` 후 실행.

### "Interactive 스크립트가 멈춤"
`prologue.py`, `combat_simulator.py`, `full_demo.py --interactive` 는 키 입력 대기. 종료: `ESC` / `Q`.

### 한글이 깨짐
```bash
export LANG=ko_KR.UTF-8
uv run python scripts/death_in_action_demo.py --lang ko
```

---

## 스토리 구조 참고

### 단편소설 vs 게임 상태
참고: `design/scenario/story-stage-comparison.md`

| 구분 | 위치 | 개수 |
|------|------|------|
| **Stage (게임)** | `src/run/state.py:Stage` | 10개 |
| **Chapter (단편)** | `data/story/chapters/` | 3개 (케이/실/카스) |
| **Scene (GN)** | `data/scenes/{case,sil,kas}/` | 24개 (8×3) |

### Gibson 텍스트 위치
- **챕터 파일** (`case.json`, `sil.json`, `kas.json`) — NEW RUN에서 확인
- **GN 씬** 각 캐릭터별 — Graphic Novel 모드에서 확인
- **`story_cinematic.PROLOGUE_SCENE`** — **DEPRECATED** (데모 스크립트에서만 사용)

### GN 메뉴 변경 (2026-06-22)
- "PROLOGUE — 3 random" → **"ALL CHARACTERS — 12 scenes"**
- Gibson 프롤로그가 아님을 명확히 구분

---

## 새 데모 추가 시

`scripts/` 에 새 `.py` 파일 추가:

1. `from __future__ import annotations`
2. `sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))`
3. `argparse` 로 옵션 (특히 `--duration`, `--step-delay`, `--no-clear`, `--lang`)
4. docstring 첫 줄에 **무엇을 검증하나** 명시
5. 끝에 `=== {script_name} complete: N steps in Ts ===` 형식 출력
6. 이 README에 항목 추가
7. `log.md` 에 기록
