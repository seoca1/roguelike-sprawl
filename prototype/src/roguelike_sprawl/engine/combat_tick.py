"""Combat tick orchestration helpers.

Phase D-1: extracted from app.py to reduce main dispatcher size.
Phase H: wires B-3 boss enhancements (spawn_phase_minions + apply_phase_aoe)
into the main loop so phase transitions actually trigger adds and AoE.
"""
from __future__ import annotations

from ..combat import boss as _boss
from ..combat import effects as _effects
from ..combat.registry import IceRegistry, ProgramRegistry
from . import combat_view
from .state import AppState


def maybe_boss_phase_transition(
    state: AppState,
    ice_registry: IceRegistry | None = None,
    program_registry: ProgramRegistry | None = None,
    portraits=None,
) -> None:
    """Check and apply boss phase transitions after each combat tick.

    Phase H: when a phase change is detected, additionally:
      1. Spawn phase.spawn_minions ICE as adds
      2. Apply phase.aoe_damage to the player (AoE burst)

    Optional registries default to None for backward compat (skip spawn);
    production callers in app.py pass them in.
    """
    cs = state.combat_state
    if cs is None or cs.boss_profile is None or cs.finished:
        return
    new_phase = _boss.phase_transition(cs.enemy, cs.boss_profile)
    if new_phase is not None:
        _boss.apply_phase_to_combatant(cs.enemy, cs.boss_profile)
        cs.push(f">>> {new_phase.intro_text}")
        # Phase H: B-3 spawn_minions — adds on phase change
        if new_phase.spawn_minions and ice_registry is not None:
            spawned = _boss.spawn_phase_minions(
                cs.enemy, new_phase, cs, ice_registry, program_registry, portraits
            )
            if spawned:
                cs.push(
                    f">>> {new_phase.name} summons "
                    f"{len(spawned)} minion(s)!"
                )
        # Phase H: B-3 aoe_damage — AoE burst on phase change
        if new_phase.aoe_damage > 0:
            _boss.apply_phase_aoe(new_phase, cs)
        try:
            ice_type = _effects.IceType(cs.enemy.id)
        except ValueError:
            ice_type = _effects.IceType.BLACK
        combat_view.spawn_phase_transition(state.combat_effects, new_phase, ice_type)
