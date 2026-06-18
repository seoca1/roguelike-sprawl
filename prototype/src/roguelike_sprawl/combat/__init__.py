"""Combat subsystem (ADR-0003, ADR-0014, ADR-0018, ADR-0019).

Phase 5: text-based combat model + simulator (developer/QA tool).
Phase 6+: full integration with the engine (animations, salvage, aftermath).
"""

from .registry import (
    IceRegistry,
    ProgramRegistry,
    build_default_player,
    build_ice_enemy,
)
from .state import Combatant, CombatState, Skill, step_combat, use_skill

__all__ = [
    "Combatant",
    "CombatState",
    "IceRegistry",
    "ProgramRegistry",
    "Skill",
    "build_default_player",
    "build_ice_enemy",
    "step_combat",
    "use_skill",
]
