# System: Progression (종합 진행)

> **상위 결정**: `../../decisions/0008-progression-system.md` (Accepted, Revised)
> **관련**: [grade-progression.md](./grade-progression.md) (등급 단계), [difficulty-rating.md](./difficulty-rating.md) (난이도), [crafting.md](./crafting.md) (제작), [economy.md](./economy.md) (재화)
> **구현**: `../../prototype/src/roguelike_sprawl/matrix/ppl.py` (PPL 계산)

## 목적

자키가 한 런 안에서 **고정**된 스탯을 가지고, 런 사이에는 **등급 (meta progression)** 으로 성장하는 시스템. Pillar 4 ("The Build") 의 직접적 표현.

## 3-tier 진행 구조

### Tier 1: 런 내 고정 (In-Run, Immutable)

한 번 런을 시작하면 캐릭터의 기본 스탯은 **변하지 않음**.

| 요소 | 정의 | 변경 가능? |
|---|---|---|
| Deck tier | T1~T5 | ❌ (런 시작시 결정) |
| Programs | T1~T5 등급 매칭 | ❌ |
| Wetware | T1~T5 | ❌ |
| Construct | T0~T5 (0 = 없음) | ❌ |
| HP / ATK | tier 기반 | ❌ |

런 중 변경 가능한 것은 **인벤토리**와 **장비** (시간 한정 buff) 뿐.

### Tier 2: 메타 진행 (Meta Progression, 자키 등급)

자키가 죽으면 (`Stage.FAILED` → `Stage.DEATH_RESTART`) **새 자키** 등장.
새 자키는 이전 자키보다 한 단계 높은 등급으로 시작.

| 자키 순번 | 등급 | 시작 데크 | 비고 |
|---|---|---|---|
| 1번째 | 1-up | T1 Wisp/Strike | 신참 |
| 2번째 | 2-up | T2 Wisp/Hammer | 일반 |
| 3번째 | 3-up | T3 Wisp/Goliath | 숙련 |
| 4번째 | 4-up | T4 Wisp/Goliath/Wardrone | 베테랑 |
| 5번째 | 5-up | T5 Kraken/Goliath/Wisp/Wardrone + Dixie construct | 전설 |

> 메타 진행은 **unlock 만** (ADR-0006). 자키는 절대 잃지 않지만,
> 새 자키는 더 강하게 시작할 뿐.

### Tier 3: 아이템 티어 (Item Tier T1~T5)

매 런 안에서 **재료 → 컴포넌트 → 최종 아이템**으로 제작 (ADR-0015).
티어가 높을수록 stats 가 좋지만, **사용 횟수** 도 늘어남.

```
T1 (재료 5개) → T2 컴포넌트 (4개) → T3+ 프로그램/아이템/construct
```

## PPL 공식 (ADR-0012)

```python
PPL = deck_tier * 3 + sum(programs * 2) + wetware_tier + construct_tier * 3
```

예시 (Grade 1): `PPL = 1*3 + (1+1)*2 + 1 + 0 = 8`
예시 (Grade 5): `PPL = 5*3 + (5+5+5+5)*2 + 5 + 5*3 = 75`

PPL 은 ICE 의 ZDR 과 비교되어 Status (SAFE/MATCH/TOUGH/DEADLY/FUTILE) 결정.

## 런 사이 전이 (Death Cycle, ADR-0040)

```
MEET_NPC → EXTRACT_DATA → DEFEAT_ICE → JACK_OUT → REWARD → DEBRIEF → COMPLETE
                                                       ↓ (사망)
                                                    FAILED → DEATH_RESTART
                                                              ↓ (새 자키 선택)
                                                          PENDING (next grade)
```

## 진행 동기

- **신규 자키 unlock**: 처음 등급의 자키만 사용 가능 → 죽으면 다음 등급 해금
- **데크 업그레이드**: 각 등급마다 새로운 프로그램 슬롯 unlock (Wardrone, Kraken)
- **Construct**: T5 만 Dixie construct 동행 가능

## 구현 위치

| 요소 | 파일 |
|---|---|
| PPL 계산 | `src/roguelike_sprawl/matrix/ppl.py:42-57` |
| Status 결정 | `src/roguelike_sprawl/matrix/zdr.py:84-100` |
| 메타 진행 | `src/roguelike_sprawl/engine/death.py:220-267` (restart_with_new_jockey) |
| 등급 곡선 | `design/systems/grade-progression.md` |
| 제작 티어 | `src/roguelike_sprawl/programs/` + `data/crafting/` |

## 미래 작업 (Phase 6+)

- **Persistent unlocks**: 자키 도감을 Hall of Dead 에서 영구 보존
- **Custom deck editor**: 런 시작 전 데크 슬롯 자유 조합
- **Achievement 보상**: 특정 조건 달성 시 추가 티어 unlock