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
                    state.phase_elapsed_ms += delta_s * 1000
                    arc = state.current_arc
                    if state.current_chapter_index < len(arc.chapters):
                        chapter = arc.chapters[state.current_chapter_index]
                        if state.current_phase_index < len(chapter.phases):
                            phase = chapter.phases[state.current_phase_index]
                            if phase.beats and state.current_beat_index < len(phase.beats):
                                beat = phase.beats[state.current_beat_index]
                                text = beat.text_en
                                typed = int(state.phase_elapsed_ms / 30)
                                state.phase_typed_chars = min(typed, len(text))
                                if typed >= len(text) and state.phase_elapsed_ms >= 500:
                                    state.phase_elapsed_ms = 0.0
                                    state.phase_typed_chars = 0
                                    _advance_arc_phase(state)

                _render(
                    root_console, t, portraits, state, _global_prog_registry, _global_ice_registry
                )
                context.present(root_console)

                for event in tcod.event.wait():
                    if isinstance(event, tcod.event.WindowEvent) and event.type == "WindowClose":
                        running = False
                        break
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


def _render_cyberspace_map(console: tcod.console.Console, t: Translator, state: AppState) -> None:
    """Render CYBERSPACE_MAP as a tree view of worlds/sectors/servers."""
    console.clear(bg=(0, 0, 0))
    width = console.width

    title = "CYBERSPACE — World Map"
    console.print(0, 0, "═" * width)
    console.print((width - len(title)) // 2, 0, f" {title} ")
    console.print(0, 1, "─" * width)

    wm = state.world_map
    if wm is None:
        return

    y = 3
    for world_id, world in wm.worlds.items():
        marker = "▸ " if world_id == wm.current_world else "  "
        console.print(x=2, y=y, string=f"{marker}WORLD: {world.name}", fg=(255, 255, 0))
        y += 1
        for sector_id, sector in world.sectors.items():
            s_marker = "→ " if sector_id == wm.current_sector else "  "
            server_count = len(sector.servers)
            console.print(
                x=6, y=y, string=f"{s_marker}SECTOR: {sector.name} [{server_count} servers]", fg=(180, 180, 100)
            )
            y += 1
            for server in sector.servers[:5]:
                sv_marker = "• " if server.id == wm.current_server else "  "
                console.print(x=10, y=y, string=f"{sv_marker}{server.name}", fg=(200, 200, 200))
                y += 1
            if len(sector.servers) > 5:
                console.print(x=10, y=y, string=f"  ... and {len(sector.servers) - 5} more", fg=(100, 100, 100))
                y += 1
        y += 1

    console.print(0, console.height - 1, "═" * width)
    console.print(x=2, y=console.height - 1, string="[ESC] Back to Hub", fg=(128, 128, 128))


def _render_arc_phase(
    console: tcod.console.Console,
    phase: object,
    beat_index: int,
    typed_chars: int,
    beat_elapsed_ms: float,
    phase_elapsed_ms: float,
    translator: Translator,
) -> None:
    """Render an arc phase using phase_view.render_arc_phase."""
    from typing import cast

    from . import phase_view
    from .chapter_cutscene import PhaseData

    phase_view.render_arc_phase(
        console, cast(PhaseData, phase), beat_index, typed_chars, beat_elapsed_ms, phase_elapsed_ms, translator
    )


def _advance_arc_phase(state: AppState) -> None:
    """Advance to the next beat, phase, or chapter in ARC_PHASE."""
    arc = state.current_arc
    if arc is None:
        state.screen = ScreenKind.MENU
        return

    if state.current_chapter_index >= len(arc.chapters):
        state.screen = ScreenKind.MENU
        return

    chapter = arc.chapters[state.current_chapter_index]
    if state.current_phase_index >= len(chapter.phases):
        state.current_chapter_index += 1
        state.current_phase_index = 0
        state.current_beat_index = 0
        state.phase_elapsed_ms = 0.0
        state.phase_typed_chars = 0
        if state.current_chapter_index >= len(arc.chapters):
            state.screen = ScreenKind.MENU
        return

    phase = chapter.phases[state.current_phase_index]
    if state.current_beat_index >= len(phase.beats):
        state.current_phase_index += 1
        state.current_beat_index = 0
        state.phase_elapsed_ms = 0.0
        state.phase_typed_chars = 0
        return

    state.current_beat_index += 1
    state.phase_typed_chars = 0


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
    elif state.screen is ScreenKind.GRAPHIC_NOVEL_MENU:
        from . import graphic_novel_view

        has_save = getattr(state, "has_save", False)
        graphic_novel_view.render_graphic_novel_menu(console, t, state.gn_menu_selected, has_save)
    elif state.screen is ScreenKind.GRAPHIC_NOVEL:
        from . import graphic_novel_view as gn_view
        from .graphic_novel_view import load_background, load_portrait

        scenes = state.gn_scenes
        if scenes and 0 <= state.gn_scene_index < len(scenes):
            scene = scenes[state.gn_scene_index]
            if scene.dialogue and 0 <= state.gn_dialogue_index < len(scene.dialogue):
                dialogue = scene.dialogue[state.gn_dialogue_index]
                bg = None
                if scene.background_id:
                    try:
                        from . import config

                        bg = load_background(config.DATA_DIR / "art", scene.background_id)
                    except Exception:
                        pass
                p_l = None
                p_r = None
                if scene.portrait_left:
                    try:
                        p_l = load_portrait(config.DATA_DIR / "portraits", scene.portrait_left)
                    except Exception:
                        pass
                if scene.portrait_right:
                    try:
                        p_r = load_portrait(config.DATA_DIR / "portraits", scene.portrait_right)
                    except Exception:
                        pass
                typed = gn_view.dialogue_typed_chars(
                    dialogue.duration_ms, state.gn_elapsed_ms, len(dialogue.text_en)
                )
                gn_view.render_scene(
                    console,
                    scene,
                    dialogue,
                    bg,
                    p_l,
                    p_r,
                    t,
                    typed,
                    state.gn_scene_index,
                    len(scenes),
                    paused=state.gn_paused,
                )
            else:
                console.clear(bg=(0, 0, 0))
                console.print(x=2, y=2, string="=== NO DIALOGUE ===", fg=(255, 0, 0))
        else:
            console.clear(bg=(0, 0, 0))
            console.print(x=2, y=2, string="=== NO SCENES LOADED ===", fg=(255, 0, 0))
    elif state.screen is ScreenKind.SAVED_PROGRESS:
        from . import config, save_progress

        save_dir = config.DATA_DIR / "saves"
        summary = save_progress.get_progress_summary(save_dir=save_dir)
        console.clear()
        width = console.width
        title = "당신의 자키" if t.lang == "ko" else "Your Jockey"
        console.print(0, 0, "═" * width)
        console.print((width - len(title)) // 2, 0, f" {title} ")
        console.print(0, 1, "─" * width)
        if not summary.has_save:
            msg = "아직 자키가 없습니다" if t.lang == "ko" else "No save file yet"
            console.print((width - len(msg)) // 2, 8, msg)
            hint = "[1] NEW RUN  [2] 다른 캐릭터  [3] 메인메뉴"
            console.print((width - len(hint)) // 2, 14, hint)
        else:
            lines = save_progress.render_summary_lines(summary, t_lang=t.lang)
            y = 3
            for line in lines:
                console.print(4, y, line)
                y += 1
            y += 1
            console.print(4, y, "─" * 40)
            y += 1
            if t.lang == "ko":
                opts = [
                    "[1] 다른 캐릭터 스토리 보기",
                    "[2] 게임플레이 계속 (HUB)",
                    "[3] 메인메뉴",
                ]
            else:
                opts = [
                    "[1] Other character stories",
                    "[2] Continue gameplay (HUB)",
                    "[3] Main menu",
                ]
            for i, opt in enumerate(opts):
                console.print(4, y + i * 2, opt)
    elif state.screen is ScreenKind.HUB:
        hub_screen.render_hub(console, t, state)
    elif state.screen is ScreenKind.NPC:
        from . import npc_view

        if state.npc_state is not None:
            npc_view.render_npc(console, t, state, state.npc_state)
        else:
            console.clear(bg=(0, 0, 0))
            console.print(x=2, y=2, string="=== NO NPC STATE ===", fg=(255, 0, 0))
    elif state.screen is ScreenKind.ENDING:
        menu_screen.render_ending(console, t, state)
    elif state.screen is ScreenKind.GRAPHIC_NOVEL_ENDING_MENU:
        from . import graphic_novel_view as gn_view

        gn_view.render_graphic_novel_ending_menu(
            console, t, state.gn_mode, state.menu_selected_index
        )
    elif state.screen is ScreenKind.SAVE_SLOT_SELECT:
        from . import save_load_view

        save_load_view.render_save_load(console, state)
    elif state.screen is ScreenKind.EVENT:
        from . import event_view

        if state.active_event is not None:
            event_view.render_event_story(console, t, state, state.active_event)
        else:
            console.clear(bg=(0, 0, 0))
            console.print(x=2, y=2, string="=== NO ACTIVE EVENT ===", fg=(255, 0, 0))
    elif state.screen is ScreenKind.STORY:
        from . import config as config_mod
        from . import story_view as story_screen

        registry = story_screen.StoryRegistry.load(config_mod.DATA_DIR)
        story_screen.render_story(console, state, registry, state.story_aftermath_id)
    elif state.screen is ScreenKind.ARC_PHASE:
        if state.current_arc is None:
            console.clear(bg=(0, 0, 0))
            console.print(x=2, y=2, string="=== NO ARC DATA ===", fg=(255, 0, 0))
            console.print(x=2, y=4, string="Play through CHAPTER first.", fg=(128, 128, 128))
        else:
            arc = state.current_arc
            if state.current_chapter_index < len(arc.chapters):
                chapter = arc.chapters[state.current_chapter_index]
                if state.current_phase_index < len(chapter.phases):
                    phase = chapter.phases[state.current_phase_index]
                    _render_arc_phase(
                        console, phase, state.current_beat_index,
                        state.phase_typed_chars, 0.0, state.phase_elapsed_ms, t
                    )
                else:
                    console.clear(bg=(0, 0, 0))
                    console.print(x=2, y=2, string="Arc complete.", fg=(180, 180, 100))
            else:
                console.clear(bg=(0, 0, 0))
                console.print(x=2, y=2, string="All arcs complete.", fg=(180, 180, 100))
    elif state.screen is ScreenKind.CYBERSPACE_BROWSER:
        from . import cyberspace_browser as cb_screen

        cb_screen.render_cyberspace_browser(console, t, state)
    elif state.screen is ScreenKind.CYBERSPACE_MAP:
        if not hasattr(state, "world_map") or state.world_map is None:
            console.clear(bg=(0, 0, 0))
            console.print(x=2, y=2, string="=== NO WORLD DATA ===", fg=(255, 0, 0))
            console.print(x=2, y=4, string="Start a mission from the Hub first.", fg=(128, 128, 128))
        else:
            _render_cyberspace_map(console, t, state)
    elif state.screen is ScreenKind.CHARACTER_SELECT:
        menu_screen.render_character_select(console, t, state)
    elif state.screen is ScreenKind.CHAPTER:
        from . import chapter_view

        if state.chapter_data:
            chapter_view.render_chapter(
                console, state.chapter_data, t, state.chapter_typed_chars, state.chapter_elapsed_ms
            )
        else:
            console.clear(bg=(0, 0, 0))
            console.print(x=2, y=2, string="=== NO CHAPTER DATA ===", fg=(255, 0, 0))
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
    elif state.screen is ScreenKind.DEATH_SUMMARY:
        from . import death as death_screen

        death_screen.render_death_summary_screen(console, state)
    elif state.screen is ScreenKind.HALL_OF_DEAD:
        from . import death as death_screen

        death_screen.render_hall_of_dead_screen(console, state)
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
            if event.sym in (tcod.event.KeySym.SPACE, tcod.event.KeySym.RETURN, tcod.event.KeySym.RIGHT):
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
