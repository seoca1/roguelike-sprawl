"""Run State system — see state.py for the data model.

Public API:
    Stage, ObjectiveKind, StageInfo
    RunState
    DEFAULT_FLOW
    get_stage_info(stage)
    start_run(initial_stage)
    ensure_run_state, start_new_run (helpers)
    resolve_target_for_stage, check_objective_at_node (matrix helpers)
    check_combat_victory, check_extract_complete, check_npc_talk_complete
"""

from __future__ import annotations

from .helpers import (
    check_combat_victory,
    check_extract_complete,
    check_npc_talk_complete,
    check_objective_at_node,
    ensure_run_state,
    resolve_target_for_stage,
    start_new_run,
)
from .state import (
    DEFAULT_FLOW,
    ObjectiveKind,
    RunState,
    Stage,
    StageInfo,
    get_stage_info,
    start_run,
)

__all__ = [
    "DEFAULT_FLOW",
    "ObjectiveKind",
    "RunState",
    "Stage",
    "StageInfo",
    "check_combat_victory",
    "check_extract_complete",
    "check_npc_talk_complete",
    "check_objective_at_node",
    "ensure_run_state",
    "get_stage_info",
    "resolve_target_for_stage",
    "start_new_run",
    "start_run",
]

