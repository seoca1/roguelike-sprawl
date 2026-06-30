# 결정 기록 (ADR Index)

Architecture Decision Records. 모든 주요 결정은 여기 추적된다.

## 상태 범례

- **Draft**: 작성 중, 사용자 결정 대기
- **Accepted**: 결정됨. 변경 시 새 ADR 작성 필요
- **Deprecated**: 더 이상 유효하지 않음. 사유 명시
- **Superseded by ADR-XXXX**: 새 결정으로 대체됨

## 결정 목록

| 번호 | 제목 | 상태 | 날짜 | 우선순위 |
| --- | --- | --- | --- | --- |
| 0001 | 엔진/프레임워크 | **Accepted** | 2026-06-17 | P0 |
| 0002 | 비주얼 스타일 | **Accepted** | 2026-06-17 | P0 |
| 0003 | 전투 시스템 (RT-MS) | **Accepted (Revised)** | 2026-06-17 | P1 |
| 0004 | 코드 아키텍처 | **Accepted** | 2026-06-17 | P0 |
| 0005 | 사이버스페이스 표현 | **Accepted** | 2026-06-17 | P1 |
| 0006 | 런 구조 (로그라이크 vs 로그라이트) | **Accepted** | 2026-06-17 | P0 |
| 0007 | 플랫폼 타겟 | **Accepted** | 2026-06-17 | P0 |
| 0008 | 진행 / 레벨업 시스템 | **Accepted (Revised)** | 2026-06-17 | P1 |
| 0009 | Story / News 전달 시스템 | **Accepted** | 2026-06-17 | P1 |
| 0010 | i18n + Content Pipeline | **Accepted** | 2026-06-17 | P1 |
| 0011 | ASCII Portraits (인물/객체 시각 식별) | **Accepted** | 2026-06-17 | P1 |
| 0012 | Combat Difficulty & Threat Level (PPL & ZDR) | **Accepted** | 2026-06-17 | P0 |
| 0013 | Story Events System (소설 스토리 이벤트) | **Accepted** | 2026-06-17 | P1 |
| 0014 | Data Salvage (전투 승리 보상 — 데이터 회수) | **Accepted** | 2026-06-18 | P1 |
| 0015 | Material & Crafting System (재료 & 조합) | **Accepted** | 2026-06-18 | P1 |
| 0016 | Jockey Avatar (자키 아바타 — 스탯 시각화) | **Accepted** | 2026-06-18 | P1 |
| 0017 | Mission-Material Integration (미션-재료 통합) | **Accepted** | 2026-06-18 | P1 |
| 0018 | Combat Animation (전투 ASCII 애니메이션) | **Accepted** | 2026-06-18 | P1 |
| 0019 | Combat Aftermath & Immersive Subtitles (전투 후일담 & 한글 자막) | **Accepted** | 2026-06-18 | P1 |
| 0020 | Fog of War + Exploration (안개 / 탐험 메카닉) | **Accepted** | 2026-06-18 | P1 |
| 0030 | GitHub Utilization Plan (GitHub 활용 계획) | **Draft** | 2026-06-18 | P2 |
| 0031 | Original Scenario Integration (단편 → 챕터 → 초반 플레이 통합) | **Accepted** | 2026-06-20 | P1 |
| 0032 | Graphic Novel Auto-Play Mode + Main Menu 확장 (5 옵션) | **Accepted** | 2026-06-20 | P1 |
| 0040 | Death & Restart Cycle (자키 사이클 + Hall of Dead) | **Accepted** | 2026-06-20 | P1 |
| 0041 | Graphic Novel Content Expansion (씬 dialogue 4× 확장) | **Accepted** | 2026-06-20 | P1 |
| 0042 | Chapter Title Cards / Scene Transitions (로마 숫자 + fade) | **Accepted** | 2026-06-20 | P2 |
| 0043 | Sound Cue Integration (15개 cue → file 매핑) | **Accepted** | 2026-06-20 | P2 |
| 0044 | Graphic Novel Save/Restore (이어서 읽기) | **Accepted** | 2026-06-20 | P2 |
| 0046 | Graphic Novel Ending B (대안 결말) | **Accepted** | 2026-06-21 | P1 |
| 0047 | Text Visibility (Typed Status Messages) | **Accepted** | 2026-06-21 | P2 |
| 0048 | GN Ending Menu + Save Migration 1.1.0 | **Accepted** | 2026-06-21 | P2 |
| 0049 | Graphic Novel Ending C (3rd ending) + Save 1.2.0 | **Accepted** | 2026-06-21 | P2 |
| 0050 | Boss ICE System (Wintermute + T-A Prime 3-phase) | **Accepted** | 2026-06-21 | P1 |
| 0052 | Short Story Expansion Plan (단편 3편 보강) | **Accepted** | 2026-06-22 | P2 |
| 0060 | Dungeon Exploration Redesign (NetHack + VFX) | **Accepted** | 2026-06-30 | P2 |
| 0061 | Novel Integration Architecture (Hook 디스패치) | **Accepted** | 2026-06-30 | P2 |

## 우선순위 정의

- **P0 (최우선)**: 0001, 0002, 0004, 0006, 0007, 0012 — Phase 4 시작 전 결정 필요
- **P1**: 0003, 0005, 0008, 0009, 0010, 0011, 0013, 0014, 0015, 0016, 0017, 0018, 0019, 0020 — Phase 5 시작 전 결정 필요
- **P2 (미정)**: 추가 결정은 Phase 5 이후 또는 진행 중 발생 시 추가

## 결정이 다른 결정에 미치는 영향 (Accepted 결정으로 인한 제약)

- **0001 → 0002**: libtcod + Python → Pure ASCII와 자연스러움
- **0001 → 0004**: Python → ECS-lite + 데이터 주도 권장
- **0001 → 0007**: libtcod은 macOS + Windows 모두 네이티브
- **0002 → 0005**: Pure ASCII → 노드 그래프 표현이 ASCII 기호로 가능
- **0003 → 0005**: AP 턴 → 노드 간 이동이 AP 비용
- **0006 → 0008**: 하이브리드 unlock → 자키 등급 시스템이 unlock 표현
- **0009**: meatspace 미표시, Story Archive로만 외부 세계 전달
- **0014**: HEAL 20% — Pillar 3 무게 유지; FRAG/CRED는 Phase 6+ 확장
- **0015**: 3-tier crafting (5 raw → 4 components → final) — Pillar 4 직접 표현
- **0016**: Stick Figure Avatar — 부위별 stat 표현 (HP 머리, programs 팔, deck 몸통, wetware 다리)
- **0017**: Mission-Material Integration — 6 미션 타입, Hub 4-패널, Recipe 트리 뷰
- **0018**: Combat Animation — 일반 240ms gray vs 스킬 600ms color, 깁슨 톤 글리치

## 일관성 (모두 Accepted)

| 항목 | 결정 |
| --- | --- |
| 언어 | Python 3.11+ |
| 엔진 | python-tcod |
| 비주얼 | Pure ASCII |
| 아키텍처 | ECS-lite + 데이터 주도 (i18n 포함) |
| 런 구조 | 하이브리드 (unlock만 메타) |
| 플랫폼 | macOS + Windows |
| 전투 | Real-Time + Menu Skills (RT-MS) |
| 매트릭스 | 노드 그래프 |
| 진행 | 런 내 스탯 고정 + 자키 등급 (메타) + 아이템 티어 (T1~T5) |
| meatspace | *절대 시각화되지 않음* |
| Story | Story Archive로 전달 |
| i18n | en (1차, 깁슨 톤) + ko (보조 번역/자막) |
| Content | 데이터 주도, 반복 보강, plot bones 사전 정의 |
| Portrait | ASCII / Unicode 기호 + 색상, cyberspace only |
| Difficulty | PPL (Player Power Level) & ZDR (Zone Difficulty Rating) |
| Events | Story Events (소설 스토리 부가 콘텐츠) |
| Combat Reward | Data Salvage (HEAL 20%, FRAG/CRED Phase 6+) |
| Crafting | 3-tier (5 raw → 4 components → program/item/construct) |
| Stat Display | Jockey Avatar (stick figure, 부위별 표현) |
| Mission-Material | 6 미션 타입, Hub 4-패널 (Avatar/Materials/Recipes/Job Board) |
| Combat Animation | Normal 240ms gray vs Skill 600ms color, 깁슨 톤 글리치 |
| Aftermath | 전투 후일담 4 importance + 소설 인물 7명 반응 + 한글 자막 |
| Exploration | Light Fog of War (현재+인접), 미니맵, breadcrumb |
| Scenario (0031) | 단편 → 챕터 → 초반 플레이 통합 (12 씬 dialogue, 4 캐릭터 × 3-4 씬) |
| Graphic Novel (0032) | 메인메뉴 5 옵션 + 12 씬 자동플레이 + Save Progress 카드 |
| Death Cycle (0040) | DEATH/DEATH_SUMMARY/HALL_OF_DEAD + restart_with_new_jockey (3 옵션) |
| Novel Layout (0041-0042) | 30줄 페이지 + chapter card I-XII + fade transition |
| Audio (0043) | 15개 scene cue → file 매핑 (theme/movement 카테고리) |
| GN Save (0044) | GNProgress atomic save + CONTINUE READING 메뉴 + version 1.0.0 |
| Ending B (0046) | 6 씬 추가 (Case/Sil/Kas × 2) + SceneData.ending 필드 + `--ending {A,B}` CLI |
| Text Visibility (0047) | MessageKind 8종 + 아이콘/색상/bg 하이라이트 + GN prose cream color |
| GN Ending Menu (0048) | GRAPHIC_NOVEL_ENDING_MENU 화면 + GNProgress.ending + Save 1.0.0→1.1.0 마이그레이션 |
| Ending C (0049) | 6 신규 씬 (Disappear/Erase/Burn) + 메뉴 4옵션 + Save 1.1.0→1.2.0 + 9 결말 조합 |
| Boss ICE (0050) | Wintermute + T-A Prime 보스 3-phase 시스템 + phase transition cinematics |

## 결정 절차 (참고용)

1. AI가 ADR 작성 (Draft 상태)
2. 사용자가 결정 또는 수정 요청
3. 결정되면 Status를 "Accepted"로 변경
4. Consequences 섹션 채우기
5. 영향 받는 design/ 시스템 명세 갱신
6. log.md에 기록

## 모든 결정 완료 — Phase 4 진입 가능

## Pillar 2 / 5 추가 영향 (ADR-0009)

meatspace 미표시는 디자인 전반에 영향을 미친다:
- **Pillar 2**: "The Matrix는 *유일한* 시각적 공간"으로 강화
- **Pillar 5**: "mediated world" 톤 — 외부 세계는 항상 텍스트/뉴스/이야기로만
- **디자인 리뷰 체크리스트**: "meatspace를 직접 묘사하고 있지 않은가?" 추가
- **세계관 wiki**: "새 플레이어", "meatspace 미표시" 명시

상세는 `decisions/0009-story-news-system.md` 참조.

## 콘텐츠 파이프라인 영향 (ADR-0010)

i18n + Content Pipeline:
- **모든 텍스트는 i18n JSON** — `data/i18n/{ko,en}.json`
- **모든 콘텐츠는 데이터** — JSON / YAML
- **plot bones 사전 정의** — `design/story_skeleton.md` (5 arcs + 4+ endings)
- **초반 미션 우선** — Arc 1 (1-3 jobs)
- **반복 보강** — 무한 side content, faction 뉴스, world events

상세는 `decisions/0010-i18n-content-pipeline.md` 및 `design/story_skeleton.md` 참조.
