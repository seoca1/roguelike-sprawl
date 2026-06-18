"""Run State system — manages a single playthrough's stage progression.

A "Run" is one complete playthrough: from accepting a mission at the
Hub to completing it (or flatlining). Each Run is divided into Stages,
which are concrete objectives the player must satisfy in order.

This module is the source of truth for "what should the player be doing
right now?" — the matrix screen, demo loop, and status panel all read
from it instead of tracking ad-hoc flags.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Stage(StrEnum):
    """Ordered stages of a single Run.

    The default first_jack mission flow:
      MEET_NPC → EXTRACT_DATA → DEFEAT_ICE → COMPLETE
    """

    PENDING = "pending"  # Run not started
    MEET_NPC = "meet_npc"  # Find and talk to a construct NPC
    EXTRACT_DATA = "extract_data"  # Find data node, extract payload
    DEFEAT_ICE = "defeat_ice"  # Find ICE node, win combat
    COMPLETE = "complete"  # Run finished, return to hub
    FAILED = "failed"  # Player flatlined


class ObjectiveKind(StrEnum):
    """What kind of in-game action satisfies a Stage.

    Used to find the right node in the matrix and detect completion.
    """

    NPC = "npc"  # Node with kind=CONSTRUCT (talk to)
    DATA = "data"  # Node with kind=DATA (extract from)
    ICE = "ice"  # Node with kind=ICE (combat)
    NONE = "none"  # No specific target (e.g. PENDING, COMPLETE)


# --- Stage metadata ---


@dataclass(frozen=True, slots=True)
class StageInfo:
    """Static description of a stage."""

    stage: Stage
    title: str
    objective_kind: ObjectiveKind
    hint: str
    next_stage: Stage | None


# Default mission flow (First Jack)
DEFAULT_FLOW: tuple[StageInfo, ...] = (
    StageInfo(
        stage=Stage.MEET_NPC,
        title="Meet the Construct",
        objective_kind=ObjectiveKind.NPC,
        hint="Find and talk to the construct (Dixie Flatline).",
        next_stage=Stage.EXTRACT_DATA,
    ),
    StageInfo(
        stage=Stage.EXTRACT_DATA,
        title="Extract the Data",
        objective_kind=ObjectiveKind.DATA,
        hint="Locate the data node and extract the payload.",
        next_stage=Stage.DEFEAT_ICE,
    ),
    StageInfo(
        stage=Stage.DEFEAT_ICE,
        title="Defeat the ICE",
        objective_kind=ObjectiveKind.ICE,
        hint="Engage and defeat the ICE protecting the data.",
        next_stage=Stage.COMPLETE,
    ),
    StageInfo(
        stage=Stage.COMPLETE,
        title="Run Complete",
        objective_kind=ObjectiveKind.NONE,
        hint="Mission complete. Return to hub for rewards.",
        next_stage=None,
    ),
    StageInfo(
        stage=Stage.FAILED,
        title="Flatline",
        objective_kind=ObjectiveKind.NONE,
        hint="Your run ended in cyberspace.",
        next_stage=None,
    ),
    StageInfo(
        stage=Stage.PENDING,
        title="Awaiting Jack-In",
        objective_kind=ObjectiveKind.NONE,
        hint="Accept a mission at the Hub to begin.",
        next_stage=None,
    ),
)


def get_stage_info(stage: Stage) -> StageInfo:
    """Return the StageInfo for a given Stage."""
    for info in DEFAULT_FLOW:
        if info.stage == stage:
            return info
    # Should not happen if DEFAULT_FLOW is exhaustive
    return StageInfo(
        stage=stage,
        title=stage.value.title(),
        objective_kind=ObjectiveKind.NONE,
        hint="",
        next_stage=None,
    )


# --- RunState ---


@dataclass
class RunState:
    """The player's current progress through a single Run.

    Replaces the old `visited_npc_dixie` / `visited_data` / `visited_ice`
    flags in the demo. The matrix screen, demo loop, and status panel
    all read from this to decide what to show and where to navigate.
    """

    current_stage: Stage = Stage.PENDING
    completed_stages: tuple[Stage, ...] = ()
    # Set when a stage's objective is satisfied but we haven't yet
    # transitioned (e.g. victory screen plays for a few seconds).
    pending_advance: bool = False
    # The node id where the current stage's objective should be done.
    # None = not yet determined (e.g. not in matrix yet).
    current_target_node: str | None = None
    # Optional: last node visited (for path context)
    last_visited_node: str | None = None

    def reset(self) -> None:
        """Reset to initial state (new Run)."""
        self.current_stage = Stage.PENDING
        self.completed_stages = ()
        self.pending_advance = False
        self.current_target_node = None
        self.last_visited_node = None

    def is_complete(self) -> bool:
        """Run is finished (success or failure)."""
        return self.current_stage in (Stage.COMPLETE, Stage.FAILED)

    def is_in_progress(self) -> bool:
        """Run is currently happening (player in cyberspace)."""
        return self.current_stage not in (
            Stage.PENDING,
            Stage.COMPLETE,
            Stage.FAILED,
        )

    def current_info(self) -> StageInfo:
        """Return info for the current stage."""
        return get_stage_info(self.current_stage)

    def objective_kind(self) -> ObjectiveKind:
        """Return the objective kind for the current stage."""
        return self.current_info().objective_kind

    def hint(self) -> str:
        """Return a player-facing hint for the current stage."""
        return self.current_info().hint

    def mark_advance(self) -> None:
        """Mark the current stage as completed and advance to the next.

        Not idempotent: calling twice will advance twice (so the same
        stage is recorded as completed twice in completed_stages). This
        is intentional — the call site is responsible for ensuring it
        is only called once per stage transition (use the various
        check_* helpers to gate the call).

        Does not change state if already at COMPLETE or FAILED.
        """
        if self.current_stage in (Stage.COMPLETE, Stage.FAILED, Stage.PENDING):
            return

        info = self.current_info()
        # Add to completed
        self.completed_stages = self.completed_stages + (self.current_stage,)
        # Advance
        if info.next_stage is not None:
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
        """Mark the run as failed (e.g. player flatlined)."""
        self.completed_stages = self.completed_stages + (self.current_stage,)
        self.current_stage = Stage.FAILED
        self.current_target_node = None
        self.pending_advance = True

    def set_target(self, node_id: str | None) -> None:
        """Set the current target node for the active stage."""
        self.current_target_node = node_id

    def mark_visited(self, node_id: str) -> None:
        """Record that the player visited a node (for path context)."""
        self.last_visited_node = node_id


# --- Factory ---


def start_run(initial_stage: Stage = Stage.MEET_NPC) -> RunState:
    """Create a fresh RunState starting at the given stage."""
    return RunState(current_stage=initial_stage)
