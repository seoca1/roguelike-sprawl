"""Main menu screen (ADR-0009).

Text-based menu. The Hub is described as a cyberspace construct, but
the main menu itself is a thin real-world UI.

Phase 5+: Uses unified screen shell (engine.layout).
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

# Main menu options (1-indexed)
OPTION_NEW_RUN = 1
OPTION_ARCHIVE = 2
OPTION_SETTINGS = 3


def render_menu(console: tcod.console.Console, t: Translator, state: AppState) -> None:
    """Render the main menu screen with unified layout."""
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

    # Main area: menu options
    options = [
        (OPTION_NEW_RUN, t("menu.new_run")),
        (OPTION_ARCHIVE, t("menu.archive")),
        (OPTION_SETTINGS, t("menu.settings")),
    ]
    y = main_r.y + 2
    for i, (_key, label) in enumerate(options):
        console.print(
            x=main_r.x + 4,
            y=y + i * 2,
            string=f"[{i + 1}] {label}",
            fg=(200, 200, 200),
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
    """Handle input on the menu screen. Returns False to quit."""
    if isinstance(event, KeyDown):
        if event.sym in (KeySym.ESCAPE, KeySym.Q):
            return False
        if event.sym is KeySym.N1:
            state.screen = ScreenKind.HUB
        elif event.sym is KeySym.N2:
            state.message = "Story Archive: (Phase 7+)"
        elif event.sym is KeySym.N3:
            state.message = "Settings: (Phase 7+)"
    return True
