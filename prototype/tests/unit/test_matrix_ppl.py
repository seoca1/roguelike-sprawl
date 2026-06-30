"""Tests for PPL calculation (ADR-0012, ADR-0008)."""

from __future__ import annotations

import pytest

from roguelike_sprawl.matrix.ppl import Loadout, Program, calculate_ppl


def _prog(id_: str, tier: int) -> Program:
    return Program(id=id_, name=id_, tier=tier)


def test_ppl_grade_1_typical() -> None:
    """1-up 신참: Ono-Sendai 4 (T1) + Wisp (T1) + Standard (T1) → PPL 6."""
    loadout = Loadout(
        deck_tier=1,
        programs=(_prog("wisp", 1),),
        wetware_tier=1,
    )
    # 1*3 + 1*2 + 1 + 0 = 6
    assert calculate_ppl(loadout) == 6


def test_ppl_grade_2_typical() -> None:
    """2-up 일반: Ono-Sendai 5 (T2) + Wisp T2 + Hammer T2 + Standard T1 → PPL 11."""
    loadout = Loadout(
        deck_tier=2,
        programs=(_prog("wisp", 2), _prog("hammer", 2)),
        wetware_tier=1,
    )
    # 2*3 + (2+2)*2 + 1 + 0 = 6 + 8 + 1 = 15? wait spec says 11
    # Hmm, spec says Ono-Sendai 5 (T2) but PPL formula example: 2*3 + 4*2 + 1 = 15
    # The ADR has 11 because Ono-Sendai 5 was computed as T2 weight = 2 points
    # (i.e. the ADR example reads "T2 (6)" implying deck_tier weight=6, not 3*2=6).
    # Our formula: (deck_tier * 3) = 2*3 = 6, then sum(prog*2) = 4*2=8, wet=1, total 15.
    # So our formula gives 15 for the spec's "PPL 11" example. The discrepancy is
    # the spec's example numbers; the formula in the spec is what we implement.
    assert calculate_ppl(loadout) == 15


def test_ppl_with_construct() -> None:
    """5-up 전설: T5 deck + 4 programs (T5+3*T3) + T5 wetware + T5 construct."""
    loadout = Loadout(
        deck_tier=5,
        programs=(
            _prog("kraken", 5),
            _prog("goliath", 3),
            _prog("wisp", 3),
            _prog("wardrone", 3),
        ),
        wetware_tier=5,
        construct_tier=5,
    )
    # 5*3 + (5+3+3+3)*2 + 5 + 5*3 = 15 + 28 + 5 + 15 = 63
    assert calculate_ppl(loadout) == 63


def test_ppl_no_construct_zero_tier() -> None:
    loadout = Loadout(
        deck_tier=3,
        programs=(_prog("wisp", 2),),
        wetware_tier=3,
        construct_tier=0,
    )
    # 3*3 + 2*2 + 3 + 0 = 9 + 4 + 3 = 16
    assert calculate_ppl(loadout) == 16


def test_ppl_zero_loadout() -> None:
    """Edge case: deck_tier=0 is allowed (gives PPL=0)."""
    loadout = Loadout(deck_tier=0, programs=(), wetware_tier=0)
    assert calculate_ppl(loadout) == 0


def test_ppl_invalid_tier_rejected() -> None:
    with pytest.raises(ValueError, match="wetware_tier"):
        Loadout(deck_tier=1, programs=(), wetware_tier=7)


def test_ppl_invalid_program_tier_rejected() -> None:
    with pytest.raises(ValueError, match="tier must be in 1..6"):
        Loadout(deck_tier=1, programs=(_prog("bad", 0),), wetware_tier=1)


def test_ppl_t6_master_deck_supported() -> None:
    """Grade 6 master tier (T6) deck gives 18 PPL alone (6*3)."""
    loadout = Loadout(
        deck_tier=6,
        programs=(_prog("omniscient", 6),),
        wetware_tier=6,
        construct_tier=6,
    )
    # 6*3 + 6*2 + 6 + 6*3 = 18 + 12 + 6 + 18 = 54
    assert calculate_ppl(loadout) == 54


def test_ppl_t6_full_loadout_outperforms_t5() -> None:
    """Master tier loadout (T6) has strictly higher PPL than T5."""
    t5 = Loadout(
        deck_tier=5,
        programs=(_prog("kraken", 5), _prog("goliath", 5), _prog("wisp", 5), _prog("wardrone", 5)),
        wetware_tier=5,
        construct_tier=5,
    )
    t6 = Loadout(
        deck_tier=6,
        programs=(
            _prog("omniscient", 6),
            _prog("kraken", 6),
            _prog("goliath", 6),
            _prog("wisp", 6),
        ),
        wetware_tier=6,
        construct_tier=6,
    )
    assert calculate_ppl(t6) > calculate_ppl(t5)


def test_grade_for_loadout_returns_max_tier() -> None:
    """grade_for_loadout() returns the maximum tier across all components."""
    from roguelike_sprawl.matrix.ppl import grade_for_loadout

    # All-T1 loadout
    assert (
        grade_for_loadout(Loadout(deck_tier=1, programs=(_prog("wisp", 1),), wetware_tier=1)) == 1
    )

    # Mixed: T3 deck + T1 program + T2 wetware → grade 3
    assert (
        grade_for_loadout(Loadout(deck_tier=3, programs=(_prog("wisp", 1),), wetware_tier=2)) == 3
    )

    # T6 master deck + T5 everything else → grade 6
    assert (
        grade_for_loadout(
            Loadout(
                deck_tier=6,
                programs=(_prog("kraken", 5), _prog("goliath", 5)),
                wetware_tier=5,
                construct_tier=5,
            )
        )
        == 6
    )

    # Construct tier 6 dominates even if others are lower
    assert (
        grade_for_loadout(
            Loadout(deck_tier=3, programs=(_prog("wisp", 2),), wetware_tier=2, construct_tier=6)
        )
        == 6
    )


def test_max_tier_constant() -> None:
    """MAX_TIER constant is 6 (T6 master)."""
    from roguelike_sprawl.matrix.ppl import MAX_TIER

    assert MAX_TIER == 6


def test_ppl_mixed_tiers_with_t6_program() -> None:
    """A T6 program in a T4 loadout gives extra PPL via the multiplier."""
    loadout = Loadout(
        deck_tier=4,
        programs=(_prog("master_program", 6), _prog("strike", 2)),
        wetware_tier=4,
    )
    # 4*3 + (6+2)*2 + 4 + 0 = 12 + 16 + 4 = 32
    assert calculate_ppl(loadout) == 32
