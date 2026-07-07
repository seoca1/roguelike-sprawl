"""Main menu screen (ADR-0009, ADR-0032).

Text-based menu. The Hub is described as a cyberspace construct, but
the main menu itself is a thin real-world UI.

Phase 5+: Uses unified screen shell (engine.layout).
ADR-0032: Extended to 5 options (NEW RUN, GRAPHIC NOVEL, CONTINUE,
          SETTINGS, CREDITS).
"""

from __future__ import annotations

import tcod.console
import tcod.context
import tcod.event
from tcod.event import KeyDown, KeySym

from ..i18n import Translator
from .layout import (
    RegionId,
    clear_region,
    draw_controls,
    draw_dividers,
    draw_footer,
    draw_title,
    make_shell,
)
from .state import AppState, ScreenKind

# Main menu options (1-indexed) — ADR-0032, ADR-0040, Phase 7
OPTION_NEW_RUN = 1
OPTION_GRAPHIC_NOVEL = 2
OPTION_CONTINUE = 3
OPTION_SETTINGS = 4
OPTION_CREDITS = 5
OPTION_HALL_OF_DEAD = 6  # Hall of Dead Jockeys (ADR-0040)
OPTION_HELP = 7  # Help screen (Phase 7: tutorial/onboarding)

MENU_OPTION_COUNT = 7


def render_menu(console: tcod.console.Console, t: Translator, state: AppState) -> None:
    """Render the main menu screen with unified layout (5 options)."""
    shell = make_shell()
    title_r = shell[RegionId.TITLE]
    main_r = shell[RegionId.MAIN]
    ctrl_r = shell[RegionId.CONTROLS]
    foot_r = shell[RegionId.FOOTER]

    # Clear and draw dividers
    for r in shell.values():
        clear_region(console, r)
    draw_dividers(console)

    # Title
    draw_title(console, title_r, title=t("app.title"), subtitle=t("app.subtitle"))

    # Main area: 7 menu options (ADR-0032 + ADR-0040 + Phase 7)
    has_save = getattr(state, "has_save", False)
    options = [
        (OPTION_NEW_RUN, t("menu.new_run")),
        (OPTION_GRAPHIC_NOVEL, t("menu.graphic_novel")),
        (OPTION_CONTINUE, t("menu.continue") + ("" if has_save else " (없음)")),
        (OPTION_SETTINGS, t("menu.settings")),
        (OPTION_CREDITS, t("menu.credits")),
        (OPTION_HALL_OF_DEAD, t("menu.hall_of_dead")),
        (OPTION_HELP, t("menu.help")),
    ]
    y = main_r.y + 1
    for i, (_key, label) in enumerate(options):
        # Dim disabled options (e.g. Continue when no save)
        dim = i + 1 == OPTION_CONTINUE and not has_save
        fg = (100, 100, 100) if dim else (200, 200, 200)
        console.print(
            x=main_r.x + 4,
            y=y + i * 2,
            string=f"[{i + 1}] {label}",
            fg=fg,
        )

    # Message (if any)
    if state.message:
        console.print(
            x=main_r.x + 4,
            y=main_r.y + main_r.h - 4,
            string=f"> {state.message}",
            fg=(255, 255, 0),
        )

    # Controls
    draw_controls(
        console,
        ctrl_r,
        lines=[t("menu.controls")],
    )

    # Footer
    draw_footer(
        console, foot_r, text=f"Main Menu  |  Step {state.demo_step}  T+{state.demo_elapsed_s:.1f}s"
    )


def handle_menu_input(event: tcod.event.Event, state: AppState) -> bool:
    """Handle input on the menu screen. Returns False to quit.

    ADR-0032: 5 menu options.
    ADR-0040: 6 menu options (added Hall of Dead Jockeys).
    """
    if isinstance(event, KeyDown):
        if event.sym in (KeySym.ESCAPE, KeySym.Q):
            return False
        if event.sym is KeySym.N1:
            # NEW RUN: skip character select → character pick → chapter
            state.screen = ScreenKind.CHARACTER_SELECT
        elif event.sym is KeySym.N2:
            # GRAPHIC NOVEL: enter graphic novel menu (ADR-0032)
            state.screen = ScreenKind.GRAPHIC_NOVEL_MENU
            state.gn_scene_chain = []
            state.gn_scene_index = 0
            state.gn_dialogue_index = 0
            state.gn_elapsed_ms = 0.0
            state.gn_paused = False
        elif event.sym is KeySym.N3:
            # CONTINUE: load latest save → HUB (or message if no save)
            if getattr(state, "has_save", False):
                state.screen = ScreenKind.HUB
                state.message = "Loading save..."
            else:
                state.message = "No save file. Use NEW RUN."
        elif event.sym is KeySym.N4:
            state.screen = ScreenKind.SETTINGS
            state.settings_selected = 0
        elif event.sym is KeySym.N5:
            state.message = "Credits: (Phase 7+)"
        elif event.sym is KeySym.N6:
            # Hall of Dead Jockeys (ADR-0040)
            state.screen = ScreenKind.HALL_OF_DEAD
            state.hall_of_dead_selected = 0
        elif event.sym is KeySym.N7:
            # Help screen (Phase 7: tutorial/onboarding)
            state.screen = ScreenKind.HELP
            state.help_page = 0
    return True


def handle_graphic_novel_menu_input(
    event: tcod.event.Event,
    state: AppState,
) -> str:
    """Handle input on the GRAPHIC_NOVEL_MENU screen.

    Returns the selected mode:
        - "prologue" | "novice" | "veteran" | "heretic" | "back"
        - "" if no action

    ADR-0048: Selecting a character (N2-N4) returns the character name to
    transition to GRAPHIC_NOVEL_ENDING_MENU. PROLOGUE (N1) and BACK (N5/ESC)
    skip the ending selection (prologue always uses ending A).
    """
    if not isinstance(event, KeyDown):
        return ""
    if event.sym in (KeySym.ESCAPE, KeySym.Q):
        return "back"
    if event.sym is KeySym.N1:
        return "prologue"
    if event.sym is KeySym.N2:
        return "novice"
    if event.sym is KeySym.N3:
        return "veteran"
    if event.sym is KeySym.N4:
        return "heretic"
    if event.sym is KeySym.N5:
        return "back"
    return ""


def handle_graphic_novel_ending_menu_input(
    event: tcod.event.Event,
    state: AppState,
) -> str:
    """Handle input on the GRAPHIC_NOVEL_ENDING_MENU screen (ADR-0048, ADR-0049).

    Returns the selected ending:
        - "A" : default ending (Finn's offer accepted, etc.)
        - "B" : alternative ending (mysterious refusal, etc.)
        - "C" : third ending — vanishing / erase / unmaking (ADR-0049)
        - "back" : return to GRAPHIC_NOVEL_MENU
        - "" if no action

    The number of options depends on how many endings exist for the current
    character (probed from :func:`available_endings`). N1..N{count} map to
    endings A..{chr(ord('A')+count-1)}. ESC/Q are always "back".
    """
    from .graphic_novel_view import available_endings

    if not isinstance(event, KeyDown):
        return ""
    if event.sym in (KeySym.ESCAPE, KeySym.Q):
        return "back"
    # Determine current character's available endings from the screen context
    # (state.gn_mode is set to novice/veteran/heretic when entering the screen).
    endings = available_endings(state.gn_mode)
    n_count = len(endings)
    back_keys = [getattr(KeySym, f"N{i}") for i in range(1, n_count + 1)]
    # Find the back key (first N-key not used by an ending option)
    for i in range(1, n_count + 2):
        sym = getattr(KeySym, f"N{i}")
        if sym not in back_keys:
            back_sym = sym
            break
    if event.sym is back_sym:
        return "back"
    for i, ending in enumerate(endings, start=1):
        if event.sym is getattr(KeySym, f"N{i}"):
            return ending
    return ""


def handle_graphic_novel_input(
    event: tcod.event.Event,
    state: AppState,
) -> str:
    """Handle input during graphic novel playback.

    Returns the action:
        - "next" : advance to next dialogue
        - "skip" : skip current scene
        - "pause" : toggle pause
        - "menu" : exit graphic novel → saved_progress
        - "" : no action
    """
    if not isinstance(event, KeyDown):
        return ""
    if event.sym in (KeySym.ESCAPE, KeySym.Q):
        return "menu"
    if event.sym in (KeySym.SPACE, KeySym.RIGHT):
        return "next"
    if event.sym is KeySym.S:
        return "skip"
    if event.sym is KeySym.P:
        return "pause"
    return ""


def handle_saved_progress_input(
    event: tcod.event.Event,
    state: AppState,
) -> str:
    """Handle input on the SAVED_PROGRESS screen.

    Returns the action:
        - "other_chars" : go to GRAPHIC_NOVEL_MENU
        - "continue" : load save → HUB
        - "menu" : back to main menu
        - "" : no action
    """
    if not isinstance(event, KeyDown):
        return ""
    if event.sym in (KeySym.ESCAPE, KeySym.Q, KeySym.N3):
        return "menu"
    if event.sym is KeySym.N1:
        return "other_chars"
    if event.sym is KeySym.N2:
        return "continue"
    return ""


def handle_save_slot_select_input(
    event: tcod.event.Event,
    state: AppState,
) -> str:
    """Handle input on the SAVE_SLOT_SELECT screen (ADR-0051).

    Returns the action:
        - "select_1" / "select_2" / "select_3" : choose slot
        - "delete_1" / "delete_2" / "delete_3" : delete slot (D key)
        - "back" : return to previous menu (ESC)
        - "" : no action
    """
    if not isinstance(event, KeyDown):
        return ""
    if event.sym in (KeySym.ESCAPE, KeySym.Q):
        return "back"
    if event.sym in (KeySym.N1, KeySym.N2, KeySym.N3):
        slot = int(event.sym.name[1:])  # "N1" → 1
        state.gn_save_slot_selected = slot
        return f"select_{slot}"
    # D + N for delete (Shift+D or just D1/D2/D3)
    if event.sym == getattr(KeySym, "D", None):
        # Plain D — delete currently selected (or last selected)
        if state.gn_save_slot_selected:
            return f"delete_{state.gn_save_slot_selected}"
    return ""
