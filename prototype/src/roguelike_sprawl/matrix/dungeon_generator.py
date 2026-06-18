"""Dungeon-style matrix generator.

Generates a 2D grid-based dungeon with rooms connected by corridors.
Uses a BFS-based layout algorithm for clean cardinal direction movement.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .graph import Edge, MatrixGraph
from .node import Faction, IceKind, Node, NodeKind, ZoneDepth


class RoomType(StrEnum):
    """Visual type of room for rendering."""

    EMPTY = "empty"
    ENTRY = "entry"
    EXIT = "exit"
    DATA = "data"
    ICE = "ice"
    NPC = "npc"
    ROUTER = "router"
    CORE = "core"


@dataclass
class Room:
    """A room in the dungeon grid."""

    id: str
    x: int
    y: int
    room_type: RoomType
    label: str
    description: str = ""


class DungeonGenerator:
    """Generates a 2D grid-based dungeon with rooms."""

    __slots__ = ()

    def generate(self, seed: int, mission_grade: int = 1) -> MatrixGraph:
        """Generate a dungeon-style MatrixGraph.

        Grid: 7x5 (cols x rows)
        Rooms: entry → npc → data → ice → exit (linear path with branches)
        """
        # Layout is deterministic; seed reserved for future random variations
        del seed

        # Define room positions manually for predictable layout
        # Path: entry(0,2) → corridor(1,2) → npc(2,2) → corridor(3,2) → data(4,2) → corridor(5,2) → ice(6,2) → exit(6,3)
        # Plus branches: (1,1) and (5,1) for atmosphere
        layout: list[tuple[str, int, int, RoomType, str]] = [
            ("entry", 0, 2, RoomType.ENTRY, "Entry"),
            ("corridor_1", 1, 2, RoomType.ROUTER, "Corridor"),
            ("npc_dixie", 2, 2, RoomType.NPC, "Dixie Flatline"),
            ("corridor_2", 3, 2, RoomType.ROUTER, "Corridor"),
            ("data", 4, 2, RoomType.DATA, "Data Vault"),
            ("corridor_3", 5, 2, RoomType.ROUTER, "Corridor"),
            ("ice", 6, 2, RoomType.ICE, "ICE Barrier"),
            ("exit", 6, 3, RoomType.EXIT, "Exit"),
            # Side rooms for atmosphere
            ("side_1", 1, 1, RoomType.ROUTER, "Side Room"),
            ("side_2", 5, 3, RoomType.ROUTER, "Side Room"),
        ]

        rooms: list[Room] = [
            Room(id=room_id, x=x, y=y, room_type=room_type, label=label)
            for room_id, x, y, room_type, label in layout
        ]

        # Define connections (cardinal moves only)
        edges: list[Edge] = [
            Edge("entry", "corridor_1"),
            Edge("corridor_1", "npc_dixie"),
            Edge("corridor_1", "side_1"),
            Edge("npc_dixie", "corridor_2"),
            Edge("corridor_2", "data"),
            Edge("data", "corridor_3"),
            Edge("corridor_3", "ice"),
            Edge("corridor_3", "side_2"),
            Edge("ice", "exit"),
            # Reverse (since graph is undirected)
            Edge("corridor_1", "entry"),
            Edge("npc_dixie", "corridor_1"),
            Edge("side_1", "corridor_1"),
            Edge("corridor_2", "npc_dixie"),
            Edge("data", "corridor_2"),
            Edge("corridor_3", "data"),
            Edge("ice", "corridor_3"),
            Edge("side_2", "corridor_3"),
            Edge("exit", "ice"),
        ]

        # Convert rooms to Nodes
        faction = Faction.SENSE_NET
        nodes: list[Node] = []

        for room in rooms:
            if room.room_type is RoomType.ENTRY:
                node_kind = NodeKind.ENTRY
                ice_kind = IceKind.NONE
            elif room.room_type is RoomType.EXIT:
                node_kind = NodeKind.EXIT
                ice_kind = IceKind.NONE
            elif room.room_type is RoomType.DATA:
                node_kind = NodeKind.DATA
                ice_kind = IceKind.NONE
            elif room.room_type is RoomType.ICE:
                node_kind = NodeKind.ICE
                ice_kind = IceKind.STANDARD
            elif room.room_type is RoomType.NPC:
                node_kind = NodeKind.CONSTRUCT
                ice_kind = IceKind.NONE
            else:
                node_kind = NodeKind.ROUTER
                ice_kind = IceKind.NONE

            node = Node(
                id=room.id,
                kind=node_kind,
                label=room.label,
                zone=ZoneDepth.SURFACE,
                ice=ice_kind,
                faction=faction,
            )
            nodes.append(node)

        return MatrixGraph(
            nodes=tuple(nodes),
            edges=tuple(edges),
            entry_id="entry",
        )
