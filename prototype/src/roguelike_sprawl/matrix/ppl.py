"""Player Power Level (PPL) and Loadout (ADR-0012, ADR-0008).

A `Loadout` is the immutable equipment snapshot of a jockey at the start
of a run. PPL is derived from the loadout.

Tiers:
  T1..T5 — normal jockeys (Grade 1..5)
  T6     — master tier for Arc 5 finale missions (Grade 6),
            reserved for neuromancer_merger and zion_express
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Program:
    """A program in the loadout. Tier is the item tier (ADR-0008)."""

    id: str
    name: str
    tier: int


@dataclass(frozen=True, slots=True)
class Loadout:
    """The starting equipment of a jockey (ADR-0008, ADR-0012).

    Tier values 0-6:
      - 0 = absent (e.g. no construct)
      - 1..5 = normal T1..T5 gear
      - 6 = master tier (T6), only available via Grade 6 master jockey
    """

    deck_tier: int
    programs: tuple[Program, ...]
    wetware_tier: int
    construct_tier: int = 0

    def __post_init__(self) -> None:
        for name, tier in (
            ("deck_tier", self.deck_tier),
            ("wetware_tier", self.wetware_tier),
            ("construct_tier", self.construct_tier),
        ):
            if not 0 <= tier <= 6:
                raise ValueError(f"{name} must be in 0..6, got {tier}")
        for p in self.programs:
            if not 1 <= p.tier <= 6:
                raise ValueError(f"program {p.id!r} tier must be in 1..6, got {p.tier}")


# Maximum tier supported across the system. Use this constant to
# guard future tier additions (e.g. T7+) without code-wide search.
MAX_TIER = 6


def calculate_ppl(loadout: Loadout) -> int:
    """Compute PPL for a loadout (ADR-0012).

    Formula: (deck * 3) + sum(prog * 2) + wetware + (construct * 3).

    For T6 master gear the same formula applies — T6 simply produces
    higher PPL naturally via the multiplier (e.g. T6 deck → 18 PPL).
    """
    ppl = loadout.deck_tier * 3
    ppl += sum(p.tier for p in loadout.programs) * 2
    ppl += loadout.wetware_tier
    if loadout.construct_tier > 0:
        ppl += loadout.construct_tier * 3
    return ppl


def grade_for_loadout(loadout: Loadout) -> int:
    """Derive the player's grade from the highest tier in the loadout.

    The grade is the maximum tier across all components (deck, programs,
    wetware, construct). For mixed-tier loadouts, this rounds up so the
    player faces the hardest challenge their gear enables.

    Returns:
        1..6 (inclusive).
    """
    tiers = [loadout.deck_tier, loadout.wetware_tier]
    if loadout.construct_tier > 0:
        tiers.append(loadout.construct_tier)
    tiers.extend(p.tier for p in loadout.programs)
    return max(tiers) if tiers else 1
