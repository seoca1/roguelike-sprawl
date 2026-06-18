"""Jockey avatar state models.

Pure data structures for avatar rendering.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum


class Status(Enum):
    """Combat status based on PPL/ZDR ratio.

    Determines avatar body pose (Pillar 3 visualization).
    """

    SAFE = "safe"          # PPL >> ZDR
    MATCH = "match"        # PPL ~= ZDR
    TOUGH = "tough"        # PPL slightly < ZDR
    DEADLY = "deadly"      # PPL << ZDR
    FUTILE = "futile"      # Nearly dead


class ConstructKind(Enum):
    """Construct companion types (echoes)."""

    DIXIE = "D"
    LOA = "L"
    THREE_JANE = "J"


@dataclass(frozen=True, slots=True)
class ProgramSlot:
    """One program slot on the avatar's arm.

    Frozen so it can be used as dict key.
    """

    id: str           # e.g. "wisp", "hammer"
    tier: int         # 1-5
    depleted: bool    # True = used (one-shot)


@dataclass(frozen=True, slots=True)
class AvatarState:
    """Player state for avatar rendering.

    Immutable snapshot; render_avatar() takes this and produces
    a static ASCII picture.
    """

    hp: int
    max_hp: int
    status: Status
    programs: tuple[ProgramSlot, ...]
    deck_tier: int                # 0-5
    wetware_tier: int             # 0-5
    construct: ConstructKind | None = None
    glitching: bool = False       # True = random flicker

    @property
    def hp_pct(self) -> float:
        """HP as 0.0-1.0."""
        if self.max_hp <= 0:
            return 0.0
        return max(0.0, min(1.0, self.hp / self.max_hp))

    @property
    def is_dead(self) -> bool:
        """True at 0% HP (flatline)."""
        return self.hp <= 0


@dataclass(slots=True)
class AvatarLines:
    """Rendered avatar as a list of (text, color) tuples.

    Each tuple is one rendered line (without trailing newline).
    Color is an (r, g, b) tuple.
    """

    lines: list[tuple[str, tuple[int, int, int]]] = field(default_factory=list)
    width: int = 0

    def __iter__(self) -> Iterator[tuple[str, tuple[int, int, int]]]:
        return iter(self.lines)

    def __len__(self) -> int:
        return len(self.lines)
