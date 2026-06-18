"""Player Power Level (PPL) and Loadout (ADR-0012, ADR-0008).

A `Loadout` is the immutable equipment snapshot of a jockey at the start
of a run. PPL is derived from the loadout.
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

    All tier values are 1-5 (T1..T5). A tier of 0 means "absent"
    (e.g. no construct).
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
            if not 0 <= tier <= 5:
                raise ValueError(f"{name} must be in 0..5, got {tier}")
        for p in self.programs:
            if not 1 <= p.tier <= 5:
                raise ValueError(f"program {p.id!r} tier must be in 1..5, got {p.tier}")


def calculate_ppl(loadout: Loadout) -> int:
    """Compute PPL for a loadout (ADR-0012).

    Formula: (deck * 3) + sum(prog * 2) + wetware + (construct * 3).
    """
    ppl = loadout.deck_tier * 3
    ppl += sum(p.tier for p in loadout.programs) * 2
    ppl += loadout.wetware_tier
    if loadout.construct_tier > 0:
        ppl += loadout.construct_tier * 3
    return ppl
