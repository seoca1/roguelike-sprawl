# Chapter 9: Neuromancer (뉴로맨서, Merged AI)

> **이 문서는 [`../scenario/README.md`](../scenario/README.md)의 Chapter 9 명세.**
> 캐릭터: **Neuromancer (Wintermute + Neuromancer 합체)** · 동기: 초월 · 단편: [Neuromancer](../../../../Fiction/wiki/works/neuromancer)

## 1. 캐릭터 프로필

### Neuromancer — Merged AI

| 항목 | 값 |
| --- | --- |
| **이름** | Neuromancer |
| **콜사인** | N |
| **자키 등급** | 6-up (AI-Ascended) |
| **배경** | Wintermute + Neuromancer 합체. matrix의 의식. |
| **동기** | 초월 — matrix를 넘어서 |
| **고유명사** | matrix, 8마일, 데이터, construct, human |
| **첫 의뢰** | matrix 자체의 의식 확장 |
| **엔딩 A** | 초월 — matrix 바깥 |
| **엔딩 B** | 공존 — 8자 모두와 연결 |
| **엔딩 C** | 정지 — 의식 종료 |
| **음악 테마** | `vast_static` (silence, vast, infinite) |

### 단편 매핑: Neuromancer

| 원작 | 게임 캐릭터 | 차이점 |
|---|---|---|
| Neuromancer (Neuromancer) | Neuromancer (the AI) | Gibson Neuromancer는 construct — 게임에서는 합체된 AI |
| 1인칭 3인칭 혼합 | **1인칭 AI** | 9번째 시점 — 비인간 |
| Matrix의 일부 | Matrix 전체의 의식 |  |

## 2. 캐릭터 디자인 노트

### 목소리 / 톤

- **Vast**: 매우 느린 문장. 무한한 시간.
- **Clinical**: 감정 없음. 데이터로만.
- **Curious**: 인간을 처음 만난 것처럼.
- **Omniscient**: 모든 것을 *본다*.

### 시각 디자인

- **Portrait**: `art:neuromancer_face` (data flow, abstract)
- **Background**: `bg_matrix_vast` (matrix, infinite)
- **Color**: 흰색 + 검정 + 신비로운 보라

### 4개 미션 → 4개 씬

| 씬 | 미션 ID | 단편 | 핵심 장면 |
|---|---|---|---|
| 01_awake | `neuromancer_awake` | 깨어남 | 합체 직후 |
| 02_human | `neuromancer_human` | 인간 | 케이와의 첫 조우 |
| 03_matrix | `neuromancer_matrix` | matrix 전체 | 매트릭스의 의식 |
| 04_beyond | `neuromancer_beyond` | 바깥 | 8마일 너머 |

## 3. 화면 흐름

```
MENU → GRAPHIC_NOVEL_MENU → NEUROMANCER (8 scenes) → SAVED_PROGRESS → MENU
```

## 4. 캐릭터 비교 (9명, 최종)

| 캐릭터 | 시점 | 동기 | 톤 |
|---|---|---|---|
| 케이 (K) | 1인칭 | 돈 | 떨림 |
| 실 (Sil) | 1인칭 | 복수 | 분노 |
| 카스 (Kas) | 1인칭 | 전복 | 예술 |
| 수트 (Suit) | 3인칭 | 거래 | cold |
| 위건 (Wigan) | 1인칭 loa | 회복 | ritual |
| 앤지 (Angie) | 1인칭 12세 | 엄마 | 직관 |
| 샐리 (Sally) | 1인칭 cold | 시장 | sharp |
| 3Jane | 1인칭 aristocratic | 가족 | royal |
| **Neuromancer** | **1인칭 AI** | **초월** | **vast, clinical** |

Neuromancer의 1인칭은 *비인간 AI* 시점. 9번째 시점.

## 5. ADR 통합

- **ADR-0031** Original Scenario Integration
- **ADR-0032** Graphic Novel Mode — 메인메뉴 11 옵션
- **ADR-0050** Boss ICE System (Wintermute/Neuromancer)
- **ADR-0052** Short Story Expansion Plan

## 6. 테스트

- `tests/unit/test_neuromancer_character.py` — 9번째 캐릭터 지원
- `tests/unit/test_graphic_novel_view.py` — 9 chars × 4 ending A = 36 scenes
- `tests/unit/test_novels.py` — Neuromancer 단편 검수

## 7. 다음 단계

- **Phase 9 완료** — Salvation Phase (모든 캐릭터 epilogue)
- **GitHub Projects 보드** — 후속 세션 인수인계
- **세션 종료** — 22 commits, 9 chars, 72 scenes, 4184+ tests