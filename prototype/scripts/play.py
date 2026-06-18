"""Quick playthrough demo — runs the game in auto-pilot mode.

Single command:
    uv run python scripts/play.py

The script initializes the full game state, then auto-progresses
through the screen state machine (Menu → Hub → Matrix → Hub cycle)
rendering every frame to stdout. Default duration is 30 seconds.

Options:
    --duration N      Total seconds (default 30)
    --step-delay D    Seconds per frame (default 0.4)
    --no-clear        Don't clear the screen between frames
    --lang {en,ko}    UI language (default en)
    --seed N          Mission seed (default 42)
    --mission N       Which mission to play (1=first, default 1)
    --show-controls   Print controls hint at start
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import tcod.console

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from roguelike_sprawl.engine import hub, matrix_view, menu, story_view
from roguelike_sprawl.engine.state import AppState, ScreenKind
from roguelike_sprawl.engine.story_view import StoryRegistry
from roguelike_sprawl.i18n import Translator
from roguelike_sprawl.matrix.exploration import ExplorationState
from roguelike_sprawl.matrix.generator import MatrixGenerator
from roguelike_sprawl.matrix.ppl import calculate_ppl
from roguelike_sprawl.matrix.zdr import node_status, node_zdr
from roguelike_sprawl.missions import JobBoard


def _setup(args: argparse.Namespace) -> tuple[AppState, Translator, StoryRegistry]:
    """Initialize the full game state from data files."""
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    t = Translator(args.lang, data_dir=data_dir / "i18n")
    state = AppState()
    state.job_board = JobBoard.load(data_dir / "missions" / "missions.json")
    registry = StoryRegistry.load(data_dir)
    return state, t, registry


def _console_to_text(console: tcod.console.Console) -> str:
    """Convert a tcod console buffer to plain text."""
    lines: list[str] = []
    for y in range(console.height):
        chars: list[str] = []
        for x in range(console.width):
            code = int(console.ch[x, y])
            chars.append(chr(code) if 0 < code < 0x110000 else " ")
        lines.append("".join(chars).rstrip())
    return "\n".join(lines)


def _render_current(
    console: tcod.console.Console,
    state: AppState,
    t: Translator,
    story_reg: StoryRegistry,
    elapsed: float,
) -> None:
    """Render the current screen onto the console."""
    state.demo_step = state.demo_step
    state.demo_elapsed_s = elapsed
    if state.screen is ScreenKind.MENU:
        menu.render_menu(console, t, state)
    elif state.screen is ScreenKind.HUB:
        hub.render_hub(console, t, state)
    elif state.screen is ScreenKind.MATRIX and state.matrix is not None:
        layout = matrix_view.get_layout(state.matrix)
        matrix_view.render_matrix(console, t, state, layout)
    elif state.screen is ScreenKind.STORY:
        story_view.render_story(
            console,
            state,
            story_reg,
            aftermath_id=state.story_aftermath_id,
            elapsed_s=elapsed,
        )


def _print_frame(
    console: tcod.console.Console,
    *,
    clear: bool,
    step: int,
    elapsed: float,
    narration: str,
) -> None:
    """Write a single frame to stdout."""
    if clear:
        sys.stdout.write("\033[2J\033[H")
    sys.stdout.write(_console_to_text(console))
    sys.stdout.write("\n")
    sys.stdout.write(
        f"[Step {step:03d}  T+{elapsed:5.1f}s  Screen: {state_screen_label(console)}]\n"
    )
    if narration:
        sys.stdout.write(f"> {narration}\n")
    sys.stdout.flush()


def state_screen_label(_: tcod.console.Console) -> str:
    # The actual screen label is rendered into the console; the line
    # above is just metadata for the demo.
    return "rendered"


def _action_menu(state: AppState) -> str:
    """MENU → HUB: select New Run (key '1')."""
    if state.screen is ScreenKind.MENU:
        state.screen = ScreenKind.HUB
        return "Auto: New Run (selected) → Hub"
    return ""


def _action_hub(state: AppState) -> str:
    """HUB → MATRIX: select first mission."""
    if state.screen is ScreenKind.HUB and state.job_board:
        missions = list(state.job_board.available_for(state.player_grade))
        if not missions:
            return "No missions for this grade."
        m = missions[0]
        state.current_mission = m
        state.matrix = MatrixGenerator().generate(
            seed=m.matrix_seed, mission_grade=state.player_grade
        )
        state.current_node_id = state.matrix.entry_id
        state.exploration = ExplorationState(current=state.matrix.entry_id)
        state.screen = ScreenKind.MATRIX
        return f"Auto: select '{m.title}' → Matrix"
    return ""


def _action_matrix(state: AppState) -> str:
    """MATRIX: navigate to next unvisited neighbor, or jack out when done."""
    if state.screen is ScreenKind.MATRIX and state.matrix is not None:
        nbrs = state.matrix.neighbors(state.current_node_id or "")
        unvisited = [
            n
            for n in nbrs
            if n.id not in (state.exploration.discovered if state.exploration else set())
        ]
        if unvisited:
            target = unvisited[0]
            state.current_node_id = target.id
            if state.exploration is not None:
                state.exploration.visit(target.id)
            ppl = calculate_ppl(state.player_loadout)
            zdr = node_zdr(target)
            st = node_status(target, ppl)
            return f"Auto: → {target.kind.value} (ZDR {zdr}, {st.value.upper()})"
        # All neighbors visited → jack out
        state.matrix = None
        state.current_node_id = None
        state.exploration = None
        state.current_mission = None
        state.screen = ScreenKind.HUB
        return "Auto: Jack out (all neighbors visited) → Hub"
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--step-delay", type=float, default=0.4)
    parser.add_argument("--no-clear", action="store_true")
    parser.add_argument("--lang", default="en", choices=["en", "ko"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--mission", type=int, default=1)
    parser.add_argument("--show-controls", action="store_true")
    args = parser.parse_args()

    state, t, story_reg = _setup(args)
    console = tcod.console.Console(80, 50, order="F")

    if args.show_controls:
        sys.stdout.write(
            "=== Quick Demo ===\n"
            "Commands: q = quit early, Enter = next frame.\n"
            f"Duration: {args.duration:.0f}s, step-delay: {args.step_delay}s, lang: {args.lang}\n\n"
        )
        sys.stdout.flush()

    start = time.monotonic()
    step = 0
    narration = "(initial)"

    _render_current(console, state, t, story_reg, 0.0)
    _print_frame(
        console,
        clear=not args.no_clear,
        step=step,
        elapsed=0.0,
        narration=narration,
    )
    step += 1
    time.sleep(args.step_delay)

    while time.monotonic() - start < args.duration:
        elapsed = time.monotonic() - start

        # Decide next action based on current screen
        # Every 4th step, act (instead of every other)
        if step % 4 == 0:
            if state.screen is ScreenKind.MENU:
                if step > 1:
                    narration = _action_menu(state)
                    # After action, transition: demo the Story screen briefly
                    if state.screen is ScreenKind.STORY:
                        pass  # already on story
                    else:
                        # Demo Story after first mission
                        if state.current_mission is not None and state.screen is ScreenKind.HUB:
                            state.screen = ScreenKind.STORY
            elif state.screen is ScreenKind.HUB:
                if step > 1:
                    narration = _action_hub(state)
            elif state.screen is ScreenKind.MATRIX:
                if step > 2:
                    narration = _action_matrix(state)
            elif state.screen is ScreenKind.STORY:
                # Auto-leave Story to Hub
                if state.current_mission is not None:
                    state.screen = ScreenKind.HUB
                    state.current_mission = None
                else:
                    state.screen = ScreenKind.MENU
                narration = "Auto: → next screen"

        _render_current(console, state, t, story_reg, elapsed)
        _print_frame(
            console,
            clear=not args.no_clear,
            step=step,
            elapsed=elapsed,
            narration=narration,
        )
        step += 1
        time.sleep(args.step_delay)

    sys.stdout.write(f"\n=== Demo complete: {step} steps in {args.duration:.0f}s ===\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.stdout.write("\n[interrupted]\n")
        sys.exit(130)
