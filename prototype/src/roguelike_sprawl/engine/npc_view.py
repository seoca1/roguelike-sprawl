"""NPC event screen: render and handle NPC dialogues.

A dedicated screen for NPC encounters with dialogue trees and player choices.
"""

from __future__ import annotations

import tcod.console
import tcod.event
from tcod.event import KeyDown, KeySym

from ..audio import safe_play
from ..i18n import Translator
from .input_utils import is_confirm_key
from .layout import (
    Region,
    RegionId,
    clear_region,
    draw_controls,
    draw_dividers,
    draw_footer,
    draw_title,
    make_shell,
)
from .npc_event import ChoiceEffect, DialogueChoice, NPCState
from .state import AppState, ScreenKind
from .status_panel import render_status_panel


def render_npc(
    console: tcod.console.Console,
    t: Translator,
    state: AppState,
    npc_state: NPCState,
) -> None:
    """Render the NPC event screen."""
    shell = make_shell()
    title_r = shell[RegionId.TITLE]
    main_r = shell[RegionId.MAIN]
    ctrl_r = shell[RegionId.CONTROLS]
    foot_r = shell[RegionId.FOOTER]
    panel_r = shell[RegionId.STATUS_PANEL]

    # Clear and draw dividers
    for r in shell.values():
        clear_region(console, r)
    draw_dividers(console, shell)

    # Title
    draw_title(
        console,
        title_r,
        title=f"NPC ENCOUNTER — {npc_state.event.npc_name}",
        subtitle=npc_state.event.description,
    )

    # Persistent status panel
    render_status_panel(console, state, panel_r)

    # Main area: dialogue
    _draw_dialogue(console, main_r, npc_state, state)

    # Controls
    draw_controls(
        console,
        ctrl_r,
        lines=[
            "↑↓ Select Choice  ENTER Confirm  ESC Leave",
            "1-9 Quick Select",
        ],
    )

    # Footer
    draw_footer(
        console,
        foot_r,
        text=f"Step {state.demo_step}  T+{state.demo_elapsed_s:.1f}s",
        status_messages=state.status_messages,
    )


def _draw_dialogue(
    console: tcod.console.Console,
    main: Region,
    npc_state: NPCState,
    state: AppState,
) -> None:
    """Draw the current dialogue line and choices."""
    line = npc_state.event.get_line(npc_state.current_line_index)
    if line is None:
        return

    x = main.x + 2
    y = main.y + 1

    # NPC portrait
    if line.portrait:
        console.print(x=x, y=y, string=line.portrait, fg=(0, 255, 255))
        # Use Korean speaker name if available
        from . import config
        from .font_loader import is_korean_capable

        speaker_name = line.speaker
        if (
            config.LANGUAGE_MODE in ("ko", "both")
            and is_korean_capable()
            and hasattr(line, "speaker_ko")
            and line.speaker_ko
        ):
            speaker_name = f"{line.speaker} ({line.speaker_ko})"
        console.print(x=x + 5, y=y, string=speaker_name, fg=(255, 255, 0))
        y += 1
        # Separator
        console.print(x=x, y=y, string="=" * (main.w - 4), fg=(80, 80, 80))
        y += 2

    # Dialogue text (wrap manually for simplicity)
    text = line.text
    max_width = main.w - 6
    words = text.split()
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 > max_width:
            console.print(x=x, y=y, string=current_line, fg=(200, 200, 200))
            y += 1
            current_line = word
        else:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
    if current_line:
        console.print(x=x, y=y, string=current_line, fg=(200, 200, 200))
        y += 2

    # Korean subtitle (if available and enabled)
    from . import config
    from .font_loader import is_korean_capable

    if config.LANGUAGE_MODE in ("ko", "both") and is_korean_capable() and line.text_ko:
        text_ko = line.text_ko
        words_ko = text_ko.split()
        current_ko = ""
        for word in words_ko:
            if len(current_ko) + len(word) + 1 > max_width:
                console.print(x=x, y=y, string=current_ko, fg=(255, 220, 100))
                y += 1
                current_ko = word
            else:
                if current_ko:
                    current_ko += " " + word
                else:
                    current_ko = word
        if current_ko:
            console.print(x=x, y=y, string=current_ko, fg=(255, 220, 100))
        y += 2

    # Choices
    if line.choices:
        console.print(x=x, y=y, string="What do you say?", fg=(180, 180, 180))
        y += 2

        # Initialize selection index
        if not hasattr(state, "npc_choice_index"):
            state.npc_choice_index = 0

        for i, choice in enumerate(line.choices):
            is_selected = i == state.npc_choice_index
            cursor = ">" if is_selected else " "
            fg = (0, 255, 255) if is_selected else (200, 200, 200)
            # Use Korean if available
            choice_text = choice.text
            if config.LANGUAGE_MODE == "ko" and choice.text_ko and is_korean_capable():
                choice_text = choice.text_ko
            console.print(
                x=x,
                y=y + i,
                string=f"  {cursor} [{choice.key}] {choice_text}",
                fg=fg,
            )
    else:
        # No choices: any key continues
        y += 1
        console.print(
            x=x,
            y=y,
            string=">> Press any key to continue...",
            fg=(128, 128, 128),
        )


def handle_npc_input(
    event: tcod.event.Event,
    state: AppState,
    npc_state: NPCState,
) -> bool:
    """Handle input on NPC screen. Returns False to quit."""
    if not isinstance(event, KeyDown):
        return True

    if event.sym is KeySym.Q:
        return False

    if event.sym is KeySym.ESCAPE:
        # Leave NPC encounter
        npc_state.finished = True
        state.status_messages.append(">>> Left NPC encounter")
        state.screen = ScreenKind.MATRIX
        return True

    line = npc_state.event.get_line(npc_state.current_line_index)
    if line is None:
        return True

    # Initialize choice index
    if not hasattr(state, "npc_choice_index"):
        state.npc_choice_index = 0

    # Navigation
    if event.sym is KeySym.UP:
        if line.choices:
            state.npc_choice_index = max(0, state.npc_choice_index - 1)
            safe_play("ui/menu_select")
        return True

    if event.sym is KeySym.DOWN:
        if line.choices:
            state.npc_choice_index = min(len(line.choices) - 1, state.npc_choice_index + 1)
        return True

    # Confirm with ENTER or SPACE
    if is_confirm_key(event.sym):
        if line.choices and 0 <= state.npc_choice_index < len(line.choices):
            safe_play("ui/menu_confirm")
            _execute_choice(state, npc_state, line.choices[state.npc_choice_index])
        else:
            safe_play("story/dialogue_advance")
            _advance_dialogue(state, npc_state)
        return True

    # Quick select with number key
    if line.choices and event.sym.name.startswith("N"):
        try:
            num = int(event.sym.name[1:])
            if 1 <= num <= len(line.choices):
                _execute_choice(state, npc_state, line.choices[num - 1])
        except (ValueError, IndexError):
            pass
        return True

    return True


def _execute_choice(state: AppState, npc_state: NPCState, choice: DialogueChoice) -> None:
    """Execute a player choice."""
    state.status_messages.append(f">>> {choice.text}")

    if choice.log_message:
        state.status_messages.append(f">>> {choice.log_message}")

    # Handle effect
    if choice.effect is ChoiceEffect.GOODBYE:
        npc_state.finished = True
        state.screen = ScreenKind.MATRIX
        state.npc_state = None
    elif choice.effect is ChoiceEffect.GAIN_INFO and "info" in choice.effect_data:
        info = choice.effect_data["info"]
        state.status_messages.append(f">>> Learned: {info}")
        _advance_dialogue(state, npc_state)
    elif choice.effect is ChoiceEffect.CONTINUE:
        if choice.response:
            state.status_messages.append(f">>> {npc_state.event.npc_name}: {choice.response}")
        _advance_dialogue(state, npc_state)
    else:
        _advance_dialogue(state, npc_state)

    # If dialogue ended naturally, clear npc_state
    if npc_state.finished and state.screen is ScreenKind.MATRIX:
        state.npc_state = None
        # Check for event story trigger after NPC dialogue
        _check_post_npc_event(state, npc_state)


def _check_post_npc_event(state: AppState, npc_state: NPCState) -> None:
    """Check if an event story should trigger after NPC dialogue."""
    from .event_story import EventRegistry, EventState, EventTrigger, check_event_trigger

    if not hasattr(state, "_event_registry") or state._event_registry is None:
        state._event_registry = EventRegistry()

    event = check_event_trigger(
        state,
        registry=state._event_registry,
        trigger=EventTrigger.NPC_GREETING,
        trigger_id=npc_state.event.id,
    )
    if event is not None:
        state.active_event = EventState(event=event)
        state.screen = ScreenKind.EVENT


def _advance_dialogue(state: AppState, npc_state: NPCState) -> None:
    """Advance to next dialogue line."""
    line = npc_state.event.get_line(npc_state.current_line_index)
    if line is None:
        return

    if line.next_line_index is not None:
        npc_state.current_line_index = line.next_line_index
    elif npc_state.current_line_index + 1 < len(npc_state.event.lines):
        npc_state.current_line_index += 1
    else:
        # End of dialogue
        npc_state.finished = True
        state.screen = ScreenKind.MATRIX

        # Advance RunState: if we're on MEET_NPC stage, talking to
        # the NPC satisfies the objective.
        from ..run import check_npc_talk_complete, ensure_run_state

        run_state = ensure_run_state(state)
        if check_npc_talk_complete(run_state):
            run_state.mark_advance()
            state.status_messages.append(f">>> Stage complete: {run_state.current_info().title}")

    # Reset choice index
    state.npc_choice_index = 0
