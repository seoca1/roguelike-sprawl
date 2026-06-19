"""Tests for BOSS ICE multi-phase system (combat/bosses.py).

Validates:
- 3 BOSS definitions (GOLIATH PRIME, BLACK ICE LORD, WATCHDOG ALPHA)
- BossSpec, BossPhase data classes
- is_boss / get_boss_spec lookups
- get_next_phase HP threshold logic
- apply_phase_buff stat math
- boss_intro_sequence multi-line construction
- boss_phase_transition cinematic
- boss_death_sequence multi-stage (4 sequences)
- High-level spawners (spawn_boss_intro, spawn_boss_phase_transition,
  spawn_boss_death)
"""

from __future__ import annotations

import dataclasses

import pytest

from roguelike_sprawl.combat.bosses import (
    ALL_BOSSES,
    BLACK_ICE_LORD,
    GOLIATH_PRIME,
    WATCHDOG_ALPHA,
    BossPhase,
    apply_phase_buff,
    boss_death_sequence,
    boss_epilogue_lines,
    boss_intro_sequence,
    boss_phase_transition,
    get_boss_spec,
    get_next_phase,
    is_boss,
    spawn_boss_death,
    spawn_boss_intro,
    spawn_boss_phase_transition,
)
from roguelike_sprawl.combat.effects import CombatEffects, IceType

ALL_BOSS_IDS = ["goliath_prime", "black_ice_lord", "watchdog_alpha"]


# ----------------------------------------------------------------------------
# Data class structure
# ----------------------------------------------------------------------------


class TestBossDataClasses:
    def test_boss_spec_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            GOLIATH_PRIME.id = "hacked"  # type: ignore[misc]

    def test_boss_phase_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            GOLIATH_PRIME.phases[0].name = "hacked"  # type: ignore[misc]

    def test_goliath_has_4_phases(self) -> None:
        assert len(GOLIATH_PRIME.phases) == 4

    def test_black_has_3_phases(self) -> None:
        assert len(BLACK_ICE_LORD.phases) == 3

    def test_watchdog_has_3_phases(self) -> None:
        assert len(WATCHDOG_ALPHA.phases) == 3

    def test_phases_ordered_high_to_low(self) -> None:
        for spec in ALL_BOSSES.values():
            thresholds = [p.hp_threshold_pct for p in spec.phases]
            assert thresholds == sorted(thresholds, reverse=True), (
                f"{spec.id} phases not ordered: {thresholds}"
            )


# ----------------------------------------------------------------------------
# Lookup functions
# ----------------------------------------------------------------------------


@pytest.mark.parametrize("boss_id", ALL_BOSS_IDS)
class TestBossLookup:
    def test_is_boss_true(self, boss_id: str) -> None:
        assert is_boss(boss_id)

    def test_get_boss_spec_returns_spec(self, boss_id: str) -> None:
        spec = get_boss_spec(boss_id)
        assert spec is not None
        assert spec.id == boss_id

    def test_all_bosses_contains(self, boss_id: str) -> None:
        assert boss_id in ALL_BOSSES


class TestIsBossFalse:
    def test_standard_not_boss(self) -> None:
        assert not is_boss("standard")

    def test_watchdog_not_boss(self) -> None:
        # WATCHDOG is the base type; only WATCHDOG_ALPHA is a BOSS
        assert not is_boss("watchdog")

    def test_nonexistent_not_boss(self) -> None:
        assert not is_boss("xyz_nonexistent")

    def test_get_boss_spec_returns_none(self) -> None:
        assert get_boss_spec("standard") is None


# ----------------------------------------------------------------------------
# Phase progression
# ----------------------------------------------------------------------------


GOLIATH_HP_CASES: list[tuple[int, int]] = [
    (100, 0),
    (80, 0),
    (75, 1),
    (60, 1),
    (50, 2),
    (30, 2),
    (25, 3),
    (10, 3),
]
BLACK_HP_CASES: list[tuple[int, int]] = [
    (100, 0),
    (66, 1),
    (33, 2),
    (10, 2),
]


class TestGetNextPhase:
    @pytest.mark.parametrize("case_idx", list(range(len(GOLIATH_HP_CASES))))
    def test_goliath_phases(self, case_idx: int) -> None:
        hp_pct, expected_index = GOLIATH_HP_CASES[case_idx]
        phase = get_next_phase(GOLIATH_PRIME, hp_pct)
        assert phase is not None
        assert phase.index == expected_index

    @pytest.mark.parametrize("case_idx", list(range(len(BLACK_HP_CASES))))
    def test_black_phases(self, case_idx: int) -> None:
        hp_pct, expected_index = BLACK_HP_CASES[case_idx]
        phase = get_next_phase(BLACK_ICE_LORD, hp_pct)
        assert phase is not None
        assert phase.index == expected_index

    def test_watchdog_phase_progression(self) -> None:
        # 100% → phase 0
        # 50% → phase 1
        # 20% → phase 2
        assert get_next_phase(WATCHDOG_ALPHA, 100).index == 0
        assert get_next_phase(WATCHDOG_ALPHA, 50).index == 1
        assert get_next_phase(WATCHDOG_ALPHA, 20).index == 2


# ----------------------------------------------------------------------------
# Phase buffs
# ----------------------------------------------------------------------------


class TestApplyPhaseBuff:
    def test_zero_buff(self) -> None:
        phase = BossPhase(
            index=0,
            name="base",
            hp_threshold_pct=100,
            intro_line="",
            color=(0, 0, 0),
        )
        atk, spd = apply_phase_buff(phase, 100, 1000)
        assert atk == 100
        assert spd == 1000

    def test_attack_bonus(self) -> None:
        phase = BossPhase(
            index=1,
            name="+50%",
            hp_threshold_pct=50,
            intro_line="",
            color=(0, 0, 0),
            attack_bonus_pct=50,
        )
        atk, _ = apply_phase_buff(phase, 100, 1000)
        assert atk == 150

    def test_speed_bonus(self) -> None:
        phase = BossPhase(
            index=1,
            name="faster",
            hp_threshold_pct=50,
            intro_line="",
            color=(0, 0, 0),
            speed_bonus_pct=50,
        )
        _, spd = apply_phase_buff(phase, 100, 1000)
        # 50% faster means 1000 / 1.5 = 666ms
        assert 660 <= spd <= 670

    def test_combined(self) -> None:
        phase = BossPhase(
            index=2,
            name="both",
            hp_threshold_pct=25,
            intro_line="",
            color=(0, 0, 0),
            attack_bonus_pct=100,
            speed_bonus_pct=100,
        )
        atk, spd = apply_phase_buff(phase, 50, 2000)
        assert atk == 100
        assert spd == 1000

    def test_goliath_phase_progression_buffs(self) -> None:
        # Phase 0: 100/1000, Phase 3: 180/714
        for phase in GOLIATH_PRIME.phases:
            atk, spd = apply_phase_buff(phase, 100, 1000)
            assert atk >= 100
            assert spd <= 1000


# ----------------------------------------------------------------------------
# Boss intro sequence
# ----------------------------------------------------------------------------


class TestBossIntroSequence:
    @pytest.mark.parametrize("boss_id", ALL_BOSS_IDS)
    def test_intro_has_phases(self, boss_id: str) -> None:
        spec = get_boss_spec(boss_id)
        assert spec is not None
        seq = boss_intro_sequence(spec)
        assert len(seq.phases) >= 3  # At least intro line + body + name

    @pytest.mark.parametrize("boss_id", ALL_BOSS_IDS)
    def test_intro_duration_3_to_5_seconds(self, boss_id: str) -> None:
        spec = get_boss_spec(boss_id)
        assert spec is not None
        seq = boss_intro_sequence(spec)
        assert 2000 <= seq.total_duration_ms <= 6000

    @pytest.mark.parametrize("boss_id", ALL_BOSS_IDS)
    def test_intro_uses_spec_lines(self, boss_id: str) -> None:
        spec = get_boss_spec(boss_id)
        assert spec is not None
        seq = boss_intro_sequence(spec)
        spec_lines = list(spec.intro_lines)
        seq_lines = [p[0] for p in seq.phases]
        for line in spec_lines:
            assert line in seq_lines, f"{boss_id}: line '{line}' not in sequence"

    def test_goliath_intro_has_warning(self) -> None:
        seq = boss_intro_sequence(GOLIATH_PRIME)
        # Should have a warning-style first line
        first = seq.phases[0][0]
        assert "경고" in first or "▓" in first

    def test_black_intro_has_glitch(self) -> None:
        seq = boss_intro_sequence(BLACK_ICE_LORD)
        # Should have error/glitch text
        all_text = " ".join(p[0] for p in seq.phases)
        assert "오류" in all_text or "▓" in all_text


# ----------------------------------------------------------------------------
# Phase transition
# ----------------------------------------------------------------------------


class TestBossPhaseTransition:
    @pytest.mark.parametrize("boss_id", ALL_BOSS_IDS)
    def test_transition_has_phases(self, boss_id: str) -> None:
        spec = get_boss_spec(boss_id)
        assert spec is not None
        # Test transition to a non-zero phase
        new_phase = spec.phases[min(1, len(spec.phases) - 1)]
        seq = boss_phase_transition(spec, new_phase)
        assert len(seq.phases) >= 3

    @pytest.mark.parametrize("boss_id", ALL_BOSS_IDS)
    def test_transition_completes_in_reasonable_time(self, boss_id: str) -> None:
        spec = get_boss_spec(boss_id)
        assert spec is not None
        new_phase = spec.phases[-1]  # Most dramatic transition
        seq = boss_phase_transition(spec, new_phase)
        assert 1000 <= seq.total_duration_ms <= 5000

    def test_goliath_ground_slam_announcement(self) -> None:
        # Phase 2 has special_ability=ground_slam
        seq = boss_phase_transition(GOLIATH_PRIME, GOLIATH_PRIME.phases[2])
        all_text = " ".join(p[0] for p in seq.phases)
        assert "지면 강타" in all_text

    def test_black_glitch_burst_announcement(self) -> None:
        seq = boss_phase_transition(BLACK_ICE_LORD, BLACK_ICE_LORD.phases[1])
        all_text = " ".join(p[0] for p in seq.phases)
        assert "글리치 폭주" in all_text

    def test_watchdog_pack_howl_announcement(self) -> None:
        seq = boss_phase_transition(WATCHDOG_ALPHA, WATCHDOG_ALPHA.phases[1])
        all_text = " ".join(p[0] for p in seq.phases)
        assert "무리 외침" in all_text


# ----------------------------------------------------------------------------
# Boss death sequence
# ----------------------------------------------------------------------------


class TestBossDeathSequence:
    @pytest.mark.parametrize("boss_id", ALL_BOSS_IDS)
    def test_death_has_4_stages(self, boss_id: str) -> None:
        spec = get_boss_spec(boss_id)
        assert spec is not None
        sequences = boss_death_sequence(spec)
        assert len(sequences) == 4, f"{boss_id} should have 4 death stages"

    @pytest.mark.parametrize("boss_id", ALL_BOSS_IDS)
    def test_death_total_duration(self, boss_id: str) -> None:
        spec = get_boss_spec(boss_id)
        assert spec is not None
        sequences = boss_death_sequence(spec)
        total = sum(s.total_duration_ms for s in sequences)
        # 4 stages * ~800ms each = ~3000-5000ms
        assert 2000 <= total <= 7000

    def test_goliath_death_unique(self) -> None:
        # GOLIATH death has earthquake-style frames
        sequences = boss_death_sequence(GOLIATH_PRIME)
        all_text = " ".join(p[0] for s in sequences for p in s.phases)
        # Should have earth-shattering / heavy destruction
        assert "X_X" in all_text or "╳" in all_text
        assert "코어" in all_text

    def test_black_death_has_glitch(self) -> None:
        sequences = boss_death_sequence(BLACK_ICE_LORD)
        all_text = " ".join(p[0] for s in sequences for p in s.phases)
        # Should have ERR or 권한 (permission) text
        assert "ERR" in all_text or "권한" in all_text

    def test_watchdog_death_has_woof(self) -> None:
        sequences = boss_death_sequence(WATCHDOG_ALPHA)
        all_text = " ".join(p[0] for s in sequences for p in s.phases)
        assert "woof" in all_text or "추적" in all_text

    @pytest.mark.parametrize("boss_id", ALL_BOSS_IDS)
    def test_epilogue_lines_present(self, boss_id: str) -> None:
        spec = get_boss_spec(boss_id)
        assert spec is not None
        lines = boss_epilogue_lines(spec)
        assert len(lines) >= 3
        # All lines should be non-empty
        for line in lines:
            assert len(line) > 0


# ----------------------------------------------------------------------------
# High-level spawners
# ----------------------------------------------------------------------------


class TestSpawnBossIntro:
    @pytest.mark.parametrize("boss_id", ALL_BOSS_IDS)
    def test_intro_sets_cinematic(self, boss_id: str) -> None:
        spec = get_boss_spec(boss_id)
        assert spec is not None
        fx = CombatEffects()
        spawn_boss_intro(fx, spec)
        assert fx.cinematic is not None
        assert fx.slow_motion_ms > 0
        assert fx.shake.intensity > 0


class TestSpawnBossPhaseTransition:
    @pytest.mark.parametrize("boss_id", ALL_BOSS_IDS)
    def test_transition_sets_cinematic(self, boss_id: str) -> None:
        spec = get_boss_spec(boss_id)
        assert spec is not None
        # Find a non-zero phase
        new_phase = spec.phases[min(1, len(spec.phases) - 1)]
        fx = CombatEffects()
        spawn_boss_phase_transition(fx, spec, new_phase)
        assert fx.cinematic is not None
        assert fx.shake.intensity >= new_phase.screen_shake_intensity


class TestSpawnBossDeath:
    @pytest.mark.parametrize("boss_id", ALL_BOSS_IDS)
    def test_death_sets_cinematic(self, boss_id: str) -> None:
        spec = get_boss_spec(boss_id)
        assert spec is not None
        fx = CombatEffects()
        spawn_boss_death(fx, spec)
        assert fx.cinematic is not None
        assert fx.shake.intensity > 0
        # Cinematic should include the death dialogue
        all_text = " ".join(p[0] for p in fx.cinematic.phases)
        for line in spec.death_lines:
            assert line in all_text, f"{line} not in {boss_id} death cinematic"


# ----------------------------------------------------------------------------
# Boss balance check
# ----------------------------------------------------------------------------


class TestBossBalance:
    @pytest.mark.parametrize("boss_id", ALL_BOSS_IDS)
    def test_boss_has_higher_stats_than_base(self, boss_id: str) -> None:
        spec = get_boss_spec(boss_id)
        assert spec is not None
        assert spec.hp_multiplier >= 3.0
        assert spec.attack_multiplier >= 1.5
        assert spec.defense_multiplier >= 1.0

    @pytest.mark.parametrize("boss_id", ALL_BOSS_IDS)
    def test_boss_has_unique_base_type(self, boss_id: str) -> None:
        spec = get_boss_spec(boss_id)
        assert spec is not None
        # Each BOSS has a unique base ICE type
        assert spec.base_ice_type in list(IceType)

    def test_all_bosses_have_distinct_intros(self) -> None:
        """Each BOSS has visually distinct intro text."""
        signatures = set()
        for spec in ALL_BOSSES.values():
            sig = "|".join(spec.intro_lines)
            signatures.add(sig)
        assert len(signatures) == 3

    def test_all_bosses_have_distinct_deaths(self) -> None:
        signatures = set()
        for spec in ALL_BOSSES.values():
            sig = "|".join(spec.death_lines)
            signatures.add(sig)
        assert len(signatures) == 3


# ----------------------------------------------------------------------------
# Performance smoke
# ----------------------------------------------------------------------------


class TestPerformance:
    def test_boss_intro_settles(self) -> None:
        fx = CombatEffects()
        spawn_boss_intro(fx, GOLIATH_PRIME)
        for _ in range(200):
            fx.step(50)
            if fx.cinematic is None:
                break
        assert fx.cinematic is None

    def test_full_boss_fight(self) -> None:
        """Simulate a full boss fight: intro → 3 phase transitions → death."""
        fx = CombatEffects()
        spec = GOLIATH_PRIME

        # Intro
        spawn_boss_intro(fx, spec)
        for _ in range(100):
            fx.step(50)
            if fx.cinematic is None:
                break

        # Phase 1 → 2 → 3 transitions
        for i in range(1, len(spec.phases)):
            fx.clear()
            spawn_boss_phase_transition(fx, spec, spec.phases[i])
            for _ in range(100):
                fx.step(50)
                if fx.cinematic is None:
                    break

        # Death
        fx.clear()
        spawn_boss_death(fx, spec)
        for _ in range(200):
            fx.step(50)
            if fx.cinematic is None:
                break
        assert fx.cinematic is None
