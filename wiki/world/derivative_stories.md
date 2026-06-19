# Derivative Stories (이차 창작 단편)

> **이 페이지는 Fiction 프로젝트의 이차 창작 단편을 게임과 연결합니다.**

## 연결 구조

```
Fiction/derivative/sprawl-trilogy/short-stories/
        ↓
    단편 3개 (Case, Marly, Kumiko)
        ↓
Game/roguelike_sprawl/ 통합
        ↓
dashboard/stories.html (대시보드 노출)
```

## 단편 목록

### 1. [잭아웃 후 30초 (Case)](../../../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-19_case_jackout-30sec.md)
- **시점**: Case (1인칭)
- **출처**: Neuromancer, 중반부
- **연결 게임 시스템**:
  - `jack_out_view.py` — 잭아웃 애니메이션 (4프레임)의 영감
  - `state.py` JACK_OUT stage
- **연결 캐릭터**: Case (오리지널 주인공)
- **테마**: 정체성, 매트릭스 중독/금단
- **게임 통합**:
  - JACK_OUT 화면에 분위기 참조
  - `event_dialogues.json`에 캐릭터 대사 인용
  - 프로로그 "case" 분기 강화

### 2. [루이지아나의 신 (Marly)](../../../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-19_marly_louisiana-god.md)
- **시점**: Marly Krushkhova (3인칭 제한)
- **출처**: Count Zero, 후반부
- **연결 게임 시스템**:
  - `event_story.py` — Loa/voodoo storyline events
  - `event_view.py` — Character art cutscenes
- **연결 캐릭터**: Marly → 게임의 "novice" 캐릭터 영감
- **테마**: Loa와 부두 매트릭스, 정체성 파편화
- **게임 통합**:
  - 3rd-act 이벤트 "voodoo broadcast" 추가
  - novice 캐릭터 ending A (Lives) 참조

### 3. [매나리사의 자정 (Kumiko)](../../../Fiction/derivative/sprawl-trilogy/short-stories/2026-06-19_kumiko_manarase-midnight.md)
- **시점**: Kumiko Yanaka (3인칭 제한)
- **출처**: Mona Lisa Overdrive, 중반부
- **연결 게임 시스템**:
  - `debrief_view.py` — DEBRIEF 화면 디자인 영감
  - `reward_view.py` — REWARD 화면 분위기
- **연결 캐릭터**: Kumiko → 게임의 "heretic" 캐릭터 영감
- **테마**: 정체성 업로드, 기억 vs 자아
- **게임 통합**:
  - heretic 캐릭터 ending A (Sprawl 변화) 참조
  - DEBRIEF 메시지 3개 중 1개 인용
  - "각성" 시스템 미캐닉으로 추가 검토 중

## 게임 통합 흐름

```
[단편 작성] → [위키 페이지 업데이트] → [event_dialogues.json 동기화]
     ↓                                    ↓
[INDEX.md 업데이트]                  [대시보드 cards]
     ↓                                    ↓
[log.md 기록]                       [play.py / full_demo.py]
```

## 게임 ↔ Fiction 양방향 인용

| 게임 파일 | 인용 Fiction 페이지 |
|---|---|
| `design/story/prologue.md` | `works/neuromancer.md` |
| `design/story/characters.md` | `characters/case.md` 외 |
| `design/systems/stage_structure.json` | `themes/identity-and-the-matrix.md` |
| `wiki/world/cyberspace.md` | `settings/cyberspace.md` |
| `engine/jack_out_view.py` | `derivative/sprawl-trilogy/short-stories/2026-06-19_case_jackout-30sec.md` |
| `engine/debrief_view.py` | `derivative/sprawl-trilogy/short-stories/2026-06-19_kumiko_manarase-midnight.md` |
| `engine/event_view.py` | `derivative/sprawl-trilogy/short-stories/2026-06-19_marly_louisiana-god.md` |

## 다음 단계

- [ ] 단편 3편을 `event_dialogues.json` NPC 대사로 직접 인용
- [ ] JACK_OUT 화면 인트로에 Case 단편 인용 추가
- [ ] DEBRIEF 화면에 Kumiko 단편 인용 추가
- [ ] heretic ending A의 일부로 Kumiko 각성 시퀀스 추가
- [ ] 4번째 단편: "리치 산맥의 마법사" (Wigan Ludgate / Beauvoir 시점)
- [ ] 5번째 단편: "프리사이드의 Sally Shears" (Molly의 Count Zero 시점)
