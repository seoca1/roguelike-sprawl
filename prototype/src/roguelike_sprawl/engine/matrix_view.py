"""Matrix screen: render the node graph and handle movement (ADR-0005).

Phase 5+ adds Fog of War / Exploration (ADR-0020):
  - current node: full info, highlighted
  - adjacent: kind only, outline box
  - discovered: full info (visited before)
  - unknown: `?` placeholder
  - minimap (side) + breadcrumb (side)

Phase 5+ adds Action Menu:
  - ENTER on a node: action menu popup
  - Actions depend on node kind (DATA/ICE/EXIT/ROUTER/etc.)

Uses the unified screen shell (engine.layout) for area separation:
  - Title: zone + status
  - Main: node graph with fog
  - Side: minimap + current info + path
  - Controls: input hints
  - Footer: step + time
"""

from __future__ import annotations

import tcod.console
import tcod.event
from tcod.event import KeyDown, KeySym

from ..combat.registry import IceRegistry, ProgramRegistry
from ..i18n import Translator
from ..matrix import (
    MatrixGraph,
    Node,
    NodeKind,
    Status,
    Visibility,
    node_zdr,
    status_color,
    zone_label,
)
from ..matrix.exploration import ExplorationState
from ..matrix.ppl import calculate_ppl
from ..matrix.zdr import node_status
from . import action_menu
from .input_utils import is_confirm_key
from .layout import (
    Region,
    RegionId,
    clear_region,
    draw_controls,
    draw_dividers,
    draw_footer,
    draw_message_log,
    draw_side,
    draw_title,
    make_shell,
)
from .state import AppState, ScreenKind
from .status_panel import render_status_panel

BOX_WIDTH = 12
BOX_HEIGHT = 4
BOX_INNER_W = BOX_WIDTH - 2

_KIND_LABEL: dict[NodeKind, str] = {
    NodeKind.ENTRY: "Entry",
    NodeKind.EXIT: "Exit",
    NodeKind.DATA: "Data",
    NodeKind.ICE: "ICE",
    NodeKind.SYSTEM: "System",
    NodeKind.ROUTER: "Router",
    NodeKind.CONSTRUCT: "Construct",
    NodeKind.CORE: "Core",
}

_STATUS_GLYPH: dict[Status, str] = {
    Status.SAFE: "+",
    Status.MATCH: "=",
    Status.TOUGH: "-",
    Status.DEADLY: "!",
    Status.FUTILE: "X",
}


def _short_kind(kind: NodeKind) -> str:
    return _KIND_LABEL.get(kind, kind.value.capitalize())


def _status_glyph(status: Status) -> str:
    return _STATUS_GLYPH.get(status, "?")


def _draw_box(
    console: tcod.console.Console,
    main: Region,
    col: int,
    row: int,
    label: str,
    zdr: int,
    status: Status,
    is_current: bool,
    direction_hints: dict[str, str] | None = None,
) -> None:
    """Draw one full-visibility node box.

    Args:
        console: tcod console.
        main: Main region.
        col: Column in main region.
        row: Row in main region.
        label: Node label.
        zdr: Zone Difficulty Rating.
        status: Status.
        is_current: Whether this is the player's current node.
        direction_hints: For current node — map of direction code to glyph shown
            on the box edge. Direction codes: "L", "R", "U", "D".
            E.g. {"L": "←", "U": "↑"} for neighbors on the left and up.
    """
    # Current node: bright cyan/yellow, double border effect
    # Other nodes: normal gray
    if is_current:
        fg_box = (0, 255, 255)  # Bright cyan for current node
        border_chars = {
            "corner": "#",
            "horiz": "=",
            "vert": "║",
        }
    else:
        fg_box = (200, 200, 200)  # Gray for other nodes
        border_chars = {
            "corner": "+",
            "horiz": "-",
            "vert": "|",
        }

    fg_status = status_color(status)
    abs_x = main.x + col
    abs_y = main.y + row
    if not main.contains(abs_x, abs_y) or not main.contains(
        abs_x + BOX_WIDTH - 1, abs_y + BOX_HEIGHT - 1
    ):
        return

    # Draw corners
    console.print(x=abs_x, y=abs_y, string=border_chars["corner"], fg=fg_box)
    console.print(x=abs_x + BOX_WIDTH - 1, y=abs_y, string=border_chars["corner"], fg=fg_box)
    console.print(x=abs_x, y=abs_y + BOX_HEIGHT - 1, string=border_chars["corner"], fg=fg_box)
    console.print(
        x=abs_x + BOX_WIDTH - 1,
        y=abs_y + BOX_HEIGHT - 1,
        string=border_chars["corner"],
        fg=fg_box,
    )

    # Draw horizontal borders (with directional hint chars if applicable)
    for c in range(abs_x + 1, abs_x + BOX_WIDTH - 1):
        console.print(x=c, y=abs_y, string=border_chars["horiz"], fg=fg_box)
        console.print(x=c, y=abs_y + BOX_HEIGHT - 1, string=border_chars["horiz"], fg=fg_box)

    # Draw vertical borders
    for r in range(abs_y + 1, abs_y + BOX_HEIGHT - 1):
        console.print(x=abs_x, y=r, string=border_chars["vert"], fg=fg_box)
        console.print(x=abs_x + BOX_WIDTH - 1, y=r, string=border_chars["vert"], fg=fg_box)

    # Inner content
    glyph = _status_glyph(status)
    inner_label = label[: BOX_INNER_W - 2].center(BOX_INNER_W - 2)
    zdr_text = f"{glyph}ZDR:{zdr:<3}".center(BOX_INNER_W)

    # Current node: bright yellow text with dark background highlight
    # Other nodes: normal gray text
    if is_current:
        fg_label = (255, 255, 0)
        bg_label = (0, 64, 64)  # Dark cyan background
        # Fill inner area with background color
        for r in range(abs_y + 1, abs_y + BOX_HEIGHT - 1):
            for c in range(abs_x + 1, abs_x + BOX_WIDTH - 1):
                console.print(x=c, y=r, string=" ", bg=bg_label)
    else:
        fg_label = (200, 200, 200)
        bg_label = (0, 0, 0)  # Default black background

    console.print(x=abs_x + 1, y=abs_y + 1, string=inner_label, fg=fg_label, bg=bg_label)
    console.print(x=abs_x + 1, y=abs_y + 2, string=zdr_text, fg=fg_status, bg=bg_label)

    # External marker (arrow pointing to current node)
    if is_current:
        # Left arrow
        if abs_x > main.x:
            console.print(x=abs_x - 1, y=abs_y + 1, string=">", fg=(255, 255, 0))
        # Right arrow
        if abs_x + BOX_WIDTH < main.x2:
            console.print(x=abs_x + BOX_WIDTH, y=abs_y + 1, string="<", fg=(255, 255, 0))
        # Top indicator
        if abs_y > main.y:
            console.print(x=abs_x + BOX_WIDTH // 2, y=abs_y - 1, string="v", fg=(255, 255, 0))
        # Bottom indicator
        if abs_y + BOX_HEIGHT < main.y2:
            console.print(
                x=abs_x + BOX_WIDTH // 2, y=abs_y + BOX_HEIGHT, string="^", fg=(255, 255, 0)
            )

        # "YOU ARE HERE" label above the box
        you_here = "[ YOU ]"
        if abs_y > main.y + 1:
            console.print(
                x=abs_x + (BOX_WIDTH - len(you_here)) // 2,
                y=abs_y - 1,
                string=you_here,
                fg=(255, 255, 0),
            )

    # Direction hints — overlay arrow glyphs on the border edges where a
    # neighboring node exists. This lets the player see at a glance which
    # arrow keys will move them somewhere.
    if is_current and direction_hints:
        hint_color = (200, 255, 200)  # Light green for hints
        cx = abs_x + BOX_WIDTH // 2  # center x
        cy = abs_y + BOX_HEIGHT // 2  # center y
        for code, glyph in direction_hints.items():
            if code == "L":
                # Left edge midpoint
                console.print(x=abs_x, y=cy, string=glyph, fg=hint_color, bg=bg_label)
            elif code == "R":
                console.print(
                    x=abs_x + BOX_WIDTH - 1, y=cy, string=glyph, fg=hint_color, bg=bg_label
                )
            elif code == "U":
                # Top edge midpoint
                console.print(x=cx, y=abs_y, string=glyph, fg=hint_color, bg=bg_label)
            elif code == "D":
                console.print(
                    x=cx, y=abs_y + BOX_HEIGHT - 1, string=glyph, fg=hint_color, bg=bg_label
                )


def _draw_box_fog(
    console: tcod.console.Console,
    main: Region,
    col: int,
    row: int,
    visibility: Visibility,
) -> None:
    """Render a fog-of-war node box."""
    abs_x = main.x + col
    abs_y = main.y + row
    if visibility is Visibility.UNKNOWN:
        console.print(x=abs_x + 4, y=abs_y + 1, string="?", fg=(64, 64, 64))
        return
    if visibility is Visibility.ADJACENT:
        dim = (120, 120, 120)
        if not main.contains(abs_x, abs_y):
            return
        for c in range(abs_x, abs_x + BOX_WIDTH):
            console.print(x=c, y=abs_y, string="-", fg=dim)
            console.print(x=c, y=abs_y + BOX_HEIGHT - 1, string="-", fg=dim)
        for r in range(abs_y + 1, abs_y + BOX_HEIGHT - 1):
            console.print(x=abs_x, y=r, string="|", fg=dim)
            console.print(x=abs_x + BOX_WIDTH - 1, y=r, string="|", fg=dim)
        console.print(
            x=abs_x + 1,
            y=abs_y + 1,
            string="?  ?".center(BOX_INNER_W),
            fg=(100, 100, 100),
        )
        console.print(
            x=abs_x + 1,
            y=abs_y + 2,
            string="(adjacent)".center(BOX_INNER_W),
            fg=(100, 100, 100),
        )


def _draw_edge_line(
    console: tcod.console.Console,
    main: Region,
    src: tuple[int, int],
    dst: tuple[int, int],
) -> None:
    """Draw an L-shaped connection (clipped to main region)."""
    sx, sy = src
    dx, dy = dst
    cnx, cny = main.x + sx + BOX_WIDTH, main.y + sy + 1
    tnx, tny = main.x + dx - 1, main.y + dy + 1
    line_color = (96, 96, 96)
    if cny == tny:
        if cnx < tnx:
            start, end = cnx + 1, tnx - 1
        else:
            start, end = tnx + 1, cnx - 1
        for c in range(start, end + 1):
            console.print(x=c, y=cny, string="-", fg=line_color)
        return
    corner_x, corner_y = tnx, cny
    if cnx < corner_x:
        for c in range(cnx + 1, corner_x):
            console.print(x=c, y=cny, string="-", fg=line_color)
    else:
        for c in range(corner_x + 1, cnx):
            console.print(x=c, y=cny, string="-", fg=line_color)
    corner_char = (
        "\u2514"
        if cnx < corner_x and tny < cny
        else "\u2518"
        if cnx > corner_x and tny < cny
        else "\u250c"
        if cnx < corner_x
        else "\u2510"
    )
    console.print(x=corner_x, y=corner_y, string=corner_char, fg=line_color)
    if tny < cny:
        for r in range(tny + 1, cny):
            console.print(x=tnx, y=r, string="|", fg=line_color)
    else:
        for r in range(cny + 1, tny):
            console.print(x=tnx, y=r, string="|", fg=line_color)


def _draw_minimap(
    console: tcod.console.Console,
    matrix: MatrixGraph,
    exploration: ExplorationState,
    side: Region,
) -> None:
    """Render the minimap in the SIDE region."""
    lines: list[str] = []
    for node in matrix.nodes:
        vis = exploration.visibility(matrix, node.id)
        if vis is Visibility.UNKNOWN:
            glyph, suffix = "?", ""
        elif vis is Visibility.CURRENT:
            glyph, suffix = "●", " (you)"
        elif vis is Visibility.ADJACENT:
            glyph, suffix = "○", " ?"
        else:  # discovered
            glyph, suffix = "●", ""
        lines.append(f"{glyph} {_short_kind(node.kind)}{suffix}")
    draw_side(console, side, label="Map", lines=lines[: side.h - 1])


def _draw_breadcrumb(
    console: tcod.console.Console,
    matrix: MatrixGraph,
    exploration: ExplorationState,
    side: Region,
) -> None:
    """Render the breadcrumb (path) in the SIDE region, below minimap."""
    if not exploration.path:
        return
    labels: list[str] = []
    for nid in exploration.path:
        node = matrix.get(nid)
        labels.append(_short_kind(node.kind) if node is not None else "?")
    path_text = " → ".join(labels)
    console.print(
        x=side.x + 2,
        y=side.y2,
        string=f"Path: {path_text[: side.w - 10]}",
        fg=(96, 96, 96),
    )


def render_matrix(
    console: tcod.console.Console,
    t: Translator,
    state: AppState,
    layouts: dict[str, tuple[int, int]],
    prog_registry: ProgramRegistry | None = None,
    ice_registry: IceRegistry | None = None,
) -> None:
    """Render the matrix screen with fog + shell (ADR-0020).

    If state.action_menu_open is True, render the action menu popup.
    """
    matrix = state.matrix
    if matrix is None or state.current_node_id is None:
        console.clear(bg=(0, 0, 0))
        console.print(x=2, y=2, string="(no matrix loaded)", fg=(255, 0, 0))
        return

    ppl = calculate_ppl(state.player_loadout)
    zone = matrix.get(state.current_node_id)
    zone_str = zone_label(t, zone.zone) if zone is not None else "?"
    if zone is not None:
        zdr = node_zdr(zone)
        st = node_status(zone, ppl)
    else:
        zdr = 0
        st = Status.MATCH

    # Build shell
    shell = make_shell()
    title_r = shell[RegionId.TITLE]
    main_r = shell[RegionId.MAIN]
    side_r = shell[RegionId.SIDE]
    ctrl_r = shell[RegionId.CONTROLS]
    foot_r = shell[RegionId.FOOTER]
    panel_r = shell[RegionId.STATUS_PANEL]

    # Clear and draw dividers
    for r in shell.values():
        clear_region(console, r)
    draw_dividers(console, shell)

    # Render persistent status panel
    render_status_panel(console, state, panel_r)

    # Title with current node prominently displayed
    if zone is not None:
        ratio = ppl / zdr if zdr > 0 else float("inf")
        # Main title with current node name
        title_text = f"MATRIX — {zone.label} [{_short_kind(zone.kind)}]"
        status_text = (
            f"PPL: {ppl}  |  Zone: {zone_str}  |  "
            f"ZDR: {zdr}  |  Status: {st.value.upper()} ({ratio:.2f}x)"
        )
        draw_title(console, title_r, title=title_text, subtitle=status_text)
    else:
        draw_title(console, title_r, title="MATRIX", subtitle="Connecting...")

    # Edges
    exploration = state.exploration
    use_fog = exploration is not None
    expl: ExplorationState | None = exploration
    for edge in matrix.edges:
        if use_fog and expl is not None:
            sv = expl.visibility(matrix, edge.src)
            dv = expl.visibility(matrix, edge.dst)
            if sv is Visibility.UNKNOWN or dv is Visibility.UNKNOWN:
                continue
        sp = layouts.get(edge.src)
        dp = layouts.get(edge.dst)
        if sp is None or dp is None:
            continue
        _draw_edge_line(console, main_r, sp, dp)

    # Compute direction hints for the current node (ADR-0045)
    direction_hints: dict[str, str] = {}
    if state.current_node_id:
        cx, cy = layouts.get(state.current_node_id, (0, 0))
        for nbr in matrix.neighbors(state.current_node_id):
            np = layouts.get(nbr.id)
            if np is None:
                continue
            nx, ny = np
            dx, dy = nx - cx, ny - cy
            # Only cardinal hints for clarity
            if dx < 0 and abs(dx) >= abs(dy):
                direction_hints.setdefault("L", "◄")
            elif dx > 0 and abs(dx) >= abs(dy):
                direction_hints.setdefault("R", "►")
            elif dy < 0 and abs(dy) > abs(dx):
                direction_hints.setdefault("U", "▲")
            elif dy > 0 and abs(dy) > abs(dx):
                direction_hints.setdefault("D", "▼")

    # Nodes
    for node in matrix.nodes:
        pos = layouts.get(node.id)
        if pos is None:
            continue
        if use_fog and expl is not None:
            vis = expl.visibility(matrix, node.id)
            if vis is Visibility.UNKNOWN:
                _draw_box_fog(console, main_r, pos[0], pos[1], Visibility.UNKNOWN)
                continue
            if vis is Visibility.ADJACENT:
                _draw_box_fog(console, main_r, pos[0], pos[1], Visibility.ADJACENT)
                continue
        _draw_box(
            console,
            main_r,
            pos[0],
            pos[1],
            _short_kind(node.kind),
            node_zdr(node),
            node_status(node, ppl),
            is_current=(node.id == state.current_node_id),
            direction_hints=direction_hints if node.id == state.current_node_id else None,
        )

    # Side: Current node status + node selection list
    if zone is not None:
        # Show adjacent node selection list (cursor-based navigation)
        neighbors = _adjacent_nodes_list(matrix, state.current_node_id) if matrix and state.current_node_id else []
        state.matrix_nav_index = max(0, min(state.matrix_nav_index, len(neighbors) - 1)) if neighbors else 0

        side_lines = [
            "=== CURRENT NODE ===",
            f"Name: {zone.label}",
            f"Type: {_short_kind(zone.kind)}",
            f"ZDR: {node_zdr(zone)} | Status: {st.value.upper()}",
            "",
        ]

        # Node selection list with cursor
        if neighbors:
            side_lines.append("=== MOVE TO ===")
            for i, n in enumerate(neighbors):
                cursor = ">" if i == state.matrix_nav_index else " "
                side_lines.append(f"{cursor} {n.label} ({_short_kind(n.kind)})")
            side_lines.extend([
                "",
                "[↑↓] Select  [Enter] Move",
                "[SPACE] Action menu",
            ])
        else:
            side_lines.extend([
                "=== WHAT TO DO ===",
                "",
                "[SPACE] Action menu",
            ])

        side_lines.extend(
            [
                "→ ESC: Leave matrix",
                "",
                f"Visited: {len(expl.discovered) if expl else 0} nodes",
            ]
        )

        draw_side(console, side_r, label="STATUS", lines=side_lines)
    elif use_fog and expl is not None:
        _draw_minimap(console, matrix, expl, side_r)
        _draw_breadcrumb(console, matrix, expl, side_r)

    # ADR-0047: show recent typed status messages as a multi-line log
    # using the SIDE area when matrix view is the primary focus.
    # We use a separate small log overlay at the bottom-right area.
    # (Already used draw_side above for status panel; add a recent-activity
    # log overlay in the area between main and controls when zone is set.)
    if zone is not None and state.status_messages:
        # Render recent 3 messages in a thin overlay strip just above controls
        # Use the bottom 3 rows of the side panel for the message log.
        log_region = Region(
            RegionId.SIDE,
            x=side_r.x,
            y=side_r.y2 - 2,
            w=side_r.w,
            h=3,
        )
        draw_message_log(
            console,
            log_region,
            state.status_messages[-3:],
            max_lines=3,
        )

    # Controls (cursor-based navigation: ↑/↓ to select, Enter to move)
    if zone is not None:
        action_hint = "SPACE: Action menu"
        if zone.kind is NodeKind.DATA:
            action_hint = "SPACE: Extract data (mission objective)"
        elif zone.kind is NodeKind.ICE:
            action_hint = "SPACE: Engage ICE (combat)"
        elif zone.kind is NodeKind.EXIT:
            action_hint = "SPACE: Jack out (exit matrix)"

        draw_controls(
            console,
            ctrl_r,
            lines=[
                f"↑/↓: Select  |  ←/→: Move spatially  |  Enter: Confirm  |  {action_hint}",
                "ESC: Leave matrix  |  Q: Quit",
            ],
        )
    else:
        draw_controls(
            console,
            ctrl_r,
            lines=[
                "[← → ↑ ↓] Move  [SPACE] Action  [ESC] Jack out",
                "[Q] Quit",
            ],
        )

    # Footer with status messages
    draw_footer(
        console,
        foot_r,
        text=f"Step {state.demo_step}  T+{state.demo_elapsed_s:.1f}s",
        status_messages=state.status_messages,
    )

    # Action menu overlay (if open)
    if state.action_menu_open:
        current_node = matrix.get(state.current_node_id)
        if current_node is not None:
            # Center popup in main area
            menu_w = 50
            menu_h = 12
            menu_x = main_r.x + (main_r.w - menu_w) // 2
            menu_y = main_r.y + (main_r.h - menu_h) // 2
            menu_region = Region(
                id=RegionId.MAIN,  # Reuse ID (not a new region)
                x=menu_x,
                y=menu_y,
                w=menu_w,
                h=menu_h,
            )
            action_menu.render_action_menu(console, t, state, current_node, menu_region)


def handle_matrix_input(
    event: tcod.event.Event,
    state: AppState,
    prog_registry: ProgramRegistry | None = None,
    ice_registry: IceRegistry | None = None,
) -> bool:
    """Handle input on the Matrix screen.

    If action_menu_open, delegate to action_menu.
    """
    if not isinstance(event, KeyDown):
        return True

    # If action menu is open, handle it separately
    if state.action_menu_open:
        if state.matrix is not None and state.current_node_id is not None:
            current_node = state.matrix.get(state.current_node_id)
            if current_node is not None and prog_registry is not None and ice_registry is not None:
                continue_running, close_menu = action_menu.handle_action_menu_input(
                    event, state, current_node, prog_registry, ice_registry
                )
                if close_menu:
                    state.action_menu_open = False
                return continue_running
        # Fallback: close menu on any key
        state.action_menu_open = False
        return True

    # Normal matrix input
    if event.sym is KeySym.ESCAPE:
        state.status_messages.append(">>> Jacking out of matrix...")
        _jack_out(state)
        return True
    if event.sym is KeySym.Q:
        state.status_messages.append(">>> Quitting game...")
        return False
    if is_confirm_key(event.sym):
        # If cursor navigation has been used, confirm node selection
        matrix = state.matrix
        if matrix is not None and state.current_node_id is not None:
            neighbors = _adjacent_nodes_list(matrix, state.current_node_id)
            if neighbors and state.matrix_nav_index < len(neighbors):
                target = neighbors[state.matrix_nav_index]
                state.status_messages.append(f">>> Moved to {target.label} ({_short_kind(target.kind)})")
                state.current_node_id = target.id
                if state.exploration is not None:
                    state.exploration.visit(target.id)
                state.matrix_nav_index = 0  # Reset cursor
                return True
        # Otherwise open action menu (ENTER or SPACE)
        if state.matrix and state.current_node_id:
            node = state.matrix.get(state.current_node_id)
            if node:
                state.status_messages.append(f">>> Action menu opened for {node.label}")
        state.action_menu_open = True
        return True
    # LEFT/RIGHT: spatial movement (vector-based, finds neighbor in that direction)
    if event.sym in (KeySym.LEFT, KeySym.RIGHT, KeySym.KP_4, KeySym.KP_6, KeySym.H, KeySym.L):
        _handle_movement(state, event.sym)
        return True
    # UP/DOWN: cursor-based node selection
    if event.sym in _NAVIGATION_KEYS:
        _handle_cursor_navigation(state, event.sym)
        return True
    return True


# Cursor navigation keys (↑/↓ to select adjacent node, Enter to move)
_NAVIGATION_KEYS: set[KeySym] = {
    KeySym.UP,
    KeySym.DOWN,
    KeySym.KP_8,  # N (alias for UP)
    KeySym.KP_2,  # S (alias for DOWN)
    KeySym.J,     # vim: down (↑ in conventional terms, but used as ↓ here)
    KeySym.K,     # vim: up (↓ in conventional terms, but used as ↑ here)
}


# Direction unit vectors for movement (ADR-0045)
_DIRECTION_VECTORS: dict[KeySym, tuple[int, int]] = {
    KeySym.LEFT: (-1, 0),
    KeySym.RIGHT: (1, 0),
    KeySym.UP: (0, -1),
    KeySym.DOWN: (0, 1),
    # Diagonals (numpad-style)
    KeySym.KP_7: (-1, -1),  # NW
    KeySym.KP_9: (1, -1),  # NE
    KeySym.KP_1: (-1, 1),  # SW
    KeySym.KP_3: (1, 1),  # SE
    KeySym.KP_8: (0, -1),  # N (alias for UP)
    KeySym.KP_2: (0, 1),  # S (alias for DOWN)
    KeySym.KP_4: (-1, 0),  # W (alias for LEFT)
    KeySym.KP_6: (1, 0),  # E (alias for RIGHT)
    # Vim-style diagonals
    KeySym.H: (-1, 0),
    KeySym.L: (1, 0),
    KeySym.K: (0, 1),
    KeySym.J: (0, -1),
    KeySym.Y: (-1, -1),
    KeySym.U: (1, -1),
    KeySym.B: (-1, 1),
    KeySym.N: (1, 1),
}

_DIRECTION_LABELS: dict[KeySym, str] = {
    KeySym.LEFT: "← LEFT",
    KeySym.RIGHT: "→ RIGHT",
    KeySym.UP: "↑ UP",
    KeySym.DOWN: "↓ DOWN",
    KeySym.KP_7: "↖ NW",
    KeySym.KP_9: "↗ NE",
    KeySym.KP_1: "↙ SW",
    KeySym.KP_3: "↘ SE",
    KeySym.KP_8: "↑ N",
    KeySym.KP_2: "↓ S",
    KeySym.KP_4: "← W",
    KeySym.KP_6: "→ E",
    KeySym.H: "← H",
    KeySym.L: "→ L",
    KeySym.K: "↓ K",
    KeySym.J: "↑ J",
    KeySym.Y: "↖ Y",
    KeySym.U: "↗ U",
    KeySym.B: "↙ B",
    KeySym.N: "↘ N",
}


def _adjacent_nodes(matrix: MatrixGraph, node_id: str) -> set[str]:
    """Return node ids connected to ``node_id`` (in or out edges)."""
    out: set[str] = set()
    for e in matrix.edges:
        if e.src == node_id:
            out.add(e.dst)
        elif e.dst == node_id:
            out.add(e.src)
    return out


def _adjacent_nodes_list(matrix: MatrixGraph, node_id: str) -> list[Node]:
    """Return list of adjacent nodes for cursor selection."""
    adj_ids = _adjacent_nodes(matrix, node_id)
    return [n for n in matrix.nodes if n.id in adj_ids]


def _handle_cursor_navigation(state: AppState, sym: KeySym) -> None:
    """Handle cursor-based node selection (↑/↓ to select, Enter to move).

    Unifies matrix navigation with combat skill selection UX.
    """
    matrix = state.matrix
    if matrix is None or state.current_node_id is None:
        return

    neighbors = _adjacent_nodes_list(matrix, state.current_node_id)
    if not neighbors:
        state.status_messages.append(">>> No adjacent nodes")
        return

    # Clamp cursor to valid range
    state.matrix_nav_index = max(0, min(state.matrix_nav_index, len(neighbors) - 1))

    # Handle key press
    if sym in (KeySym.UP, KeySym.KP_8, KeySym.K):
        # Move cursor up (previous node)
        if state.matrix_nav_index > 0:
            state.matrix_nav_index -= 1
        else:
            state.matrix_nav_index = len(neighbors) - 1  # Wrap to last
        selected = neighbors[state.matrix_nav_index]
        state.status_messages.append(f">>> [{state.matrix_nav_index + 1}/{len(neighbors)}] {selected.label}")
    elif sym in (KeySym.DOWN, KeySym.KP_2, KeySym.J):
        # Move cursor down (next node)
        if state.matrix_nav_index < len(neighbors) - 1:
            state.matrix_nav_index += 1
        else:
            state.matrix_nav_index = 0  # Wrap to first
        selected = neighbors[state.matrix_nav_index]
        state.status_messages.append(f">>> [{state.matrix_nav_index + 1}/{len(neighbors)}] {selected.label}")



def _handle_movement(state: AppState, sym: KeySym) -> None:
    """Move to the neighbor that best matches the pressed direction (ADR-0045).

    Algorithm:
        1. For each adjacent neighbor (in/out edges), compute the unit
           direction vector using Euclidean normalization.
        2. Score by dot product with the pressed direction (higher = better).
        3. Tie-break by total Manhattan distance (closer = better).
        4. Move to the best-scoring neighbor if score > 0.

    This naturally handles:
        - Cardinal directions (← → ↑ ↓)
        - Diagonal directions (numpad 7/9/1/3, vim Y/U/B/N)
        - Best-match fallback (when no neighbor is exactly in that direction,
          the closest diagonal neighbor wins)

    The matrix is a DAG, but for *exploration* movement we treat edges as
    bidirectional — players should be able to backtrack through visited nodes.
    """
    matrix = state.matrix
    if matrix is None or state.current_node_id is None:
        return
    if sym not in _DIRECTION_VECTORS:
        return

    layouts = _last_layout.get(matrix)
    if layouts is None:
        return
    current_pos = layouts.get(state.current_node_id)
    if current_pos is None:
        return
    cx, cy = current_pos
    press_dx, press_dy = _DIRECTION_VECTORS[sym]

    # Get all adjacent node ids (in or out edges — movement is bidirectional)
    adjacent_ids = _adjacent_nodes(matrix, state.current_node_id)

    best: tuple[float, int, Node] | None = None
    for n in matrix:
        if n.id not in adjacent_ids:
            continue
        if n.id == state.current_node_id:
            continue
        pos = layouts.get(n.id)
        if pos is None:
            continue
        nx, ny = pos
        dx, ny_dy = nx - cx, ny - cy
        # Euclidean-normalize neighbor direction so diagonals preserve angle.
        mag_sq = dx * dx + ny_dy * ny_dy
        if mag_sq == 0:
            continue
        mag = mag_sq**0.5
        ndx, ndy = dx / mag, ny_dy / mag
        # Dot product with pressed direction (1.0 = perfect, 0 = perpendicular).
        dot = ndx * press_dx + ndy * press_dy
        if dot <= 0:
            continue
        # Score: prefer high dot, then short Manhattan distance
        dist = abs(dx) + abs(ny_dy)
        if best is None or (dot, -dist) > (best[0], -best[1]):
            best = (dot, dist, n)
        elif dot == best[0] and dist == best[1]:
            if n.id < best[2].id:
                best = (dot, dist, n)

    if best is not None:
        _, _, target = best
        direction = _DIRECTION_LABELS.get(sym, "?")
        state.status_messages.append(
            f">>> Moved {direction} to {target.label} ({_short_kind(target.kind)})"
        )
        state.current_node_id = target.id
        if state.exploration is not None:
            state.exploration.visit(target.id)
    else:
        direction = _DIRECTION_LABELS.get(sym, "?")
        state.status_messages.append(f">>> No node in direction {direction}")


def _jack_out(state: AppState) -> None:
    state.matrix = None
    state.current_node_id = None
    state.current_mission = None
    state.exploration = None
    state.screen = ScreenKind.HUB
    state.message = ""


_last_layout: dict[MatrixGraph, dict[str, tuple[int, int]]] = {}


def get_layout(matrix: MatrixGraph) -> dict[str, tuple[int, int]]:
    cached = _last_layout.get(matrix)
    if cached is not None:
        return cached
    from ..matrix.graph import compute_layout

    layout = compute_layout(matrix)
    _last_layout[matrix] = layout
    return layout
