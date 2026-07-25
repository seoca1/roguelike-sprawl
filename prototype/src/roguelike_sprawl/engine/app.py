"""Main application entry point.

Phase 5: screen state machine (Menu → Hub → Matrix → back).
"""

from __future__ import annotations

import sys
import time

import tcod.console
import tcod.context
import tcod.tileset

from ..audio import sound_manager
from ..combat.registry import IceRegistry, ProgramRegistry
from ..combat.state import step_combat
from ..i18n import Translator
from ..missions import JobBoard
from ..portraits import PortraitManager
from . import combat_view, config, dungeon_view, hacking_view, story_cinematic
from . import hub as hub_screen
from . import menu as menu_screen
from .combat_tick import maybe_boss_phase_transition
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
        last_time = time.monotonic()
        while running:
            try:
                now = time.monotonic()
                delta_s = now - last_time
                last_time = now
                if state.screen is ScreenKind.GRAPHIC_NOVEL and state.gn_scenes:
                    state.gn_elapsed_ms += delta_s * 1000
                    if not state.gn_paused:
                        scenes = state.gn_scenes
                        if scenes and 0 <= state.gn_scene_index < len(scenes):
                            scene = scenes[state.gn_scene_index]
                            if scene.dialogue and 0 <= state.gn_dialogue_index < len(
                                scene.dialogue
                            ):
                                dialogue = scene.dialogue[state.gn_dialogue_index]
                                if state.gn_elapsed_ms >= dialogue.duration_ms:
                                    if state.gn_dialogue_index < len(scene.dialogue) - 1:
                                        state.gn_dialogue_index += 1
                                        state.gn_elapsed_ms = 0.0
                                    elif state.gn_scene_index < len(scenes) - 1:
                                        state.gn_scene_index += 1
                                        state.gn_dialogue_index = 0
                                        state.gn_elapsed_ms = 0.0
                                    else:
                                        state.screen = ScreenKind.MENU
                if state.screen is ScreenKind.CHAPTER and state.chapter_data:
                    state.chapter_elapsed_ms += delta_s * 1000
                    cd = state.chapter_data
                    typed = int(state.chapter_elapsed_ms / cd.char_delay_ms)
                    state.chapter_typed_chars = min(typed, len(cd.excerpt_en))
                    if state.chapter_elapsed_ms >= cd.duration_ms:
                        if state.current_arc is not None:
                            state.current_chapter_index = 0
                            state.current_phase_index = 0
                            state.current_beat_index = 0
                            state.phase_elapsed_ms = 0.0
                            state.phase_typed_chars = 0
                            state.screen = ScreenKind.ARC_PHASE
                        else:
                            state.screen = ScreenKind.HUB

                if state.screen is ScreenKind.ARC_PHASE and state.current_arc is not None:
                    arc = state.current_arc
                    if state.current_chapter_index < len(arc.chapters):
                        chapter = arc.chapters[state.current_chapter_index]
                        if state.current_phase_index < len(chapter.phases):
                            phase = chapter.phases[state.current_phase_index]
                            if phase.beats:
                                if state.current_beat_index < len(phase.beats):
                                    state.phase_elapsed_ms += delta_s * 1000
                                    beat = phase.beats[state.current_beat_index]
                                    text = beat.text_en
                                    typed = int(state.phase_elapsed_ms / 30)
                                    state.phase_typed_chars = min(typed, len(text))
                                    typecomplete_ms = len(text) * 30
                                    if state.phase_elapsed_ms >= typecomplete_ms + 50:
                                        state.phase_elapsed_ms = 0.0
                                        state.phase_typed_chars = 0
                                        _advance_arc_phase(state)
                                else:
                                    # All beats done — accumulate elapsed time so SPACE advances
                                    state.phase_elapsed_ms += delta_s * 1000

                if state.screen is ScreenKind.COMBAT and state.combat_state is not None:
                    step_combat(state.combat_state)
                    # Phase H: pass registries so B-3 spawn_minions can build ICE
                    maybe_boss_phase_transition(
                        state,
                        ice_registry=ice_registry,
                        program_registry=prog_registry,
                    )

                if state.screen is ScreenKind.HACK:
                    hacking_view.step_hack(state, delta_s)

                _render(
                    root_console, t, portraits, state, _global_prog_registry, _global_ice_registry
                )
                context.present(root_console)

                for event in tcod.event.wait():
                    if isinstance(event, tcod.event.WindowEvent) and event.type == "WindowClose":
                        running = False
                        break
                    result = _handle_input(
                        event, state, _global_prog_registry, _global_ice_registry
                    )
                    if not result:
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


def _render_cyberspace_map(console: tcod.console.Console, t: Translator, state: AppState) -> None:
    """Render CYBERSPACE_MAP (Phase D-2: thin wrapper, see cyberspace_map_view)."""
    from .cyberspace_map_view import render_cyberspace_map as _do_render

    _do_render(console, state)


def _advance_arc_phase(state: AppState) -> None:
    """Advance arc phase (Phase D-2: thin wrapper, see arc_phase)."""
    from .arc_phase import advance_arc_phase as _do_advance

    _do_advance(state)


def _render(
    console: tcod.console.Console,
    t: Translator,
    portraits: PortraitManager,
    state: AppState,
    prog_registry: ProgramRegistry,
    ice_registry: IceRegistry,
) -> None:
    """Render the current screen (Phase D-2 deep2: dispatch table).

    ``portraits`` is reserved for later use. Actual rendering logic lives
    in screen_dispatch.py — this function just sets BGM theme + delegates.
    """
    _ = portraits
    # BGM: play appropriate theme for the current screen
    try:
        from . import original_story

        original_story.update_screen_theme(state.screen.value, state.sound_config)
    except Exception:
        pass
    from .screen_dispatch import render_current_screen

    render_current_screen(
        console, t, state,
        prog_registry=prog_registry,
        ice_registry=ice_registry,
    )



def _handle_global_hotkeys(
    event: object,
    state: AppState,
) -> bool | None:
    """Phase D-2 deep: process global hotkeys (work on all screens).

    Returns:
        True: hotkey handled (event consumed)
        False: global quit signal
        None: not a hotkey, defer to per-screen handler
    """
    import tcod.event
    if not isinstance(event, tcod.event.KeyDown):
        return None

    if event.sym is tcod.event.KeySym.F5:
        from .save_manager import SaveManager, SaveSlotEmptyError

        manager = SaveManager()
        try:
            meta = manager.save(1, state, elapsed_seconds=int(state.demo_elapsed_s))
            state.status_messages.append(
                f">>> Quicksaved to slot 1 ({meta.size_bytes} bytes)"
            )
        except Exception as e:
            state.status_messages.append(f">>> Quicksave failed: {e}")
        return True

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
        state.status_messages.append(
            f">>> Sound category '{category.value}' toggled: {label}"
        )
        return True

    return None


def _handle_input(
    event: object,
    state: AppState,
    prog_registry: ProgramRegistry,
    ice_registry: IceRegistry,
) -> bool:
    """Dispatch an event to the current screen's handler. False = quit.

    Phase D-2 deep: delegates global hotkeys to _handle_global_hotkeys.
    """
    global_result = _handle_global_hotkeys(event, state)
    if global_result is not None:
        return global_result

    if state.screen is ScreenKind.MENU:
        return menu_screen.handle_menu_input(event, state)  # type: ignore[arg-type]
    if state.screen is ScreenKind.GRAPHIC_NOVEL_MENU:
        return menu_screen.handle_graphic_novel_menu_input(event, state)  # type: ignore[arg-type]
    if state.screen is ScreenKind.GRAPHIC_NOVEL:
        action = menu_screen.handle_graphic_novel_input(event, state)  # type: ignore[arg-type]
        if action == "menu":
            state.screen = ScreenKind.MENU
            return True
        if action == "next":
            scenes = state.gn_scenes
            if scenes and 0 <= state.gn_scene_index < len(scenes):
                scene = scenes[state.gn_scene_index]
                if scene.dialogue and state.gn_dialogue_index < len(scene.dialogue) - 1:
                    state.gn_dialogue_index += 1
                    state.gn_elapsed_ms = 0.0
                elif state.gn_scene_index < len(scenes) - 1:
                    state.gn_scene_index += 1
                    state.gn_dialogue_index = 0
                    state.gn_elapsed_ms = 0.0
                else:
                    state.screen = ScreenKind.MENU
            else:
                state.screen = ScreenKind.MENU
            return True
        if action == "skip":
            scenes = state.gn_scenes
            if scenes and state.gn_scene_index < len(scenes) - 1:
                state.gn_scene_index += 1
                state.gn_dialogue_index = 0
                state.gn_elapsed_ms = 0.0
            else:
                state.screen = ScreenKind.MENU
            return True
        if action == "pause":
            state.gn_paused = not state.gn_paused
            return True
        return True
    if state.screen is ScreenKind.SAVED_PROGRESS:
        return menu_screen.handle_saved_progress_input(event, state)  # type: ignore[arg-type]
    if state.screen is ScreenKind.HUB:
        return hub_screen.handle_hub_input(event, state)  # type: ignore[arg-type]
    if state.screen is ScreenKind.CHAPTER:
        from . import chapter_view

        chapter_view.handle_chapter_input(event, state)
        return True
    if state.screen is ScreenKind.CHARACTER_SELECT:
        menu_screen.handle_character_select_input(event, state)
        return True
    if state.screen is ScreenKind.ENDING:
        menu_screen.handle_ending_input(event, state)
        return True
    if state.screen is ScreenKind.GRAPHIC_NOVEL_ENDING_MENU:
        import tcod.event

        if isinstance(event, tcod.event.KeyDown):
            if event.sym in (tcod.event.KeySym.ESCAPE, tcod.event.KeySym.Q):
                state.screen = ScreenKind.MENU
                return True
        return True
    if state.screen is ScreenKind.SAVE_SLOT_SELECT:
        from . import save_load_view

        return save_load_view.handle_save_load_input(event, state)  # type: ignore[arg-type]
    if state.screen is ScreenKind.EVENT:
        from . import event_view

        if state.active_event is not None:
            return event_view.handle_event_input(event, state, state.active_event)  # type: ignore[arg-type]
        return True
    if state.screen is ScreenKind.STORY:
        from . import story_view as story_screen

        return story_screen.handle_story_input(event, state)
    if state.screen is ScreenKind.ARC_PHASE:
        import tcod.event

        if isinstance(event, tcod.event.KeyDown):
            if event.sym in (tcod.event.KeySym.ESCAPE, tcod.event.KeySym.Q):
                state.screen = ScreenKind.MENU
                return True
            if event.sym in (
                tcod.event.KeySym.SPACE,
                tcod.event.KeySym.RETURN,
                tcod.event.KeySym.RIGHT,
            ):
                _advance_arc_phase(state)
                return True
            if event.sym in (tcod.event.KeySym.S,):
                state.phase_elapsed_ms = float("inf")
                state.phase_typed_chars = 9999
                _advance_arc_phase(state)
                return True
        return True
    if state.screen is ScreenKind.CYBERSPACE_BROWSER:
        from . import cyberspace_browser as cb_screen

        return cb_screen.handle_browser_input(event, state)  # type: ignore[arg-type]
    if state.screen is ScreenKind.CYBERSPACE_MAP:
        import tcod.event

        if isinstance(event, tcod.event.KeyDown):
            if event.sym in (tcod.event.KeySym.ESCAPE, tcod.event.KeySym.Q):
                state.screen = ScreenKind.MENU
                return True
        return True
    if state.screen is ScreenKind.NPC:
        from . import npc_view

        if state.npc_state is not None:
            npc_view.handle_npc_input(event, state, state.npc_state)  # type: ignore[arg-type]
        return True
    if state.screen is ScreenKind.HACK:
        hacking_view.handle_hack_input(event, state)  # type: ignore[arg-type]
        return True
    if state.screen is ScreenKind.MATRIX:
        return dungeon_view.handle_dungeon_input(
            event,  # type: ignore[arg-type]
            state,
            prog_registry,
            ice_registry,
        )
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
    if state.screen is ScreenKind.DEATH_SUMMARY:
        from . import death as death_screen

        return death_screen.handle_death_summary_input(event, state)  # type: ignore[arg-type]
    if state.screen is ScreenKind.HALL_OF_DEAD:
        from . import death as death_screen

        return death_screen.handle_hall_of_dead_input(event, state)  # type: ignore[arg-type]
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
