# Derivative Stories (이차 창작 단편)

> **이 페이지는 Fiction 프로젝트의 이차 창작 단편을 게임과 연결합니다.**

## 연결 구조

```
Fiction/derivative/sprawl-trilogy/short-stories/
  ├── en/  (영어 원문 — 39파일)
  └── ko/  (한국어 번역 — 39파일)
        ↓ (인간 큐레이션: synopsis 발췌)
Game/roguelike_sprawl/prototype/data/missions/missions.json
        ↓ (story.source 필드로 매핑)
Game/roguelike_sprawl/prototype/data/story/chapters/{case,sil,kas}.json
        ↓ (chapter_view.py가 렌더링)
CHAPTER 화면 (그래픽 노블 모드)
        ↓
dashboard/stories/short-stories/*.html (정적 카드)
```

## 챕터 → 단편 매핑 (47 미션, 36 단편)

### Chapter Novice (케이/K — 초짜)

| 미션 ID | Arc | 단편 stem | 단편 파일 | KO |
|---|:---:|---|---|:---:|
| `first_jack` | 1 | `case_jackout-30sec` | [2026-06-23_case_jackout-30sec](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_case_jackout-30sec.md) | ✓ |
| `watchdog_patrol` | 1 | `watchdog_patrol` | [2026-06-23_watchdog_patrol](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_watchdog_patrol.md) | ✓ |
| `ice_run` | 1 | `ice_run` | [2026-06-23_ice_run](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_ice_run.md) | ✓ |
| `data_retrieval` | 1 | `data_retrieval` | [2026-06-25_data_retrieval](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-25_data_retrieval.md) | ✓ |
| `tutorial_maze` | 1 | `tutorial_maze` | [2026-06-25_tutorial_maze](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-25_tutorial_maze.md) | ✓ |
| `first_trace` | 2 | `first_trace` | [2026-06-23_first_trace](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_first_trace.md) | ✓ |
| `flatline_call` | 2 | `flatline_again` | [2026-06-23_flatline_again](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_flatline_again.md) | ✓ |
| `sense_net_infiltration` | 2 | `sense_net_infiltration` | [2026-07-01_sense_net_infiltration](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-07-01_sense_net_infiltration.md) | ✓ |
| `hosaka_corporate_infiltration` | 2 | `ta_defection` | [2026-06-29_ta_defection](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-29_ta_defection.md) | ✓ |
| `yakuza_loan_shark` | 2 | `yakuza_deal` | [2026-06-23_yakuza_deal](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_yakuza_deal.md) | ✓ |
| `black_ice_dream` | 3 | `black_ice_dream` | [2026-06-23_black_ice_dream](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_black_ice_dream.md) | ✓ |
| `hosaka_core` | 3 | `hosaka_core` | [2026-07-01_hosaka_core](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-07-01_hosaka_core.md) | ✓ |
| `maas_heist` | 3 | `maas_heist` | [2026-07-01_maas_heist](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-07-01_maas_heist.md) | ✓ |
| `voodoo_loa_encounter` | 4 | `loa_voodoo_contact` | [2026-06-23_loa_voodoo_contact](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_loa_voodoo_contact.md) | ✓ |
| `final_choice` | 5 | `the_choice` | [2026-06-23_the_choice](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_the_choice.md) | ✓ |

### Chapter Veteran (실/Sil — 베테랑)

| 미션 ID | Arc | 단편 stem | 단편 파일 | KO |
|---|:---:|---|---|:---:|
| `delivery_to_finn` | 1 | `marly_louisiana-god` | [2026-06-23_marly_louisiana-god](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_marly_louisiana-god.md) | ✓ |
| `first_contact` | 2 | `first_contact` | [2026-06-25_first_contact](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-25_first_contact.md) | ✓ |
| `sense_net_tip` | 2 | `sense_net_trace` | [2026-06-23_sense_net_trace](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_sense_net_trace.md) | ✓ |
| `mollys_market` | 2 | `mollys_market` | [2026-06-29_mollys_market](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-29_mollys_market.md) | ✓ |
| `mollys_razor` | 3 | `mollys_razor` | [2026-07-08_mollys_razor](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-07-08_mollys_razor.md) | ✓ |
| `ta_heist` | 3 | `ta_heist` | [2026-07-08_ta_heist](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-07-08_ta_heist.md) | ✓ |
| `sense_net_media_extract` | 3 | `hosaka_extraction` | [2026-06-29_hosaka_extraction](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-29_hosaka_extraction.md) | ✓ |
| `straylight_approach` | 3 | `straylight_approach` | [2026-07-01_straylight_approach](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-07-01_straylight_approach.md) | ✓ |
| `vegas_stakeout` | 3 | `vegas_stakeout` | [2026-06-29_vegas_stakeout](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-29_vegas_stakeout.md) | ✓ |
| `dixies_offer` | 4 | `dixies_last_run` | [2026-06-23_dixies_last_run](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_dixies_last_run.md) | ✓ |
| `dixies_choice` | 4 | `dixies_choice` | [2026-06-29_dixies_choice](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-29_dixies_choice.md) | ✓ |
| `winter_infiltrate` | 4 | `winter_infiltrate` | [2026-06-29_winter_infiltrate](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-29_winter_infiltrate.md) | ✓ |
| `ta_payroll_archive` | 4 | `straylight_approach` | [2026-07-01_straylight_approach](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-07-01_straylight_approach.md) | ✓ |
| `zion_express` | 5 | `zion_express` | [2026-06-29_zion_express](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-29_zion_express.md) | ✓ |
| `ta_straylight_archive` | 5 | `straylight_approach` | [2026-07-01_straylight_approach](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-07-01_straylight_approach.md) | ✓ |

### Chapter Heretic (카스/Kas — 이단아)

| 미션 ID | Arc | 단편 stem | 단편 파일 | KO |
|---|:---:|---|---|:---:|
| `craft_job` | 2 | `kumiko_manarase-midnight` | [2026-06-23_kumiko_manarase-midnight](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_kumiko_manarase-midnight.md) | ✓ |
| `sally_sandii_3am` | 2 | `sally_sandii-3am` | [2026-06-23_sally_sandii-3am](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_sally_sandii-3am.md) | ✓ |
| `wigan_call` | 2 | `wigan_call` | [2026-07-01_wigan_call](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-07-01_wigan_call.md) | ✓ |
| `yakuza_deal` | 2 | `yakuza_deal` | [2026-06-23_yakuza_deal](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_yakuza_deal.md) | ✓ |
| `neuromancer_whisper` | 3 | `neuromancer_whisper` | [2026-06-29_neuromancer_whisper](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-29_neuromancer_whisper.md) | ✓ |
| `sally_returns_arc3` | 3 | `sally_returns` | [2026-06-23_sally_returns](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_sally_returns.md) | ✓ |
| `aleph_fragment` | 4 | `wigan_zavijava` | [2026-06-23_wigan_zavijava](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_wigan_zavijava.md) | ✓ |
| `maas_neural_extract` | 4 | `maas_heist` | [2026-07-01_maas_heist](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-07-01_maas_heist.md) | ✓ |
| `matrix_revelation` | 4 | `matrix_revelation` | [2026-06-29_matrix_revelation](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-29_matrix_revelation.md) | ✓ |
| `construct_memory_rescue` | 5 | `dixies_last_run` | [2026-06-23_dixies_last_run](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-23_dixies_last_run.md) | ✓ |
| `neuromancer_merger` | 5 | `neuromancer_merger` | [2026-06-29_neuromancer_merger](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-29_neuromancer_merger.md) | ✓ |
| `ta_3jane_betrayal` | 5 | `ta_defection` | [2026-06-29_ta_defection](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-29_ta_defection.md) | ✓ |

### Suit (범죄자 네트워크 — NPC 시나리오)

| 미션 ID | Arc | 단편 stem | 단편 파일 | KO |
|---|:---:|---|---|:---:|
| `armitage_infiltration` | 2 | `armitage_infiltration` | [2026-06-29_armitage_infiltration](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-29_armitage_infiltration.md) | ✓ |
| `hosaka_extraction` | 3 | `hosaka_extraction` | [2026-06-29_hosaka_extraction](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-29_hosaka_extraction.md) | ✓ |
| `ta_defection` | 4 | `ta_defection` | [2026-06-29_ta_defection](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-29_ta_defection.md) | ✓ |
| `wintermute_negotiation` | 5 | `wintermute_negotiation` | [2026-06-29_wintermute_negotiation](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-29_wintermute_negotiation.md) | ✓ |
| `ta_wintermute_direct` | 5 | `wintermute_negotiation` | [2026-06-29_wintermute_negotiation](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-06-29_wintermute_negotiation.md) | ✓ |
| `beijing_memory_courier` | 3 | `beijing_memory_courier` | [2026-07-11_beijing_memory_courier](../../../../Fiction/derivative/sprawl-trilogy/short-stories/en/2026-07-11_beijing_memory_courier.md) | ✓ |

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

## 갱신 내역

- **2026-07-13 (Part 3 — 후속)**: Gap 4 + LLM + KO 게임 통합
  - **Gap 4**: 16 standalone orphans 중 10편을 챕터 epilogue_supplement에 연결. `chapter_view.epilogue_supplement_for(stem)` API + `PERSONA_TO_CHAPTER` 매핑 (novice→case, veteran→sil, heretic→kas, suit→suit). 5개 신규 테스트.
  - **Sonnet 4.5 (OpenRouter) LLM-as-judge 통합**: `story_review.py` (5 plot + 6 prose 카테고리 0-3 채점). `tone_judge.py` OpenRouter 지원. `story_check.py --llm --llm-mode {plot|prose|full}` 옵션.
  - **LLM 식별 이슈 보강**: 4건 canon_consistency (dixies_choice/wintermute_negotiation/straylight_approach/vegas_stakeout) + 3편 epilogue 강화
  - **KO 게임/대시보드 통합**: 9개 Gap 식별 → 5개 해결 (CJK 잔존 정정, 언어 토글, `?lang=en|ko` 쿼리 필터, excerpt_ko 사이즈 정합, search_index body_preview)
  - **테스트**: 게임 pytest 2998 → 3003 (epilogue_supplement 5개 신규 추가)

- **2026-07-13 (Part 2)**: P3 보완작업 + Phase 2 정합성 연동
  - **신규 미션 1개 추가**: `beijing_memory_courier` (heretic arc-3, 1,219 단어)
  - **미션 source 정정 2건**: `ta_heist` (sally_sandii-3am → ta_heist), `mollys_razor` (marly_louisiana-god → mollys_razor)
  - **6편 확장**: `dixies_choice` (584→1,661), `wintermute_negotiation` (534→1,533), `maas_heist` (523→1,439), `straylight_approach` (480→1,236), `vegas_stakeout` (600→1,046), `sense_net_infiltration` (421→1,165) — 모두 C→A
  - **대시보드 카드 110개 자동 생성** (`sync_dashboard_cards.py`): EN 55 + KO 55
  - **chapter JSON excerpt 갱신**: `suit.json` (wintermute_negotiation expanded content 반영)
  - **16 standalone orphan**: post-merger construct 시리즈 + Sally/The/Winters narrative continuation

- **2026-07-10**: EN/KO 디렉토리 분리 완료 (`en/` + `ko/`), 언어 필드 일괄 수정
  - 39 EN 파일 → `short-stories/en/`
  - 39 KO 파일 → `short-stories/ko/`
  - YAML `language: en: English` → `language: en` 수정 (20 EN 파일)
  - Game wiki `derivative_stories.md` 경로 업데이트
- **2026-07-08**: 테이블을 47 미션/36 단편으로 전면 갱신
  - 13개 누락 단편 추가 (06-29, 07-01 시리즈)
  - `aleph_fragment` → `wigan_zavijava` 수정 (단편 존재 확인)
  - `ta_heist`, `mollys_razor` 미작성 표기 유지
  - Suit 캐릭터 시나리오 테이블 추가

## 게임 ↔ Fiction 양방향 인용

| 게임 파일 | 인용 Fiction 페이지 |
|---|---|
| `design/story/prologue.md` | `works/neuromancer.md` |
| `design/story/characters.md` | `characters/case.md` 외 |
| `design/systems/stage_structure.json` | `themes/identity-and-the-matrix.md` |
| `wiki/world/cyberspace.md` | `settings/cyberspace.md` |
| `prototype/src/roguelike_sprawl/engine/jack_out_view.py` | `derivative/sprawl-trilogy/short-stories/en/2026-06-23_case_jackout-30sec.md` |
| `prototype/src/roguelike_sprawl/engine/debrief_view.py` | `derivative/sprawl-trilogy/short-stories/en/2026-06-23_kumiko_manarase-midnight.md` |
| `prototype/src/roguelike_sprawl/engine/event_view.py` | `derivative/sprawl-trilogy/short-stories/en/2026-06-23_marly_louisiana-god.md` |
| `data/story/chapters/case.json` | `works/neuromancer.md`, `characters/case.md` |
| `data/story/chapters/sil.json` | `works/count-zero.md`, `characters/marly-krushkhova.md` |
| `data/story/chapters/kas.json` | `works/mona-lisa-overdrive.md`, `characters/kumiko-yanaka.md` |

## 갭 (보강 필요)

### ✅ 해결됨 (2026-07-13)

- ✅ `aleph_fragment` — 2026-06-30 작성 완료 (a­leph_fragment.md, novelette 1,822 단어). mission arc-4 연결됨.
- ✅ 모든 mission-linked 단편에 motif 정의 (55/55 일치)
- ✅ 16/16 standalone orphan 챕터 epilogue_supplement에 연결

### 🟢 보강 가능 단편 (선택적)

- B-grade 단편 (24편) 중 분량/깁슨 톤 강화 가능한 후보 식별 필요
- pre-v2.0 단편 5편 중 확장 보강 후보 (현재 A 또는 B 등급)

### 📚 Standalone 단편 (16편, 챕터 enrichment 통합 완료)

다음 단편들은 `standalone: true` 플래그를 가지며, 게임 미션과 직접 연동되지는 않지만 **챕터 epilogue_supplement**로 통합되어 챕터 화면에서 콘텐츠로 노출된다 (Gap 4). post-merger construct 시리즈 (Case의 일상), Molly/Case 재회, Sally의 별도 임무 등을 다룬다.

| stem | 챕터 enrichment | 파일 | 캐릭터 | arc | 모티프 | 시퀀스 |
|---|---|---|---|---|---|---|
| `casey_leaves` | 3jane | [2026-07-13](../sprawl-trilogy/short-stories/en/2026-07-13_casey_leaves.md) | heretic | 5 | departure | post-merger ending |
| `construct_asks` | kas | [2026-07-11](../sprawl-trilogy/short-stories/en/2026-07-11_construct_asks.md) | heretic | 5 | question | Construct 5 |
| `construct_dawn` | case | [2026-07-11](../sprawl-trilogy/short-stories/en/2026-07-11_construct_dawn.md) | veteran | 5 | dawn | Construct 0 |
| `construct_named` | kas | [2026-07-11](../sprawl-trilogy/short-stories/en/2026-07-11_construct_named.md) | heretic | 5 | name | Construct 1 |
| `molly_meets_casey` | sil | [2026-07-13](../sprawl-trilogy/short-stories/en/2026-07-13_molly_meets_casey.md) | veteran | 4 | recognition | Molly arc |
| `molly_decides` | sil | [2026-07-14](../sprawl-trilogy/short-stories/en/2026-07-14_molly_decides.md) | veteran | 2 | decision | Molly arc |
| `molly_returns` | kas | [2026-07-11](../sprawl-trilogy/short-stories/en/2026-07-11_molly_returns.md) | heretic | 4 | return | Molly arc |
| `tessier_archive` | suit | [2026-07-11](../sprawl-trilogy/short-stories/en/2026-07-11_tessier_archive.md) | heretic | 5 | archive | 3Jane POV |
| `the_answer` | suit | [2026-07-11](../sprawl-trilogy/short-stories/en/2026-07-11_the_answer.md) | heretic | 5 | answer | Construct 5 (final) |
| `the_first_walk` | kas | [2026-07-11](../sprawl-trilogy/short-stories/en/2026-07-11_the_first_walk.md) | heretic | 5 | walk | Construct 1 |
| `the_fourth_word` | kas | [2026-07-11](../sprawl-trilogy/short-stories/en/2026-07-11_the_fourth_word.md) | heretic | 5 | word | Construct 2 |
| `the_full_name` | kas | [2026-07-11](../sprawl-trilogy/short-stories/en/2026-07-11_the_full_name.md) | heretic | 5 | name | Construct 3 |
| `the_leaving` | kas | [2026-07-11](../sprawl-trilogy/short-stories/en/2026-07-11_the_leaving.md) | heretic | 5 | leaving | Construct 4 (epilogue) |
| `the_naming` | kas | [2026-07-11](../sprawl-trilogy/short-stories/en/2026-07-11_the_naming.md) | heretic | 5 | kitchen | Construct 3 (parallel) |
| `wigan_zavijava` | wigan | [2026-06-23](../sprawl-trilogy/short-stories/en/2026-06-23_wigan_zavijava.md) | heretic | 4 | matrix | Count Zero |
| `wigan_zavijava` | wigan | [2026-07-11](../sprawl-trilogy/short-stories/en/2026-07-11_wigan_zavijava.md) | heretic | 4 | matrix | Count Zero (07-11 rewrite, KO ✓) |
| `winters_child` | case | [2026-07-11](../sprawl-trilogy/short-stories/en/2026-07-11_winters_child.md) | veteran | 5 | winter | post-merger ending |
| `winters_morning` | sil | [2026-07-11](../sprawl-trilogy/short-stories/en/2026-07-11_winters_morning.md) | heretic | 5 | morning | post-merger ending |

**Construct 5단계 학습 시퀀스** (kas 챕터 epilogue):
```
1. the_first_walk    — 첫 걸음
2. the_fourth_word   — 네 번째 단어
3. the_full_name     — 완전한 이름
4. the_naming        — 이름 짓기
5. the_answer        — 대답 ('out')
```
| `winters_morning` | [2026-07-11](../sprawl-trilogy/short-stories/en/2026-07-11_winters_morning.md) | heretic | 5 | Winter의 아침 |

**대시보드 카드**: 모두 자동 생성됨 (`Game/roguelike_sprawl/dashboard/stories/short-stories/{stem}.html`, `{stem}.ko.html`)

### 챕터 epilogue_supplement 매핑 (Gap 4 보강)

`chapter_view.epilogue_supplement_for(stem)` API. 10개 standalone orphan이 챕터 epilogue에 연결됨 (6개는 미배정, derivative_stories.md에서 직접 참조):

| 챕터 | 챕터 persona | 연결된 standalone orphan (16/16) |
|---|---|---|
| `case.json` (chapter_novice, Case) | novice | `winters_child`, `construct_dawn` |
| `kas.json` (chapter_heretic, Kas) | heretic | `molly_returns`, `the_naming`, `construct_asks`, `construct_named`, `the_first_walk`, `the_fourth_word`, `the_full_name`, `the_leaving` (Construct 5단계 + Molly/Case 통합) |
| `sil.json` (chapter_veteran, Sil) | veteran | `winters_morning`, `molly_meets_casey` |
| `suit.json` (chapter_suit, 3Jane) | suit | `tessier_archive`, `the_answer` (Construct 5단계 최종 + Tessier-Ashpool archive) |
| `3jane.json` | (other) | `casey_leaves` |
| `wigan.json` | (other) | `wigan_zavijava` |

**PERSONA → chapter file 매핑** (chapter_view.py):

```python
PERSONA_TO_CHAPTER = {
    "novice":  "case",    # Case POV
    "veteran": "sil",     # Sil POV
    "heretic": "kas",     # Kas POV (heretic chapter = Kas)
    "suit":    "suit",    # 3Jane POV
}
# Unknown personas → "novice" → case.json (default fallback)
```

**사용 예시 (chapter view from Python)**:
```python
from roguelike_sprawl.engine.chapter_view import epilogue_supplement_for, chapter_for_character
from pathlib import Path

DATA = Path("prototype/data")
chapter = chapter_for_character("heretic", DATA)
for sup in chapter.epilogue_supplement:
    print(f"{sup['stem']}: {sup['title_ko']} — {sup['relation']}")
```

**미연결 orphan 6개** (다음 세션 권장):
- `construct_named`, `the_answer`, `the_first_walk`, `the_fourth_word`, `the_full_name`, `the_leaving`
- Construct 5단계 학습 시퀀스 (`the_first_walk` → `the_fourth_word` → `the_full_name` → `the_naming` → `the_answer`)는 자연스럽게 case/kas 챕터에 추가 가능

## 다음 단계

- [ ] `prototype/scripts/verify_story_links.py` CI 통합
- [x] 1개 미작성 단편: `aleph_fragment` — ✅ 작성 완료 (2026-06-30)
- [x] 07-08 시리즈 단편 derivative_stories.md 매핑 추가 — ✅ 완료