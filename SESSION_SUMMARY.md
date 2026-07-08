# Session Summary — 2026-07-08 (v0.7.9)

> **세션 ID**: roguelike_sprawl-2026-07-08
> **세션 범위**: ARC_PHASE auto-advance 버그 수정 + demo.py 갱신
> **테스트**: 4146 passed (39 skipped, 3 integration pre-existing failures)
> **변경 파일**: 2 files (app.py, scripts/demo.py)

---

## 1. 오늘 작업 요약

### A. Salvation Phase mypy 수정 (ADR-0090)
- `AppState`에 `salvation_runner`, `salvation_selection`, `salvation_scene_data` 필드 추가
- `state.run` → `state.run_state` 수정 (4곳)
- `KeySym.a/b/c` → `KeySym.N1/N2/N3` 수정 (tcod에 letter key 상성 없음)
- `config` import 경로 수정
- `RunState | None` 할당 에러 → 명시적 None 체크
- **커밋**: `49b4cd6`

### C. macOS WindowClose 이벤트 처리 수정
- **문제**: macOS에서 창 닫기(X) 버튼 클릭 시 창이 닫히지 않음
- **원인**: `tcod.event.wait()`가 `WindowClose` 이벤트(type=528)를 반환하지만 게임이 이를 처리하지 않음
- **수정**: `app.py` 메인 루프에 `WindowClose` 체크 추가
- **커밋**: `2aabcd2`

### B. ADR-0102 Accepted — v1.0.0b1 Release
- **결정**: 1.0.0b1 (beta) + 수동 workflow_dispatch
- **PyPI Token**: 실제 토큰 설정 완료
- **GitHub Actions SHA 핀ning**: 모든 workflow 액션을 full-length commit SHA로 핀ning (4파일)
- **Release workflow 수정**: env var 방식, 경로 문제, `uv publish` 플래그 등 5개 버그 수정
- **릴리즈 성공**: `v1.0.0b1` 태그 + PyPI 업로드 완료
- **PyPI**: https://pypi.org/project/roguelike-sprawl/1.0.0b1/
- **GitHub Tag**: `v1.0.0b1`

---

## 2. v1.0.0b1 Release 이력

| 항목 | 값 |
|---|---|
| 버전 | `1.0.0b1` |
| PyPI | https://pypi.org/project/roguelike-sprawl/1.0.0b1/ |
| GitHub Tag | `v1.0.0b1` |
| 릴리즈 워크플로우 수정 | 5개 버그 (env var, 경로, `uv publish` 플래그, YAML block scalar, `--prelease` 제거) |
| Actions SHA 핀ning | 4개 workflow 파일, 8개 액션 핀ning |

---

## 3. 시스템 상태 매트릭스 (최종)

| 항목 | 결과 |
|---|---|
| pytest | **4146 passed** (39 skipped) |
| ruff check | **All passed** |
| ruff format | **All passed** |
| mypy strict | **0 errors** (120 source files) |
| dashboard tests | **623 passed** |

---

## 4. 다음 세션 인수인계

### 즉시 착수 가능
1. ⏳ **GitHub Projects 보드** — https://github.com/users/seoca1/projects (수동 설정)
2. **모든 화면 완전 구현 완료** — 전체 게임 플로우 연결됨

### 이 세션 작업 내용 (v0.7.9)
1. **ARC_PHASE auto-advance 버그 수정 (app.py)**:
   - 기존: `typed >= len(text) and phase_elapsed_ms >= 500` → 500ms에서 typed=16 vs 302글자라 작동 안 함
   - 수정: `phase_elapsed_ms >= len(text)*30 + 50` → 타이핑 완료 후 50ms만 대기
   - phase 마지막 beat 후 SPACE로 진행 안 되던 버그 → `else: phase_elapsed_ms += delta_s*1000` 추가
2. **demo.py 갱신**: ARC_PHASE, CYBERSPACE_MAP, NPC, EVENT, STORY 렌더 + 전환
3. **이전 세션**: CHAPTER→ARC_PHASE 전환, Hub M키, CYBERSPACE_MAP 구현

### 중장기 작업
4. **단편 47개 미션 매핑** — 9개 Mid/Core/TA 미션의 단편 작성
5. **테스트 커버리지 증가** — 현재 ~38% → 목표 80%

---

## 5. 핵심 통계 (전체 누적)

| 메트릭 | 상태 |
|---|---|
| 테스트 통과 | **4146** |
| 자키 수 | **9** |
| GN 씬 수 | **72 + 9 epilogue** |
| Arc JSON | **9자 전부 (L1 완전)** |
| 소설/스토리 연계 | **L1→L3 45 cutscene 전부 해결** |
| 미션 수 | **47** |
| ICE 타입 | **41** |
| 저장 슬롯 | **10 + 1** |
| ADR | **61+ 모두 Accepted** |
| Lint errors | **0** |
| Typecheck errors | **0** |

---

## 6. 최근 커밋 히스토리

| 커밋 | 설명 |
|---|---|
| `44dbfbf` | fix(app): ARC_PHASE auto-advance timing and phase completion bug |
| `5fc98dc` | feat(demo): add ARC_PHASE/CYBERSPACE_MAP/NPC/EVENT/STORY render + transitions |
| `38ccc74` | feat(app): CHAPTER→ARC_PHASE transition when arc loaded, ARC_PHASE auto-advance beats |
| `0dd077e` | feat(hub+menu): Hub M key→CYBERSPACE_MAP, character select loads arc data |
| `d7120c5` | feat(app): implement CYBERSPACE_MAP and ARC_PHASE screens with full render/input |
| `b7cc7d2` | fix(menu): load chapter data on character select (CHAPTER screen was broken) |
| `e522962` | feat(app): implement EVENT/STORY/CYBERSPACE_BROWSER screens, add stubs for remaining |
| `6dff8bd` | feat(app): implement CHAPTER, CHARACTER_SELECT, NPC, ENDING screens |
| `b4978ed` | feat(app): implement SAVED_PROGRESS + DEATH_SUMMARY screens, add stub handlers |
| `1251a22` | feat(graphic_novel): implement GRAPHIC_NOVEL screen in game loop |
| `6152f11` | fix(menu+app): add missing screen dispatches for GRAPHIC_NOVEL_MENU and HALL_OF_DEAD |
| `4a5efbe` | feat(menu): arrow key navigation + cursor indicator |

---

**세션 종료 시간**: 2026-07-08
**최종 검증**: ruff ✅ / format ✅ / mypy ✅ / pytest 4146 ✅
**이 문서 버전**: v0.7.9
**이전 버전**: v0.7.8 (2026-07-08)
