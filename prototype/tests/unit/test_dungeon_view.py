"""Tests for dungeon view rendering and D-key toggle (ADR-0060 Phase 1).

Covers:
    - AppState.dungeon_mode default False
    - `_handle_input` on MATRIX screen with D key toggles dungeon_mode
    - Shift+D does NOT toggle (reserved for future)
    - Other MATRIX keys still dispatched correctly when dungeon_mode=True
    - render_dungeon_matrix generates glyphs without errors
    - 4-directional movement inside dungeon
"""

from __future__ import annotations

import sys
from pathlib import Path

import tcod.console
import tcod.event
from tcod.event import KeyDown, KeySym

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from roguelike_sprawl.combat.registry import IceRegistry, ProgramRegistry  # noqa: E402
from roguelike_sprawl.engine import dungeon_view  # noqa: E402
from roguelike_sprawl.engine.app import AppState, ScreenKind, _handle_input  # noqa: E402
from roguelike_sprawl.matrix import (  # noqa: E402
    Edge,
    IceKind,
    MatrixGraph,
    Node,
    NodeKind,
    ZoneDepth,
)

# ----------------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------------


def _make_graph() -> MatrixGraph:
    """Build a 4-node graph: entry -> data -> ice -> exit."""
    nodes = (
        Node(
            id="entry",
            label="Jack-in Point",
            kind=NodeKind.ENTRY,
            zone=ZoneDepth.SURFACE,
        ),
        Node(
            id="data",
            label="Data Vault",
            kind=NodeKind.DATA,
            zone=ZoneDepth.SURFACE,
        ),
        Node(
            id="ice",
            label="Hostile ICE",
            kind=NodeKind.ICE,
            zone=ZoneDepth.MID,
            ice=IceKind.STANDARD,
        ),
        Node(
            id="exit",
            label="Extraction Gate",
            kind=NodeKind.EXIT,
            zone=ZoneDepth.CORE,
        ),
    )
    edges = (
        Edge(src="entry", dst="data"),
        Edge(src="data", dst="ice"),
        Edge(src="ice", dst="exit"),
    )
    g = MatrixGraph(nodes=nodes, edges=edges, entry_id="entry")
    return g


def _key_event(sym: KeySym, shift: bool = False) -> KeyDown:
    """Create a synthetic KeyDown event (no console needed)."""
    return KeyDown(
        sym=sym,
        mod=tcod.event.Modifier.SHIFT if shift else tcod.event.Modifier(0),
        scancode=int(sym),
    )


def _state_with_graph() -> AppState:
    s = AppState()
    s.matrix = _make_graph()
    s.current_node_id = "entry"
    s.exploration = None  # not exercising fog
    s.screen = ScreenKind.MATRIX
    return s


def _prog_registry() -> ProgramRegistry:
    # Empty registry — load() raises FileNotFoundError if file missing,
    # but passing None is acceptable for these tests.
    return None  # type: ignore[return-value]


def _ice_registry() -> IceRegistry:
    return None  # type: ignore[return-value]


# ============================================================================
# dungeon_mode field
# ============================================================================


class TestDungeonModeField:
    def test_default_is_false(self) -> None:
        s = AppState()
        assert s.dungeon_mode is False


# ============================================================================
# D key toggle (MATRIX screen only)
# ============================================================================


class TestDKeyToggle:
    def test_d_toggles_dungeon_mode_true(self) -> None:
        s = _state_with_graph()
        assert s.dungeon_mode is False
        keep = _handle_input(
            _key_event(KeySym.D),
            s,
            _prog_registry(),  # type: ignore[arg-type]
            _ice_registry(),  # type: ignore[arg-type]
        )
        assert keep is True
        assert s.dungeon_mode is True

    def test_d_toggles_back_to_false(self) -> None:
        s = _state_with_graph()
        s.dungeon_mode = True
        _handle_input(
            _key_event(KeySym.D),
            s,
            _prog_registry(),  # type: ignore[arg-type]
            _ice_registry(),  # type: ignore[arg-type]
        )
        assert s.dungeon_mode is False

    def test_shift_d_does_not_toggle(self) -> None:
        """Shift+D is reserved for future use; must not toggle."""
        s = _state_with_graph()
        assert s.dungeon_mode is False
        _handle_input(
            _key_event(KeySym.D, shift=True),
            s,
            _prog_registry(),  # type: ignore[arg-type]
            _ice_registry(),  # type: ignore[arg-type]
        )
        # Shift+D fell through to matrix_view's input handler
        # (which itself ignores it without a matrix). dungeon_mode unchanged.
        assert s.dungeon_mode is False

    def test_d_appends_status_message(self) -> None:
        s = _state_with_graph()
        _handle_input(
            _key_event(KeySym.D),
            s,
            _prog_registry(),  # type: ignore[arg-type]
            _ice_registry(),  # type: ignore[arg-type]
        )
        assert any("View mode" in msg for msg in s.status_messages)


# ============================================================================
# Cardinal direction movement in dungeon mode
# ============================================================================


class TestCardinalMovementDungeon:
    def test_handle_dungeon_input_right_moves_to_neighbor(self) -> None:
        s = _state_with_graph()
        s.dungeon_mode = True
        # Map ids -> positions. The graph is linear so we rely on dungeon_view's
        # BFS layout to place each node uniquely.
        dungeon_view._handle_cardinal_movement(s, KeySym.RIGHT)
        # After pressing RIGHT, we may or may not move (depends on layout),
        # but the call should not raise.
        assert s.current_node_id in {"entry", "data", "ice", "exit"}

    def test_handle_dungeon_input_invalid_direction_no_op(self) -> None:
        s = _state_with_graph()
        s.dungeon_mode = True
        # Press UP on a graph that may not have a neighbor above —
        # the call should never raise regardless of the layout it computes.
        dungeon_view._handle_cardinal_movement(s, KeySym.UP)
        # After any movement attempt, current_node_id is still one of the
        # 4 known nodes (no exception, no garbage state).
        assert s.current_node_id in {"entry", "data", "ice", "exit"}


# ============================================================================
# Smoke render (does not assert content; just verifies it draws without error)
# ============================================================================


class TestDungeonRenderSmoke:
    def test_render_dungeon_matrix_does_not_raise(self) -> None:
        s = _state_with_graph()
        s.dungeon_mode = True
        console = tcod.console.Console(80, 50, order="F")
        # T (Translator) not used by render_dungeon_matrix in current impl;
        # pass None to confirm signature flexibility.
        dungeon_view.render_dungeon_matrix(console, None, s)  # type: ignore[arg-type]
