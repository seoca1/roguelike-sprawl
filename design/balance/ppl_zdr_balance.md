# Balance: PPL / ZDR (난이도 곡선 검증)

> **관련**: [difficulty-rating.md](../systems/difficulty-rating.md), [grade-progression.md](../systems/grade-progression.md)
> **구현**: `../../prototype/src/roguelike_sprawl/matrix/ppl.py`, `matrix/zdr.py`
> **ADR**: 0012 (PPL/ZDR)

## 목적

등급 1~5 별 **PPL 곡선** 과 **ZDR 범위** 가 일관되게 매칭되어야
플레이어가 *성장감* 을 체감하면서도 *불가능한 도전을 거부받지 않음*.

## PPL 곡선 (검증됨)

```
PPL = deck_tier * 3 + sum(prog_tier * 2) + wetware_tier + construct_tier * 3
```

| Grade | deck | programs | wetware | construct | **PPL** |
|---|---|---|---|---|---:|
| 1 (신참) | T1 | Wisp T1, Strike T1 (×2) | T1 | — | **8** |
| 2 (일반) | T2 | Wisp T2, Hammer T2 (×2) | T2 | — | **16** |
| 3 (숙련) | T3 | Wisp T3, Goliath T3 (×2) | T3 | — | **24** |
| 4 (베테랑) | T4 | Wisp T4, Goliath T4, Wardrone T4 (×3) | T4 | — | **40** |
| 5 (전설) | T5 | Kraken T5, Goliath T5, Wisp T5, Wardrone T5 (×4) | T5 | Dixie T5 | **75** |
| 6 (마스터, Arc 5 finale) | T6 | Master programs (T6) (×4) | T6 | Dixie T6 | **120+** |

### Grade 6 (Master) — Arc 5 Finale

T6 장비 3종이 `equipment/equipment.py` 에 추가됨:

- `deck_master` (T6) — Wintermute/Neuromancer Merged, program_power=150
- `bodysuit_master` (T6) — Full-Body Cyborg Conversion, hp_bonus=120 + 한 번 부활
- `trodes_zion` (T6) — Zion Direct-Neural Link, ap_regen +100%

Loadout tier 검증: `0..6` 까지 허용. `MAX_TIER = 6` 상수.

PPL 성장 곡선: 8 → 16 → 24 → 40 → 75 (2배, 1.5배, 1.67배, 1.88배)
→ 가속 성장 — 메타 진행의 *성장감* 극대화.

## ZDR 베이스 (ZoneDepth)

| Zone | Base ZDR | 의도 |
|---|---:|---|
| SURFACE | 1 | 신참 데뷔 |
| MID | 5 | 중간 |
| DEEP | 8 | Loa / construct |
| CORE | 12 | 기업 핵심 |
| TA | 25 | Tessier-Ashpool |
| FREESIDE | 30 | 궤도 식민지 (최하) |

ICE / Alarm / Faction modifier 가 더해져 최종 ZDR 결정.

## Status 매트릭스 (PPL/ZDR 비율)

`calculate_status(ppl, zdr)`:
- `ratio > 1.5` → SAFE (green)
- `1.0 <= ratio <= 1.5` → MATCH (cyan)
- `0.75 <= ratio < 1.0` → TOUGH (yellow)
- `0.5 <= ratio < 0.75` → DEADLY (red)
- `ratio < 0.5` → FUTILE (dark_red)

### Grade 1 PPL=8 기준

| ZDR | ratio | Status |
|---:|---:|---|
| 1 (Surface) | 8.0 | SAFE |
| 5 (Mid) | 1.6 | SAFE |
| 8 (Deep) | 1.0 | MATCH |
| 12 (Core) | 0.67 | DEADLY |
| 25 (TA) | 0.32 | FUTILE |
| 30 (Freeside) | 0.27 | FUTILE |

→ Grade 1 은 Surface/Mid 까지 SAFE, Deep 에서 MATCH. Core 부터 위험.
   TA/Freeside 는 자키 사망 위험. 의도된 *성장 곡선*.

### Grade 5 PPL=75 기준

| ZDR | ratio | Status |
|---:|---:|---|
| 1 (Surface) | 75.0 | SAFE |
| 5 (Mid) | 15.0 | SAFE |
| 8 (Deep) | 9.4 | SAFE |
| 12 (Core) | 6.25 | SAFE |
| 25 (TA) | 3.0 | SAFE |
| 30 (Freeside) | 2.5 | SAFE |

→ Grade 5 는 모든 zone 에서 SAFE — *전설의 자키*.

## 미션 보상 공식

```
credits = arc * 800 + (grade - 1) * 300
```

| Arc | Grade | 공식 | 실제 평균 | 비율 |
|---|---|---:|---:|---:|
| 1 | 1 | 800 | 550 | 69% |
| 2 | 2 | 2,200 | 1,200 | 55% |
| 3 | 3 | 3,300 | 2,200 | 67% |
| 4 | 4 | 4,400 | 3,300 | 75% |
| 5 | 5 | 5,200 | 5,000 | 96% |

→ **공식 대비 55~96%** 로 보수적 설정 (깁슨 톤: 런은 빡빡함).
   Arc 5 (finale) 만 공식 근접 — 엔딩 보상 풍성.

## ICE stat 스케일

ICE 종류별 hp_base / hp_per_grade / dmg_base / dmg_per_grade:

| ICE | tier | hp_base | hp_per_grade | dmg_base | dmg_per_grade |
|---|---|---:|---:|---:|---:|
| standard | 1 | 80 | 15 | 3 | 1 |
| watchdog | 1 | 50 | 10 | 2 | 1 |
| black | 3 | 200 | 40 | 8 | 2 |
| goliath | 3 | 150 | 30 | 5 | 2 |
| construct | 2 | 90 | 18 | 4 | 1 |
| boss | 4 | 280 | 50 | 12 | 3 |
| wintermute | 4 | 260 | 50 | 11 | 3 |
| neuromancer | 5 | 320 | 60 | 14 | 3 |
| revelation | 3 | 160 | 30 | 7 | 2 |
| loa | 3 | 100 | 22 | 5 | 2 |

스케일 공식:
```
hp = hp_base + hp_per_grade * max(0, player_grade - ice_tier)
dmg = dmg_base + dmg_per_grade * max(0, player_grade - ice_tier)
```

플레이어가 ICE tier 이상이면 보너스. 미만이면 0.7~1.0 scale 로 약화.

## 알려진 이슈 / 미래 작업

- **Grade 6 (Arc 5 finale)**: `grade_max=6` 미션 2개 (neuromancer_merger, zion_express). 
  Grade 6 PPL 공식 미정의 — 현재는 Grade 5 로 처리 (PPL=75 한계).
  → Phase 6: Grade 6 PPL 정의 (master tier)
- **low-PPL 디스크립션시 점프**: Grade 1 PPL=8 → Core ZDR=12 즉시 DEADLY.
  → 의도된 난이도이나 시각적 표시 강화 필요 (P2 #7)
- **Status threshold 비선형**: ratio 0.499 vs 0.5 가 다른 카테고리
  → 0.499 = FUTILE, 0.5 = DEADLY. 미세한 차이가 큰 결과.
  → Phase 6: threshold smoothing 검토

## 검증

- `test_matrix_ppl.py` (PPL 계산)
- `test_matrix_serialization.py` (ZDR roundtrip)
- `test_grade_progression.py` (5 단계 비교)
- `test_combat_to_death.py` (전투 → 사망 사이클)