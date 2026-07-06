# Derivative Stories (이차 창작 단편)

> **이 페이지는 Fiction 프로젝트의 이차 창작 단편을 게임과 연결합니다.**

## 연결 구조

```
Fiction/derivative/sprawl-trilogy/short-stories/  (단편 파일)
        ↓ (인간 큐레이션: synopsis 발췌)
Game/roguelike_sprawl/prototype/data/missions/missions.json
        ↓ (story.source 필드로 매핑)
Game/roguelike_sprawl/prototype/data/story/chapters/{case,sil,kas}.json
        ↓ (chapter_view.py가 렌더링)
CHAPTER 화면 (그래픽 노블 모드)
        ↓
dashboard/stories/short-stories/*.html (정적 카드)
```

## 챕터 → 단편 매핑 (15 미션, 12 단편)

### Chapter Novice (케이/K — 초짜)

| 미션 ID | Arc | 단편 stem | 단편 파일 | KO |
|---|:---:|---|---|:---:|
| `first_jack` | 1 | `case_jackout-30sec` | [2026-06-23_case_jackout-30sec](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-23_case_jackout-30sec.md) | ✓ |
| `watchdog_patrol` | 1 | `watchdog_patrol` | [2026-06-23_watchdog_patrol](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-23_watchdog_patrol.md) | ✓ |
| `ice_run` | 1 | `ice_run` | [2026-06-23_ice_run](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-23_ice_run.md) | ✓ |
| `first_trace` | 2 | `first_trace` | [2026-06-23_first_trace](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-23_first_trace.md) | ✓ |

### Chapter Veteran (실/Sil — 베테랑)

| 미션 ID | Arc | 단편 stem | 단편 파일 | KO |
|---|:---:|---|---|:---:|
| `delivery_to_finn` | 1 | `marly_louisiana-god` | [2026-06-23_marly_louisiana-god](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-23_marly_louisiana-god.md) | ✓ |
| `sense_net_tip` | 2 | `sense_net_trace` | [2026-06-23_sense_net_trace](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-23_sense_net_trace.md) | ✓ |
| `black_ice_dream` | 3 | `black_ice_dream` | [2026-06-23_black_ice_dream](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-23_black_ice_dream.md) | ✓ |
| `ta_heist` | 3 | `ta_heist` | **단편 미작성** 🔴 | — |
| `mollys_razor` | 3 | `mollys_razor` | **단편 미작성** 🔴 | — |
| `dixies_offer` | 4 | `dixies_last_run` | [2026-06-23_dixies_last_run](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-23_dixies_last_run.md) | ✓ |
| `voodoo_loa_encounter` | 4 | `loa_voodoo_contact` | [2026-06-23_loa_voodoo_contact](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-23_loa_voodoo_contact.md) | ✓ |
| `aleph_fragment` | 4 | `aleph_fragment` | **단편 미작성** 🔴 | — |
| `final_choice` | 5 | `the_choice` | [2026-06-23_the_choice](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-23_the_choice.md) | ✓ |

### Chapter Heretic (카스/Kas — 이단아)

| 미션 ID | Arc | 단편 stem | 단편 파일 | KO |
|---|:---:|---|---|:---:|
| `craft_job` | 2 | `kumiko_manarase-midnight` | [2026-06-23_kumiko_manarase-midnight](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-23_kumiko_manarase-midnight.md) | ✓ |
| `yakuza_deal` | 2 | `yakuza_deal` | [2026-06-23_yakuza_deal](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-23_yakuza_deal.md) | ✓ |

## 단편 상세 (시점 / 출처 / 게임 통합)

### 1. 잭아웃 후 30초 (Case)
- **시점**: Case (1인칭)
- **출처**: Neuromancer, 중반부 ("고철책장 위의 케이스" 직전)
- **게임 통합**:
  - `jack_out_view.py` — 잭아웃 애니메이션 (4프레임)의 영감
  - `state.py` JACK_OUT stage
  - CHAPTER 화면 (chapter_novice)
  - 30초 카운트다운 모티프

### 2. 루이지아나의 신 (Marly)
- **시점**: Marly Krushkhova (3인칭 제한)
- **출처**: Count Zero, 4장 (Maison de Loa)
- **게임 통합**:
  - CHAPTER 화면 (chapter_veteran)
  - Loa/voodoo storyline events
  - 73 Eridani / Zavijava 모티프

### 3. 매나리사의 자정 (Kumiko)
- **시점**: Kumiko Yanaka (3인칭 제한)
- **출처**: Mona Lisa Overdrive, 2장
- **게임 통합**:
  - CHAPTER 화면 (chapter_heretic)
  - `debrief_view.py` 영감
  - "바퀴" 메타포, 엔딩 A (선언) 분기

### 4. 워치독 순찰 (K)
- **시점**: K (1인칭)
- **출처**: Neuromancer (Sense/Net ICE)
- **게임 통합**: `first_jack` 미션의 후속 (Arc 1)

### 5. 얼음 달콤 (K)
- **시점**: K (1인칭)
- **출처**: Neuromancer (ice shard 수집)
- **게임 통합**: ice_shard 미션 collect_material

### 6. 센스/넷 추적 (Sil)
- **시점**: Sil (1인칭)
- **출처**: Count Zero (Sense/Net 데이터 추적)
- **게임 통합**: veteran 미션

### 7. 블랙 아이스 드림 (Sil)
- **시점**: Sil (1인칭)
- **출처**: Neuromancer (Black ICE)
- **게임 통합**: black_ice_dream 미션

### 8. 부두 loa 연락 (Sil)
- **시점**: Sil (1인칭)
- **출처**: Count Zero (Loa 채널)
- **게임 통합**: voodoo_loa_encounter 미션

### 9. 딕시의 마지막 운영 (Dixie)
- **시점**: Dixie Flatline (1인칭)
- **출처**: Neuromancer (ROM construct)
- **게임 통합**: dixies_offer 미션

### 10. 선택 (Sil)
- **시점**: Sil (1인칭)
- **출처**: Sprawl Trilogy (Endgame)
- **게임 통합**: final_choice 미션 (Arc 5, 엔딩 결정)

### 11. 야쿠자 거래 (Kas)
- **시점**: Kas (1인칭)
- **출처**: Mona Lisa Overdrive (야쿠자)
- **게임 통합**: yakuza_deal 미션

### 12. 퍼스트 트레이스 (K)
- **시점**: K (1인칭)
- **출처**: Neuromancer (첫 매트릭스 진입)
- **게임 통합**: first_trace 미션

## 게임 ↔ Fiction 양방향 인용

| 게임 파일 | 인용 Fiction 페이지 |
|---|---|
| `design/story/prologue.md` | `works/neuromancer.md` |
| `design/story/characters.md` | `characters/case.md` 외 |
| `design/systems/stage_structure.json` | `themes/identity-and-the-matrix.md` |
| `wiki/world/cyberspace.md` | `settings/cyberspace.md` |
| `prototype/src/roguelike_sprawl/engine/jack_out_view.py` | `derivative/sprawl-trilogy/short-stories/2026-06-23_case_jackout-30sec.md` |
| `prototype/src/roguelike_sprawl/engine/debrief_view.py` | `derivative/sprawl-trilogy/short-stories/2026-06-23_kumiko_manarase-midnight.md` |
| `prototype/src/roguelike_sprawl/engine/event_view.py` | `derivative/sprawl-trilogy/short-stories/2026-06-23_marly_louisiana-god.md` |
| `data/story/chapters/case.json` | `works/neuromancer.md`, `characters/case.md` |
| `data/story/chapters/sil.json` | `works/count-zero.md`, `characters/marly-krushkhova.md` |
| `data/story/chapters/kas.json` | `works/mona-lisa-overdrive.md`, `characters/kumiko-yanaka.md` |

## 갭 (보강 필요)

### 🔴 미작성 단편 (3개)
- `mollys_razor` — veteran Arc 3, 5,000자 이상 필요
- `ta_heist` — veteran Arc 3, 5,000자 이상 필요
- `aleph_fragment` — veteran Arc 4, 5,000자 이상 필요

### 🟢 보강 가능 단편
- 12개 작성된 단편 중 분량/깁슨 톤 강화 가능한 후보 식별 필요



## 신규 단편 매핑 (06-25, 06-29, 06-30 시리즈)

### Chapter Novice (케이/K — 초짜)

| 미션 ID | Arc | 단편 stem | 단편 파일 | KO |
|---|:---:|---|---|:---:|
| `data_retrieval` | 1 | `data_retrieval` | [2026-06-25_data_retrieval](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-25_data_retrieval.md) | ✓ |
| `tutorial_maze` | 1 | `tutorial_maze` | [2026-06-25_tutorial_maze](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-25_tutorial_maze.md) | ✓ |

### Chapter Veteran (실/Sil — 베테랑)

| 미션 ID | Arc | 단편 stem | 단편 파일 | KO |
|---|:---:|---|---|:---:|
| `first_contact` | 2 | `first_contact` | [2026-06-25_first_contact](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-25_first_contact.md) | ✓ |
| `mollys_market` | 2 | `mollys_market` | [2026-06-29_mollys_market](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-29_mollys_market.md) | ✓ |
| `vegas_stakeout` | 3 | `vegas_stakeout` | [2026-06-29_vegas_stakeout](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-29_vegas_stakeout.md) | ✓ |
| `dixies_choice` | 4 | `dixies_choice` | [2026-06-29_dixies_choice](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-29_dixies_choice.md) | ✓ |
| `winter_infiltrate` | 4 | `winter_infiltrate` | [2026-06-29_winter_infiltrate](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-29_winter_infiltrate.md) | ✓ |
| `zion_express` | 5 | `zion_express` | [2026-06-29_zion_express](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-29_zion_express.md) | ✓ |

### Chapter Heretic (카스/Kas — 이단아)

| 미션 ID | Arc | 단편 stem | 단편 파일 | KO |
|---|:---:|---|---|:---:|
| `neuromancer_whisper` | 3 | `neuromancer_whisper` | [2026-06-29_neuromancer_whisper](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-29_neuromancer_whisper.md) | ✓ |
| `matrix_revelation` | 4 | `matrix_revelation` | [2026-06-29_matrix_revelation](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-29_matrix_revelation.md) | ✓ |
| `neuromancer_merger` | 5 | `neuromancer_merger` | [2026-06-29_neuromancer_merger](../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-29_neuromancer_merger.md) | ✓ |

### 신규 오리지널 단편 (06-30 시리즈 — 게임 통합 강화)

| 미션 ID | Arc | 단편 stem | 단편 파일 | KO | 챕터 | 동기 |
|---|:---:|---|---|:---:|---|---|
| `mollys_razor` | 3 | `mollys_razor` | `2026-06-30_mollys_razor` (미작성) | ⏳ | veteran | Molly 자취 추적 (면도칼 모티프) |
| `ta_heist` | 3 | `ta_heist` | `2026-06-30_ta_heist` (미작성) | ⏳ | veteran | T-A Straylight 침투 (3백 년 모티프) |
| `aleph_fragment` | 4 | `aleph_fragment` | `2026-06-30_aleph_fragment` (미작성) | ⏳ | heretic | Aleph 파편 (loa 매개, 모든 미래) |

## 다음 단계

- [x] 12개 단편 → 미션 매핑 (R5)
- [x] 챕터 ID ↔ 미션 ID 매핑 (chapter_novice / chapter_veteran / chapter_heretic)
- [ ] `prototype/scripts/verify_story_links.py` CI 통합 (R2)
- [ ] `prototype/src/roguelike_sprawl/story/loader.py` 정규화 헬퍼 (R1)
- [ ] 3개 미작성 단편 작성 (`mollys_razor`, `ta_heist`, `aleph_fragment`)
- [ ] 단편 보강: WRITING_PROCESS.md 중단편 단계 추가