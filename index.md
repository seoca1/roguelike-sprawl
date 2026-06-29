# Roguelike Sprawl - Wiki Index

위키/디자인/결정/테스트 페이지 카탈로그. LLM Wiki 표준 패턴.

**현재 상태**: Phase 5 (Vertical Slice) 완료. **2970 tests pass**. 핵심 시스템 + 그래픽 노블 + 이어서 읽기.

## 메타
- [README](README.md) - 프로젝트 개요
- [AGENTS](AGENTS.md) - AI 에이전트 가이드
- [ROADMAP](ROADMAP.md) - 단계별 계획 (Phase 4 완료)
- [SETUP_LOG](SETUP_LOG.md) - 환경 구축 기록
- [log](log.md) - 활동 로그
- [prototype/](../prototype/) - **Phase 4: 코드 프로젝트**

## 세계관 (World)
- [Sprawl Universe](wiki/world/sprawl_universe.md) - 시간/공간, 기본 컨셉
- [Cyberspace](wiki/world/cyberspace.md) - 매트릭스의 정의와 작동
- [Factions](wiki/world/factions.md) - 주요 세력
- [Glossary](wiki/world/glossary.md) - 용어 사전
- [Style Guide](wiki/world/style_guide.md) - 톤과 미적 가이드

> **Primary source**: `../../../Fiction/wiki/` — 깁슨 원작 분석 (Sprawl Trilogy, characters, settings). 게임 wiki는 게임용 요약.

## 디자인 (Design)
- [Pillars](design/pillars.md) - 디자인 기둥
- [Core Loop](design/core_loop.md) - 핵심 게임 루프
- [Character Paths](design/CHARACTER_PATHS.md) - **3캐릭터 × 15미션 진행 경로 (2026-06-25 신규)**
- [GDD](design/GDD.md) - Game Design Document
- [Glossary](design/glossary.md) - 게임 용어
- [Story Skeleton](design/story_skeleton.md) - **주요 줄기 뼈대 (5 arcs + 4+ endings)**
- [Systems: ASCII Portraits](design/systems/ascii-portraits.md) - **인물/객체 시각 식별**
- [Systems: Difficulty Rating (PPL & ZDR)](design/systems/difficulty-rating.md) - **전투 난이도 가시화**
- [Systems: Story Events](design/systems/story-events.md) - **소설 스토리 부가 이벤트**
- [Systems: Hacking (Cyberspace / Matrix)](design/systems/hacking.md) - **매트릭스 / 해킹 시스템 (Phase 5 신규)**
- [Systems: Combat (RT-MS + Data Salvage)](design/systems/combat.md) - **전투 + 전투 승리 보상 (ADR-0003 + ADR-0014)**
- [Systems: Crafting (Material & 조합)](design/systems/crafting.md) - **3-tier 재료 & 조합 시스템 (ADR-0015)**
- [Systems: Jockey Avatar (스탯 시각화)](design/systems/avatar.md) - **자키 아바타, 부위별 stat 표현 (ADR-0016)**
- [Systems: Missions (미션-재료 통합)](design/systems/missions.md) - **미션 시스템 + Hub 4-패널 + Recipe 트리 (ADR-0017)**
- [Systems: Animations (전투 ASCII 애니메이션)](design/systems/animations.md) - **Normal vs Skill ASCII 애니메이션 (ADR-0018)**
- [Systems: Aftermath & Subtitles (전투 후일담 & 한글 자막)](design/systems/aftermath.md) - **전투 후일담 + 소설 인물 반응 + 한글 자막 (ADR-0019)**
- [Systems: Grade Progression (5단계 전투 검증)](design/systems/grade-progression.md) - **자키 등급 1~5 전투 & 결과 이벤트 (ADR-0008 + ADR-0019)**
- [Systems: Exploration (Fog of War)](design/systems/exploration.md) - **안개 / 탐험 메카닉 (ADR-0020)**
- [Scenario Overview](design/scenario/README.md) - **오리지널 시나리오 통합 (ADR-0031)**
- [Chapter 1: 케이 (Novice)](design/scenario/chapter-1-novice.md) - **첫 잭인**
- [Chapter 2: 실 (Veteran)](design/scenario/chapter-2-veteran.md) - **오래된 의문**
- [Chapter 3: 카스 (Heretic)](design/scenario/chapter-3-heretic.md) - **선언**
- [Graphic Novel Mode](design/scenario/graphic-novel.md) - **그래픽 노블 자동플레이 (ADR-0032, 0041 톤 가이드라인 §10)**
- [Death & Restart Cycle](design/scenario/death-restart.md) - **자키 사이클 + Hall of Dead (ADR-0040)**
- [Story vs Stage Comparison](design/scenario/story-stage-comparison.md) - **단편소설/그래픽노블/게임스테이지 비교표**
- [Game Structure (5-Chapter Architecture)](design/scenario/game-structure.md) - **챕터/Arc/Prologue 용어 재정의 + 5챕터 설계**
- [Chapter Progress Tracker](design/scenario/chapter-progress.md) - **15챕터 구현 진도 추적표**
- [Session Handover](SESSION_HANDOVER.md) - **다른 세션 인수인계 (현재 상태, 다음 작업 후보, 함정)**

## 결정 기록 (Decisions)
- [Index](decisions/README.md) - 모든 ADR 목록

## 테스트 케이스
- [Index](testcases/README.md) - 모든 테스트 시나리오

## 최근 결정 (ADR-0041~0044, 2026-06-21)
- **0041 Content Expansion** — 12 씬 dialogue 4× 확장 (4188 → 16862 chars)
- **0042 Chapter Cards** — 챕터 I-XII + fade transition (║ ─ ·)
- **0043 Sound Cues** — 15개 scene cue → file 매핑 (path 버그 fix)
- **0044 GN Save/Restore** — `GNProgress` atomic save + CONTINUE READING 메뉴

## 데모 / 검증 스크립트
- [Scripts 가이드](prototype/scripts/README.md) - **모든 데모/검증 스크립트 실행법 (27+ scripts, 추천 순서, 비교표)**
- [Death in Action Demo](prototype/scripts/death_in_action_demo.py) - **전투 → 사망 사이클 end-to-end 데모 (ADR-0040 + combat 통합)**
- [Combat Effects Demo](prototype/scripts/combat_effects_demo.py) - **5-Layer VFX 10-씬 검증 (palette, crit, 15 skills, 5 ICE, HUD, combo, Bundle)**
- [Death Demo](prototype/scripts/death_demo.py) - 사망 화면 / 요약 / Hall of Dead 단독 데모
- [Combat Grades](prototype/scripts/combat_grades.py) - 5등급 진행 비교
- [Visual Demo](prototype/scripts/visual_demo.py) - 8개 시스템 한 번에 검증
- [Demo All](prototype/scripts/demo_all.py) - 풀 게임 + 그래픽 노블 통합 자동플레이 (ADR-0032)
- [Graphic Novel](prototype/scripts/graphic_novel.py) - 12-씬 그래픽 노블 자동플레이
- [Play](prototype/scripts/play.py) - 빠른 자동플레이 (MENU → HUB → MATRIX → COMBAT)
- [Combat → Death Integration Test](prototype/tests/unit/test_combat_to_death.py) - **전투 패배 → trigger_death → 새 자키 (11 tests)**
- [Graphic Novel Content Quality](prototype/tests/unit/test_graphic_novel_content_quality.py) - **12 씬 dialogue 길이/톤/한글 동기화 (76 tests, ADR-0041)**
- [Graphic Novel Novel Layout](prototype/tests/unit/test_graphic_novel_novel_layout.py) - **30줄 페이지 layout + pagination (28 tests)**
- [Graphic Novel Chapter Cards](prototype/tests/unit/test_graphic_novel_chapter_cards.py) - **챕터 타이틀 카드 + fade transition (37 tests, ADR-0042)**
- [Graphic Novel Endings](prototype/tests/unit/test_graphic_novel_endings.py) - **엔딩 A/B 분기 + 6 신규 씬 (22 tests, ADR-0046)**
- [Status Message](prototype/tests/unit/test_status_message.py) - **카테고리형 메시지 + 색상/아이콘 (43 tests, ADR-0047)**
- [GN Ending Menu](prototype/tests/unit/test_graphic_novel_ending_menu.py) - **엔딩 A/B 메뉴 화면 + Save 1.0.0→1.1.0 마이그레이션 (35 tests, ADR-0048)**
- [GN Ending C](prototype/tests/unit/test_graphic_novel_ending_c.py) - **엔딩 C (소멸/망각/파괴) + 메뉴 4옵션 + Save 1.1.0→1.2.0 (62 tests, ADR-0049)**
- [Boss ICE](prototype/tests/unit/test_boss_ice.py) - **Wintermute + T-A Prime 3-phase 시스템 + transition cinematics (52 tests, ADR-0050)**
- [Graphic Novel Audio](prototype/tests/unit/test_graphic_novel_audio.py) - **15개 scene cue → file 매핑 검증 + path 버그 fix (23 tests, ADR-0043)**
- [Graphic Novel Save/Restore](prototype/tests/unit/test_graphic_novel_save.py) - **이어보기 save/load + CONTINUE READING 메뉴 (24 tests, ADR-0044)**
- [Matrix Movement](prototype/tests/unit/test_matrix_movement.py) - **15개 키 + direction vector + 시각 힌트 (27 tests, ADR-0045)**
