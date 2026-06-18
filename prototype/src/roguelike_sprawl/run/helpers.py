"""Helpers for integrating RunState with AppState.

These functions handle the boilerplate of:
- Lazy-initializing ``state.run_state`` if it's None
- Finding the next target node in the matrix for the active stage
- Detecting when a player's action satisfies the current stage's objective
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..matrix.node import NodeKind
from .state import ObjectiveKind, RunState, Stage, start_run

if TYPE_CHECKING:
    from ..engine.state import AppState
    from ..matrix.graph import MatrixGraph


# --- Run lifecycle ---


def ensure_run_state(state: AppState) -> RunState:
    """Get state.run_state, creating it if missing."""
    if state.run_state is None:
        state.run_state = start_run()
    return state.run_state


def start_new_run(state: AppState, initial_stage: Stage = Stage.MEET_NPC) -> RunState:
    """Reset run state to start a new run at the given stage."""
    state.run_state = start_run(initial_stage)
    return state.run_state


# --- Target resolution ---


def resolve_target_for_stage(
    run_state: RunState,
    matrix: MatrixGraph | None,
) -> str | None:
    """Find the matrix node id that satisfies the current stage.

    For each objective kind, scans the matrix for the first matching node:
      - NPC → CONSTRUCT node
      - DATA → DATA node
      - ICE → ICE node
      - NONE → None (no target)

    Returns None if no matching node exists.
    """
    if matrix is None or not matrix.nodes:
        return None

    kind = run_state.objective_kind()
    target_kind: NodeKind | None = None
    if kind is ObjectiveKind.NPC:
        target_kind = NodeKind.CONSTRUCT
    elif kind is ObjectiveKind.DATA:
        target_kind = NodeKind.DATA
    elif kind is ObjectiveKind.ICE:
        target_kind = NodeKind.ICE
    else:
        return None

    for node in matrix.nodes:
        if node.kind is target_kind:
            return node.id
    return None


# --- Objective detection ---


def check_objective_at_node(
    run_state: RunState,
    node_id: str,
    matrix: MatrixGraph | None,
) -> bool:
    """Check if the player being at a given node satisfies the current stage.

    Returns True if the stage is now complete (call mark_advance next).
    """
    if matrix is None or not run_state.is_in_progress():
        return False

    node = matrix.get(node_id)
    if node is None:
        return False

    kind = run_state.objective_kind()
    if kind is ObjectiveKind.NPC and node.kind is NodeKind.CONSTRUCT:
        return True
    if kind is ObjectiveKind.DATA and node.kind is NodeKind.DATA:
        return True
    if kind is ObjectiveKind.ICE and node.kind is NodeKind.ICE:
        return True
    return False


def check_combat_victory(run_state: RunState) -> bool:
    """Check if a combat victory satisfied the current stage.

    Used by the combat_view after a victory: if the stage was DEFEAT_ICE
    and the player won, the stage is complete.
    """
    return run_state.is_in_progress() and run_state.objective_kind() is ObjectiveKind.ICE


def check_extract_complete(run_state: RunState) -> bool:
    """Check if a data extraction satisfied the current stage."""
    return run_state.is_in_progress() and run_state.objective_kind() is ObjectiveKind.DATA


def check_npc_talk_complete(run_state: RunState) -> bool:
    """Check if talking to the NPC satisfied the current stage."""
    return run_state.is_in_progress() and run_state.objective_kind() is ObjectiveKind.NPC
