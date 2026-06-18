"""Dungeon-style matrix view: 2D grid rendering with rooms.

Renders the matrix as a top-down dungeon with rooms connected by corridors.
Uses cardinal direction movement (N/S/E/W).
"""

from __future__ import annotations

import tcod.console
import tcod.event
from tcod.event import KeyDown, KeySym

from ..combat.registry import IceRegistry, ProgramRegistry
from ..i18n import Translator
from ..matrix import MatrixGraph, Node, NodeKind
from ..matrix.dungeon_generator import RoomType
from . import action_menu
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
from .npc_event import DIXIE_FLATLINE_EVENT, NPCState
from .state import AppState, ScreenKind
from .status_panel import render_status_panel

# Room glyphs
_ROOM_GLYPHS = {
    RoomType.ENTRY: "[]",
    RoomType.EXIT: ">>",
    RoomType.DATA: "D",
    RoomType.ICE: "!",
    RoomType.NPC: "?",
    RoomType.ROUTER: ".",
    RoomType.CORE: "C",
    RoomType.EMPTY: " ",
}

_ROOM_NAMES = {
    RoomType.ENTRY: "Entry",
    RoomType.EXIT: "Exit",
    RoomType.DATA: "Data",
    RoomType.ICE: "ICE",
    RoomType.NPC: "NPC",
    RoomType.ROUTER: "Router",
    RoomType.CORE: "Core",
    RoomType.EMPTY: "Empty",
}


def render_dungeon_matrix(
    console: tcod.console.Console,
    t: Translator,
    state: AppState,
    prog_registry: ProgramRegistry | None = None,
    ice_registry: IceRegistry | None = None,
) -> None:
    """Render the matrix screen as a 2D dungeon grid."""
    matrix = state.matrix
    if matrix is None or state.current_node_id is None:
        return

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

    # Persistent status panel
    render_status_panel(console, state, panel_r)

    # Title
    current_node = matrix.get(state.current_node_id)
    if current_node:
        title = f"DUNGEON — {current_node.label} [{current_node.kind.value.upper()}]"
        subtitle = "Use ↑↓←→ to move through connected rooms"
    else:
        title = "DUNGEON"
        subtitle = "Navigating..."
    draw_title(console, title_r, title=title, subtitle=subtitle)

    # Main area: render dungeon
    _render_dungeon_grid(console, main_r, state, matrix)

    # Action menu overlay
    if state.action_menu_open and current_node:
        menu_w = 50
        menu_h = 12
        menu_x = main_r.x + (main_r.w - menu_w) // 2
        menu_y = main_r.y + (main_r.h - menu_h) // 2
        menu_region = Region(
            id=RegionId.MAIN,
            x=menu_x,
            y=menu_y,
            w=menu_w,
            h=menu_h,
        )
        action_menu.render_action_menu(console, t, state, current_node, menu_region)

    # Controls
    draw_controls(
        console,
        ctrl_r,
        lines=[
            "↑↓←→ Move between rooms  |  SPACE Action menu  |  ESC Leave",
            "Q Quit",
        ],
    )

    # Footer
    draw_footer(
        console,
        foot_r,
        text=f"Step {state.demo_step}  T+{state.demo_elapsed_s:.1f}s",
        status_messages=state.status_messages,
    )


def _render_dungeon_grid(
    console: tcod.console.Console,
    main: Region,
    state: AppState,
    matrix: MatrixGraph,
) -> None:
    """Render the 2D dungeon grid."""
    # Build room map: node_id -> (x, y) based on id format
    room_map: dict[str, tuple[int, int]] = {}

    # Try to extract grid positions from node IDs (if dungeon generator format)
    # Otherwise, fall back to auto-layout
    max_x = 0
    max_y = 0

    for node in matrix.nodes:
        # Check if this is a dungeon-generated node
        # For now, just use the layout based on connected components
        pos = _get_room_position(node.id, matrix)
        if pos is not None:
            room_map[node.id] = pos
            max_x = max(max_x, pos[0])
            max_y = max(max_y, pos[1])

    if not room_map:
        # Fallback: linear layout
        _render_linear_fallback(console, main, state, matrix)
        return

    # Calculate cell size
    cell_w = 10
    cell_h = 5
    grid_x = main.x + 2
    grid_y = main.y + 2

    # Draw each room
    for node in matrix.nodes:
        if node.id not in room_map:
            continue
        rx, ry = room_map[node.id]
        cell_x = grid_x + rx * cell_w
        cell_y = grid_y + ry * cell_h

        is_current = node.id == state.current_node_id

        # Determine room type (visual)
        if node.kind is NodeKind.ENTRY:
            room_type = RoomType.ENTRY
        elif node.kind is NodeKind.EXIT:
            room_type = RoomType.EXIT
        elif node.kind is NodeKind.DATA:
            room_type = RoomType.DATA
        elif node.kind is NodeKind.ICE:
            room_type = RoomType.ICE
        elif node.kind is NodeKind.CONSTRUCT:
            room_type = RoomType.NPC
        else:
            room_type = RoomType.ROUTER

        _draw_room_cell(
            console,
            main,
            cell_x,
            cell_y,
            cell_w,
            cell_h,
            node,
            room_type,
            is_current,
        )

    # Draw connections (corridors)
    for edge in matrix.edges:
        if edge.src in room_map and edge.dst in room_map:
            sx, sy = room_map[edge.src]
            dx, dy = room_map[edge.dst]
            _draw_corridor(
                console,
                main,
                grid_x + sx * cell_w,
                grid_y + sy * cell_h,
                grid_x + dx * cell_w,
                grid_y + dy * cell_h,
                cell_w,
                cell_h,
            )


def _draw_room_cell(
    console: tcod.console.Console,
    main: Region,
    x: int,
    y: int,
    w: int,
    h: int,
    node: Node,
    room_type: RoomType,
    is_current: bool,
) -> None:
    """Draw a single room cell."""
    # Border
    if is_current:
        fg_border = (0, 255, 255)  # Cyan for current
    elif room_type is RoomType.ICE:
        fg_border = (255, 50, 50)  # Red for ICE
    elif room_type is RoomType.DATA:
        fg_border = (255, 215, 0)  # Gold for data
    elif room_type is RoomType.NPC:
        fg_border = (255, 0, 255)  # Magenta for NPC
    elif room_type is RoomType.EXIT:
        fg_border = (0, 255, 0)  # Green for exit
    else:
        fg_border = (128, 128, 128)  # Gray

    # Top/bottom borders
    for xi in range(x, x + w):
        if main.contains(xi, y):
            console.print(x=xi, y=y, string="-", fg=fg_border)
        if main.contains(xi, y + h - 1):
            console.print(x=xi, y=y + h - 1, string="-", fg=fg_border)

    # Left/right borders
    for yi in range(y, y + h):
        if main.contains(x, yi):
            console.print(x=x, y=yi, string="|", fg=fg_border)
        if main.contains(x + w - 1, yi):
            console.print(x=x + w - 1, y=yi, string="|", fg=fg_border)

    # Corners
    for cx, cy, char in [
        (x, y, "+"),
        (x + w - 1, y, "+"),
        (x, y + h - 1, "+"),
        (x + w - 1, y + h - 1, "+"),
    ]:
        if main.contains(cx, cy):
            console.print(x=cx, y=cy, string=char, fg=fg_border)

    # Content
    if main.contains(x + 1, y + 1):
        # Room glyph
        glyph_map = {
            RoomType.ENTRY: "▶",
            RoomType.EXIT: "■",
            RoomType.DATA: "$",
            RoomType.ICE: "!",
            RoomType.NPC: "?",
            RoomType.ROUTER: "·",
            RoomType.CORE: "◎",
            RoomType.EMPTY: " ",
        }
        glyph = glyph_map.get(room_type, "?")

        # Current marker
        marker = "▶" if is_current else " "
        console.print(
            x=x + 1,
            y=y + 1,
            string=f"{marker}{glyph}",
            fg=(255, 255, 0) if is_current else (200, 200, 200),
        )

        # Label
        label = node.label[: w - 3]
        if main.contains(x + 1, y + 2):
            console.print(
                x=x + 1,
                y=y + 2,
                string=label,
                fg=(255, 255, 0) if is_current else (200, 200, 200),
            )


def _draw_corridor(
    console: tcod.console.Console,
    main: Region,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    cell_w: int,
    cell_h: int,
) -> None:
    """Draw a corridor between two room centers."""
    # Calculate centers
    c1x = x1 + cell_w // 2
    c1y = y1 + cell_h // 2
    c2x = x2 + cell_w // 2
    c2y = y2 + cell_h // 2

    fg = (80, 80, 80)

    # Draw L-shaped path
    # Horizontal segment
    x_min = min(c1x, c2x)
    x_max = max(c1x, c2x)
    for xi in range(x_min, x_max + 1):
        if main.contains(xi, c1y):
            console.print(x=xi, y=c1y, string="─", fg=fg)

    # Vertical segment
    y_min = min(c1y, c2y)
    y_max = max(c1y, c2y)
    for yi in range(y_min, y_max + 1):
        if main.contains(c2x, yi):
            console.print(x=c2x, y=yi, string="│", fg=fg)

    # Corner
    if c1x != c2x and c1y != c2y:
        corner_char = "┘" if c1x < c2x and c1y < c2y else "└"
        if main.contains(c2x, c1y):
            console.print(x=c2x, y=c1y, string=corner_char, fg=fg)


def _render_linear_fallback(
    console: tcod.console.Console,
    main: Region,
    state: AppState,
    matrix: MatrixGraph,
) -> None:
    """Fallback rendering if no room positions are available."""
    console.print(
        x=main.x + 2,
        y=main.y + 2,
        string="(dungeon layout unavailable)",
        fg=(128, 128, 128),
    )


def _get_room_position(node_id: str, matrix: MatrixGraph) -> tuple[int, int] | None:
    """Get the (x, y) grid position for a room.

    Uses a simple layout algorithm based on BFS from entry.
    """
    # For now, use deterministic layout based on node count
    # Try to get entry position
    entry = matrix.get(matrix.entry_id)
    if entry is None:
        return None

    # BFS from entry to assign grid positions
    visited: dict[str, tuple[int, int]] = {matrix.entry_id: (0, 0)}
    queue = [matrix.entry_id]

    while queue:
        current_id = queue.pop(0)
        cx, cy = visited[current_id]

        # Get neighbors
        for neighbor in matrix.neighbors(current_id):
            if neighbor.id in visited:
                continue

            # Try to place adjacent (prefer right, then up/down, then left)
            # Check available positions
            candidates = [
                (cx + 1, cy),  # right
                (cx, cy - 1),  # up
                (cx, cy + 1),  # down
                (cx - 1, cy),  # left
            ]

            placed = False
            for nx, ny in candidates:
                # Check if position is free
                if not any(pos == (nx, ny) for pos in visited.values()):
                    visited[neighbor.id] = (nx, ny)
                    queue.append(neighbor.id)
                    placed = True
                    break

            if not placed:
                # Fallback: place anywhere
                visited[neighbor.id] = (cx + 1, cy)

    return visited.get(node_id)


# ============================================================================
# Input handling
# ============================================================================


def handle_dungeon_input(
    event: tcod.event.Event,
    state: AppState,
    prog_registry: ProgramRegistry | None = None,
    ice_registry: IceRegistry | None = None,
) -> bool:
    """Handle input on the dungeon matrix screen."""
    if not isinstance(event, KeyDown):
        return True

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
        state.action_menu_open = False
        return True

    if event.sym is KeySym.Q:
        return False
    if event.sym is KeySym.ESCAPE:
        # Leave matrix
        state.screen = ScreenKind.HUB
        state.status_messages.append(">>> Jacked out of matrix")
        return True
    if is_confirm_key(event.sym):
        # Open action menu (ENTER or SPACE)
        if state.matrix and state.current_node_id:
            node = state.matrix.get(state.current_node_id)
            if node:
                # Check if NPC
                if node.kind is NodeKind.CONSTRUCT and node.id == "npc_dixie":
                    # Start NPC encounter
                    state.npc_state = NPCState(event=DIXIE_FLATLINE_EVENT)
                    state.screen = ScreenKind.NPC
                    state.status_messages.append(">>> Started NPC encounter: Dixie Flatline")
                    return True
                # Normal action menu
                state.status_messages.append(f">>> Action menu opened for {node.label}")
                state.action_menu_open = True
        return True

    # Cardinal direction movement
    if event.sym in (KeySym.UP, KeySym.DOWN, KeySym.LEFT, KeySym.RIGHT):
        _handle_cardinal_movement(state, event.sym)
        return True

    return True


def _handle_cardinal_movement(state: AppState, sym: KeySym) -> None:
    """Handle movement in cardinal directions."""
    matrix = state.matrix
    if matrix is None or state.current_node_id is None:
        return

    # Get current position
    current_pos = _get_room_position(state.current_node_id, matrix)
    if current_pos is None:
        return

    cx, cy = current_pos
    target_dir = {
        KeySym.UP: (0, -1),
        KeySym.DOWN: (0, 1),
        KeySym.LEFT: (-1, 0),
        KeySym.RIGHT: (1, 0),
    }[sym]

    target_x = cx + target_dir[0]
    target_y = cy + target_dir[1]
    direction_name = {
        KeySym.UP: "NORTH",
        KeySym.DOWN: "SOUTH",
        KeySym.LEFT: "WEST",
        KeySym.RIGHT: "EAST",
    }[sym]

    # Find node at target position
    target_node = None
    for node in matrix.nodes:
        pos = _get_room_position(node.id, matrix)
        if pos == (target_x, target_y):
            # Check if connected
            if any(e.dst == node.id for e in matrix.edges if e.src == state.current_node_id):
                target_node = node
                break

    if target_node:
        state.current_node_id = target_node.id
        if state.exploration is not None:
            state.exploration.visit(target_node.id)
        state.status_messages.append(
            f">>> Moved {direction_name} to {target_node.label} ({target_node.kind.value})"
        )
    else:
        state.status_messages.append(f">>> No room to the {direction_name}")
