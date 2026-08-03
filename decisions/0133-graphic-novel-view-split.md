# ADR-0133: graphic_novel_view.py Split — Implementation (Supplements ADR-0111)

**상태**: Accepted
**날짜**: 2026-07-27
**결정자**: 사용자
**우선순위**: P2 (Build Health)
**연관**: ADR-0111 (graphic_novel_view size — Accepted Option 4 정당화만), ADR-0112/0113 (deferred)

---

## 컨텍스트 (Context)

ADR-0111 (2026-07-12) 에서 graphic_novel_view.py (1594 LOC) 가 1000+ LOC 임을 인정하고 Option 4 (정당화만, 분할 보류) 로 Accepted. 2026-07-27 게임성 점검 사이클에서 우선순위 재평가 → **분할 실행** 결정.

combat/effects.py (1246 LOC, ADR-0112), combat_view.py (1053 LOC, ADR-0113) 도 동일 패턴이지만 *이번 사이클에서는 보류* — 한 세션에 너무 많은 변경 금지 (AGENTS.md).

---

## 적용된 변경

### 분할 구조 (post split)

| 모듈 | LOC | 책임 |
|---|---:|---|
| `graphic_novel_data.py` (신규) | 123 | Dataclasses: Portrait, Background, DialogueLine, SceneData |
| `graphic_novel_loaders.py` (신규) | 262 | JSON parsing + scene/art loaders |
| `graphic_novel_view.py` (축소) | 1272 | Render + menu + screen render |

**Before**: 1 module, 1594 LOC
**After**: 3 modules, 1657 LOC total (63 LOC overhead for module headers/imports)

### Backward Compatibility

graphic_novel_view.py 는 다음을 **재export**:
- Dataclasses: Portrait, Background, DialogueLine, SceneData
- Loaders: load_portrait, load_background, load_scene, load_scene_chain, load_prologue_chain, list_scenes_for_character
- Internal: _parse_palette, _parse_char_colors, _parse_scene

기존 import 문 (`from .graphic_novel_view import SceneData, load_prologue_chain` 등) 변경 없이 동작. `__all__` 명시 + `# noqa: F401` 로 mypy/ruff 호환.

---

## 보류 (deferred to v1.1.0+)

### ADR-0112: combat/effects.py split
- 1246 LOC → ~3 modules (effect types, VFX spawning, color palettes)
- 5-Layer VFX 시스템 + Boss VFX themes
- 후속 사이클 검토

### ADR-0113: combat_view.py split
- 1096 LOC → ~3 modules (HUD, status panel, combat log)
- 전투 화면 렌더링 + HUD + 액션 메뉴
- 후속 사이클 검토

---

## 검증

- ruff check ✓ / ruff format ✓ / mypy strict ✓ (134 source files, +4 신규)
- 175 GN-related tests pass (test_graphic_novel_view, endings, ending_menu, ending_c, wigan_character)
- 전체 suite: 3178 passed (+27 신규), 592 skipped, 0 failed
- Backward compat: 기존 import (`from .graphic_novel_view import SceneData` 등) 변경 없이 동작

---

## 결과 (Consequences)

**Accepted** (2026-07-27). Pillar 정합:
- P5 (The Style): 코드 조직 명확화 — 신규 contributor 진입 장벽 ↓
- 효과: graphic_novel_view 1,272 LOC (1,000+ 한계 통과, ADR-0110/0111 정합)

회귀 위험 평가:
- `__all__` + `# noqa: F401` 로 외부 API 변동 없음
- 신규 import path (`graphic_novel_data`, `graphic_novel_loaders`) 도 사용 가능 (forward compat)
- 잔존: import * 사용처는 영향 없음 (전체 grep 확인)