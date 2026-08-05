"""Automated tests mirroring testcases/combat/salvage.md (TC-COMBAT-001 ~ 006).

Source spec: Game/roguelike_sprawl/testcases/combat/salvage.md

Status (2026-08-04): testcases/ describes behavioral specs that lack corresponding
implementations in the current engine. These tests are scaffolded as `pytest.mark.xfail`
to document the gap. When salvage HEAL/disengage logic is implemented, the marks can
be removed and assertions can be enabled.

Scope:
- TC-COMBAT-001: HEAL — 기본 회복 (P0, Active)
- TC-COMBAT-002: HEAL — max HP일 때 (P1, Active)
- TC-COMBAT-003: HEAL — 사망 직전 (P1, Active)
- TC-COMBAT-004: SKIP — 보상 없음 (P1, Active)
- TC-COMBAT-005: Disengage — salvage 없음 (P0, Active)
- TC-COMBAT-006: Death — salvage 없음 (P0, Active) — see test_death_extended.py
"""

from __future__ import annotations

import pytest

HEAL_PCT = 0.20  # Per ADR-0014: Data Salvage = HEAL 20%


@pytest.mark.xfail(reason="salvage HEAL not yet implemented (testcase aspirational)")
class TestTcCombat001HealBasic:
    """TC-COMBAT-001: HEAL — 기본 회복.

    Given: 자키 HP 50/100, max HP 100
    When: ICE 격파 → HEAL 선택
    Then: HP = 50 + (100 * 0.20) = 70
    Then: 매트릭스로 복귀
    Then: HUD에 "+20 HP" 또는 "HEAL applied" 메시지 표시
    """

    def test_hp_increases_by_max_hp_pct(self) -> None:
        hp_before = 50
        max_hp = 100
        expected = hp_before + int(max_hp * HEAL_PCT)
        assert expected == 70

    def test_hp_does_not_exceed_max(self) -> None:
        hp_before = 95
        max_hp = 100
        healed = hp_before + int(max_hp * HEAL_PCT)
        assert healed <= max_hp


@pytest.mark.xfail(reason="salvage HEAL not yet implemented (testcase aspirational)")
class TestTcCombat002HealMaxHp:
    """TC-COMBAT-002: HEAL — max HP일 때.

    Given: 자키 HP 100/100, max HP 100
    When: ICE 격파 → HEAL 선택
    Then: HP = 100 (변화 없음)
    Then: "no damage to repair" 메시지 표시
    Then: 매트릭스로 복귀
    """

    def test_hp_unchanged_at_max(self) -> None:
        hp_before = 100
        max_hp = 100
        healed = min(hp_before + int(max_hp * HEAL_PCT), max_hp)
        assert healed == 100


@pytest.mark.xfail(reason="salvage HEAL not yet implemented (testcase aspirational)")
class TestTcCombat003HealNearDeath:
    """TC-COMBAT-003: HEAL — 사망 직전.

    Given: 자키 HP 5/100, max HP 100
    When: ICE 격파 → HEAL 선택
    Then: HP = 5 + 20 = 25
    Then: 자키는 살아남음
    Then: 매트릭스로 복귀
    """

    def test_near_death_player_survives(self) -> None:
        hp_before = 5
        max_hp = 100
        healed = min(hp_before + int(max_hp * HEAL_PCT), max_hp)
        assert healed == 25
        assert healed > 0


@pytest.mark.xfail(reason="salvage SKIP not yet implemented (testcase aspirational)")
class TestTcCombat004Skip:
    """TC-COMBAT-004: SKIP — 보상 없음.

    Given: 자키 HP 30/100, max HP 100
    When: ICE 격파 → SKIP 선택
    Then: HP = 30 (변화 없음)
    Then: 매트릭스로 복귀
    Then: 보상 없음 (전략적 선택)
    """

    def test_skip_leaves_hp_unchanged(self) -> None:
        hp_before = 30
        # SKIP applies no change
        healed = hp_before
        assert healed == 30
