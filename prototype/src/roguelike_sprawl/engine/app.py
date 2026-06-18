"""Main application entry point.

Phase 5: screen state machine (Menu → Hub → Matrix → back).
"""

from __future__ import annotations

import sys

import tcod.console
import tcod.context
import tcod.tileset

from ..audio import sound_manager
from ..combat.registry import IceRegistry, ProgramRegistry
from ..i18n import Translator
from ..missions import JobBoard
from ..portraits import PortraitManager
from . import combat_view, config, matrix_view, story_cinematic
from . import hub as hub_screen
from . import menu as menu_screen
from .state import AppState, ScreenKind


def _load_job_board() -> JobBoard:
    """Load the mission JSON if present; return an empty board otherwise."""
    return JobBoard.load(config.DATA_DIR / "missions" / "missions.json")


def main() -> int:
    """Run the game. Returns exit code (0 = success)."""
    if not config.FONT_PATH.exists() and config.find_ttf_font() is None:
        sys.stderr.write(
            f"ERROR: No font found.\n"
            f"  Bitmap: {config.FONT_PATH}\n"
            f"  TTF: search system fonts\n"
            f"Run: make download-font\n"
        )
        return 1

    from .font_loader import load_font

    tileset, is_ttf = load_font()

    t = Translator(config.DEFAULT_LANGUAGE, data_dir=config.DATA_DIR / "i18n")
    portraits = PortraitManager(data_dir=config.DATA_DIR / "portraits")
    prog_registry = ProgramRegistry.load(config.DATA_DIR / "programs" / "programs.json")
    ice_registry = IceRegistry.load(config.DATA_DIR / "combat" / "ice_types.json")

    state = AppState()
    state.job_board = _load_job_board()

    # Store registries for combat (passed to _render/_handle_input)
    _global_prog_registry = prog_registry
    _global_ice_registry = ice_registry

    with tcod.context.new(
        columns=config.SCREEN_WIDTH,
        rows=config.SCREEN_HEIGHT,
        tileset=tileset,  # type: ignore[arg-type]
        title=config.SCREEN_TITLE,
        vsync=True,
    ) as context:
        root_console = tcod.console.Console(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, order="F")

        running = True
        while running:
            _render(root_console, t, portraits, state, _global_prog_registry, _global_ice_registry)
            context.present(root_console)

            for event in tcod.event.wait():
                if not _handle_input(event, state, _global_prog_registry, _global_ice_registry):
                    running = False
                    break

        return 0


def _render(
    console: tcod.console.Console,
    t: Translator,
    portraits: PortraitManager,
    state: AppState,
    prog_registry: ProgramRegistry,
    ice_registry: IceRegistry,
) -> None:
    """Render the current screen. ``portraits`` is reserved for later use."""
    _ = portraits
    if state.screen is ScreenKind.MENU:
        menu_screen.render_menu(console, t, state)
    elif state.screen is ScreenKind.HUB:
        hub_screen.render_hub(console, t, state)
    elif state.screen is ScreenKind.MATRIX:
        if state.matrix is not None:
            layout = matrix_view.get_layout(state.matrix)
        else:
            layout = {}
        matrix_view.render_matrix(console, t, state, layout, prog_registry, ice_registry)
    elif state.screen is ScreenKind.COMBAT:
        if state.combat_state is not None:
            combat_view.render_combat(console, t, state, state.combat_state)
        else:
            console.clear(bg=(0, 0, 0))
            console.print(x=2, y=2, string="=== COMBAT ERROR ===", fg=(255, 0, 0))
            console.print(x=2, y=4, string="No combat state loaded", fg=(128, 128, 128))
    elif state.screen is ScreenKind.CINEMATIC:
        if state.cinematic_state is not None:
            # Calculate elapsed time (placeholder: use demo_elapsed_s)
            elapsed_ms = int(state.demo_elapsed_s * 1000)
            story_cinematic.render_cinematic(console, t, state, state.cinematic_state, elapsed_ms)
        else:
            console.clear(bg=(0, 0, 0))
            console.print(x=2, y=2, string="=== CINEMATIC ERROR ===", fg=(255, 0, 0))
            console.print(x=2, y=4, string="No cinematic state loaded", fg=(128, 128, 128))
    elif state.screen is ScreenKind.DEATH:
        from . import death as death_screen

        death_screen.render_death_screen(console, state)
    elif state.screen is ScreenKind.JACK_OUT:
        from . import jack_out_view

        jack_out_view.render_jack_out(console, state)
    elif state.screen is ScreenKind.REWARD:
        from . import reward_view

        reward_view.render_reward(console, state)
    elif state.screen is ScreenKind.DEBRIEF:
        from . import debrief_view

        debrief_view.render_debrief(console, state)


def _handle_input(
    event: object,
    state: AppState,
    prog_registry: ProgramRegistry,
    ice_registry: IceRegistry,
) -> bool:
    """Dispatch an event to the current screen's handler. False = quit."""
    import tcod.event

    # Global hotkeys (work on all screens)
    if isinstance(event, tcod.event.KeyDown):
        if event.sym is tcod.event.KeySym.M:
            muted = sound_manager.toggle_mute()
            label = "MUTED" if muted else "UNMUTED"
            state.status_messages.append(f">>> Audio {label}")
            return True
        if event.sym in (
            tcod.event.KeySym.EQUALS,
            tcod.event.KeySym.PLUS,
            tcod.event.KeySym.KP_PLUS,
        ):
            from .settings_ui import adjust_volume

            new_vol = adjust_volume(+0.1)
            state.status_messages.append(f">>> Volume: {int(new_vol * 100)}%")
            return True
        if event.sym in (tcod.event.KeySym.MINUS, tcod.event.KeySym.KP_MINUS):
            from .settings_ui import adjust_volume

            new_vol = adjust_volume(-0.1)
            state.status_messages.append(f">>> Volume: {int(new_vol * 100)}%")
            return True

        # Per-category sound toggles
        # T = theme, E = events, K = keys, B = combat, V = movement, I = items
        from ..audio.config import SoundCategory
        from .settings_ui import toggle_category

        category_by_key = {
            tcod.event.KeySym.T: SoundCategory.THEME,
            tcod.event.KeySym.E: SoundCategory.EVENTS,
            tcod.event.KeySym.K: SoundCategory.KEYS,
            tcod.event.KeySym.B: SoundCategory.COMBAT,
            tcod.event.KeySym.V: SoundCategory.MOVEMENT,
            tcod.event.KeySym.I: SoundCategory.ITEMS,
        }
        if event.sym in category_by_key:
            category = category_by_key[event.sym]
            new_state = toggle_category(category)
            label = "ON" if new_state else "OFF"
            state.status_messages.append(f">>> Sound category '{category.value}' toggled: {label}")
            return True

    if state.screen is ScreenKind.MENU:
        return menu_screen.handle_menu_input(event, state)  # type: ignore[arg-type]
    if state.screen is ScreenKind.HUB:
        return hub_screen.handle_hub_input(event, state)  # type: ignore[arg-type]
    if state.screen is ScreenKind.MATRIX:
        return matrix_view.handle_matrix_input(event, state, prog_registry, ice_registry)  # type: ignore[arg-type]
    if state.screen is ScreenKind.COMBAT:
        if state.combat_state is not None:
            return combat_view.handle_combat_input(event, state, state.combat_state)  # type: ignore[arg-type]
        return True
    if state.screen is ScreenKind.CINEMATIC:
        if state.cinematic_state is not None:
            return story_cinematic.handle_cinematic_input(event, state, state.cinematic_state)
        return True
    if state.screen is ScreenKind.DEATH:
        from . import death as death_screen

        return death_screen.handle_death_input(event, state)  # type: ignore[arg-type]
    if state.screen is ScreenKind.JACK_OUT:
        from . import jack_out_view

        return jack_out_view.handle_jack_out_input(event, state)  # type: ignore[arg-type]
    if state.screen is ScreenKind.REWARD:
        from . import reward_view

        return reward_view.handle_reward_input(event, state)  # type: ignore[arg-type]
    if state.screen is ScreenKind.DEBRIEF:
        from . import debrief_view

        return debrief_view.handle_debrief_input(event, state)  # type: ignore[arg-type]
    return True


if __name__ == "__main__":
    sys.exit(main())
