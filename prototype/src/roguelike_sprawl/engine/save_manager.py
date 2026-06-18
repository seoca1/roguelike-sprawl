"""Save/Load system for Run state.

Persists the current Run (and relevant AppState) to a JSON file so the
player can continue later. Save format is versioned for future
migration.

Save format (JSON):
    {
      "version": "0.1.0",
      "saved_at": "2026-06-18T20:00:00Z",
      "elapsed_seconds": 480,
      "run_state": {
        "current_stage": "jack_out",
        "completed_stages": ["meet_npc", "extract_data", "defeat_ice"],
        "pending_advance": true,
        "current_target_node": "ice1",
        "last_visited_node": "data1",
        "mission_id": "first_jack",
        "started_at_ms": 0
      },
      "mission": {
        "id": "first_jack",
        "title": "First Jack",
        "fixer": "finn",
        "arc": 1,
        "grade_min": 1,
        "grade_max": 1,
        "matrix_seed": 42,
        "zone": "surface",
        "rewards": {
          "credits": 500,
          "materials": {"data_fragment": 2}
        }
      },
      "app_state": {
        "inventory": {"data_fragment": 2, "ice_shard": 1},
        "credits": 500,
        "current_node_id": "data1",
        "defeated_nodes": ["ice1"],
        "extracted_nodes": ["data1"],
        "mission_progress": {"extract_data": 1, "defeat": 1}
      },
      "metadata": {
        "player_grade": 1,
        "screen": "matrix"
      }
    }

Auto-save triggers:
- JACK_OUT entry (after defeating ICE, before disconnect)
- DEATH (player can choose to load or restart)
- Manual: F5 (quick save to slot 1), F9 (quick load slot 1)
- Hub menu: Save / Load buttons

Save slots: 5 slots, files in `<save_dir>/slot_N.json`.
Default save dir: `~/.roguelike_sprawl/saves/` (cross-platform).
"""

from __future__ import annotations

import json
import os
import platform
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .state import AppState


# --- Save format ---


SAVE_FORMAT_VERSION = "0.1.0"
MAX_SLOTS = 5
DEFAULT_SLOT = 1


class SaveError(Exception):
    """Base class for save/load errors."""


class SaveSlotEmptyError(SaveError):
    """Save slot has no data."""


class SaveVersionMismatchError(SaveError):
    """Save file version doesn't match current code version."""


class SaveCorruptedError(SaveError):
    """Save file is corrupted or unreadable."""


# --- Save metadata ---


@dataclass(frozen=True, slots=True)
class SaveMetadata:
    """Metadata about a save file (for listing/displays)."""

    slot: int
    exists: bool
    version: str | None
    saved_at: str | None
    elapsed_seconds: int
    mission_id: str | None
    current_stage: str | None
    player_grade: int | None
    credits: int
    size_bytes: int
    is_compatible: bool


# --- Saved run data ---


@dataclass
class SavedRun:
    """A complete saved Run that can be restored.

    Attributes:
        version: Save format version.
        saved_at: ISO 8601 timestamp.
        elapsed_seconds: Game time elapsed (for display).
        run_state: The RunState as a dict (Stage enums as strings).
        mission: The mission as a dict (enums as strings).
        app_state: AppState fields needed for Run continuation.
        metadata: Display metadata (grade, screen, etc.).
    """

    version: str
    saved_at: str
    elapsed_seconds: int
    run_state: dict[str, Any]
    mission: dict[str, Any] | None
    app_state: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "version": self.version,
            "saved_at": self.saved_at,
            "elapsed_seconds": self.elapsed_seconds,
            "run_state": self.run_state,
            "mission": self.mission,
            "app_state": self.app_state,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SavedRun:
        """Deserialize from JSON dict. Validates version."""
        version = data.get("version")
        if version != SAVE_FORMAT_VERSION:
            raise SaveVersionMismatchError(
                f"Save version {version!r} != current {SAVE_FORMAT_VERSION!r}"
            )
        return cls(
            version=version,
            saved_at=data.get("saved_at", ""),
            elapsed_seconds=data.get("elapsed_seconds", 0),
            run_state=data.get("run_state", {}),
            mission=data.get("mission"),
            app_state=data.get("app_state", {}),
            metadata=data.get("metadata", {}),
        )


# --- Save manager ---


def _default_save_dir() -> Path:
    """Return the platform-appropriate save directory.

    - macOS/Linux: $XDG_DATA_HOME/roguelike_sprawl/saves/ or ~/.local/share/...
    - Windows: %APPDATA%/roguelike_sprawl/saves/
    """
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
    else:
        # Unix-like: XDG_DATA_HOME or ~/.local/share
        xdg = os.environ.get("XDG_DATA_HOME")
        if xdg:
            base = xdg
        else:
            base = str(Path.home() / ".local" / "share")
    return Path(base) / "roguelike_sprawl" / "saves"


def _atomic_write(path: Path, data: str) -> None:
    """Write data to path atomically (write to temp + rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp_path, path)
    except Exception:
        # Clean up temp file on error
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


class SaveManager:
    """Manages save slots and Run persistence."""

    def __init__(self, save_dir: Path | None = None) -> None:
        """Initialize save manager.

        Args:
            save_dir: Directory for save files. Defaults to platform-appropriate path.
        """
        self.save_dir = save_dir or _default_save_dir()
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def _slot_path(self, slot: int) -> Path:
        """Get the file path for a save slot."""
        if not 1 <= slot <= MAX_SLOTS:
            raise ValueError(f"slot must be 1..{MAX_SLOTS}, got {slot}")
        return self.save_dir / f"slot_{slot}.json"

    def has_save(self, slot: int) -> bool:
        """Check if a slot has a save file."""
        return self._slot_path(slot).exists()

    def list_slots(self) -> list[SaveMetadata]:
        """List all save slots (1..MAX_SLOTS) with metadata.

        Empty slots are included with exists=False.
        """
        result: list[SaveMetadata] = []
        for slot in range(1, MAX_SLOTS + 1):
            result.append(self.get_metadata(slot))
        return result

    def get_metadata(self, slot: int) -> SaveMetadata:
        """Get metadata for a single slot (without loading full data)."""
        path = self._slot_path(slot)
        if not path.exists():
            return SaveMetadata(
                slot=slot,
                exists=False,
                version=None,
                saved_at=None,
                elapsed_seconds=0,
                mission_id=None,
                current_stage=None,
                player_grade=None,
                credits=0,
                size_bytes=0,
                is_compatible=False,
            )
        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
            version = data.get("version", "")
            return SaveMetadata(
                slot=slot,
                exists=True,
                version=version,
                saved_at=data.get("saved_at"),
                elapsed_seconds=data.get("elapsed_seconds", 0),
                mission_id=(data.get("mission") or {}).get("id"),
                current_stage=(data.get("run_state") or {}).get("current_stage"),
                player_grade=(data.get("metadata") or {}).get("player_grade"),
                credits=(data.get("app_state") or {}).get("credits", 0),
                size_bytes=path.stat().st_size,
                is_compatible=(version == SAVE_FORMAT_VERSION),
            )
        except (json.JSONDecodeError, OSError):
            return SaveMetadata(
                slot=slot,
                exists=True,
                version=None,
                saved_at=None,
                elapsed_seconds=0,
                mission_id=None,
                current_stage=None,
                player_grade=None,
                credits=0,
                size_bytes=path.stat().st_size if path.exists() else 0,
                is_compatible=False,
            )

    def save(
        self,
        slot: int,
        state: AppState,
        elapsed_seconds: int = 0,
    ) -> SaveMetadata:
        """Save current Run state to a slot.

        Args:
            slot: Save slot (1..MAX_SLOTS).
            state: App state to save.
            elapsed_seconds: Game time elapsed (for display).

        Returns:
            Metadata of the saved file.

        Raises:
            ValueError: If slot is invalid.
        """
        from .state import AppState

        if not isinstance(state, AppState):
            raise TypeError(f"state must be AppState, got {type(state).__name__}")

        # Build saved run from AppState
        run_state = state.run_state
        if run_state is None:
            raise SaveError("No run in progress to save")

        # Run state as dict (Stage enums -> strings)
        run_state_dict: dict[str, Any] = {
            "current_stage": run_state.current_stage.value,
            "completed_stages": [s.value for s in run_state.completed_stages],
            "pending_advance": run_state.pending_advance,
            "current_target_node": run_state.current_target_node,
            "last_visited_node": run_state.last_visited_node,
            "mission_id": run_state.mission_id,
            "started_at_ms": run_state.started_at_ms,
        }

        # Mission as dict
        mission_dict: dict[str, Any] | None = None
        if state.current_mission is not None:
            m = state.current_mission
            mission_dict = {
                "id": m.id,
                "title": m.title,
                "fixer": m.fixer,
                "arc": m.arc,
                "grade_min": m.grade_min,
                "grade_max": m.grade_max,
                "matrix_seed": m.matrix_seed,
                "zone": m.zone.value,
                "rewards": {
                    "credits": m.rewards.credits if m.rewards else 0,
                    "materials": dict(m.rewards.materials) if m.rewards else {},
                },
            }

        # App state — only the fields needed to resume a Run
        # Include matrix graph if present (for complete state restoration)
        matrix_dict: dict[str, object] | None = None
        if state.matrix is not None:
            try:
                matrix_dict = state.matrix.to_dict()
            except Exception:
                matrix_dict = None

        app_state_dict: dict[str, Any] = {
            "inventory": dict(state.inventory),
            "credits": state.credits,
            "current_node_id": state.current_node_id,
            "defeated_nodes": list(state.defeated_nodes),
            "extracted_nodes": list(state.extracted_nodes),
            "mission_progress": dict(state.mission_progress),
            "in_server_browser": state.in_server_browser,
            "selected_server_index": state.selected_server_index,
            "current_mission_id": state.current_mission.id if state.current_mission else None,
            "matrix": matrix_dict,
        }

        # Metadata for display
        metadata_dict: dict[str, Any] = {
            "player_grade": state.player_grade,
            "screen": state.screen.value,
        }

        saved_run = SavedRun(
            version=SAVE_FORMAT_VERSION,
            saved_at=datetime.now(UTC).isoformat(),
            elapsed_seconds=elapsed_seconds,
            run_state=run_state_dict,
            mission=mission_dict,
            app_state=app_state_dict,
            metadata=metadata_dict,
        )

        # Atomic write
        json_data = json.dumps(saved_run.to_dict(), indent=2, ensure_ascii=False)
        _atomic_write(self._slot_path(slot), json_data)

        return self.get_metadata(slot)

    def load(self, slot: int) -> SavedRun:
        """Load a saved Run from a slot.

        Args:
            slot: Save slot (1..MAX_SLOTS).

        Returns:
            The SavedRun.

        Raises:
            SaveSlotEmptyError: If the slot has no save.
            SaveVersionMismatchError: If version doesn't match.
            SaveCorruptedError: If the file is corrupted.
        """
        path = self._slot_path(slot)
        if not path.exists():
            raise SaveSlotEmptyError(f"Slot {slot} is empty")

        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise SaveCorruptedError(f"Slot {slot} file is corrupted: {e}") from e
        except OSError as e:
            raise SaveCorruptedError(f"Slot {slot} file is unreadable: {e}") from e

        try:
            return SavedRun.from_dict(data)
        except SaveVersionMismatchError:
            raise
        except Exception as e:
            raise SaveCorruptedError(f"Slot {slot} data is invalid: {e}") from e

    def restore_state(self, slot: int, state: AppState) -> None:
        """Restore AppState from a saved Run.

        Args:
            slot: Save slot (1..MAX_SLOTS).
            state: AppState to modify in-place.

        Raises:
            SaveSlotEmptyError, SaveVersionMismatchError, SaveCorruptedError
        """
        from ..run import RunState, Stage
        from .state import ScreenKind

        saved = self.load(slot)
        rs_data = saved.run_state
        app_data = saved.app_state

        # Restore RunState
        try:
            current_stage = Stage(rs_data.get("current_stage", "pending"))
        except ValueError:
            current_stage = Stage.PENDING

        completed_stages: tuple[Stage, ...] = tuple(
            Stage(s) for s in rs_data.get("completed_stages", [])
        )

        state.run_state = RunState(
            current_stage=current_stage,
            completed_stages=completed_stages,
            pending_advance=rs_data.get("pending_advance", False),
            current_target_node=rs_data.get("current_target_node"),
            last_visited_node=rs_data.get("last_visited_node"),
            mission_id=rs_data.get("mission_id", "first_jack"),
            started_at_ms=rs_data.get("started_at_ms", 0),
        )

        # Restore AppState fields
        state.inventory = dict(app_data.get("inventory", {}))
        state.credits = int(app_data.get("credits", 0))
        state.current_node_id = app_data.get("current_node_id")
        state.defeated_nodes = set(app_data.get("defeated_nodes", []))
        state.extracted_nodes = set(app_data.get("extracted_nodes", []))
        state.mission_progress = dict(app_data.get("mission_progress", {}))
        state.in_server_browser = app_data.get("in_server_browser", True)
        state.selected_server_index = int(app_data.get("selected_server_index", 0))
        # Restore player_grade from metadata (persistent across runs)
        if saved.metadata.get("player_grade") is not None:
            state.player_grade = int(saved.metadata["player_grade"])

        # Matrix and other state — try to restore from saved data.
        # If the matrix can't be restored (corrupted/missing), the player
        # will need to re-jack-in but other state is preserved.
        matrix_data = app_data.get("matrix")
        matrix_restored = False
        if matrix_data and isinstance(matrix_data, dict):
            try:
                from ..matrix.graph import MatrixGraph

                state.matrix = MatrixGraph.from_dict(matrix_data)
                matrix_restored = True
            except Exception as e:
                state.status_messages.append(
                    f">>> Warning: matrix restore failed ({e}), re-jack-in required"
                )
                state.matrix = None
        else:
            state.matrix = None

        # Recompute cyberspace_layouts if matrix was restored
        if matrix_restored and state.matrix is not None:
            try:
                from ..matrix.graph import compute_layout

                state.cyberspace_layouts = dict(compute_layout(state.matrix))
            except Exception:
                state.cyberspace_layouts = None
        else:
            state.cyberspace_layouts = None

        state.server_subgraph = None
        state.combat_state = None
        state.cinematic_state = None
        state.npc_state = None
        state.active_event = None

        # Restore mission (just id reference; full data is in saved file)
        # The mission is reloaded from mission data when needed
        if app_data.get("current_mission_id"):
            from ..missions import JobBoard
            from . import config as _engine_config

            try:
                board = JobBoard.load(_engine_config.DATA_DIR / "missions" / "missions.json")
                state.current_mission = board.get(app_data["current_mission_id"])
            except Exception:
                state.current_mission = None

        # Set screen based on saved stage
        # If matrix was restored, go to MATRIX (continue exploration).
        # Otherwise, fall back to HUB (player must re-jack-in).
        if current_stage in (Stage.PENDING, Stage.MEET_NPC, Stage.EXTRACT_DATA, Stage.DEFEAT_ICE):
            state.screen = ScreenKind.MATRIX if state.matrix is not None else ScreenKind.HUB
        elif current_stage in (Stage.JACK_OUT, Stage.REWARD, Stage.DEBRIEF):
            # Post-combat: return to hub to continue
            state.screen = ScreenKind.HUB
        elif current_stage in (Stage.COMPLETE,):
            state.screen = ScreenKind.HUB
        elif current_stage in (Stage.FAILED, Stage.DEATH_RESTART):
            state.screen = ScreenKind.DEATH

        state.status_messages.append(f">>> Game loaded from slot {slot}")
        state.status_messages.append(f">>> Stage: {current_stage.value}")
        if matrix_restored and state.matrix is not None:
            state.status_messages.append(
                f">>> Matrix restored: {len(state.matrix.nodes)} nodes, "
                f"{len(state.matrix.edges)} edges"
            )

    def delete(self, slot: int) -> bool:
        """Delete a save slot.

        Returns:
            True if a file was deleted, False if slot was empty.
        """
        path = self._slot_path(slot)
        if not path.exists():
            return False
        path.unlink()
        return True

    def quick_save(self, state: AppState, elapsed_seconds: int = 0) -> SaveMetadata:
        """Save to the default quick-save slot (1)."""
        return self.save(DEFAULT_SLOT, state, elapsed_seconds)

    def quick_load(self, state: AppState) -> None:
        """Load from the default quick-save slot (1)."""
        self.restore_state(DEFAULT_SLOT, state)
