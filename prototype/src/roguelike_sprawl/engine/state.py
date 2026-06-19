"""App state (ADR-0006, ADR-0009, design/systems/hacking.md).

A single mutable ``AppState`` is shared by all screens. Screens are
implemented as functions over the state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

from ..combat.effects import CombatEffects
from ..combat.state import CombatState
from ..matrix.exploration import ExplorationState
from ..matrix.graph import MatrixGraph
from ..matrix.ppl import Loadout, Program
from ..missions import JobBoard, Mission

if TYPE_CHECKING:
    from ..audio import SoundConfig
    from ..cyberspace.world import WorldMap
    from ..run.state import RunState
    from .event_story import EventRegistry, EventState
    from .npc_event import NPCState
    from .story_cinematic import CinematicState


class ScreenKind(StrEnum):
    """Top-level screens of the game (ADR-0006, ADR-0009)."""

    MENU = "menu"
    HUB = "hub"
    MATRIX = "matrix"
    CYBERSPACE_BROWSER = "cyberspace_browser"  # Browse worlds/sectors/servers
    CYBERSPACE_MAP = "cyberspace_map"  # World/sector map view
    COMBAT = "combat"  # Real-Time with Menu Skills (ADR-0003)
    CINEMATIC = "cinematic"  # Story presentation with typing effects (Phase 5+)
    STORY = "story"  # Aftermath / narrative / character reactions (ADR-0019)
    DEATH = "death"
    NPC = "npc"  # NPC encounter with dialogue choices
    EVENT = "event"  # Event story (cutscene with character art)
    JACK_OUT = "jack_out"  # Matrix disconnect animation (Stage.JACK_OUT)
    REWARD = "reward"  # Mission rewards screen (Stage.REWARD)
    DEBRIEF = "debrief"  # Optional narrative between REWARD and COMPLETE
    SAVE_LOAD = "save_load"  # Save/Load slot browser (Hub)


# A grade-1 (1-up) loadout: Ono-Sendai 4 (T1) + Wisp (T1) + Standard (T1).
# PPL = 1*3 + 1*2 + 1 = 6. Matches the ADR-0012 example.
DEFAULT_LOADOUT_T1 = Loadout(
    deck_tier=1,
    programs=(Program(id="wisp", name="Wisp", tier=1),),
    wetware_tier=1,
)


@dataclass
class AppState:
    """Mutable game state shared by all screens."""

    screen: ScreenKind = ScreenKind.MENU
    player_grade: int = 1
    player_loadout: Loadout = field(default_factory=lambda: DEFAULT_LOADOUT_T1)
    job_board: JobBoard = field(default_factory=JobBoard)
    current_mission: Mission | None = None
    matrix: MatrixGraph | None = None
    current_node_id: str | None = None
    hub_selected_index: int = 0
    message: str = ""
    # Fog of war / exploration state (ADR-0020). None until a matrix
    # is loaded. Owned by the matrix screen.
    exploration: ExplorationState | None = None
    # Combat state (ADR-0003). None until combat starts.
    combat_state: CombatState | None = None
    # Action menu state (Phase 5). True when action menu is open.
    action_menu_open: bool = False
    # Action menu navigation (arrow key selection)
    action_menu_index: int = 0
    # Combat skill menu navigation (arrow key selection)
    combat_skill_index: int = 0
    # Cinematic state (Phase 5+). None until cinematic starts.
    cinematic_state: CinematicState | None = None
    # NPC encounter state. None until NPC encounter starts.
    npc_state: NPCState | None = None
    # NPC choice navigation (arrow key selection)
    npc_choice_index: int = 0
    # Event story state (cutscenes with character art)
    active_event: EventState | None = None
    # Set of shown event IDs (one-time events)
    shown_events: set[str] = field(default_factory=set)
    # Story flags (for event conditions)
    story_flags: set[str] = field(default_factory=set)
    # Event registry (initialized lazily)
    _event_registry: EventRegistry | None = None
    # Player inventory (item_id -> count)
    inventory: dict[str, int] = field(default_factory=dict)
    # Equipped loadout (cyberpunk gear)
    equipment_loadout: object = None  # EquipmentLoadout
    # Defeated nodes (node_id set) - removed from dungeon after combat
    defeated_nodes: set[str] = field(default_factory=set)
    # Extracted data nodes (node_id set) - data already collected
    extracted_nodes: set[str] = field(default_factory=set)
    # Cyberspace layout (node_id -> (x, y, depth)) for scrolling view
    cyberspace_layouts: dict[str, object] | None = None
    # World map (World → Sector → Server hierarchy)
    world_map: WorldMap | None = None
    # Current server's subgraph (the explorable graph)
    server_subgraph: object | None = None  # tuple[MatrixGraph, dict]
    # Server list (for the server browser)
    available_servers: list[str] = field(default_factory=list)
    # Selected server in browser
    selected_server_index: int = 0
    # Server view mode (browsing vs exploring)
    in_server_browser: bool = True
    # Story event fields (ADR-0019)
    story_aftermath_id: str = "aftermath_black_ice"
    story_importance: str = "major"
    # Display fields (filled by the demo / shell)
    player_ppl: int = 0
    player_hp: int = 0
    player_max_hp: int = 0
    demo_step: int = 0
    demo_elapsed_s: float = 0.0
    # Status messages (shown in footer or side panel)
    status_messages: list[str] = field(default_factory=list)
    # Current context hint (what to do now)
    context_hint: str = ""
    # Player credits (wallet)
    credits: int = 0
    # Mission progress: objective_type -> count
    # (e.g. {"extract_data": 1, "defeat": 2})
    mission_progress: dict[str, int] = field(default_factory=dict)
    # Completed mission IDs (so we don't re-offer them)
    completed_missions: set[str] = field(default_factory=set)
    # Player is dead (flatline); True until reset
    is_dead: bool = False
    # Death reason (e.g. "Combat", "ICE breach", "Jack-out failure")
    death_reason: str = ""
    # Run progress (stages + current target). The single source of truth
    # for "what should the player be doing right now?"
    run_state: RunState | None = None
    # Sound configuration (per-category on/off + master volume)
    sound_config: SoundConfig | None = None
    # Jack Out animation state (Stage.JACK_OUT)
    jack_out_started_at: float = 0.0
    jack_out_frame_index: int = 0
    # Debrief state (Stage.DEBRIEF)
    debrief_character: str = "novice"
    debrief_index: int = 0
    # Save/Load browser state (ScreenKind.SAVE_LOAD)
    save_load_selected: int = 1
    # Combat visual effects (animations, particles, screen shake, etc.)
    combat_effects: CombatEffects = field(default_factory=CombatEffects)
