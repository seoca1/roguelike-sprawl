# Session Handover — 2026-06-30

> **다음 세션을 위한 종합 상태 보고서**
> 게임 구조, 완료된 작업, 결정사항, 다음 단계 작업 명세

---

## 1. 프로젝트 개요

| 항목 | 값 |
|---|---|
| 프로젝트 | Roguelike Sprawl (William Gibson 사이버펑크 로그라이크) |
| 언어 | Python 3.11+ (3.12, 3.14 호환) |
| 렌더링 | python-tcod 16.0+ |
| 아키텍처 | ECS-lite, RT-MS (Real-Time with Menu Skills) |
| 라이브 | https://seoca1.github.io/roguelike-sprawl/ |
| 저장소 | https://github.com/seoca1/roguelike-sprawl |
| Git 커밋 | 7개 푸시 완료 (a5f0de5 ~ main) |
| 테스트 | 2,257+ 단위 테스트 |

---

## 2. 현재 게임 아키텍처

### 2-1. 디렉토리 구조
```
Game/roguelike_sprawl/prototype/
├── src/roguelike_sprawl/         # 게임 코드
│   ├── engine/                    # 게임 루프 (app.py, state.py)
│   │   ├── chapter_view.py
│   │   ├── original_story.py       # 캐릭터 선택 + 엔딩
│   │   ├── matrix_view.py          # ★ 현재 MATRIX 화면
│   │   ├── dungeon_view.py         # ★ 구현됨, 미사용
│   │   ├── combat_view.py
│   │   └── chapter_cutscene.py
│   ├── matrix/                    # 매트릭스 시스템
│   │   ├── graph.py                # 노드/엣지 그래프
│   │   ├── node.py                 # Node/NodeKind/Faction/IceKind
│   │   ├── exploration.py          # ADR-0020 Fog of War
│   │   ├── generator.py            # 절차적 그래프 생성
│   │   ├── dungeon_generator.py    # ★ 7x5 그리드 던전 (수동 레이아웃)
│   │   └── cyberspace_generator.py  # 사이버스페이스 절차 생성
│   ├── cyberspace/                 # 다중 월드/서버 시스템
│   ├── missions/                   # 29 미션 시스템
│   ├── combat/                     # RT-MS 전투
│   ├── ecs/                        # ECS-lite
│   ├── data/                       # JSON 데이터
│   │   ├── missions/missions.json   # 29 미션
│   │   ├── story/chapters/*.json    # 3 챕터
│   │   ├── story/arcs/*.json         # 3 아크 (5 chapter × 5 phase)
│   │   └── story/prologues/*.json    # 3 프롤로그
│   ├── i18n/                       # UI 번역 (en/ko)
│   └── ...
├── tests/unit/                    # 2,257+ 단위 테스트
└── data/                           # 게임 데이터
    └── story/chapters/case.json, sil.json, kas.json
```

### 2-2. 게임 루프 (ScreenKind Enum)
```
MENU → CHARACTER_SELECT → CHAPTER (12s typing) → HUB → MATRIX → COMBAT
                                                          ↓
                          JACK_OUT → REWARD → (DEBRIEF) → HUB
DEATH → DEATH_SUMMARY → HALL_OF_DEAD
GRAPHIC_NOVEL_MENU → GRAPHIC_NOVEL → SAVED_PROGRESS
```

### 2-3. 데이터 흐름
```
missions.json (29 미션)
  ↓ story.source 정규화
  ↓ stem 매칭 (date prefix 자동)
  ↓
단편 파일 ({date}_{stem}.md / .ko.md)
  ↓ 인용 발췌
  ↓
chapters/{case,sil,kas}.json (CHAPTER 화면 excerpt)
```

---

## 3. 이번 세션에서 완료된 작업

### 3-1. 문서/위키/LLM Wiki 정비
- ✅ LLM Wiki Vault 검증 및 정리 (전체 4,034 파일 중 깨진 링크 0건)
- ✅ Fiction + Language 단/복수 폴더 통합 (단수형 → 복수형으로 19개 파일 이동)
- ✅ Fiction + Language 카테고리 폴더 통합 (912개 중복 파일 제거, 24개 폴더 삭제)
- ✅ Fiction/wiki/ 오타 폴더(sprawl-trilology) 삭제
- ✅ VAULT_AUDIT_REPORT.md 작성

### 3-2. 게임 시스템 검증 및 개선
- ✅ 미션-단편 매핑 정규화 헬퍼 (`story_resolver.py`)
- ✅ 검증 CLI (`verify_story_links.py`)
- ✅ 15개 단위 테스트 추가 (전체 15/15 PASS)
- ✅ 미션 데이터 갱신: `voodoo_loa_contact` → `loa_voodoo_contact` (stem 오타 수정)
- ✅ 챕터 JSON 메타데이터 경로 오타 수정 (`data/` → `prototype/data/`)
- ✅ 챕터 JSON "연결 캐릭터" 정확화 (3개 파일)
- ✅ 단편 frontmatter `character_ref` 표준화 (32개 파일)
- ✅ Orphan 단편 3개 미션 추가 (`flatline_call`, `sally_returns_arc3`, `sally_sandii_3am`)
- ✅ 3개 미작성 단편 novelette 작성 (`mollys_razor`, `ta_heist`, `aleph_fragment`)
- ✅ 9개 빈약 단편 novelette 보강 (에필로그 + 모티프 변주)
- ✅ 11개 신규 단편 미션 추가 (06-25/06-29 시리즈)

### 3-3. 캐릭터 진행 데모 스토리
- ✅ 3개 캐릭터 (Novice/Veteran/Heretic) 진행 스토리 작성
- ✅ Journey 페이지 4개 (MD) + 4개 (HTML) 생성
- ✅ 통합 README + 구조 검증 보고

### 3-4. 대시보드 검증 및 배포
- ✅ 19건 깨진 HTML 링크 모두 수정 (3가지 패턴)
- ✅ 81개 HTML 페이지 모두 통과 (깨진 링크 0건)
- ✅ GitHub Pages 배포 (`pages.yml` workflow)
- ✅ 라이브 사이트: https://seoca1.github.io/roguelike-sprawl/

---

## 4. 핵심 결정사항 (ADR)

| ADR | 제목 | 상태 |
|---|---|---|
| ADR-0031 | Original Scenario Integration | ✅ Accepted (캐릭터 3명 + 챕터 스크린) |
| ADR-0032 | Graphic Novel Mode | ✅ Accepted |
| ADR-0040 | Death Restart Cycle (FLATLINE) | ✅ Accepted |
| ADR-0041 | Graphic Novel Content Expansion | ✅ Accepted |
| ADR-0048 | GN Ending Menu + Save Migration | ✅ Accepted |
| ADR-0050 | Boss ICE System | ✅ Accepted |
| ADR-0051 | GN Save Slots + Mission Story Metadata | ✅ Accepted |
| ADR-0052 | Short Story Expansion Plan | ✅ Accepted |

---

## 5. 미해결 이슈 / Known Issues

### 5-1. CI 실패
- GitHub Actions CI (lint + typecheck + test)가 마지막 푸시 후 `failure` 상태
- 사이트 배포는 영향 없음 (별도 workflow)
- 원인 추정: 게임 코드 변경에 따른 lint/test 실패
- 조치 필요 시: `prototype/scripts/ci_check.sh` 또는 pytest로 로컬 재현

### 5-2. 던전 뷰 미사용
- `dungeon_view.py` (415 lines) 구현되어 있으나 `app.py`에서 호출되지 않음
- 현재 MATRIX 화면은 `matrix_view.py` 사용
- 다음 세션 목표: dungeon_view 활성화 또는 통합 결정

### 5-3. ADR-0020 (Fog of War) 부분 구현
- `exploration.py` 정의되어 있으나 dungeon_view와의 완전 통합 미확인
- 검증 필요

---

## 6. 다음 단계: 게임플레이 개량 (Dungeon 탐색)

### 6-1. 개량 목표
**현재 시스템 한계**:
- 매트릭스가 추상적 노드 그래프 (matrix_view)
- 던전 그리드 (7x5, 수동 레이아웃)는 구현되어 있지만 미사용
- 절차적 생성 미흡 (랜덤 시드 활용 안 됨)
- 미션과 던전 룸 매핑 미흡
- 캐릭터별 분기 미통합
- Arc 시스템 (1~5)과의 연결 미흡

### 6-2. 검토된 옵션
- **옵션 A**: dungeon_view.py 활성화 (최소 변경, 수동 레이아웃)
- **옵션 B**: dungeon_view + 절차적 생성 강화 (랜덤 시드, 적 배치)
- **옵션 C**: 완전 절차적 BSP (Hades/Enter the Gungeon 스타일)
- **옵션 D**: 하이브리드 (수동 던전 + 절차적 변형)

자세한 분석: `docs/DUNGEON_EXPLORATION_REVIEW.md` (작성 예정)

### 6-3. 권장 사항
- 옵션 B (점진적 강화) 권장
- 이유: 기존 dungeon_view 활용, 미션/Arc 시스템과 자연 통합
- 5단계 로드맵:
  1. dungeon_view 활성화 (app.py 수정)
  2. 미션 → 던전 룸 자동 매핑
  3. 캐릭터별 시드/레이아웃 변형
  4. 적 배치 절차화 (랜덤)
  5. ECS 통합 + 보상 시스템

---

## 7. 데이터 통계

| 지표 | 값 |
|---|---:|
| 미션 시스템 | 29개 |
| 챕터 | 3 (Novice/Veteran/Heretic) |
| 아크 | 3 (5 chapter × 5 phase = 25 phase/chapter) |
| 단편 파일 | 35개 EN / 30개 KO |
| 단편 매핑 | 29/29 ✓ |
| 캐릭터 진행 데모 | 3 캐릭터 × 5 챕터 |
| 픽서 | 6종 (finn/dixie/sally/maas/kumiko/ta_rep/yakuza) |
| 엔딩 | 6 (각 캐릭터 A/B) |
| 단위 테스트 | 2,257+ (15 신규 추가) |
| 대시보드 HTML | 81개 (깨진 링크 0건) |
| Journey 페이지 | 8개 (4 MD + 4 HTML) |
| 깁슨 위키 페이지 | 120개 |
| 단편 카드 | 58개 (29 × 2 언어) |
| 챕터 카드 | 6개 (3 × 2 언어) |
| 라이브 사이트 | https://seoca1.github.io/roguelike-sprawl/ |

---

## 8. 다음 세션 즉시 시작 가이드

### 8-1. 환경 활성화
```bash
cd /Users/emilio/projects/Projects/Game/roguelike_sprawl
source prototype/.venv/bin/activate  # 또는 직접 .venv/bin/python
```

### 8-2. 빠른 검증
```bash
# 테스트
.venv/bin/python -m pytest prototype/tests/unit/ -q

# 미션 매핑
python3 prototype/scripts/verify_story_links.py

# 게임 실행
.venv/bin/python -m roguelike_sprawl  # 또는 prototype/scripts/play.py
```

### 8-3. 다음 작업 시작점
1. `docs/DUNGEON_EXPLORATION_REVIEW.md` 작성
2. dungeon_view.py vs matrix_view.py 비교 분석
3. 옵션 A 최소 통합 PoC 작성 (app.py 수정)
4. 통합 후 회귀 테스트

---

## 9. 핵심 파일 위치

| 항목 | 경로 |
|---|---|
| 게임 루프 | `prototype/src/roguelike_sprawl/engine/app.py` |
| 매트릭스 화면 | `prototype/src/roguelike_sprawl/engine/matrix_view.py` |
| 던전 화면 (미사용) | `prototype/src/roguelike_sprawl/engine/dungeon_view.py` |
| 던전 생성기 | `prototype/src/roguelike_sprawl/matrix/dungeon_generator.py` |
| 미션 데이터 | `prototype/data/missions/missions.json` |
| 챕터 JSON | `prototype/data/story/chapters/{case,sil,kas}.json` |
| 캐릭터 진행 데모 | `dashboard/stories/journey/{novice,veteran,heretic}.md` |
| 단편 카드 | `dashboard/stories/short-stories/` (58개) |
| 단위 테스트 | `prototype/tests/unit/` (2,257+) |
| 정규화 헬퍼 | `prototype/src/roguelike_sprawl/data/story_resolver.py` |
| 검증 CLI | `prototype/scripts/verify_story_links.py` |
| GitHub Pages 설정 | `.github/workflows/pages.yml` |

---

## 10. ADR + 결정 흐름

**게임플레이 개량 작업 시작 시 권장 ADR 작성**:
- `decisions/0060-dungeon-exploration-redesign.md`
- 목적: dungeon_view 활성화 + 절차적 강화 결정
- 배경: 현재 matrix_view 한계, dungeon_view 미사용
- 옵션: A/B/C/D 비교
- 권장안: 옵션 B (점진적 강화)
- 결과 (Consequences): 게임플레이 변화, 코드 영향 범위

---

## 11. 위험 요소 및 제약

### 11-1. 기술적 위험
- **던전 ↔ 미션 매핑 복잡성**: 29개 미션을 7x5 그리드 룸에 자연스럽게 배치하기 어려움
- **Faction 균형**: SENSE_NET/T-A/MaaS/야쿠자 별 적 배치 분포
- **난이도 곡선**: 미션 grade 1~5 → 던전 complexity 1~5 매핑

### 11-2. 시간적 위험
- dungeon_view 활성화만 해도 1~2일 (app.py 수정 + 테스트)
- 절차적 생성 강화는 3~5일
- ECS 통합은 1~2주 (ECS 시스템 영향)

### 11-3. 콘텐츠 위험
- 29개 미션의 분량 다양성 (단편 3,236자~9,628자)
- 캐릭터별 동적 분기 (novice/veteran/heretic 시점 다름)
- 깁슨 원작과의 정합성 유지 필요

---

## 12. 다음 세션 TODO (우선순위)

| 순서 | 작업 | 우선순위 |
|---|---|---|
| 1 | `docs/DUNGEON_EXPLORATION_REVIEW.md` 작성 | 🔴 높음 |
| 2 | dungeon_view vs matrix_view 비교 분석 | 🔴 높음 |
| 3 | 미션-던전 룸 매핑 매트릭스 초안 | 🟡 중간 |
| 4 | 옵션 A PoC 작성 (app.py 수정) | 🟡 중간 |
| 5 | 검증 체크리스트 작성 | 🟡 중간 |
| 6 | ADR-0060 작성 (던전 개량 결정) | 🟢 보통 |
| 7 | CI 실패 원인 분석 및 수정 | 🟢 보통 |

---

*Generated: 2026-06-30 23:30 by opencode session*
*Next session: roguelike dungeon 탐색방식 개량*