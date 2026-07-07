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
from . import combat_view, config, dungeon_view, matrix_view, story_cinematic
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

    try:
        return _main_inner()
    except Exception as exc:  # pragma: no cover
        from . import crash_reporter

        crash_reporter.report_crash(exc, None, "main() top-level")
        sys.stderr.write(
            f"CRASH: {exc.__class__.__name__}: {exc}\n"
            f"Crash log: {crash_reporter.crash_report_path()}\n"
        )
        return 1


def _main_inner() -> int:
    """Inner main function where crash reporter is not yet active."""
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
            try:
                _render(
                    root_console, t, portraits, state, _global_prog_registry, _global_ice_registry
                )
                context.present(root_console)

                for event in tcod.event.wait():
                    if not _handle_input(event, state, _global_prog_registry, _global_ice_registry):
                        running = False
                        break
            except Exception as exc:  # pragma: no cover
                from . import crash_reporter

                crash_reporter.report_crash(exc, state, "game loop")
                sys.stderr.write(
                    f"CRASH during loop: {exc.__class__.__name__}: {exc}\n"
                    f"Crash log: {crash_reporter.crash_report_path()}\n"
                )
                return 1

        return 0


def _maybe_spawn_jackin_glitch(state: AppState) -> None:
    """Spawn a one-shot jack-in glitch VFX when toggling into dungeon mode.

    ADR-0060 Phase 1.5: this provides the cyberspace atmosphere that the
    map no longer carries. Without 3D cyberspace glyphs, the visual
    transition is the only \"cyberspace\" hint at the map level.
    """
    try:
        from ..combat.effects import spawn_jackin_glitch

        spawn_jackin_glitch(state.combat_effects)
    except ImportError:
        # Combat effects not loaded yet; fall back to a status hint only.
        state.status_messages.append(">>> Jacking into the matrix...")


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
    # BGM: play appropriate theme for the current screen
    try:
        from . import original_story

        original_story.update_screen_theme(state.screen.value, state.sound_config)
    except Exception:
        pass
    if state.screen is ScreenKind.MENU:
        menu_screen.render_menu(console, t, state)
    elif state.screen is ScreenKind.HUB:
        hub_screen.render_hub(console, t, state)
    elif state.screen is ScreenKind.MATRIX:
        if state.dungeon_mode:
            # ADR-0060 Phase 1: NetHack-style 2D room grid
            dungeon_view.render_dungeon_matrix(console, t, state, prog_registry, ice_registry)
        else:
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
    elif state.screen is ScreenKind.SAVE_LOAD:
        from . import save_load_view

        save_load_view.render_save_load(console, state)
    elif state.screen is ScreenKind.HELP:
        from . import help_view

        help_view.render_help(console, t, state)
    elif state.screen is ScreenKind.SETTINGS:
        from . import settings_view

        settings_view.render_settings(console, t, state)
    elif state.screen is ScreenKind.SALVATION_INTRO:
        from . import salvation_view

        salvation_view.render_salvation_intro(console, t, state)
    elif state.screen is ScreenKind.SALVATION_EPILOGUE:
        from . import salvation_view

        salvation_view.render_salvation_epilogue(console, t, state)
    elif state.screen is ScreenKind.SALVATION_ENDING:
        from . import salvation_view

        salvation_view.render_salvation_ending(console, t, state)


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
        # F5: quick save (slot 1)
        if event.sym is tcod.event.KeySym.F5:
            from .save_manager import SaveManager, SaveSlotEmptyError

            manager = SaveManager()
            try:
                meta = manager.save(1, state, elapsed_seconds=int(state.demo_elapsed_s))
                state.status_messages.append(f">>> Quicksaved to slot 1 ({meta.size_bytes} bytes)")
            except Exception as e:
                state.status_messages.append(f">>> Quicksave failed: {e}")
            return True

        # F9: quick load (slot 1)
        if event.sym is tcod.event.KeySym.F9:
            from .save_manager import SaveError, SaveManager, SaveSlotEmptyError

            manager = SaveManager()
            try:
                manager.restore_state(1, state)
            except SaveSlotEmptyError:
                state.status_messages.append(">>> Quickload failed: slot 1 is empty")
            except SaveError as e:
                state.status_messages.append(f">>> Quickload failed: {e}")
            return True

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
        # ADR-0060 Phase 1: `D` key toggles NetHack-style dungeon view
        # (dungeon_view) vs abstract node graph (matrix_view).
        if (
            isinstance(event, tcod.event.KeyDown)
            and event.sym is tcod.event.KeySym.D
            and not (event.mod & tcod.event.Modifier.SHIFT)
        ):
            state.dungeon_mode = not state.dungeon_mode
            label = "DUNGEON (NetHack)" if state.dungeon_mode else "MATRIX (graph)"
            state.status_messages.append(f">>> View mode: {label}")
            if state.dungeon_mode:
                _maybe_spawn_jackin_glitch(state)
            return True
        if state.dungeon_mode:
            return dungeon_view.handle_dungeon_input(
                event,  # type: ignore[arg-type]
                state,
                prog_registry,
                ice_registry,
            )
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
    if state.screen is ScreenKind.SAVE_LOAD:
        from . import save_load_view

        return save_load_view.handle_save_load_input(event, state)  # type: ignore[arg-type]
    if state.screen is ScreenKind.HELP:
        from . import help_view

        return help_view.handle_help_input(event, state)  # type: ignore[arg-type,return-value]
    if state.screen is ScreenKind.SETTINGS:
        from . import settings_view

        return settings_view.handle_settings_input(event, state)  # type: ignore[arg-type,return-value]
    if state.screen is ScreenKind.SALVATION_INTRO:
        from . import salvation_view

        return salvation_view.handle_salvation_intro_input(event, state)  # type: ignore[arg-type]
    if state.screen is ScreenKind.SALVATION_EPILOGUE:
        from . import salvation_view

        return salvation_view.handle_salvation_epilogue_input(event, state)  # type: ignore[arg-type]
    if state.screen is ScreenKind.SALVATION_ENDING:
        from . import salvation_view

        return salvation_view.handle_salvation_ending_input(event, state)  # type: ignore[arg-type]
    return True


if __name__ == "__main__":
    sys.exit(main())
