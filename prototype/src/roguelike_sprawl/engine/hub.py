"""Hub screen: the cyberspace construct job board (ADR-0009, ADR-0017).

Meatspace is *not* shown (Pillar 2). The Hub is a text-based construct
interface. Fixer dialogue is also text-only — no portraits of meatspace
people.

Phase 5+: 4-panel layout (Avatar / Materials / Recipes / Job Board).
Uses unified screen shell (engine.layout).
"""

from __future__ import annotations

import tcod.console
import tcod.event
from tcod.event import KeyDown, KeySym

from ..i18n import Translator
from ..matrix.ppl import calculate_ppl
from ..matrix.zdr import calculate_status, calculate_zdr, status_color
from ..missions import Mission
from .layout import (
    Region,
    RegionId,
    clear_region,
    draw_controls,
    draw_dividers,
    draw_footer,
    draw_side,
    draw_title,
    make_shell,
)
from .state import AppState, ScreenKind


def render_hub(console: tcod.console.Console, t: Translator, state: AppState) -> None:
    """Render the Hub (job board) screen with unified layout."""
    shell = make_shell()
    title_r = shell[RegionId.TITLE]
    main_r = shell[RegionId.MAIN]
    side_r = shell[RegionId.SIDE]
    ctrl_r = shell[RegionId.CONTROLS]
    foot_r = shell[RegionId.FOOTER]

    # Clear and draw dividers
    for r in shell.values():
        clear_region(console, r)
    draw_dividers(console)

    # Title
    ppl = calculate_ppl(state.player_loadout)
    subtitle = t("hub.fixer_intro") + f"  |  Grade: {state.player_grade}-up  |  PPL: {ppl}"
    draw_title(console, title_r, title=t("hub.title"), subtitle=subtitle)

    # Main area: 4-panel layout
    _draw_4panel(console, main_r, t, state, ppl)

    # Side panel: Mission details (if selected)
    available = state.job_board.available_for(state.player_grade)
    if available and 0 <= state.hub_selected_index < len(available):
        selected = available[state.hub_selected_index]
        zdr = _preview_zdr(selected)
        status = calculate_status(ppl, zdr)
        draw_side(
            console,
            side_r,
            label="Mission Details",
            lines=[
                f"Title: {selected.title}",
                f"Objective: {selected.objective}",
                f"ZDR: {zdr}  Status: {status.value.upper()}",
                f"Reward: T{selected.reward_tier} + {selected.reward_credits} cr",
            ],
        )
    else:
        draw_side(console, side_r, label="Mission Details", lines=["No mission selected"])

    # Controls
    draw_controls(
        console,
        ctrl_r,
        lines=[
            "[1-9] Select Mission  [ESC] Back to Menu",
            "[Q] Quit",
        ],
    )

    # Footer
    draw_footer(
        console, foot_r, text=f"Hub  |  Step {state.demo_step}  T+{state.demo_elapsed_s:.1f}s"
    )


def _draw_4panel(
    console: tcod.console.Console,
    main: Region,
    t: Translator,
    state: AppState,
    ppl: int,
) -> None:
    """Draw the 4-panel Hub layout in the MAIN region (ADR-0017).

    Layout (35 rows in main):
      Row 0-7:   Panel 1 - Avatar (left half)
      Row 0-7:   Panel 2 - Materials (right half)
      Row 8:     divider
      Row 9-16:  Panel 3 - Recipes (left half)
      Row 9-16:  Panel 4 - Job Board (right half)
      Row 17+:   overflow (job list continuation)
    """
    half_w = main.w // 2

    # Panel 1: Avatar (top-left)
    _draw_avatar_panel(console, main, x_offset=0, y_offset=0, width=half_w, state=state, ppl=ppl)

    # Panel 2: Materials (top-right)
    _draw_materials_panel(console, main, x_offset=half_w, y_offset=0, width=half_w, state=state)

    # Mid divider
    console.print(
        x=main.x,
        y=main.y + 8,
        string="─" * main.w,
        fg=(64, 64, 64),
    )

    # Panel 3: Recipes (bottom-left)
    _draw_recipes_panel(console, main, x_offset=0, y_offset=9, width=half_w, state=state)

    # Panel 4: Job Board (bottom-right)
    _draw_job_board_panel(
        console, main, x_offset=half_w, y_offset=9, width=half_w, state=state, ppl=ppl
    )


def _draw_avatar_panel(
    console: tcod.console.Console,
    main: Region,
    x_offset: int,
    y_offset: int,
    width: int,
    state: AppState,
    ppl: int,
) -> None:
    """Draw the Avatar panel (ADR-0016)."""
    x = main.x + x_offset + 2
    y = main.y + y_offset
    console.print(x=x, y=y, string="[Avatar]", fg=(180, 180, 180))
    y += 1
    # Simplified avatar (Phase 5: placeholder)
    console.print(x=x, y=y, string="  ◉P◉", fg=(0, 255, 0))
    y += 1
    console.print(x=x, y=y, string="  /|\\", fg=(180, 180, 180))
    y += 1
    console.print(x=x, y=y, string=" ★W★", fg=(255, 0, 255))
    y += 1
    console.print(
        x=x, y=y, string="║DK" + str(state.player_loadout.deck_tier) + "║", fg=(200, 200, 200)
    )
    y += 1
    console.print(x=x, y=y + 1, string=f"PPL: {ppl}", fg=(0, 255, 0))
    console.print(x=x, y=y + 2, string=f"Grade: {state.player_grade}-up", fg=(200, 200, 200))


def _draw_materials_panel(
    console: tcod.console.Console,
    main: Region,
    x_offset: int,
    y_offset: int,
    width: int,
    state: AppState,
) -> None:
    """Draw the Materials panel (ADR-0015, ADR-0017)."""
    x = main.x + x_offset + 2
    y = main.y + y_offset
    console.print(x=x, y=y, string="[Materials]", fg=(180, 180, 180))
    y += 1
    # Placeholder materials (Phase 5: static)
    materials = [
        ("ICE Shard", 3, 5),
        ("Data Fragment", 2, 4),
        ("ROM Echo", 1, 3),
        ("Wetware Chip", 0, 2),
        ("Biosoft Agent", 0, 1),
    ]
    for name, have, need in materials:
        if y >= main.y + y_offset + 7:
            break
        gauge = _material_gauge(have, need, width=5)
        console.print(
            x=x,
            y=y,
            string=f"{name[:14]:<14} {gauge} {have}/{need}",
            fg=(160, 160, 160),
        )
        y += 1


def _material_gauge(have: int, need: int, width: int = 5) -> str:
    """Generate a graphical gauge: ▓▓▓░░."""
    filled = min(have, need)
    empty = need - filled
    # Clamp to width
    if filled + empty > width:
        ratio = width / (filled + empty)
        filled = int(filled * ratio)
        empty = width - filled
    return "▓" * filled + "░" * empty


def _draw_recipes_panel(
    console: tcod.console.Console,
    main: Region,
    x_offset: int,
    y_offset: int,
    width: int,
    state: AppState,
) -> None:
    """Draw the Recipes panel (ADR-0015, ADR-0017)."""
    x = main.x + x_offset + 2
    y = main.y + y_offset
    console.print(x=x, y=y, string="[Recipes]", fg=(180, 180, 180))
    y += 1
    # Placeholder recipes (Phase 5: static)
    recipes = [
        ("T1 Program", "·W·", True),
        ("T2 Program", ":H:", False),
        ("T3 Program", "|G|", False),
        ("T4 Program", "▓W▓", False),
        ("T5 Kraken", "★K★", False),
    ]
    for name, glyph, ready in recipes:
        if y >= main.y + y_offset + 7:
            break
        status_str = "READY ✓" if ready else "need materials"
        fg = (0, 255, 0) if ready else (128, 128, 128)
        console.print(
            x=x,
            y=y,
            string=f"{glyph}  {name:<12} {status_str}",
            fg=fg,
        )
        y += 1


def _draw_job_board_panel(
    console: tcod.console.Console,
    main: Region,
    x_offset: int,
    y_offset: int,
    width: int,
    state: AppState,
    ppl: int,
) -> None:
    """Draw the Job Board panel."""
    x = main.x + x_offset + 2
    y = main.y + y_offset
    console.print(x=x, y=y, string="[Job Board]", fg=(180, 180, 180))
    y += 1

    available = state.job_board.available_for(state.player_grade)
    if not available:
        console.print(x=x, y=y, string="No jobs available", fg=(128, 128, 128))
        return

    for i, mission in enumerate(available):
        if y >= main.y + main.h - 2:
            break
        zdr = _preview_zdr(mission)
        status = calculate_status(ppl, zdr)
        color = status_color(status)
        prefix = ">" if i == state.hub_selected_index else " "
        fg_title = (255, 255, 0) if i == state.hub_selected_index else (200, 200, 200)

        console.print(
            x=x,
            y=y,
            string=f"{prefix}[{i + 1}] {mission.title[: width - 6]}",
            fg=fg_title,
        )
        y += 1
        console.print(
            x=x + 2,
            y=y,
            string=f"ZDR: {zdr} ({status.value})",
            fg=color,
        )
        y += 1
        console.print(
            x=x + 2,
            y=y,
            string=f"Reward: {mission.reward_credits} cr",
            fg=(200, 200, 0),
        )
        y += 2  # spacing


def _preview_zdr(mission: Mission) -> int:
    """Return the ZDR of the mission's entry node (used as a quick preview)."""
    # We use the zone's base ZDR plus a sense_net faction modifier (typical Arc 1).
    from ..matrix.node import Faction

    faction = Faction.SENSE_NET  # Arc 1 default
    return calculate_zdr(mission.zone, faction=faction)


def handle_hub_input(event: tcod.event.Event, state: AppState) -> bool:
    """Handle input on the Hub screen. Returns False to quit."""
    if isinstance(event, KeyDown):
        if event.sym in (KeySym.ESCAPE,):
            state.screen = ScreenKind.MENU
            state.message = ""
            return True
        if event.sym is KeySym.Q:
            return False
        if event.sym in (KeySym.N1, KeySym.N2, KeySym.N3, KeySym.N4, KeySym.N5):
            available = state.job_board.available_for(state.player_grade)
            idx = int(event.sym.name[1:]) - 1
            if 0 <= idx < len(available):
                _start_mission(state, available[idx])
    return True


def _start_mission(state: AppState, mission: Mission) -> None:
    """Transition from Hub to Cyberspace Browser."""
    from ..cyberspace.registry import WorldRegistry

    state.current_mission = mission

    # Load world map if not loaded
    if not hasattr(state, "world_map") or state.world_map is None:
        from . import config

        registry = WorldRegistry.load(config.DATA_DIR / "cyberspace" / "worlds.json")
        state.world_map = registry.world_map

    # Find the server for this mission
    registry = WorldRegistry(state.world_map)
    location = registry.get_server_by_mission(mission.id)
    if location is not None:
        world_id, sector_id, server = location
        state.world_map.set_location(world_id, sector_id, server.id)
        # Find the server index

        world = state.world_map.get_current_world()
        if world is not None:
            sector = world.get_sector(sector_id)
            if sector is not None:
                for i, s in enumerate(sector.servers):
                    if s.id == server.id:
                        state.selected_server_index = i
                        break
    else:
        # Default to first sector's first server
        world = state.world_map.get_current_world()
        if world is not None and world.sectors:
            first_sector = list(world.sectors.values())[0]
            if first_sector.servers:
                state.world_map.set_location(
                    world.id,
                    first_sector.id,
                    first_sector.servers[0].id,
                )

    state.in_server_browser = True
    state.screen = ScreenKind.CYBERSPACE_BROWSER
    state.message = ""
