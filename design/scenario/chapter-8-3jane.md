# Chapter 8: 3Jane Tessier-Ashpool (3Jane, Family Heir)

> **이 문서는 [`../scenario/README.md`](../scenario/README.md)의 Chapter 8 명세.**
> 캐릭터: **3Jane 테시에-애스풀 (3Jane Tessier-Ashpool)** · 동기: 가족 통합 · 단편: [3Jane Tessier-Ashpool](../../Fiction/wiki/characters/lady-3jane-tessier-ashpool)

## 1. 캐릭터 프로필

### 3Jane Tessier-Ashpool — Family Heir

| 항목 | 값 |
| --- | --- |
| **이름** | 3Jane Tessier-Ashpool |
| **콜사인** | 3Jane |
| **자키 등급** | 5-up (Family Heir) |
| **배경** | T-A 가족의 후계자. Straylight 거주. Wintermute의 의지에 영향. |
| **동기** | 가족 통합 — T-A를 다시 하나로 |
| **고유명사** | Straylight, Freeside, 8 마일, Ashpool, Wintermute, Neuromancer |
| **첫 의뢰** | 가족 기록 보관소에서 Bobby의 recording 추출 |
| **엔딩 A** | 통합 — Wintermute/Neuromancer 합체 후 가족의식 회복 |
| **엔딩 B** | 매각 — 가족을 Freeside 매각 |
| **엔딩 C** | 단절 — 3Jane이 가족을 떠나 Straylight 폐쇄 |
| **음악 테마** | `freeside_drone` (aristocratic, Freeside 정체) |

### 단편 매핑: 3Jane

| 단편 캐릭터 | 게임 캐릭터 | 차이점 |
| --- | --- | --- |
| Lady 3Jane Tessier-Ashpool | 3Jane | Gibson의 3Jane은 *aristocratic cold* — 가족 = "we" |
| 1인칭 aristocratic | **1인칭 aristocratic (royal "we")** | 8번째 시점 |
| Straylight 거주 | Straylight 거주 (Freeside 끝) |  |

## 2. 캐릭터 디자인 노트

### 목소리 / 톤

- **Aristocratic**: 영어를 정확하게 구사. 문법 완벽. 단어 선택 정밀.
- **Royal "we"**: 가족을 "we"라 칭함. 개인 = 가족의 일부.
- **Cold**: 감정 없음. 가족 우선.
- **Patient**: 수십 년을 기다린 후.

### 시각 디자인

- **Portrait**: `art:3jane_portrait` (aristocratic, white)
- **Background**: `tessier_ashpool_lab` (Straylight 내부)
- **Color**: 흰색 + 검정 `(255, 255, 255)` + `(0, 0, 0)`

### 4개 미션 → 4개 씬

| 씬 | 미션 ID | 단편 | 핵심 장면 |
|---|---|---|---|
| 01_straylight | `3jane_straylight_dawn` | Straylight 새벽 | Straylight 일상 |
| 02_recording | `3jane_bobby_recording` | Bobby recording | 가족 기록 보관소 |
| 03_aleph | `3jane_aleph_chamber` | Aleph 방 | Aleph의 발견 |
| 04_merge | `3jane_wintermute_merge` | Wintermute 합체 | Wintermute/Neuromancer merge |

## 3. 화면 흐름

```
MENU → GRAPHIC_NOVEL_MENU → 3JANE (8 scenes) → SAVED_PROGRESS → MENU
```

## 4. ADR 통합

- **ADR-0031** Original Scenario Integration
- **ADR-0032** Graphic Novel Mode — 메인메뉴 10 옵션
- **ADR-0050** Boss ICE System (Wintermute)
- **ADR-0052** Short Story Expansion Plan

## 5. 캐릭터 비교 (8명)

| 캐릭터 | 시점 | 동기 | 톤 |
|---|---|---|---|
| 케이 (K) | 1인칭 | 돈 (생존) | 떨림 |
| 실 (Sil) | 1인칭 | 복수 | 분노 |
| 카스 (Kas) | 1인칭 | 전복 | 예술 |
| 수트 (Suit) | 3인칭 | 거래 | cold |
| 위건 (Wigan) | 1인칭 loa | 회복 | ritual |
| 앤지 (Angie) | 1인칭 12세 | 엄마 | 직관 |
| 샐리 (Sally) | 1인칭 cold | 시장 지배 | sharp |
| **3Jane** | **1인칭 aristocratic** | **가족 통합** | **aristocratic, royal** |

3Jane의 1인칭은 *royal "we"* — 가족 = 자기. 8번째 시점.

## 6. 테스트

- `tests/unit/test_3jane_character.py` — 8번째 캐릭터 지원
- `tests/unit/test_graphic_novel_view.py` — 8 chars × 4 ending A = 32 scenes
- `tests/unit/test_novels.py` — 3jane 관련 단편

## 7. 다음 단계

- 9번째 캐릭터? (Neuromancer — 합체된 AI)
- T-A 가족 관련 미션 missions.json 추가
- Straylight 깊이 진입 미니게임