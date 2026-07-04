# System: Combat (전투 시스템)

> **상위 결정**: `../../decisions/0003-combat-system.md` (Accepted, Revised), `../../decisions/0014-data-salvage.md` (Accepted)
> **관련**: ADR-0008 (Item Tier), ADR-0011 (Portraits), ADR-0012 (PPL/ZDR), ADR-0013 (Events)

## 목적

사이버스페이스 안에서 ICE / 적 decker와의 전투를 *실시간 + 메뉴 스킬* (RT-MS)로 표현. Pillar 1 (The Run), 3 (The Flatline), 5 (The Style)를 모두 만족.

> **Pillar 3 (강화, ADR-0014)**: 전투 승리 시 *Data Salvage*로 부분 회복 가능. 단, *이겨야만* + *20%만* + *선택해야만* — 무게 유지.

## RT-MS (Real-Time with Menu Skills)

ADR-0003의 핵심. 한 줄 요약: **실시간 자동 공격 + 메뉴로 강력한 스킬**.

### 자원 (Resources)

| 자원 | 설명 | 회복 |
| --- | --- | --- |
| **HP** (Health) | 데크의 무결성. 0 = flatline. | 전투 승리 시 Data Salvage (HEAL 20%) |
| **AP** (Action Points) | 스킬 비용. 시간 경과로 자동 회복. | 자연 회복 |
| **BW** (Bandwidth) | 동시 활성 program 수. | 자연 회복 |
| **PW** (Processing Power) | program 복잡도 한계. | 고정 (장비 의존) |

**HP 풀 (T1~T5)**:
- T1: 100 HP
- T2: 120 HP
- T3: 150 HP
- T4: 200 HP
- T5: 300 HP

(구체 수치는 `decisions/0008-progression-system.md` L213 "향후 결정" — Phase 5+ 밸런스 패치에서 확정)

### 자동 공격 (Auto-Attack)

- 양쪽 (플레이어 + 적)이 일정 간격으로 자동 공격
- 1 attack / 2초 (양쪽 동시)
- 기본 데미지: 자키 기본 5, ICE 기본 3 (T1 기준)
- 시각: ASCII 깜빡임, 사이드 이동, 데미지 숫자
- 한쪽 HP 0 또는 플레이어가 결정할 때까지 지속

### 메뉴 스킬 (Skill)

- `[SPACE]` → 메뉴 열림, **시간 정지**
- 사용 가능한 스킬 목록 (AP 비용, 효과)
- 방향키 선택, `[ENTER]`로 실행 → 시간 재개
- 명확한 피드백: 데미지, 효과, 자원 변화 표시

### Programs (메뉴 스킬)

| Program | Type | AP | 효과 |
| --- | --- | --- | --- |
| **Goliath** | Attack | 3 | heavy hit (3x base, 25 dmg) |
| **Kraken** | Attack | 4 | strongest attack (50 dmg) |
| **Hammer** | Attack | 2 | medium attack |
| **Virus** | Attack | 2 | DoT (3 ticks) |
| **Worm** | Attack | 2 | multi-hit (2-3 hits) |
| **Wisp** | Defense | 2 | shield +1 (active) |
| **Wardrone** | Defense | 2 | auto-counter (active) |
| **Shield** | Defense | 1 | one-time block |
| **Watchdog** | Detect | 1 | reveal enemy next attack |
| **Probe** | Detect | 1 | show enemy HP / skill |
| **Hellhound** | Track | 3 | forced engagement |

(데이터: `data/programs/programs.json`)

### Combat Flow

```
[Matrix: encounter ICE]
  ↓
[PPL vs ZDR 표시 — 진입 결정]
  ↓ (Continue)
[Combat begins: real-time, auto-attack starts]
  ↓ (continuous)
[Auto-attack ticks: 양쪽 자동 공격, 시각: 깜빡임/숫자]
  ↓ (player presses SPACE anytime)
[Menu: time pauses]
  ↓
[Player selects skill]
  ↓
[Time resumes, skill executes]
  ↓
[Combat continues until: ICE HP 0 OR player HP 0 OR player disengages]
  ↓ (ICE 격파 시)
[Data Salvage 메뉴 — 시간 정지 유지 (ADR-0014)]
  ↓
[매트릭스 복귀]
```

## Data Salvage (ADR-0014)

전투 승리 후 *데이터 회수* 흐름. Pillar 3의 무게를 일부 완화하되, *선택 + 승리 + 제한* 으로 무게 유지.

### Salvage 메뉴

```
=========================
   DATA SALVAGE
=========================
ICE 격파. 잔여 데이터 회수 가능.

> HEAL    +20% max HP (T1 = +20, T3 = +30)
  FRAG    program fragment (Phase 6+)
  CRED    credits (Phase 6+)
  SKIP    no reward

↑/↓ select, ENTER confirm
=========================
```

### Phase 5 범위

- **HEAL만 작동** (FRAG, CRED는 "Phase 6+: not yet implemented" 안내)
- 회복량: `round(max_hp * 0.20)`, 최소 1
- HP가 max인 상태에서 HEAL 선택 → "no damage to repair" 메시지 + 회복 0 (자원 낭비 알림)

### Phase 6+ 확장

- **FRAG**: program 1개 unlock (런 내 — unlock이 런 내에 머무름, 메타 X)
- **CRED**: Info Market (픽서 construct)에서 정보 구매 — 미션 목표 힌트, alarm 감소 아이템 등
- 디시전 트레이드오프: HEAL 즉시 vs FRAG/CRED 장기 보상

### Disengage / Death

- **Disengage (철수)**: ICE 격파 X → salvage 없음 (ADR-0003)
- **Death (자키 HP 0)**: salvage 없음 → flatline (Pillar 3)

### Pillar 정합

- **P1 (The Run)**: 한 런 = 한 무게. 회복은 *승리의 보상*. 매번 모든 전투 이길 수 없음 → 자키는 여전히 위험.
- **P2 (The Matrix)**: salvage는 매트릭스 안의 *데이터 추출*. Pillar 2 정합.
- **P3 (The Flatline)**: 회복이 *있지만* (a) 이겨야만, (b) HEAL만, (c) 20%만. 무조건 회복 X. 자키가 5번 싸워서 1번 회복할 수 있는 구조 — 무게 유지.
- **P4 (The Build)**: FRAG (런 내 unlock), CRED (메타 진행) — Pillar 4와 정합.
- **P5 (The Style)**: ICE 격파 → "data exposed" → salvage — 깁슨 어휘.

## 비주얼 디자인 (ADR-0011, ADR-0003)

### 전투 화면

```
[Player]              [Enemy]
◉P◉                   ▲ICE▲
[▓▓▓▓▓░░░] HP 50/100  [▓▓▓▓▓▓▓▓] HP 80/100
[█] AP 4/6            (ICE: AP N/A)

Action log:
> You hit ICE for 5 damage.
> ICE hits you for 3 damage.
> You hit ICE for 5 damage.

[SPACE] for skills   [ESC] to disengage
```

### 메뉴 (시간 정지)

```
=========================
        MENU
=========================
Skills available (AP 4/6):

> GOLIATH    (3 AP)  - heavy attack
  WISP       (2 AP)  - shield (active)
  WARDRONE   (2 AP)  - auto-counter (active)
  PROBE      (1 AP)  - reveal enemy
  VIRUS      (2 AP)  - DoT
  CANCEL

↑/↓ select, ENTER confirm
=========================
```

### 애니메이션

- **자동 공격**: 0.2초 깜빡임 + 데미지 숫자 표시
- **스킬 발동**: 0.5초 효과 (브래킷 변경, 색 변화, 큰 데미지)
- **메뉴 열림**: 화면 dim, 메뉴 박스 fade-in
- **HP 변화**: HP 바 색 변화 (녹→황→적)
- **상호작용**: 적 공격 시 화면 흔들림 효과 (ASCII)
- **ICE 격파**: portrait fade-out (선택)

## PPL & ZDR 통합 (ADR-0012)

### Combat 진입 전

```
> You approach: [ICE — Standard]
> ZDR: 7 (TOUGH for your PPL 6)
> Recommendation: Disengage or upgrade.

[Continue] [Disengage]
```

### Combat 중 HUD

```
[YOU: PPL 6]  [ZONE: ZDR 7]  Status: TOUGH (0.86x)
◉P◉ [▓▓▓▓▓░░░] HP 50/100     ▲ICE▲ [▓▓▓▓▓▓▓▓] HP 80/100
```

### Status (5 categories)

| Ratio | Status | 색상 | 의미 |
| --- | --- | --- | --- |
| > 1.5 | SAFE | green | 압도적 |
| 1.0 - 1.5 | MATCH | cyan | 균등 |
| 0.75 - 1.0 | TOUGH | yellow | 불리 |
| 0.5 - 0.75 | DEADLY | red | 매우 위험 |
| < 0.5 | FUTILE | dark_red | 자살행위 |

## 구현 가이드

### Phase 5+ Combat 모듈 구조

```
src/roguelike_sprawl/combat/
├── __init__.py
├── state.py        # CombatState (player, enemy, tick, menu)
├── programs.py     # Program 데이터 + 사용 가능 슬롯
├── engine.py       # 자동 공격 tick, menu pause/resume
├── damage.py       # damage 계산, HP 변화
├── salvage.py      # Data Salvage 메뉴 (ADR-0014)
└── render.py       # combat 화면 렌더링
```

### Player state 확장

```python
@dataclass
class Player:
    loadout: Loadout
    hp: int           # current HP
    max_hp: int       # calculated from tier
    ap: int           # current AP
    bw: int           # bandwidth
    pw: int           # processing power
```

### Salvage flow

```python
def apply_salvage(choice: SalvageChoice, player: Player) -> int:
    """Return new HP after applying salvage choice."""
    if choice is SalvageChoice.HEAL:
        heal = max(1, round(player.max_hp * 0.20))
        return min(player.max_hp, player.hp + heal)
    if choice is SalvageChoice.SKIP:
        return player.hp
    # FRAG, CRED: Phase 6+
    return player.hp
```

## 향후 결정

- HP 풀 T1~T5 구체적 수치 (Phase 5+ 밸런스)
- 자동 공격 속도 (1-2초)
- AP 회복 속도
- 메뉴 키 (Space vs Tab)
- 다중 적 (1-3 동시)
- 시각 효과 디테일
- HEAL 비율 (20% 적절? 15%? 25%?)
- FRAG / CRED 시스템 상세 (Phase 6+)
- 알람 / trace와 salvage의 상호작용

## 관련 문서

- `decisions/0003-combat-system.md` — RT-MS
- `decisions/0014-data-salvage.md` — Data Salvage
- `decisions/0008-progression-system.md` — Item Tier, HP 풀
- `decisions/0011-ascii-portraits.md` — combat portrait
- `decisions/0012-difficulty-rating.md` — PPL/ZDR
- `decisions/0013-story-events.md` — combat event
- `design/core_loop.md` — combat micro-loop
- `design/glossary.md` — HP, AP, BW, PW, Salvage
- `testcases/combat/salvage.md` — TC-COMBAT-001~008
