"""Save/Load slot browser — select a slot to load or delete.

Reached from the Hub menu. Shows 5 save slots with metadata
(mission, stage, credits, timestamp). Player can:
- ENTER: load selected slot
- DELETE/D: delete selected slot
- ESC: cancel and return to Hub

References:
    save_manager.SaveManager
    save_manager.SaveMetadata
"""

from __future__ import annotations

import tcod.console
import tcod.event

from . import config as _engine_config
from .save_manager import SaveError, SaveManager, SaveSlotEmptyError
from .state import AppState, ScreenKind

# --- Selection state (per AppState) ---


def get_selected_slot(state: AppState) -> int:
    """Get currently selected slot (1..MAX_SLOTS)."""
    return max(1, min(5, getattr(state, "save_load_selected", 1)))


def set_selected_slot(state: AppState, slot: int) -> None:
    """Set the currently selected slot."""
    state.save_load_selected = max(1, min(5, slot))


# --- Screen transitions ---


def enter_save_load(state: AppState) -> None:
    """Transition into the Save/Load browser."""
    state.screen = ScreenKind.SAVE_LOAD
    state.save_load_selected = 1
    state.status_messages.append(">>> Save/Load — select a slot")
    state.status_messages.append(">>> [ENTER] Load  [DEL] Delete  [ESC] Cancel")


def load_selected_slot(state: AppState) -> None:
    """Load the currently selected slot into AppState.

    Returns to Hub on success. On error, stays on the screen with a message.
    """
    slot = get_selected_slot(state)
    manager = SaveManager()
    try:
        manager.restore_state(slot, state)
        state.screen = ScreenKind.HUB
        state.status_messages.append(f">>> Loaded slot {slot}")
    except SaveSlotEmptyError:
        state.status_messages.append(f">>> Slot {slot} is empty — cannot load")
    except SaveError as e:
        state.status_messages.append(f">>> Load failed: {e}")


def delete_selected_slot(state: AppState) -> None:
    """Delete the currently selected slot."""
    slot = get_selected_slot(state)
    manager = SaveManager()
    if manager.delete(slot):
        state.status_messages.append(f">>> Slot {slot} deleted")
    else:
        state.status_messages.append(f">>> Slot {slot} was already empty")


def cancel_save_load(state: AppState) -> None:
    """Return to Hub without changes."""
    state.screen = ScreenKind.HUB
    state.status_messages.append(">>> Save/Load cancelled")


# --- Rendering ---


def _format_saved_at(iso: str | None) -> str:
    """Format ISO timestamp for display (truncated for compactness)."""
    if not iso:
        return "—"
    # Strip microseconds, keep just YYYY-MM-DD HH:MM
    if "T" in iso:
        date_part, time_part = iso.split("T", 1)
        # Remove timezone suffix and microseconds
        time_part = time_part.split("+", 1)[0].split("Z", 1)[0]
        if "." in time_part:
            time_part = time_part.split(".", 1)[0]
        return f"{date_part} {time_part}"
    return iso[:16]


def _format_elapsed(seconds: int) -> str:
    """Format elapsed seconds as MM:SS or HH:MM:SS."""
    if seconds < 0:
        return "—"
    if seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m}m {s:02d}s"
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m:02d}m"


def render_save_load(console: tcod.console.Console, state: AppState) -> None:
    """Render the Save/Load browser."""
    SCREEN_WIDTH = _engine_config.SCREEN_WIDTH  # noqa: N806
    SCREEN_HEIGHT = _engine_config.SCREEN_HEIGHT  # noqa: N806

    console.clear(bg=(0, 0, 0))

    # Title
    title = "═══ SAVE / LOAD ═══"
    console.print(
        x=(SCREEN_WIDTH - len(title)) // 2,
        y=2,
        string=title,
        fg=(100, 200, 255),
    )

    # Subtitle
    subtitle = "Select a slot to load or delete"
    console.print(
        x=(SCREEN_WIDTH - len(subtitle)) // 2,
        y=3,
        string=subtitle,
        fg=(150, 150, 150),
    )

    # Get metadata for all slots
    manager = SaveManager()
    slots = manager.list_slots()

    # Render slots as a vertical list
    start_y = 6
    slot_h = 6  # height per slot
    slot_w = 60
    slot_x = (SCREEN_WIDTH - slot_w) // 2

    selected = get_selected_slot(state)

    for i, meta in enumerate(slots):
        slot_y = start_y + i * slot_h
        is_selected = meta.slot == selected

        # Highlight selected slot
        if is_selected:
            border_color = (255, 200, 100)
            text_color = (255, 255, 200)
        else:
            border_color = (80, 80, 100)
            text_color = (180, 180, 180)

        # Slot frame
        top = "┌" + "─" * (slot_w - 2) + "┐"
        bottom = "└" + "─" * (slot_w - 2) + "┘"
        console.print(x=slot_x, y=slot_y, string=top, fg=border_color)
        for y in range(slot_y + 1, slot_y + slot_h - 1):
            console.print(x=slot_x, y=y, string="│" + " " * (slot_w - 2) + "│", fg=border_color)
        console.print(x=slot_x, y=slot_y + slot_h - 1, string=bottom, fg=border_color)

        # Slot content
        cursor = "▶" if is_selected else " "
        slot_label = f"{cursor} Slot {meta.slot}"
        if meta.exists:
            compat = "✓" if meta.is_compatible else "⚠"
            mission_str = meta.mission_id or "?"
            stage_str = meta.current_stage or "?"
            elapsed_str = _format_elapsed(meta.elapsed_seconds)
            saved_str = _format_saved_at(meta.saved_at)
            size_kb = meta.size_bytes / 1024.0

            line1 = f"{slot_label}  [{compat}]  {mission_str}"
            line2 = f"    Stage: {stage_str:<14}  Credits: {meta.credits}"
            line3 = f"    Grade: {meta.player_grade or '?':<14}  Time:  {elapsed_str}"
            line4 = f"    Saved: {saved_str}  ({size_kb:.1f} KB)"

            console.print(x=slot_x + 2, y=slot_y + 1, string=line1, fg=text_color)
            console.print(x=slot_x + 2, y=slot_y + 2, string=line2, fg=text_color)
            console.print(x=slot_x + 2, y=slot_y + 3, string=line3, fg=text_color)
            console.print(x=slot_x + 2, y=slot_y + 4, string=line4, fg=(120, 120, 130))
        else:
            line = f"{slot_label}  (empty)"
            console.print(
                x=slot_x + 2,
                y=slot_y + 2,
                string=line,
                fg=(80, 80, 90),
            )

    # Controls
    controls_y = SCREEN_HEIGHT - 5
    controls_lines = [
        "[↑/↓] Select  [1-5] Jump to slot",
        "[ENTER] Load  [DEL] Delete  [ESC] Cancel",
    ]
    for i, line in enumerate(controls_lines):
        console.print(
            x=(SCREEN_WIDTH - len(line)) // 2,
            y=controls_y + i,
            string=line,
            fg=(150, 150, 150),
        )

    # Recent status
    if state.status_messages:
        for i, msg in enumerate(state.status_messages[-3:]):
            console.print(
                x=2,
                y=SCREEN_HEIGHT - 3 + i,
                string=msg,
                fg=(120, 120, 120),
            )


# --- Input ---


def handle_save_load_input(event: tcod.event.Event, state: AppState) -> bool:
    """Handle input on the Save/Load screen. Returns False to quit."""
    if not isinstance(event, tcod.event.KeyDown):
        return True

    if event.sym is tcod.event.KeySym.Q:
        return False

    if event.sym is tcod.event.KeySym.ESCAPE:
        cancel_save_load(state)
        return True

    # Navigation
    if event.sym is tcod.event.KeySym.UP:
        current = get_selected_slot(state)
        set_selected_slot(state, current - 1 if current > 1 else 5)
        return True

    if event.sym is tcod.event.KeySym.DOWN:
        current = get_selected_slot(state)
        set_selected_slot(state, current + 1 if current < 5 else 1)
        return True

    # Jump to slot number
    if event.sym in (
        tcod.event.KeySym.N1,
        tcod.event.KeySym.N2,
        tcod.event.KeySym.N3,
        tcod.event.KeySym.N4,
        tcod.event.KeySym.N5,
    ):
        slot = int(event.sym.name[1:])
        set_selected_slot(state, slot)
        return True

    # Load
    if event.sym in (
        tcod.event.KeySym.RETURN,
        tcod.event.KeySym.SPACE,
        tcod.event.KeySym.KP_ENTER,
    ):
        load_selected_slot(state)
        return True

    # Delete
    if event.sym in (
        tcod.event.KeySym.DELETE,
        tcod.event.KeySym.D,
    ):
        delete_selected_slot(state)
        return True

    return True
