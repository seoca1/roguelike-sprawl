# Death & Restart Cycle (자키 사이클)

> **이 문서는 [`../../decisions/0040-death-restart-cycle.md`](../../decisions/0040-death-restart-cycle.md)의 디자인 명세.**
> 플레이어 자키가 HP 0이 되면 *인격이 보존된 채로* 사망 → 새 자키 또는 같은 자키로 재시작.

## 1. 개요

깁슨 소설에서 자키는 단순한 도구가 아닌 *인격체*다. "The Flatline"이라는 말은 단순한 게임오버가 아니라 *인격의 종결*을 의미한다. 이 디자인은 죽음을 서사적 무게로 다룬다.

| 단계 | 화면 | 내용 |
| --- | --- | --- |
| 1 | COMBAT | HP 0 |
| 2 | DEATH | FLATLINE 화면, X 머리, 2초 정적 |
| 3 | JACK_OUT | 4프레임 애니메이션 |
| 4 | **DEATH_SUMMARY** (신규) | 자키 리포트, 런 통계, Sprawl의 평가 |
| 5 | **RESTART_OPTIONS** (신규) | 새 자키 / 같은 자키 / Hall of Dead / 메뉴 |
| 6 | CHARACTER_SELECT or HUB or MENU | 선택에 따라 분기 |

## 2. DEATH_SUMMARY 화면

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    > FLATLINE <                            ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   ┌─────────────┐                                            ║
║   │  X  (X head) │   실 (Sil) — Veteran                    ║
║   │  ▲▲▲        │   Grade: 3-up                            ║
║   │  ║║║  ███   │   Run #7                                  ║
║   └─────────────┘   Died: TA Payroll                       ║
║                       Time: 47 minutes                      ║
║                                                              ║
║   ═══ RUNTIME STATS ═══                                     ║
║   Missions completed: 3 / 5                                ║
║   Data recovered: 234 / 500                                ║
║   Programs used: hammer, wisp, virus                       ║
║   Inventory: 2 materials, 1 program                        ║
║                                                              ║
║   ═══ INVENTORY AT DEATH ═══                                ║
║   - Jack-in Zapper (T2)                                     ║
║   - 3× raw_credit_chips                                     ║
║                                                              ║
║   ──────────────────────────────────────────                ║
║                                                              ║
║      "Old scores die hard. Mara's not waiting."           ║
║                                                              ║
║   ──────────────────────────────────────────                ║
║                                                              ║
║      [1] 새 자키 (다른 자키 선택)                          ║
║      [2] 같은 자키 (HUB로)                                  ║
║      [3] Hall of Dead Jockeys                               ║
║      [4] 메인메뉴                                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

## 3. Hall of Dead Jockeys 화면

```
╔══════════════════════════════════════════════════════════════╗
║                HALL OF DEAD JOCKEYS                          ║
║                                                              ║
║   "The Sprawl remembers everyone."                          ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   You have outlived 7 jockeys.                               ║
║   Longest run: 47m (Sil — Veteran)                          ║
║                                                              ║
║   ─── RECENTLY FALLEN ───                                  ║
║                                                              ║
║   > 1. 실 (Sil) — Veteran, 3-up                            ║
║       TA Payroll · 2026-06-20 14:30                        ║
║       "Old scores die hard."                                ║
║                                                              ║
║     2. 케이 (K) — Novice, 1-up                             ║
║       Chiba 11 · 2026-06-19 23:15                          ║
║       "You died a wage slave."                              ║
║                                                              ║
║     3. 카스 (Kas) — Heretic, 5-up                           ║
║       Sense/Net Core · 2026-06-19 11:00                   ║
║       "The wheel keeps turning."                            ║
║                                                              ║
║   ─── ARCHIVE STATS ───                                    ║
║   Total runs: 23                                            ║
║   Total deaths: 7                                           ║
║   Survival rate: 70%                                        ║
║   Avg missions/run: 2.3                                     ║
║                                                              ║
║   [↑/↓] navigate   [ENTER] detail   [ESC] back            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

## 4. Epitaph 풀 (Sprawl의 평가)

깁슨 톤 — 짧고 냉소적. 캐릭터별 3개씩, 총 9개.

### Novice (케이, K)
- "You died a wage slave."
- "Sprawl is short on memory."
- "Cash for the next, then."

### Veteran (실, Sil)
- "Old scores die hard."
- "Mara's not waiting."
- "T-A doesn't forget."

### Heretic (카스, Kas)
- "The wheel keeps turning."
- "Loa hears you still."
- "One spoke, not the wheel."

## 5. 데이터 구조

`engine/jockey_history.py`:
```python
@dataclass(frozen=True, slots=True)
class DeceasedJockey:
    """A record of a jockey who flatlined (ADR-0040)."""
    jockey_id: str
    name: str
    character_id: str
    grade: int
    died_at_node: str
    died_at_mission: str
    died_at_timestamp_ms: int
    inventory_snapshot: tuple[str, ...]
    missions_completed: int
    data_recovered: int
    playtime_minutes: int
    epitaph: str

class JockeyHistory:
    """Manages the Hall of Dead Jockeys archive."""
    def __init__(self, save_path: Path | None = None) -> None: ...
    def add(self, jockey: DeceasedJockey) -> None: ...
    def all(self) -> list[DeceasedJockey]: ...
    def recent(self, n: int = 10) -> list[DeceasedJockey]: ...
    def stats(self) -> JockeyStats: ...
    def save(self) -> None: ...
    def load(self) -> None: ...
    def render_lines(self, jockey: DeceasedJockey, lang: str = "en") -> list[str]: ...
```

## 6. AppState 확장

```python
# Jockey cycle (ADR-0040)
jockey_history: tuple[DeceasedJockey, ...] = ()
total_runs: int = 0
total_deaths: int = 0
total_missions_completed: int = 0
longest_run_minutes: int = 0
last_jockey_summary: DeceasedJockey | None = None
death_cause: str = ""  # "Combat" / "Black ICE" / "T-A ICE" / "Black ICE breach"
```

`ScreenKind` 추가:
- `DEATH_SUMMARY` (자키 리포트)
- `HALL_OF_DEAD` (Archive)

## 7. 화면 흐름 (상태 머신)

```
COMBAT (HP=0)
    ↓ trigger_death()
DEATH (FLATLINE, X 머리, 2초)
    ↓ 자동 전환
JACK_OUT (4프레임 애니메이션)
    ↓ 자동 전환
DEATH_SUMMARY (자키 리포트)
    ↓ [1] 새 자키 / [2] 같은 자키 / [3] Hall of Dead / [4] 메뉴
    ├── [1] → CHARACTER_SELECT → HUB (새 자키)
    ├── [2] → HUB (같은 자키, 인벤토리/미션 초기화)
    ├── [3] → HALL_OF_DEAD (Archive)
    └── [4] → MENU

HALL_OF_DEAD
    ↓ [ENTER] detail / [ESC] back
    └── [ESC] → DEATH_SUMMARY (다시)
```

## 8. MENU 통계 패널

MENU 우측에 누적 통계 표시:
```
RUN STATS
─────────
Jockeys outlived: 7
Total runs: 23
Total deaths: 7
Longest run: 47m
Avg missions/run: 2.3

[6] Hall of Dead Jockeys
```

## 9. 의존성

- `engine/death.py` — 기존 trigger_death / jack_out_to_hub 확장
- `engine/state.py` — jockey_history, ScreenKind 추가
- `engine/jack_out_view.py` — JACK_OUT 후 DEATH_SUMMARY로 전환
- `data/jockeys/deceased.json` — 누적 데이터 (영구 보존)
- `engine/jockey_history.py` (신규) — Archive 관리

## 10. 완료 조건 (Acceptance Criteria)

### Phase 1: 데이터
- [ ] `engine/jockey_history.py` 신규 (DeceasedJockey + JockeyHistory)
- [ ] `data/jockeys/deceased.json` 초기 (빈 배열)
- [ ] `AppState`에 jockey_history, total_runs, total_deaths 등 추가

### Phase 2: 화면
- [ ] `engine/death.py` — `render_death_summary()` 신규
- [ ] `engine/death.py` — `render_restart_options()` 신규
- [ ] `engine/death.py` — `render_hall_of_dead()` 신규
- [ ] `engine/state.py` — ScreenKind 2개 추가

### Phase 3: 입력 처리
- [ ] DEATH_SUMMARY에서 [1/2/3/4] 선택 처리
- [ ] HALL_OF_DEAD에서 [↑/↓/ENTER/ESC] 처리
- [ ] 새 자키 선택 시 player_grade, inventory 등 초기화

### Phase 4: 메뉴 확장
- [ ] MENU 5 옵션 → 6 옵션 (Hall of Dead 추가)
- [ ] MENU 우측에 RUN STATS 패널

### Phase 5: 테스트 (30+)
- [ ] DeceasedJockey 생성 / 직렬화 (5 tests)
- [ ] JockeyHistory add/all/recent/stats (8 tests)
- [ ] Epitaph 선택 (3 tests)
- [ ] DEATH_SUMMARY 렌더 (3 tests)
- [ ] HALL_OF_DEAD 렌더 (3 tests)
- [ ] 입출력 핸들러 (5 tests)
- [ ] 통합 시나리오 (3 tests)

### Phase 6: 데모
- [ ] `scripts/death_demo.py` — 자키 사망 → DEATH_SUMMARY → 새 자키 시연

### Phase 7: 메타 문서
- [ ] `index.md` 갱신
- [ ] `log.md` 갱신
- [ ] `ROADMAP.md` 갱신
- [ ] `dashboard/graphic-novel.html` (없으면 안 해도 됨)

## 11. 열린 결정 사항

- [ ] 자키 데이터 인계 여부 (ROM construct)
- [ ] Hall of Dead 보존 한도 (무제한 vs 최근 20)
- [ ] MENU 통계 표시 (항상 vs 옵션)
- [ ] deceased.json 영구 보존 (게임 삭제 시)

## 12. 다음 단계

1. 결정 사항 확정
2. `jockey_history.py` 구현
3. `death.py` 확장 (DEATH_SUMMARY, RESTART_OPTIONS, HALL_OF_DEAD)
4. AppState 확장
5. 메뉴 [6] 옵션 추가
6. 테스트 30+ 추가
7. `death_demo.py` 시연
8. 메타 문서 동기화
