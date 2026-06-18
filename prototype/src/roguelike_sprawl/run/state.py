"""Run State system — manages a single playthrough's stage progression.

A "Run" is one complete playthrough: from accepting a mission at the
Hub to completing it (or flatlining). Each Run is divided into Stages,
which are concrete objectives the player must satisfy in order.

This module is the source of truth for "what should the player be doing
right now?" — the matrix screen, demo loop, and status panel all read
from it instead of tracking ad-hoc flags.

Stage Flow (Pillar 6: Stage Flow):

    ┌─────────┐
    │ PENDING │  (Hub: Accept mission)
    └────┬────┘
         ↓
    ┌──────────┐
    │ MEET_NPC │  (Matrix: Talk to construct)
    └────┬─────┘
         ↓
    ┌─────────────┐
    │ EXTRACT_DATA│  (Matrix: Extract data — optional per mission)
    └────┬────────┘
         ↓
    ┌──────────┐
    │ DEFEAT_ICE│  (Matrix: Win combat)
    └────┬──────┘
         ↓
    ┌─────────┐
    │ JACK_OUT│  (Animation: Disconnect from matrix)
    └────┬────┘
         ↓
    ┌─────────┐
    │ REWARD  │  (Hub: Show rewards)
    └────┬────┘
         ↓
    ┌──────────┐
    │ COMPLETE │  (Run done)
    └──────────┘

On any failure (combat defeat, etc.):
         ↓
    ┌──────────────┐
    │ FAILED      │  (Death screen)
    └────┬─────────┘
         ↓
    ┌────────────────┐
    │ DEATH_RESTART  │  (Hub: Restart option)
    └────┬───────────┘
         ↓
    (back to PENDING for new run)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Stage(StrEnum):
    """Ordered stages of a single Run.

    Default first_jack mission flow:
      PENDING → MEET_NPC → EXTRACT_DATA → DEFEAT_ICE → JACK_OUT → REWARD → COMPLETE
    """

    PENDING = "pending"  # Run not started (Hub: waiting for mission accept)
    MEET_NPC = "meet_npc"  # Find and talk to a construct NPC
    EXTRACT_DATA = "extract_data"  # Find data node, extract payload
    DEFEAT_ICE = "defeat_ice"  # Find ICE node, win combat
    JACK_OUT = "jack_out"  # Disconnect from matrix (animation)
    REWARD = "reward"  # Show mission rewards
    DEBRIEF = "debrief"  # Optional narrative between COMPLETE and Hub
    COMPLETE = "complete"  # Run finished, return to hub
    DEATH_RESTART = "death_restart"  # After death, show restart option
    FAILED = "failed"  # Player flatlined


class ObjectiveKind(StrEnum):
    """What kind of in-game action satisfies a Stage.

    Used to find the right node in the matrix and detect completion.
    """

    NPC = "npc"  # Node with kind=CONSTRUCT (talk to)
    DATA = "data"  # Node with kind=DATA (extract from)
    ICE = "ice"  # Node with kind=ICE (combat)
    NONE = "none"  # No specific target (e.g. PENDING, JACK_OUT, REWARD)


# --- Stage metadata ---


@dataclass(frozen=True, slots=True)
class StageInfo:
    """Static description of a stage.

    Attributes:
        stage: The Stage enum value.
        title: Short, human-readable title.
        objective_kind: What kind of action satisfies this stage.
        hint: Player-facing hint for the current stage.
        next_stage: The stage that follows this one in the mission flow.
        on_enter: Optional callback when entering this stage.
        on_exit: Optional callback when leaving this stage.
        ascii_art: Optional ASCII art displayed in the stage view.
    """

    stage: Stage
    title: str
    objective_kind: ObjectiveKind
    hint: str
    next_stage: Stage | None = None
    on_enter: str | None = None
    on_exit: str | None = None
    ascii_art: tuple[str, ...] = field(default_factory=tuple)


# --- Default mission flow (First Jack) ---


DEFAULT_FLOW: dict[Stage, StageInfo] = {
    Stage.PENDING: StageInfo(
        stage=Stage.PENDING,
        title="Awaiting Jack-In",
        objective_kind=ObjectiveKind.NONE,
        hint="Accept a mission at the Hub to begin.",
        next_stage=Stage.MEET_NPC,
    ),
    Stage.MEET_NPC: StageInfo(
        stage=Stage.MEET_NPC,
        title="Meet the Construct",
        objective_kind=ObjectiveKind.NPC,
        hint="Find and talk to the construct (Dixie Flatline).",
        next_stage=Stage.EXTRACT_DATA,
        on_enter="Dixie's voice crackles: 'Hey cowboy. Ready?'",
    ),
    Stage.EXTRACT_DATA: StageInfo(
        stage=Stage.EXTRACT_DATA,
        title="Extract the Data",
        objective_kind=ObjectiveKind.DATA,
        hint="Locate the data node and extract the payload.",
        next_stage=Stage.DEFEAT_ICE,
        on_enter="Data fragment detected. Locking on...",
    ),
    Stage.DEFEAT_ICE: StageInfo(
        stage=Stage.DEFEAT_ICE,
        title="Defeat the ICE",
        objective_kind=ObjectiveKind.ICE,
        hint="Engage and defeat the ICE protecting the data.",
        next_stage=Stage.JACK_OUT,
        on_enter="⚠ ICE detected. Combat initiated.",
    ),
    Stage.JACK_OUT: StageInfo(
        stage=Stage.JACK_OUT,
        title="Jack Out",
        objective_kind=ObjectiveKind.NONE,
        hint="Disconnecting from the matrix...",
        next_stage=Stage.REWARD,
        ascii_art=(
            "  ░░░░░░░░░░░░░░░░░░░░░░░░░░",
            "  ░  ◢◣◢◣◢◣◢◣◢◣◢◣◢◣  ░",
            "  ░  ── JACKING OUT ──     ░",
            "  ░  ░▒▓█             ▓▒░  ░",
            "  ░  ░▒▓█             ▓▒░  ░",
            "  ░░░░░░░░░░░░░░░░░░░░░░░░░░",
        ),
    ),
    Stage.REWARD: StageInfo(
        stage=Stage.REWARD,
        title="Mission Rewards",
        objective_kind=ObjectiveKind.NONE,
        hint="Collect your rewards.",
        next_stage=Stage.COMPLETE,
        ascii_art=(
            "  ┌──────────────────────┐",
            "  │  ✓ MISSION COMPLETE  │",
            "  │  ◢◣◢◣◢◣◢◣◢◣◢◣◢◣◢◣◢◣  │",
            "  │  ░▒▓ Credits  +500  ▓▒░  │",
            "  │  ░▒▓ Materials +2   ▓▒░  │",
            "  │  ░▒▓ Press ENTER    ▓▒░  │",
            "  └──────────────────────┘",
        ),
    ),
    Stage.DEBRIEF: StageInfo(
        stage=Stage.DEBRIEF,
        title="Debrief",
        objective_kind=ObjectiveKind.NONE,
        hint="Mission summary and intel unlocked.",
        next_stage=Stage.COMPLETE,
    ),
    Stage.COMPLETE: StageInfo(
        stage=Stage.COMPLETE,
        title="Run Complete",
        objective_kind=ObjectiveKind.NONE,
        hint="Mission complete. Return to hub for next job.",
        next_stage=None,
    ),
    Stage.DEATH_RESTART: StageInfo(
        stage=Stage.DEATH_RESTART,
        title="Restart",
        objective_kind=ObjectiveKind.NONE,
        hint="Press ENTER to restart, ESC to quit to menu.",
        next_stage=Stage.PENDING,
    ),
    Stage.FAILED: StageInfo(
        stage=Stage.FAILED,
        title="Flatline",
        objective_kind=ObjectiveKind.NONE,
        hint="Your run ended in cyberspace.",
        next_stage=Stage.DEATH_RESTART,
    ),
}


def get_stage_info(stage: Stage) -> StageInfo:
    """Return the StageInfo for a given Stage."""
    return DEFAULT_FLOW.get(stage, StageInfo(stage=stage, title=stage.value.title(),
                                              objective_kind=ObjectiveKind.NONE, hint=""))


# --- Per-mission stage flows ---


# Type alias for stage flow sequence
StageSequence = tuple[StageInfo, ...]


# Each mission has its own stage sequence.
# Watchdog Patrol skips EXTRACT_DATA (no data to extract).
# Ice Run has same flow as First Jack but different ICE count.
MISSION_FLOWS: dict[str, StageSequence] = {
    "first_jack": (
        DEFAULT_FLOW[Stage.MEET_NPC],
        DEFAULT_FLOW[Stage.EXTRACT_DATA],
        DEFAULT_FLOW[Stage.DEFEAT_ICE],
        DEFAULT_FLOW[Stage.JACK_OUT],
        DEFAULT_FLOW[Stage.REWARD],
        DEFAULT_FLOW[Stage.COMPLETE],
    ),
    "watchdog_patrol": (
        DEFAULT_FLOW[Stage.MEET_NPC],
        # No EXTRACT_DATA — pure combat mission
        DEFAULT_FLOW[Stage.DEFEAT_ICE],
        DEFAULT_FLOW[Stage.JACK_OUT],
        DEFAULT_FLOW[Stage.REWARD],
        DEFAULT_FLOW[Stage.COMPLETE],
    ),
    "ice_run": (
        DEFAULT_FLOW[Stage.MEET_NPC],
        DEFAULT_FLOW[Stage.EXTRACT_DATA],
        DEFAULT_FLOW[Stage.DEFEAT_ICE],
        DEFAULT_FLOW[Stage.JACK_OUT],
        DEFAULT_FLOW[Stage.REWARD],
        DEFAULT_FLOW[Stage.COMPLETE],
    ),
}


def get_mission_flow(mission_id: str) -> StageSequence:
    """Return the stage sequence for a given mission.

    Falls back to first_jack's flow if mission_id is unknown.
    """
    return MISSION_FLOWS.get(mission_id, MISSION_FLOWS["first_jack"])


def get_mission_stage_count(mission_id: str) -> int:
    """Return the number of stages in a mission's flow."""
    return len(get_mission_flow(mission_id))


# --- Stage validation ---


def validate_stage_transition(
    from_stage: Stage,
    to_stage: Stage,
    mission_id: str,
) -> bool:
    """Check if a stage transition is valid for the given mission.

    A transition is valid if `to_stage` follows `from_stage` in the
    mission's flow, OR if `to_stage` is FAILED (which can happen from
    any non-terminal stage).

    Args:
        from_stage: Current stage.
        to_stage: Proposed next stage.
        mission_id: The mission context.

    Returns:
        True if the transition is valid.
    """
    # FAILED is reachable from any in-progress stage
    if to_stage is Stage.FAILED:
        return from_stage not in (Stage.COMPLETE, Stage.FAILED, Stage.PENDING)

    flow = get_mission_flow(mission_id)
    stage_order = [info.stage for info in flow]

    if from_stage not in stage_order:
        return False

    from_idx = stage_order.index(from_stage)
    # Next stage in flow
    if from_idx + 1 < len(stage_order) and stage_order[from_idx + 1] is to_stage:
        return True
    # Allow staying in same stage (re-entry)
    if from_stage is to_stage:
        return True
    return False


def get_next_stage_in_flow(current: Stage, mission_id: str) -> Stage | None:
    """Get the next stage in the mission flow after `current`.

    Returns None if current is the last stage in the flow.
    """
    flow = get_mission_flow(mission_id)
    stage_order = [info.stage for info in flow]
    if current not in stage_order:
        return None
    idx = stage_order.index(current)
    if idx + 1 < len(stage_order):
        return stage_order[idx + 1]
    return None


# --- RunState ---


@dataclass
class RunState:
    """The player's current progress through a single Run.

    Replaces the old `visited_npc_dixie` / `visited_data` / `visited_ice`
    flags in the demo. The matrix screen, demo loop, and status panel all
    read from this to decide what to show and where to navigate.

    Attributes:
        current_stage: The stage the player is currently in.
        completed_stages: Tuple of stages the player has completed.
        pending_advance: Set when a stage transition just happened but
            the UI hasn't acknowledged it yet.
        current_target_node: Matrix node id where the current stage's
            objective should be done. None = not yet determined.
        last_visited_node: Last matrix node visited (for path context).
        mission_id: The mission this run belongs to.
        started_at: Timestamp (ms) when the run started.
    """

    current_stage: Stage = Stage.PENDING
    completed_stages: tuple[Stage, ...] = ()
    pending_advance: bool = False
    current_target_node: str | None = None
    last_visited_node: str | None = None
    mission_id: str = "first_jack"
    started_at_ms: int = 0

    # --- Lifecycle ---

    def reset(self, mission_id: str = "first_jack") -> None:
        """Reset to initial state for a new Run."""
        self.current_stage = Stage.MEET_NPC
        self.completed_stages = ()
        self.pending_advance = False
        self.current_target_node = None
        self.last_visited_node = None
        self.mission_id = mission_id
        self.started_at_ms = 0

    def is_complete(self) -> bool:
        """Run is finished (success or failure)."""
        return self.current_stage in (Stage.COMPLETE, Stage.FAILED, Stage.DEATH_RESTART)

    def is_in_progress(self) -> bool:
        """Run is currently happening (player in cyberspace)."""
        return self.current_stage not in (
            Stage.PENDING,
            Stage.COMPLETE,
            Stage.FAILED,
            Stage.DEATH_RESTART,
        )

    def is_in_cyberspace(self) -> bool:
        """Player is currently jacked into the matrix."""
        return self.current_stage in (Stage.MEET_NPC, Stage.EXTRACT_DATA, Stage.DEFEAT_ICE)

    def current_info(self) -> StageInfo:
        """Return info for the current stage."""
        return get_stage_info(self.current_stage)

    def objective_kind(self) -> ObjectiveKind:
        """Return the objective kind for the current stage."""
        return self.current_info().objective_kind

    def hint(self) -> str:
        """Return a player-facing hint for the current stage."""
        return self.current_info().hint

    def title(self) -> str:
        """Return the title for the current stage."""
        return self.current_info().title

    # --- Progress ---

    def progress_fraction(self) -> float:
        """Return current progress as a fraction (0.0-1.0)."""
        total = get_mission_stage_count(self.mission_id)
        if total == 0:
            return 0.0
        completed = len(self.completed_stages)
        return min(1.0, completed / total)

    def stages_total(self) -> int:
        """Return total stages in the current mission."""
        return get_mission_stage_count(self.mission_id)

    def stages_completed(self) -> int:
        """Return number of stages completed in the current run."""
        return len(self.completed_stages)

    # --- Stage transitions ---

    def mark_advance(self) -> None:
        """Mark the current stage as completed and advance to the next.

        Not idempotent: calling twice will advance twice (so the same
        stage is recorded as completed twice in completed_stages). This
        is intentional — the call site is responsible for ensuring it
        is only called once per stage transition (use the various
        check_* helpers to gate the call).

        Does not change state if already at COMPLETE or FAILED.
        """
        if self.current_stage in (
            Stage.COMPLETE,
            Stage.FAILED,
            Stage.PENDING,
            Stage.DEATH_RESTART,
        ):
            return

        info = self.current_info()
        # Add to completed
        self.completed_stages = self.completed_stages + (self.current_stage,)
        # Advance via mission flow (preferred) or info.next_stage (fallback)
        next_in_flow = get_next_stage_in_flow(self.current_stage, self.mission_id)
        if next_in_flow is not None:
            self.current_stage = next_in_flow
        elif info.next_stage is not None:
            self.current_stage = info.next_stage
        else:
            self.current_stage = Stage.COMPLETE
        # Reset target (will be re-resolved by matrix screen)
        self.current_target_node = None
        # Mark that a transition just happened (used by UI to show
        # "Stage complete" message until the player dismisses it).
        self.pending_advance = True

    def confirm_advance(self) -> None:
        """Acknowledge that the stage transition has been observed."""
        self.pending_advance = False

    def mark_failed(self) -> None:
        """Mark the run as failed (e.g. player flatlined).

        No-op if the run is already at a terminal stage
        (COMPLETE, FAILED, DEATH_RESTART).
        """
        if self.current_stage in (Stage.COMPLETE, Stage.FAILED, Stage.DEATH_RESTART):
            return
        self.completed_stages = self.completed_stages + (self.current_stage,)
        self.current_stage = Stage.FAILED
        self.current_target_node = None
        self.pending_advance = True

    def mark_death_restart(self) -> None:
        """Transition from FAILED to DEATH_RESTART (after death screen)."""
        if self.current_stage is Stage.FAILED:
            self.current_stage = Stage.DEATH_RESTART
            self.pending_advance = True

    def set_target(self, node_id: str | None) -> None:
        """Set the current target node for the active stage."""
        self.current_target_node = node_id

    def mark_visited(self, node_id: str) -> None:
        """Record that the player visited a node (for path context)."""
        self.last_visited_node = node_id


# --- Factory ---


def start_run(mission_id: str = "first_jack", initial_stage: Stage | None = None) -> RunState:
    """Create a fresh RunState for a given mission.

    Args:
        mission_id: The mission to start. Defaults to "first_jack".
        initial_stage: Override the initial stage (default: MEET_NPC for
            active missions, PENDING for unstarted).

    Returns:
        A new RunState.
    """
    if initial_stage is None:
        initial_stage = Stage.MEET_NPC
    return RunState(
        current_stage=initial_stage,
        mission_id=mission_id,
    )
