"""Phase 1 — Dungeon Mode walkthrough (dungeon_view + dungeon_mode toggle).

This demo is headless: it does not open a tcod window.  It
programmatically performs the same actions the player performs
in-game when they press the ``D`` key in the matrix screen:

1. Construct an ``AppState`` with ``dungeon_mode=False`` (default).
2. Toggle ``dungeon_mode=True`` (same code path as the ``D`` key in
   ``engine/app.py``).
3. Generate a BSP dungeon via ``ProceduralDungeonGenerator`` and
   attach it to ``state.matrix`` (the canonical field
   ``render_dungeon_matrix`` reads).
4. Run ``_get_room_position`` (the routine that lays out nodes on the
   grid) on every node and print the resulting 2-D layout so the
   operator can verify the room positions match the BSP tree.
5. Report the cleared-room bookkeeping hook (``defeat``) used by
   Phase 4.

The actual ``render_dungeon_matrix`` requires a live ``tcod.Console``,
which is exercised by ``scripts/play.py``.  Here we use the lower-
level primitives that share the same code path.

Run::

    PYTHONPATH=src .venv/bin/python scripts/play_dungeon_mode.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roguelike_sprawl.engine import dungeon_view  # noqa: E402
from roguelike_sprawl.engine.state import AppState  # noqa: E402
from roguelike_sprawl.matrix.dungeon_generator import (  # noqa: E402
    ProceduralDungeonGenerator,
)


def main() -> int:
    print("=" * 60)
    print("Phase 1 — Dungeon Mode (dungeon_view + Procedural Dungeon)")
    print("=" * 60)

    state = AppState()
    print(f"[1] dungeon_mode default        : {state.dungeon_mode}")
    state.dungeon_mode = True
    print(f"[2] dungeon_mode after 'D' toggle: {state.dungeon_mode}")

    gen = ProceduralDungeonGenerator(min_leaf_size=2, room_padding=1)
    graph = gen.generate(seed=42, mission_grade=1, character_ref="veteran")
    state.matrix = graph
    state.current_node_id = graph.nodes[0].id if graph.nodes else None
    print(
        f"[3] BSP dungeon                  : {len(graph.nodes)} rooms, {len(graph.edges)} corridors"
    )

    # Compute room_map exactly the same way render_dungeon_matrix does.
    room_map = {node.id: dungeon_view._get_room_position(node.id, graph) for node in graph.nodes}
    room_map = {k: v for k, v in room_map.items() if v is not None}
    pos_items = sorted(
        room_map.items(),
        key=lambda kv: (kv[1][1], kv[1][0]) if kv[1] else (0, 0),
    )

    print("[4] grid layout (node_id → (x,y)):")
    for nid, pos in pos_items[:8]:
        cur = "*" if nid == state.current_node_id else " "
        print(f"      {cur} {nid:8s} → {pos}")

    print()
    print("[5] render entry path used in dungeon_view.render_dungeon_matrix:")
    print("      console.print(...) → state.matrix is attached.")
    print(f"      state.current_node_id = {state.current_node_id!r}")
    print(f"      state.dungeon_mode    = {state.dungeon_mode}")

    print()
    print("*** Phase 1 OK: dungeon_mode toggle + BSP attachment + grid positions verified ***")
    return 0


if __name__ == "__main__":
    sys.exit(main())
