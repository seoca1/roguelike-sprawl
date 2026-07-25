"""Combat tick orchestration helpers.

Phase D-1: extracted from app.py to reduce main dispatcher size.
Boss phase transitions, damage tick orchestration, and ICE skill use
live here so app.py stays focused on the screen state machine.
"""
from __future__ import annotations

from ..combat import boss as _boss
from ..combat import effects as _effects
from . import combat_view
from .state import AppState


def maybe_boss_phase_transition(state: AppState) -> None:
    """Check and apply boss phase transitions after each combat tick."""
    cs = state.combat_state
    if cs is None or cs.boss_profile is None or cs.finished:
        return
    new_phase = _boss.phase_transition(cs.enemy, cs.boss_profile)
    if new_phase is not None:
        _boss.apply_phase_to_combatant(cs.enemy, cs.boss_profile)
        cs.push(f">>> {new_phase.intro_text}")
        try:
            ice_type = _effects.IceType(cs.enemy.id)
        except ValueError:
            ice_type = _effects.IceType.BLACK
        combat_view.spawn_phase_transition(state.combat_effects, new_phase, ice_type)
