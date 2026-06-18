"""Matrix graph and BFS layout (ADR-0005)."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass

from .node import Node, NodeKind


@dataclass(frozen=True, slots=True)
class Edge:
    """A directed edge between two matrix nodes (ADR-0005)."""

    src: str
    dst: str

    def __post_init__(self) -> None:
        if not self.src or not self.dst:
            raise ValueError("Edge endpoints must be non-empty")
        if self.src == self.dst:
            raise ValueError("Edge cannot be a self-loop")


@dataclass(frozen=True, slots=True)
class MatrixGraph:
    """The cyberspace node graph for a single mission (ADR-0005).

    The graph is a DAG: edges point from shallower to deeper nodes.
    """

    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]
    entry_id: str

    def __post_init__(self) -> None:
        ids = {n.id for n in self.nodes}
        if len(ids) != len(self.nodes):
            raise ValueError("MatrixGraph: duplicate node ids")
        if self.entry_id and self.entry_id not in ids:
            raise ValueError(f"entry_id {self.entry_id!r} not in nodes")
        for e in self.edges:
            if e.src not in ids:
                raise ValueError(f"edge src {e.src!r} not in nodes")
            if e.dst not in ids:
                raise ValueError(f"edge dst {e.dst!r} not in nodes")

    def get(self, node_id: str) -> Node | None:
        """Return the Node with the given id, or None if absent."""
        for n in self.nodes:
            if n.id == node_id:
                return n
        return None

    def neighbors(self, node_id: str) -> list[Node]:
        """Return nodes reachable in one step from ``node_id``."""
        out_ids = {e.dst for e in self.edges if e.src == node_id}
        out: list[Node] = []
        for n in self.nodes:
            if n.id in out_ids:
                out.append(n)
        return out

    def is_connected(self, src: str, dst: str) -> bool:
        """Return True if there is a direct edge from ``src`` to ``dst``."""
        return any(e.src == src and e.dst == dst for e in self.edges)

    def exits(self) -> list[Node]:
        """Return all exit nodes."""
        return [n for n in self.nodes if n.kind is NodeKind.EXIT]

    def __contains__(self, node_id: object) -> bool:
        return isinstance(node_id, str) and any(n.id == node_id for n in self.nodes)

    def __iter__(self) -> Iterator[Node]:
        return iter(self.nodes)

    def __len__(self) -> int:
        return len(self.nodes)

    def __repr__(self) -> str:
        return f"MatrixGraph(nodes={len(self.nodes)}, edges={len(self.edges)}, entry={self.entry_id!r})"


def compute_layout(
    graph: MatrixGraph,
    *,
    col_step: int = 18,
    row_step: int = 8,
    origin_x: int = 2,
    origin_y: int = 12,
) -> dict[str, tuple[int, int]]:
    """Compute a (col, row) grid position for each node (BFS-layer layout).

    Layer 0 (entry) is leftmost. Each BFS layer is a column. Within a
    column nodes are stacked vertically and sorted by id for determinism.

    Returns a dict mapping node id -> (col, row) suitable for tcod consoles.
    """
    if len(graph) == 0:
        return {}

    # BFS to compute layer (shortest distance from entry)
    layers: dict[int, list[str]] = {}
    visited: dict[str, int] = {graph.entry_id: 0}
    layers[0] = [graph.entry_id]
    queue: deque[tuple[str, int]] = deque([(graph.entry_id, 0)])
    while queue:
        nid, layer = queue.popleft()
        for nbr in graph.neighbors(nid):
            if nbr.id not in visited:
                visited[nbr.id] = layer + 1
                layers.setdefault(layer + 1, []).append(nbr.id)
                queue.append((nbr.id, layer + 1))

    # Sort within each layer for deterministic layout
    for nids in layers.values():
        nids.sort()

    # Center each layer vertically around ``origin_y``.
    positions: dict[str, tuple[int, int]] = {}
    for layer, nids in layers.items():
        col = origin_x + layer * col_step
        total = len(nids)
        for i, nid in enumerate(nids):
            if total == 1:
                row = origin_y
            else:
                # Center the column around origin_y
                start = origin_y - (total - 1) * row_step // 2
                row = start + i * row_step
            positions[nid] = (col, row)
    return positions
