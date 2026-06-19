"""Tests for skill combo system (combat/combo.py).

Validates:
- 5 ComboStage definitions
- CombatCombo: register_hit, window expiry, stage progression
- Stage transition flags (stage_up_pending, just_ended)
- Damage bonus application
- AP regen tracking
- ComboVisual updates
- render functions (counter, stage_up, end)
- spawn_combo_hit high-level entry
- Stats tracking (max_combo_reached, total_damage_dealt)
"""

from __future__ import annotations

import pytest

from roguelike_sprawl.combat.combo import (
    ALL_STAGES,
    ANNIHILATION,
    CHAIN,
    FLURRY,
    RAMPAGE,
    WARMUP,
    CombatCombo,
    ComboVisual,
    render_combo_counter,
    render_combo_end,
    render_combo_stage_up,
    spawn_combo_hit,
    update_combo_visual,
)

# ----------------------------------------------------------------------------
# Stage definitions
# ----------------------------------------------------------------------------


class TestStageDefinitions:
    def test_five_stages(self) -> None:
        assert len(ALL_STAGES) == 5

    def test_stage_order(self) -> None:
        # Stages should be ordered WARMUP → CHAIN → FLURRY → RAMPAGE → ANNIHILATION
        expected = ["WARMUP", "CHAIN", "FLURRY", "RAMPAGE", "ANNIHILATION"]
        actual = [s.name for s in ALL_STAGES]
        assert actual == expected

    def test_min_count_increases(self) -> None:
        counts = [s.min_count for s in ALL_STAGES]
        assert counts == sorted(counts)

    def test_damage_bonus_increases(self) -> None:
        bonuses = [s.damage_bonus_pct for s in ALL_STAGES]
        assert bonuses == sorted(bonuses)

    def test_all_stages_have_korean(self) -> None:
        for stage in ALL_STAGES:
            assert stage.name_ko
            # WARMUP may have empty label (no stage callout), others should
            if stage.index > 0:
                assert stage.label


# ----------------------------------------------------------------------------
# CombatCombo: hit registration
# ----------------------------------------------------------------------------


class TestCombatComboRegisterHit:
    def test_first_hit_count_one(self) -> None:
        c = CombatCombo()
        c.register_hit(current_ms=0)
        assert c.count == 1

    def test_consecutive_hits_increment(self) -> None:
        c = CombatCombo()
        for i in range(5):
            c.register_hit(current_ms=i * 500)
        assert c.count == 5

    def test_window_expiry_resets(self) -> None:
        c = CombatCombo(window_ms=1000)
        c.register_hit(current_ms=0)
        c.register_hit(current_ms=500)
        assert c.count == 2
        # After window expires
        c.register_hit(current_ms=2000)
        assert c.count == 1  # Reset

    def test_total_damage_tracked(self) -> None:
        c = CombatCombo()
        c.register_hit(current_ms=0, damage_dealt=50)
        c.register_hit(current_ms=500, damage_dealt=80)
        c.register_hit(current_ms=1000, damage_dealt=120)
        assert c.total_damage_dealt == 250

    def test_max_combo_tracked(self) -> None:
        c = CombatCombo()
        for i in range(7):
            c.register_hit(current_ms=i * 500)
        assert c.max_combo_reached == 7


# ----------------------------------------------------------------------------
# Stage progression
# ----------------------------------------------------------------------------


STAGE_PROGRESSION_CASES: list[tuple[int, str]] = [
    (1, "WARMUP"),
    (2, "WARMUP"),
    (3, "CHAIN"),
    (4, "FLURRY"),
    (5, "RAMPAGE"),
    (6, "ANNIHILATION"),
    (10, "ANNIHILATION"),
]


class TestStageProgression:
    @pytest.mark.parametrize("case_idx", list(range(len(STAGE_PROGRESSION_CASES))))
    def test_stage_at_count(self, case_idx: int) -> None:
        hits, expected_stage = STAGE_PROGRESSION_CASES[case_idx]
        c = CombatCombo()
        for i in range(hits):
            c.register_hit(current_ms=i * 500)
        assert c.current_stage.name == expected_stage

    def test_stage_up_flag_set(self) -> None:
        c = CombatCombo()
        c.register_hit(current_ms=0)  # 1, WARMUP
        c.register_hit(current_ms=500)  # 2, WARMUP (no stage change)
        assert not c.stage_up_pending
        c.register_hit(current_ms=1000)  # 3, CHAIN (stage up!)
        assert c.stage_up_pending

    def test_stage_up_consumed_once(self) -> None:
        c = CombatCombo()
        c.register_hit(current_ms=0)
        c.register_hit(current_ms=500)
        c.register_hit(current_ms=1000)  # stage up
        first = c.consume_stage_up()
        assert first is not None
        assert first.name == "CHAIN"
        # Second consume returns None
        second = c.consume_stage_up()
        assert second is None

    def test_previous_stage_tracked(self) -> None:
        c = CombatCombo()
        for i in range(5):
            c.register_hit(current_ms=i * 500)
        # After 5 hits, current=RAMPAGE, previous=FLURRY
        assert c.current_stage.name == "RAMPAGE"
        assert c.previous_stage.name == "FLURRY"


# ----------------------------------------------------------------------------
# Window expiry and end
# ----------------------------------------------------------------------------


class TestWindowExpiry:
    def test_step_detects_expiry(self) -> None:
        c = CombatCombo(window_ms=1000)
        c.register_hit(current_ms=0)
        c.register_hit(current_ms=500)
        # Step past window
        c.step(600)  # elapsed = 600, still within window
        assert not c.just_ended
        c.step(500)  # elapsed = 1100, past window
        assert c.just_ended

    def test_combo_ends_resets_count(self) -> None:
        c = CombatCombo(window_ms=1000)
        c.register_hit(current_ms=0)
        c.register_hit(current_ms=500)
        c.step(1100)
        assert c.count == 0
        assert c.current_stage.name == "WARMUP"

    def test_combo_ends_returns_true_once(self) -> None:
        c = CombatCombo(window_ms=1000)
        c.register_hit(current_ms=0)
        c.step(1100)
        first = c.consume_just_ended()
        assert first is True
        second = c.consume_just_ended()
        assert second is False


# ----------------------------------------------------------------------------
# Reset
# ----------------------------------------------------------------------------


class TestReset:
    def test_reset_clears_count(self) -> None:
        c = CombatCombo()
        for i in range(5):
            c.register_hit(current_ms=i * 500)
        c.reset()
        assert c.count == 0
        assert c.current_stage.name == "WARMUP"

    def test_reset_preserves_max(self) -> None:
        c = CombatCombo()
        for i in range(7):
            c.register_hit(current_ms=i * 500)
        c.reset()
        # max_combo_reached persists (it's a stat)
        assert c.max_combo_reached == 7


# ----------------------------------------------------------------------------
# Damage bonus
# ----------------------------------------------------------------------------


DAMAGE_BONUS_CASES: list[tuple[str, int, int]] = [
    ("WARMUP", 100, 100),  # +0%
    ("CHAIN", 100, 120),  # +20%
    ("FLURRY", 100, 150),  # +50%
    ("RAMPAGE", 100, 200),  # +100%
    ("ANNIHILATION", 100, 300),  # +200%
]


class TestDamageBonus:
    @pytest.mark.parametrize("case_idx", list(range(len(DAMAGE_BONUS_CASES))))
    def test_bonus_at_stage(self, case_idx: int) -> None:
        stage_name, base, expected = DAMAGE_BONUS_CASES[case_idx]
        c = CombatCombo()
        stage = next(s for s in ALL_STAGES if s.name == stage_name)
        c.count = stage.min_count
        c.current_stage = stage
        assert c.apply_damage_bonus(base) == expected


# ----------------------------------------------------------------------------
# AP regen
# ----------------------------------------------------------------------------


class TestAPRegen:
    def test_warmup_no_regen(self) -> None:
        c = CombatCombo()
        c.count = 1
        c.current_stage = WARMUP
        assert c.get_ap_regen() == 0

    def test_chain_no_regen(self) -> None:
        c = CombatCombo()
        c.count = 3
        c.current_stage = CHAIN
        assert c.get_ap_regen() == 0

    def test_flurry_regen_1(self) -> None:
        c = CombatCombo()
        c.count = 4
        c.current_stage = FLURRY
        assert c.get_ap_regen() == 1

    def test_rampage_regen_2(self) -> None:
        c = CombatCombo()
        c.count = 5
        c.current_stage = RAMPAGE
        assert c.get_ap_regen() == 2

    def test_annihilation_regen_3(self) -> None:
        c = CombatCombo()
        c.count = 6
        c.current_stage = ANNIHILATION
        assert c.get_ap_regen() == 3


# ----------------------------------------------------------------------------
# ComboVisual
# ----------------------------------------------------------------------------


class TestComboVisual:
    def test_initial_state(self) -> None:
        v = ComboVisual()
        assert v.counter_text == ""
        assert v.stage_up_text == ""
        assert v.end_text == ""

    def test_update_with_combo(self) -> None:
        c = CombatCombo()
        v = ComboVisual()
        c.register_hit(current_ms=0)
        c.register_hit(current_ms=500)
        c.register_hit(current_ms=1000)  # stage up to CHAIN
        update_combo_visual(v, c)
        assert v.counter_text == "3x CHAIN!"
        assert v.counter_color == CHAIN.color
        assert v.stage_up_text != ""  # "▸ 연쇄 단계 돌입 ..."

    def test_pulse_set_on_hit(self) -> None:
        c = CombatCombo()
        v = ComboVisual()
        c.register_hit(current_ms=0)
        c.register_hit(current_ms=500)
        c.register_hit(current_ms=1000)  # 3rd hit
        update_combo_visual(v, c)
        assert v.counter_pulse_ms > 0


# ----------------------------------------------------------------------------
# Render functions
# ----------------------------------------------------------------------------


class TestRenderFunctions:
    def test_render_counter_empty(self) -> None:
        v = ComboVisual()
        assert render_combo_counter(v) == ""

    def test_render_counter_padded(self) -> None:
        v = ComboVisual()
        v.counter_text = "3x CHAIN!"
        s = render_combo_counter(v, width=30)
        assert s.strip() == "3x CHAIN!"

    def test_render_stage_up(self) -> None:
        v = ComboVisual()
        v.stage_up_text = "▸ 연쇄 단계 돌입"
        v.stage_up_ms = 500
        assert render_combo_stage_up(v) == "▸ 연쇄 단계 돌입"

    def test_render_stage_up_expired(self) -> None:
        v = ComboVisual()
        v.stage_up_text = "▸ 연쇄 단계 돌입"
        v.stage_up_ms = 0
        assert render_combo_stage_up(v) == ""

    def test_render_end(self) -> None:
        v = ComboVisual()
        v.end_text = "[ 콤보 종료 ]"
        v.end_ms = 1000
        assert render_combo_end(v) == "[ 콤보 종료 ]"

    def test_render_end_expired(self) -> None:
        v = ComboVisual()
        v.end_text = "[ 콤보 종료 ]"
        v.end_ms = 0
        assert render_combo_end(v) == ""


# ----------------------------------------------------------------------------
# spawn_combo_hit
# ----------------------------------------------------------------------------


class TestSpawnComboHit:
    def test_first_hit(self) -> None:
        c = CombatCombo()
        v = ComboVisual()
        stage = spawn_combo_hit(c, v, current_ms=0, damage_dealt=50)
        assert stage.name == "WARMUP"
        assert c.count == 1

    def test_three_hits_chains(self) -> None:
        c = CombatCombo()
        v = ComboVisual()
        spawn_combo_hit(c, v, current_ms=0)
        spawn_combo_hit(c, v, current_ms=500)
        stage = spawn_combo_hit(c, v, current_ms=1000)
        assert stage.name == "CHAIN"
        assert v.counter_text == "3x CHAIN!"

    def test_six_hits_annihilates(self) -> None:
        c = CombatCombo()
        v = ComboVisual()
        for i in range(6):
            spawn_combo_hit(c, v, current_ms=i * 500, damage_dealt=50)
        assert c.current_stage.name == "ANNIHILATION"
        assert c.max_combo_reached == 6
        assert c.total_damage_dealt == 300


# ----------------------------------------------------------------------------
# Window timer visual
# ----------------------------------------------------------------------------


class TestWindowTimer:
    def test_window_progress_zero_at_hit(self) -> None:
        c = CombatCombo()
        c.register_hit(current_ms=0)
        assert c.window_progress == 0.0

    def test_window_progress_increases(self) -> None:
        c = CombatCombo(window_ms=1000)
        c.register_hit(current_ms=0)
        c.step(500)
        assert 0.4 < c.window_progress < 0.6

    def test_window_remaining_pct(self) -> None:
        c = CombatCombo(window_ms=1000)
        c.register_hit(current_ms=0)
        c.step(250)
        # 75% remaining
        assert 70 < c.window_remaining_pct < 80


# ----------------------------------------------------------------------------
# Display label
# ----------------------------------------------------------------------------


class TestDisplayLabel:
    def test_label_empty_at_low_count(self) -> None:
        c = CombatCombo()
        assert c.display_label == ""

    def test_label_includes_count_and_stage(self) -> None:
        c = CombatCombo()
        for i in range(3):
            c.register_hit(current_ms=i * 500)
        assert "3x" in c.display_label
        assert "CHAIN" in c.display_label

    def test_label_clamps_at_99(self) -> None:
        c = CombatCombo()
        for i in range(150):
            c.register_hit(current_ms=i * 100)  # 100ms apart
        # Display count should be 99, not 150
        assert c.display_count == 99
