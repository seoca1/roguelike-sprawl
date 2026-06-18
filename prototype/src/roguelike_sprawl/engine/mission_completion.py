"""Mission completion system (ADR-0017).

When a player satisfies a mission's primary objective (e.g. extracted
data, defeated ICE), the mission is marked complete:
1. Reward credits and materials are added to state.
2. Mission is added to ``completed_missions`` set.
3. Current mission is cleared.
4. The next mission (if any) for the player's grade becomes available.

This is the game's primary progression loop: do mission → get reward →
unlock next mission → repeat.
"""

from __future__ import annotations

from .state import AppState


def check_mission_completion(state: AppState) -> bool:
    """Check if the current mission is complete based on player progress.

    Returns:
        True if mission was completed (and rewards were awarded).
    """
    if state.current_mission is None:
        return False

    if not state.current_mission.check_completion(state.mission_progress):
        return False

    # Already completed (shouldn't happen, but safety)
    if state.current_mission.id in state.completed_missions:
        return False

    complete_mission(state, state.current_mission)
    return True


def complete_mission(state: AppState, mission: object) -> None:
    """Award rewards and mark mission as complete.

    Args:
        state: App state.
        mission: The Mission to complete.
    """
    # Import here to avoid circular import
    from ..missions.mission import Mission

    if not isinstance(mission, Mission):
        return

    # Award credits
    credits_amount = mission.reward_credits
    if credits_amount > 0:
        state.credits += credits_amount
        state.status_messages.append(f">>> +{credits_amount} credits")
        state.status_messages.append(f"   Total: {state.credits} credits")

    # Award materials
    rewards = mission.rewards
    if rewards is not None:
        for mat_id, count in rewards.materials.items():
            if not hasattr(state, "inventory") or state.inventory is None:
                state.inventory = {}
            state.inventory[mat_id] = state.inventory.get(mat_id, 0) + count
            state.status_messages.append(f">>> +{count}x {mat_id}")

    # Mark complete
    state.completed_missions.add(mission.id)
    state.current_mission = None

    # Reset progress for next mission
    state.mission_progress = {}

    # Show completion message
    state.status_messages.append(f">>> MISSION COMPLETE: {mission.title}")
    state.status_messages.append(">>> Return to hub for next job")


def update_mission_progress(
    state: AppState,
    objective_type: str,
    count: int = 1,
) -> bool:
    """Increment progress toward current mission's primary objective.

    Args:
        state: App state.
        objective_type: The objective type to progress (e.g. "extract_data", "defeat").
        count: How much to increment by.

    Returns:
        True if mission was completed as a result.
    """
    if state.current_mission is None:
        return False

    if state.current_mission.primary_objective is None:
        return False

    if state.current_mission.primary_objective.type != objective_type:
        # Not the primary objective; ignore
        return False

    state.mission_progress[objective_type] = (
        state.mission_progress.get(objective_type, 0) + count
    )

    state.status_messages.append(
        f">>> Progress: {objective_type} {state.mission_progress[objective_type]}"
        f"/{state.current_mission.primary_objective.count}"
    )

    # Check if this completes the mission
    return check_mission_completion(state)


def get_next_available_mission(state: AppState) -> object | None:
    """Get the next available mission for the player's grade.

    Skips completed missions. Returns None if all available missions
    are done.
    """
    if not hasattr(state, "job_board") or state.job_board is None:
        return None

    available = state.job_board.available_for(state.player_grade)
    for mission in available:
        if mission.id not in state.completed_missions:
            return mission
    return None


def get_mission_summary(state: AppState) -> str:
    """Get a one-line summary of current mission status.

    Returns:
        String like "First Jack — extract_data 1/1 (75%)" or "No mission".
    """
    if state.current_mission is None:
        return "No active mission"

    m = state.current_mission
    pct = int(m.progress_pct(state.mission_progress) * 100)
    if m.primary_objective is not None:
        current = state.mission_progress.get(m.primary_objective.type, 0)
        required = m.primary_objective.count
        return f"{m.title} — {m.primary_objective.type} {current}/{required} ({pct}%)"
    return f"{m.title} — (no objective)"
