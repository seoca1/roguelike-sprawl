"""Cyberspace graph generator: large branching tree.

Generates a graph-based exploration with:
- Branching paths (binary/ternary tree)
- Multiple depth levels
- Wider than screen (requires scrolling)
- Various node types at different depths
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import StrEnum

from .graph import Edge, MatrixGraph
from .node import Faction, IceKind, Node, NodeKind, ZoneDepth


class DepthLevel(StrEnum):
    """Depth levels in cyberspace (cyberspace hierarchy)."""

    SURFACE = "surface"  # Entry level
    SHALLOW = "shallow"  # First branching
    MID = "mid"  # Middle layers
    DEEP = "deep"  # Deep system
    CORE = "core"  # Core systems


@dataclass
class CyberspaceLayout:
    """Layout information for cyberspace nodes.

    Stores absolute positions for each node (not constrained to a grid).
    """

    node_id: str
    x: float  # Continuous x coordinate
    y: float  # Continuous y coordinate (0 = surface, positive = deeper)
    depth: DepthLevel


class CyberspaceGenerator:
    """Generates a large branching cyberspace graph.

    Layout strategy:
    - Entry at (0, 0)
    - Each level adds y depth
    - Branching factor 2-3 per node
    - Width grows with depth (exponential)
    - Total ~30-50 nodes
    """

    __slots__ = ()

    def generate(
        self, seed: int, mission_grade: int = 1
    ) -> tuple[MatrixGraph, dict[str, CyberspaceLayout]]:
        """Generate cyberspace graph with layout info.

        Returns:
            (graph, layouts) where layouts is a dict of node_id -> CyberspaceLayout
        """
        rng = random.Random(seed)
        layouts: dict[str, CyberspaceLayout] = {}
        nodes: list[Node] = []
        edges: list[Edge] = []

        faction = Faction.SENSE_NET

        # Layout configuration
        y_spacing = 8  # Vertical distance between depth levels
        x_branching = 12  # Horizontal distance between branches

        # ===== Level 0: Entry (surface) =====
        entry_id = "entry"
        nodes.append(self._make_node(entry_id, NodeKind.ENTRY, "Entry", faction, ZoneDepth.SURFACE))
        layouts[entry_id] = CyberspaceLayout(entry_id, 0, 0, DepthLevel.SURFACE)

        # ===== Level 1: Shallow - 2-3 branches from entry =====
        n_l1 = rng.randint(2, 3)
        l1_nodes = self._generate_level(
            rng,
            entry_id,
            n_l1,
            x_branching,
            y_spacing,
            DepthLevel.SHALLOW,
            ZoneDepth.SURFACE,
            faction,
            node_kinds=[NodeKind.ROUTER, NodeKind.DATA, NodeKind.CONSTRUCT],
            nodes=nodes,
            edges=edges,
            layouts=layouts,
        )

        # ===== Level 2: Mid - branch from L1 nodes =====
        # Each L1 node leads to 1-2 L2 nodes
        l2_parents = l1_nodes
        l2_nodes = []
        for parent in l2_parents:
            n_children = rng.randint(1, 2)
            children = self._generate_level(
                rng,
                parent,
                n_children,
                x_branching,
                y_spacing,
                DepthLevel.MID,
                ZoneDepth.SURFACE,
                faction,
                node_kinds=[NodeKind.ROUTER, NodeKind.ICE, NodeKind.SYSTEM],
                nodes=nodes,
                edges=edges,
                layouts=layouts,
            )
            l2_nodes.extend(children)

        # ===== Level 3: Deep - branch from some L2 nodes =====
        # Some L2 nodes lead to L3 (data, ice, core)
        l3_parents = [n for n in l2_nodes if rng.random() < 0.6]  # 60% branch further
        for parent in l3_parents:
            n_children = rng.randint(1, 2)
            children = self._generate_level(
                rng,
                parent,
                n_children,
                x_branching * 1.5,
                y_spacing,
                DepthLevel.DEEP,
                ZoneDepth.MID,
                faction,
                node_kinds=[NodeKind.ICE, NodeKind.DATA, NodeKind.CONSTRUCT],
                nodes=nodes,
                edges=edges,
                layouts=layouts,
            )
            # Ensure at least one ICE in deep level
            for c in children:
                if c == "ice_1":  # First ICE generated
                    # Force this to be ICE
                    for i, n in enumerate(nodes):
                        if n.id == c:
                            nodes[i] = Node(
                                id=c,
                                kind=NodeKind.ICE,
                                label="ICE Sentinel",
                                zone=ZoneDepth.MID,
                                ice=IceKind.STANDARD,
                                faction=faction,
                            )
                            break

        # ===== Ensure exactly 1 main ICE for mission =====
        # Find or create one ICE at deep level
        if not any(n.kind is NodeKind.ICE for n in nodes):
            # Add one at deep level
            parent = l2_nodes[0] if l2_nodes else entry_id
            parent_layout = layouts[parent]
            ice_id = "ice_main"
            nodes.append(
                Node(
                    id=ice_id,
                    kind=NodeKind.ICE,
                    label="ICE Sentinel",
                    zone=ZoneDepth.MID,
                    ice=IceKind.STANDARD,
                    faction=faction,
                )
            )
            layouts[ice_id] = CyberspaceLayout(
                ice_id,
                parent_layout.x,
                parent_layout.y + y_spacing,
                DepthLevel.DEEP,
            )
            edges.append(Edge(parent, ice_id))

        # ===== Level 4: Core - exit at the end =====
        # Find deepest nodes and add exit
        deepest_nodes = [n for n in nodes if layouts[n.id].depth is DepthLevel.DEEP]
        if deepest_nodes:
            exit_parent_node = deepest_nodes[0]
            exit_parent_id = exit_parent_node.id
            exit_id = "exit"
            parent_layout = layouts[exit_parent_id]
            nodes.append(
                Node(
                    id=exit_id,
                    kind=NodeKind.EXIT,
                    label="Exit",
                    zone=ZoneDepth.CORE,
                    faction=faction,
                )
            )
            layouts[exit_id] = CyberspaceLayout(
                exit_id,
                parent_layout.x,
                parent_layout.y + y_spacing,
                DepthLevel.CORE,
            )
            edges.append(Edge(exit_parent_id, exit_id))

        # ===== Ensure there's an NPC somewhere =====
        if not any(n.kind is NodeKind.CONSTRUCT for n in nodes):
            # Add NPC near entry
            npc_id = "npc_dixie"
            npc_parent = entry_id
            parent_layout = layouts[npc_parent]
            nodes.append(
                Node(
                    id=npc_id,
                    kind=NodeKind.CONSTRUCT,
                    label="Dixie Flatline",
                    zone=ZoneDepth.SURFACE,
                    faction=faction,
                )
            )
            layouts[npc_id] = CyberspaceLayout(
                npc_id,
                parent_layout.x - x_branching,
                parent_layout.y + y_spacing,
                DepthLevel.SHALLOW,
            )
            edges.append(Edge(npc_parent, npc_id))

        # ===== Add some data nodes =====
        router_nodes = [
            n
            for n in nodes
            if n.kind is NodeKind.ROUTER
            and layouts[n.id].depth in (DepthLevel.SHALLOW, DepthLevel.MID)
        ]
        for i, router in enumerate(router_nodes[:2]):
            data_id = f"data_{i}"
            parent_layout = layouts[router.id]
            nodes.append(
                Node(
                    id=data_id,
                    kind=NodeKind.DATA,
                    label="Data Vault",
                    zone=ZoneDepth.SURFACE,
                    faction=faction,
                )
            )
            layouts[data_id] = CyberspaceLayout(
                data_id,
                int(parent_layout.x + (2 if i % 2 == 0 else -2)),
                int(parent_layout.y + y_spacing * 0.5),
                DepthLevel.SHALLOW,
            )
            edges.append(Edge(router.id, data_id))

        graph = MatrixGraph(
            nodes=tuple(nodes),
            edges=tuple(edges),
            entry_id=entry_id,
        )

        return graph, layouts

    def _generate_level(
        self,
        rng: random.Random,
        parent_id: str,
        n_children: int,
        x_spacing: float,
        y_spacing: float,
        depth: DepthLevel,
        zone: ZoneDepth,
        faction: Faction,
        node_kinds: list[NodeKind],
        nodes: list[Node],
        edges: list[Edge],
        layouts: dict[str, CyberspaceLayout],
    ) -> list[str]:
        """Generate child nodes from a parent."""
        parent_layout = layouts[parent_id]
        children: list[str] = []

        # Calculate x positions for children
        if n_children == 1:
            x_offsets: list[float] = [0]
        elif n_children == 2:
            x_offsets = [-x_spacing / 2, x_spacing / 2]
        elif n_children == 3:
            x_offsets = [-x_spacing, 0, x_spacing]
        else:
            x_offsets = [(i - (n_children - 1) / 2) * x_spacing for i in range(n_children)]

        for i in range(n_children):
            child_id = f"{parent_id}_{depth.value}_{i}"
            kind = rng.choice(node_kinds)

            # Random label
            labels = {
                NodeKind.ROUTER: "Router",
                NodeKind.DATA: "Data Vault",
                NodeKind.ICE: "ICE",
                NodeKind.SYSTEM: "System",
                NodeKind.CONSTRUCT: "Construct",
            }
            label = labels.get(kind, "Node")

            nodes.append(self._make_node(child_id, kind, label, faction, zone))
            layouts[child_id] = CyberspaceLayout(
                child_id,
                int(parent_layout.x + x_offsets[i]),
                int(parent_layout.y + y_spacing),
                depth,
            )
            edges.append(Edge(parent_id, child_id))
            children.append(child_id)

        return children

    def _make_node(
        self,
        node_id: str,
        kind: NodeKind,
        label: str,
        faction: Faction,
        zone: ZoneDepth,
    ) -> Node:
        """Create a node with default settings."""
        ice_kind = IceKind.STANDARD if kind is NodeKind.ICE else IceKind.NONE
        return Node(
            id=node_id,
            kind=kind,
            label=label,
            zone=zone,
            ice=ice_kind,
            faction=faction,
        )
