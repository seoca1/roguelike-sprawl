"""Construct Whisper combat integration hook (ADR-0140 §Proposal 1).

Called on combat start to deliver faction-aware hints based on
the player's reputation. Hints are added to status_messages.
"""

from __future__ import annotations

from typing import Any

from ..matrix.node import Faction
from .construct_whisper import (
    get_hint_for_faction,
)


def check_construct_whisper_on_combat_start(state: Any) -> list[str]:
    """Deliver eligible faction whispers on combat start.

    Iterates eligible factions (rep >= TRUSTED, not yet whispered
    this run), records the whisper, and appends hint text to
    state.status_messages.

    Args:
        state: AppState-like object with reputation, construct_whisper_tracker,
            and status_messages attributes.

    Returns:
        List of hint strings that were appended.
    """
    reputation = getattr(state, "reputation", None)
    tracker = getattr(state, "construct_whisper_tracker", None)
    if reputation is None or tracker is None:
        return []

    eligible = tracker.find_eligible_factions(reputation)
    delivered: list[str] = []
    status_list = getattr(state, "status_messages", None)

    for faction, tier in eligible:
        hint = get_hint_for_faction(faction, tier)
        if hint is None:
            continue
        if not tracker.record_whisper(faction):
            continue
        msg = f">>> [{faction.value.upper()} construct whispers] {hint}"
        if isinstance(status_list, list):
            status_list.append(msg)
        delivered.append(msg)

    return delivered


__all__ = ["check_construct_whisper_on_combat_start"]


# Import Faction for callers that re-export
_ = Faction
