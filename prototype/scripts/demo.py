"""Auto-progressing headless demo (ADR-0005, design/systems/hacking.md).

Runs the game state machine without a tcod window, rendering each
frame to plain text on stdout. The state advances automatically:
Menu -> Hub -> Matrix (navigate) -> Jack out -> Hub -> ...

Usage:
    python scripts/demo.py                  # 120s demo, 1.0s per step
    python scripts/demo.py --duration 30   # 30s demo
    python scripts/demo.py --step-delay 0.5
    python scripts/demo.py --no-clear      # don't clear the screen between frames
    python scripts/demo.py --lang ko       # Korean translation

Frames are dumped to stdout. With --no-clear, every frame is appended
so the terminal scrolls through the whole playthrough.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import tcod.console

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from roguelike_sprawl.engine import hub, matrix_view, menu
from roguelike_sprawl.engine.state import AppState, ScreenKind
from roguelike_sprawl.i18n import Translator
from roguelike_sprawl.matrix import MatrixGenerator
from roguelike_sprawl.matrix.ppl import calculate_ppl
from roguelike_sprawl.matrix.zdr import node_status, node_zdr
from roguelike_sprawl.missions import JobBoard


def render_to_text(console: tcod.console.Console) -> str:
    """Convert a tcod console buffer to plain text (one char per cell)."""
    lines: list[str] = []
    for y in range(console.height):
        chars: list[str] = []
        for x in range(console.width):
            code = int(console.ch[x, y])
            if 0 < code < 0x110000:
                chars.append(chr(code))
            else:
                chars.append(" ")
        lines.append("".join(chars).rstrip())
    return "\n".join(lines)


def render_frame(
    console: tcod.console.Console,
    state: AppState,
    t: Translator,
) -> None:
    """Render the current screen onto ``console`` (in place)."""
    if state.screen is ScreenKind.MENU:
        menu.render_menu(console, t, state)
    elif state.screen is ScreenKind.HUB:
        hub.render_hub(console, t, state)
    elif state.screen is ScreenKind.MATRIX and state.matrix is not None:
        layout = matrix_view.get_layout(state.matrix)
        matrix_view.render_matrix(console, t, state, layout)


def print_frame(
    console: tcod.console.Console,
    state: AppState,
    step: int,
    elapsed: float,
    narration: str,
    *,
    clear: bool,
) -> None:
    """Write a single frame to stdout."""
    if clear:
        sys.stdout.write("\033[2J\033[H")
    sys.stdout.write(render_to_text(console))
    sys.stdout.write("\n")
    sys.stdout.write(f"[Step {step:03d}  T+{elapsed:5.1f}s  Screen: {state.screen.value}]\n")
    if narration:
        sys.stdout.write(f"> {narration}\n")
    sys.stdout.write("\n")
    sys.stdout.flush()


def _step_auto(
    state: AppState,
    missions: list,
    visited: set[str],
    mission_idx: list[int],
) -> str:
    """Advance the state by one auto-step. Returns narration."""
    if state.screen is ScreenKind.MENU:
        state.screen = ScreenKind.HUB
        return "Auto: New Run. Jacked in to the Hub."

    if state.screen is ScreenKind.HUB:
        if not missions:
            return "No jobs for your grade. Sit tight."
        from roguelike_sprawl.matrix.exploration import ExplorationState

        m = missions[mission_idx[0] % len(missions)]
        state.current_mission = m
        gen = MatrixGenerator()
        state.matrix = gen.generate(seed=m.matrix_seed, mission_grade=state.player_grade)
        state.current_node_id = state.matrix.entry_id
        state.exploration = ExplorationState(current=state.matrix.entry_id)
        visited.clear()
        visited.add(state.current_node_id)
        state.screen = ScreenKind.MATRIX
        mission_idx[0] += 1
        return f"Auto: selected {m.title!r}. Jacking in..."

    if state.screen is ScreenKind.MATRIX:
        assert state.matrix is not None
        assert state.current_node_id is not None
        nbrs = state.matrix.neighbors(state.current_node_id)
        unvisited = [n for n in nbrs if n.id not in visited]
        if unvisited:
            target = unvisited[0]
            state.current_node_id = target.id
            if state.exploration is not None:
                state.exploration.visit(target.id)
            visited.add(target.id)
            ppl = calculate_ppl(state.player_loadout)
            zdr = node_zdr(target)
            st = node_status(target, ppl)
            return f"Auto: -> {target.kind.value} (ZDR {zdr}, {st.value.upper()})"
        # All neighbors visited -> jack out and return to Hub
        state.matrix = None
        state.current_node_id = None
        state.current_mission = None
        state.screen = ScreenKind.HUB
        return "Auto: all neighbors visited. Jacking out. Heart racing."

    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--duration", type=float, default=120.0)
    parser.add_argument("--step-delay", type=float, default=1.0)
    parser.add_argument(
        "--no-clear", action="store_true", help="Append frames instead of clearing the screen."
    )
    parser.add_argument("--lang", default="en", choices=["en", "ko"])
    parser.add_argument(
        "--missions", type=int, default=2, help="How many missions to cycle through."
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    t = Translator(args.lang, data_dir=data_dir / "i18n")

    state = AppState()
    state.job_board = JobBoard.load(data_dir / "missions" / "missions.json")
    console = tcod.console.Console(80, 50, order="F")

    available = list(state.job_board.available_for(state.player_grade))
    if not available:
        sys.stderr.write("No missions available. Add missions to data/missions/.\n")
        return 1
    missions = available[: args.missions]
    visited: set[str] = set()
    mission_idx = [0]

    start = time.monotonic()
    step = 0
    narration = "Auto-demo. The world goes gray."
    render_frame(console, state, t)
    print_frame(console, state, step, 0.0, narration, clear=not args.no_clear)
    step += 1
    time.sleep(args.step_delay)

    while time.monotonic() - start < args.duration:
        elapsed = time.monotonic() - start
        narration = _step_auto(state, missions, visited, mission_idx)
        render_frame(console, state, t)
        print_frame(console, state, step, elapsed, narration, clear=not args.no_clear)
        step += 1
        time.sleep(args.step_delay)

    sys.stdout.write(f"\n=== Demo complete: {step} steps in {args.duration:.0f}s ===\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
