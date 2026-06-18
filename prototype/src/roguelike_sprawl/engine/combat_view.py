"""Combat screen: Real-Time with Menu Skills (RT-MS, ADR-0003).

Phase 5+: Integrates combat/ module with unified screen shell (layout).

Combat flow:
  1. Auto-attacks (both sides) every 2s
  2. Player can pause (M) to open skill menu
  3. Skill menu: select a skill (1-9), costs AP
  4. Time resumes after skill use
  5. Victory → Data Salvage (ADR-0014) → Hub
  6. Defeat → Death screen (ADR-0008)
"""

from __future__ import annotations

import tcod.console
import tcod.event
from tcod.event import KeyDown, KeySym

from ..audio import safe_play
from ..combat.registry import IceRegistry, ProgramRegistry, build_ice_enemy
from ..combat.state import (
    Combatant,
    CombatState,
    Skill,
    SkillEffect,
    use_skill,
)
from ..i18n import Translator
from ..matrix.graph import MatrixGraph
from ..matrix.node import Node
from ..matrix.ppl import calculate_ppl
from ..matrix.zdr import node_status, node_zdr
from .input_utils import is_confirm_key
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
from .status_panel import render_status_panel

_SKILL_SOUND_MAP: dict[SkillEffect, str] = {
    SkillEffect.ATTACK: "combat/skill_physical",
    SkillEffect.HEAVY_ATTACK: "combat/skill_physical",
    SkillEffect.PIERCE: "combat/skill_physical",
    SkillEffect.MULTI_HIT: "combat/skill_physical",
    SkillEffect.DOT: "combat/skill_magic",
    SkillEffect.POISON: "combat/skill_magic",
    SkillEffect.SHIELD: "combat/block",
    SkillEffect.HEAL: "combat/skill_heal",
    SkillEffect.REGEN: "combat/skill_heal",
    SkillEffect.BUFF: "combat/skill_buff",
    SkillEffect.DEBUFF: "combat/skill_debuff",
    SkillEffect.STUN: "combat/stun",
    SkillEffect.LIFESTEAL: "combat/skill_physical",
    SkillEffect.DETECT: "ui/notification",
}


def render_combat(
    console: tcod.console.Console,
    t: Translator,
    state: AppState,
    combat_state: CombatState,
) -> None:
    """Render the combat screen (RT-MS, ADR-0003)."""
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

    # Title
    ppl = calculate_ppl(state.player_loadout)
    # Assume current_node_id points to the ICE node
    ice_node: Node | None = None
    if state.matrix is not None and state.current_node_id is not None:
        ice_node = state.matrix.get(state.current_node_id)
    if ice_node is not None:
        zdr = node_zdr(ice_node)
        status = node_status(ice_node, ppl)
        ratio = ppl / zdr if zdr > 0 else float("inf")
        subtitle = f"PPL: {ppl}  vs  ZDR: {zdr}  |  Status: {status.value.upper()} ({ratio:.2f}x)"
    else:
        subtitle = "Combat"
    draw_title(console, title_r, title="COMBAT — RT-MS", subtitle=subtitle)

    # Main area: combatants + effects
    _draw_combatants(console, main_r, combat_state)
    _draw_combat_effects(console, main_r, combat_state)

    # Action log (in main area, below combatants)
    _draw_action_log(console, main_r, combat_state)

    # Side panel: skill menu (if paused) or stats
    if combat_state.finished:
        draw_side(
            console,
            side_r,
            label="Combat Over",
            lines=[
                f"Outcome: {combat_state.outcome.upper()}",
                f"Duration: {combat_state.tick_ms / 1000:.1f}s",
                f"Player HP: {combat_state.player.hp}/{combat_state.player.max_hp}",
            ],
        )
    else:
        _draw_skills_menu(console, side_r, combat_state, state)

    # Controls
    if combat_state.finished:
        draw_controls(
            console,
            ctrl_r,
            lines=[
                "[Space] Continue  [ESC] Back to Hub",
                "[Q] Quit",
            ],
        )
    else:
        draw_controls(
            console,
            ctrl_r,
            lines=[
                "↑↓ Select Skill  ENTER Use  [1-9] Quick Use",
                "[ESC] Disengage  [Q] Quit",
            ],
        )

    # Footer with status messages
    elapsed_s = combat_state.tick_ms / 1000.0
    draw_footer(
        console,
        foot_r,
        text=f"Combat  |  T+{elapsed_s:.1f}s  |  Step {state.demo_step}",
        status_messages=state.status_messages,
    )


def _draw_combatants(
    console: tcod.console.Console,
    main: Region,
    combat_state: CombatState,
) -> None:
    """Draw player and enemy portraits + HP bars."""
    player = combat_state.player
    enemy = combat_state.enemy

    # Player (left side)
    x = main.x + 4
    y = main.y + 2
    console.print(x=x, y=y, string=player.portrait, fg=player.color)
    y += 1
    console.print(x=x, y=y, string=f"{player.name}", fg=(200, 200, 200))
    y += 1
    console.print(x=x, y=y, string=f"HP: {player.hp}/{player.max_hp}", fg=(0, 255, 0))
    y += 1
    hp_bar = _hp_bar(player.hp, player.max_hp, width=20)
    console.print(x=x, y=y, string=hp_bar, fg=(0, 255, 0))
    y += 1
    console.print(x=x, y=y, string=f"AP: {player.ap}/{player.max_ap}", fg=(0, 200, 255))
    y += 1
    console.print(x=x, y=y, string=f"ATK: {player.auto_attack_damage}", fg=(180, 180, 180))
    if combat_state.shield > 0:
        y += 1
        console.print(
            x=x,
            y=y,
            string=f"Shield: {combat_state.shield}",
            fg=(0, 255, 255),
        )

    # Enemy (right side)
    x = main.x + main.w - 25
    y = main.y + 2
    console.print(x=x, y=y, string=enemy.portrait, fg=enemy.color)
    y += 1
    console.print(x=x, y=y, string=f"{enemy.name}", fg=(200, 200, 200))
    y += 1
    console.print(x=x, y=y, string=f"HP: {enemy.hp}/{enemy.max_hp}", fg=(255, 100, 100))
    y += 1
    hp_bar = _hp_bar(enemy.hp, enemy.max_hp, width=20)
    console.print(x=x, y=y, string=hp_bar, fg=(255, 100, 100))
    y += 1
    console.print(x=x, y=y, string=f"ATK: {enemy.auto_attack_damage}", fg=(180, 180, 180))


def _hp_bar(hp: int, max_hp: int, width: int = 20) -> str:
    """Generate an HP bar: [▓▓▓▓▓░░░░░]."""
    if max_hp <= 0:
        return "[" + "░" * width + "]"
    ratio = hp / max_hp
    filled = int(ratio * width)
    empty = width - filled
    return "[" + "▓" * filled + "░" * empty + "]"


def _draw_combat_effects(
    console: tcod.console.Console,
    main: Region,
    combat_state: CombatState,
) -> None:
    """Draw visual effects overlay (center of screen)."""
    # Only show recent effects (last 1 second)
    elapsed = combat_state.tick_ms - combat_state.last_event_tick
    if elapsed > 1500 or combat_state.last_event == "":
        return

    # Calculate effect intensity (fade over time)
    intensity = max(0, 1.0 - elapsed / 1500.0)

    # Get effect color and glyph
    color = combat_state.last_event_color
    glyph_map = {
        "player_attack": "─→",
        "enemy_attack": "←─",
        "skill_attack": "✦✦✦",
        "heavy_attack": "💥",  # Will render as multiple chars
        "pierce": "»»",
        "multi_hit": "≡≡≡",
        "dot": "♣",
        "shield": "◇",
        "heal": "+HP",
        "regen": "+♥",
        "buff": "↑ATK",
        "debuff": "↓ATK",
        "stun": "★",
        "lifesteal": "♥+",
    }
    text = glyph_map.get(combat_state.last_event, "*")

    # Apply intensity to color
    faded_color = (
        int(color[0] * intensity + 50 * (1 - intensity)),
        int(color[1] * intensity + 50 * (1 - intensity)),
        int(color[2] * intensity + 50 * (1 - intensity)),
    )

    # Draw effect text in center of screen
    center_y = main.y + 4
    center_x = main.x + (main.w - len(text)) // 2

    if 0 <= center_x and center_x + len(text) < main.x2:
        console.print(
            x=center_x,
            y=center_y,
            string=text,
            fg=faded_color,
        )


def _draw_action_log(
    console: tcod.console.Console,
    main: Region,
    combat_state: CombatState,
) -> None:
    """Draw the action log in the lower part of the main area."""
    x = main.x + 2
    y = main.y + 15
    console.print(x=x, y=y, string="═══ COMBAT LOG ═══", fg=(100, 100, 200))
    y += 1

    for i, line in enumerate(combat_state.log[-7:]):
        # Color code log entries
        line_lower = line.lower()
        if "critical" in line_lower or "devastating" in line_lower or "pierces" in line_lower:
            fg = (255, 255, 0)  # Yellow for crit
        elif "stun" in line_lower or "weakened" in line_lower:
            fg = (255, 150, 0)  # Orange for CC
        elif "burn" in line_lower or "poison" in line_lower:
            fg = (100, 255, 100)  # Green for DoT
        elif (
            "heal" in line_lower
            or "regen" in line_lower
            or "shield" in line_lower
            or "powered" in line_lower
        ):
            fg = (100, 200, 255)  # Cyan for buffs
        elif "smash" in line_lower or "strikes" in line_lower:
            fg = (255, 100, 100)  # Red for big attacks
        elif "hit" in line_lower or "damage" in line_lower:
            fg = (200, 200, 200)  # Gray for normal hits
        else:
            fg = (180, 180, 180)

        console.print(
            x=x,
            y=y + i,
            string=line[: main.w - 4],
            fg=fg,
        )


def _draw_skills_menu(
    console: tcod.console.Console,
    side_r: Region,
    combat_state: CombatState,
    state: AppState,
) -> None:
    """Draw skills menu with arrow key navigation support."""

    x = side_r.x + 2
    y = side_r.y + 1

    console.print(x=x, y=y, string="=== SKILLS ===", fg=(255, 255, 255))
    y += 2

    selected_index = state.combat_skill_index
    player = combat_state.player

    for i, skill in enumerate(player.skills):
        is_selected = i == selected_index
        cooldown_remaining = combat_state.skill_cooldowns.get(skill.id, 0)
        is_disabled = not _can_use_skill(combat_state, skill)

        # Visual indicators
        cursor = ">" if is_selected else " "
        glyph = skill.effect_glyph

        # Color and status based on state
        if cooldown_remaining > 0:
            fg = (80, 80, 80)  # Dark gray for cooldown
            status = f"[{cooldown_remaining / 1000:.1f}s]"
        elif is_disabled:
            fg = (80, 80, 80)  # Dark gray for disabled (not enough AP)
            status = f"[{skill.ap_cost} AP]"
        elif is_selected:
            fg = skill.effect_color  # Use skill's color
            status = f"[{skill.ap_cost} AP]"
        else:
            fg = (200, 200, 200)  # Light gray for normal
            status = f"[{skill.ap_cost} AP]"

        # Build line: cursor + key + glyph + name + status
        line = f"{cursor} [{i + 1}] {glyph} {skill.name} {status}"
        console.print(x=x, y=y + i, string=line, fg=fg)

        # Show effect type as small subtitle (if selected)
        if is_selected:
            effect_desc = _get_skill_effect_description(skill)
            console.print(
                x=x + 2,
                y=y + i + 1,
                string=effect_desc[: side_r.w - 4],
                fg=skill.effect_color,
            )

    # Show active status effects on player
    y = side_r.y + side_r.h - 12
    # Access statuses via getattr to avoid forward reference issues
    statuses = getattr(player, "statuses", []) or []
    if statuses:
        console.print(x=x, y=y, string="STATUS:", fg=(180, 180, 180))
        y += 1
        for status in statuses[:3]:
            secs_left = max(0, status.remaining_ms / 1000)
            line = f"  {status.effect_id}: {secs_left:.1f}s"
            color = (200, 200, 100) if "burn" in status.effect_id else (100, 255, 100)
            console.print(x=x, y=y, string=line, fg=color)
            y += 1

    # Instructions
    y = side_r.y + side_r.h - 6
    console.print(x=x, y=y, string="↑↓ Select  ENTER/SPACE Use", fg=(128, 128, 128))
    y += 1
    console.print(x=x, y=y, string="1-9 Quick use", fg=(128, 128, 128))
    y += 1
    console.print(x=x, y=y, string="ESC Disengage", fg=(128, 128, 128))


def _get_skill_effect_description(skill: Skill) -> str:
    """Get a short description of what a skill does."""
    from ..combat.state import SkillEffect

    descriptions = {
        SkillEffect.ATTACK: f"Deal {skill.damage} damage",
        SkillEffect.HEAVY_ATTACK: f"SMASH for {skill.damage} damage",
        SkillEffect.PIERCE: f"{skill.damage} dmg (ignores shield)",
        SkillEffect.MULTI_HIT: f"Hit {skill.hit_count}x for {skill.damage} each",
        SkillEffect.DOT: f"{skill.damage} dmg + burn ({skill.dot_damage}/s)",
        SkillEffect.POISON: f"{skill.damage} dmg + poison ({skill.dot_damage}/s)",
        SkillEffect.SHIELD: f"+{skill.shield} shield",
        SkillEffect.HEAL: f"+{skill.heal} HP",
        SkillEffect.REGEN: f"+{skill.heal} HP over time",
        SkillEffect.BUFF: f"+{skill.buff_amount} attack power",
        SkillEffect.DEBUFF: f"Reduce enemy atk by {skill.buff_amount}",
        SkillEffect.STUN: f"Stun enemy for {skill.stun_duration_ms // 1000}s",
        SkillEffect.DETECT: "Reveal enemy stats",
        SkillEffect.LIFESTEAL: f"{skill.damage} dmg + heal half",
    }
    return descriptions.get(skill.effect, "Special effect")


def _can_use_skill(combat_state: CombatState, skill: Skill) -> bool:
    """Check if a skill can be used (enough AP, no cooldown)."""
    player = combat_state.player
    cooldown_remaining = combat_state.skill_cooldowns.get(skill.id, 0)
    return player.ap >= skill.ap_cost and cooldown_remaining <= 0 and not combat_state.finished


def handle_combat_input(
    event: tcod.event.Event,
    state: AppState,
    combat_state: CombatState,
) -> bool:
    """Handle input on the Combat screen. Returns False to quit."""
    if not isinstance(event, KeyDown):
        return True
    if event.sym is KeySym.Q:
        return False
    if event.sym is KeySym.ESCAPE:
        # Disengage (flee)
        safe_play("ui/menu_cancel")
        if not combat_state.finished:
            combat_state.finished = True
            combat_state.outcome = "defeat"
            combat_state.push(">> You disengage. The ICE holds.")
        _end_combat(state, combat_state)
        return True
    if is_confirm_key(event.sym) and combat_state.finished:
        # Continue after combat ends (ENTER or SPACE)
        safe_play("ui/menu_confirm")
        _end_combat(state, combat_state)
        return True

    # Arrow key navigation for skills
    if event.sym is KeySym.UP:
        safe_play("ui/menu_select")
        old_idx = state.combat_skill_index
        state.combat_skill_index = max(0, state.combat_skill_index - 1)
        if old_idx != state.combat_skill_index:
            skill = combat_state.player.skills[state.combat_skill_index]
            state.status_messages.append(f">>> Selected: {skill.name}")
        return True

    if event.sym is KeySym.DOWN:
        max_idx = len(combat_state.player.skills) - 1
        old_idx = state.combat_skill_index
        state.combat_skill_index = min(max_idx, state.combat_skill_index + 1)
        if old_idx != state.combat_skill_index:
            skill = combat_state.player.skills[state.combat_skill_index]
            state.status_messages.append(f">>> Selected: {skill.name}")
        return True

    # ENTER or SPACE to use selected skill
    if is_confirm_key(event.sym):
        if not combat_state.finished:
            idx = state.combat_skill_index
            if 0 <= idx < len(combat_state.player.skills):
                skill = combat_state.player.skills[idx]
                if _can_use_skill(combat_state, skill):
                    state.status_messages.append(f">>> Used skill: {skill.name}")
                    # Play skill sound based on effect (with random pitch variation)
                    from ..audio import sound_manager as _sm

                    sound_name = _SKILL_SOUND_MAP.get(skill.effect, "combat/skill_physical")
                    _sm.get_sound_manager().play(sound_name)
                    use_skill(combat_state, skill)

                else:
                    cooldown = combat_state.skill_cooldowns.get(skill.id, 0)
                    if cooldown > 0:
                        state.status_messages.append(
                            f">>> {skill.name} on cooldown ({cooldown / 1000:.1f}s)"
                        )
                    elif combat_state.player.ap < skill.ap_cost:
                        state.status_messages.append(
                            f">>> Not enough AP ({combat_state.player.ap}/{skill.ap_cost})"
                        )
        return True

    # Legacy: Direct number key shortcuts (1-9)
    if event.sym in (
        KeySym.N1,
        KeySym.N2,
        KeySym.N3,
        KeySym.N4,
        KeySym.N5,
        KeySym.N6,
        KeySym.N7,
        KeySym.N8,
        KeySym.N9,
    ):
        if not combat_state.finished:
            idx = int(event.sym.name[1:]) - 1
            if 0 <= idx < len(combat_state.player.skills):
                skill = combat_state.player.skills[idx]
                use_skill(combat_state, skill)
    return True


def _end_combat(state: AppState, combat_state: CombatState) -> None:
    """Transition from Combat to next state with rewards."""
    if combat_state.outcome == "victory":
        # Play victory sound
        safe_play("combat/victory")
        # Award rewards: ICE Shard material + credits
        if not hasattr(state, "inventory") or state.inventory is None:
            state.inventory = {}
        state.inventory["ice_shard"] = state.inventory.get("ice_shard", 0) + 1
        state.status_messages.append(">>> VICTORY! Gained: 1x ICE Shard")
        state.status_messages.append(">>> Gained: 50 credits")

        # Progress mission objective (defeat)
        from .mission_completion import update_mission_progress

        update_mission_progress(state, "defeat", 1)

        # Advance RunState: if we're on the DEFEAT_ICE stage, this
        # victory satisfies the objective and we should move forward.
        from ..run import Stage, check_combat_victory, ensure_run_state

        run_state = ensure_run_state(state)
        if check_combat_victory(run_state):
            run_state.mark_advance()
            state.status_messages.append(f">>> Stage complete: {run_state.current_info().title}")

            # If we advanced to JACK_OUT, switch to the jack out screen
            if run_state.current_stage is Stage.JACK_OUT:
                from .jack_out_view import enter_jack_out

                enter_jack_out(state)
                # Mark current ICE node as defeated before returning
                _defeat_current_ice_node(state)
                # Trigger victory event (ICE destruction)
                _check_post_combat_event(state, "standard_ice_victory")
                return  # Don't return to matrix; we're entering JACK_OUT

        # Mark current ICE node as defeated - removed from dungeon
        if state.matrix is not None and state.current_node_id is not None:
            _defeat_current_ice_node(state)

        # Return to matrix (player can continue exploring)
        state.screen = ScreenKind.MATRIX
        state.message = "ICE defeated! Path is now clear."

        # Trigger victory event (ICE destruction)
        _check_post_combat_event(state, "standard_ice_victory")
    elif combat_state.outcome == "defeat":
        # Player died — Pillar 3: The Flatline
        from ..run import ensure_run_state
        from .death import trigger_death

        run_state = ensure_run_state(state)
        run_state.mark_failed()
        trigger_death(state, reason="ICE breach")
    else:
        # Disengage (player fled)
        state.screen = ScreenKind.MATRIX
        state.message = "Disengaged from combat."


def _check_post_combat_event(state: AppState, trigger_id: str) -> None:
    """Check if an event story should trigger after combat."""
    from .event_story import EventRegistry, EventState, EventTrigger, check_event_trigger

    if not hasattr(state, "_event_registry") or state._event_registry is None:
        state._event_registry = EventRegistry()

    event = check_event_trigger(
        state,
        registry=state._event_registry,
        trigger=EventTrigger.COMBAT_END,
        trigger_id=trigger_id,
    )
    if event is not None:
        state.active_event = EventState(event=event)
        state.screen = ScreenKind.EVENT


def _defeat_current_ice_node(state: AppState) -> None:
    """Mark the current ICE node as defeated and remove from graph.

    Helper for _end_combat() — used in both the JACK_OUT path and
    the standard matrix-return path.
    """
    if state.matrix is None or state.current_node_id is None:
        return
    defeated_id = state.current_node_id
    state.defeated_nodes.add(defeated_id)
    state.status_messages.append(f">>> ICE [{defeated_id}] destroyed")
    state.matrix = _remove_node_from_graph(state.matrix, defeated_id)
    if state.matrix is not None and len(state.matrix.nodes) > 0:
        neighbors = (
            state.matrix.neighbors(defeated_id)
            if defeated_id in [n.id for n in state.matrix.nodes]
            else []
        )
        if neighbors:
            state.current_node_id = neighbors[0].id
        else:
            state.current_node_id = state.matrix.entry_id


def _remove_node_from_graph(matrix: MatrixGraph | None, node_id: str) -> MatrixGraph | None:
    """Remove a node from the matrix graph (returns new graph or None)."""
    if matrix is None:
        return None

    # Filter out the node
    new_nodes = tuple(n for n in matrix.nodes if n.id != node_id)

    # Filter out edges involving the node
    new_edges = tuple(e for e in matrix.edges if e.src != node_id and e.dst != node_id)

    # Need to import here to avoid circular imports
    from ..matrix.graph import MatrixGraph

    if not new_nodes:
        return None

    # Update entry_id if the removed node was the entry
    new_entry_id = matrix.entry_id
    if matrix.entry_id == node_id and new_nodes:
        new_entry_id = new_nodes[0].id

    return MatrixGraph(
        nodes=new_nodes,
        edges=new_edges,
        entry_id=new_entry_id,
    )


# (No additional definitions below)


def start_combat(
    state: AppState,
    ice_node: Node,
    prog_registry: ProgramRegistry,
    ice_registry: IceRegistry,
) -> CombatState:
    """Initialize a CombatState from the current player loadout and ICE node."""
    # Build player combatant
    _ = calculate_ppl(state.player_loadout)  # Reserved for future use (scaling damage)
    player_skills: list[Skill] = []
    for prog in state.player_loadout.programs:
        skill = prog_registry.get(prog.id)
        if skill is not None:
            player_skills.append(skill)

    # Get base player stats
    base_hp = 100
    base_attack = 5
    base_max_ap = 6
    equip_attack_bonus = 0
    equip_defense = 0
    equip_hp_bonus = 0
    equip_shield_bonus = 0
    equip_ap_bonus = 0
    equip_program_power = 0
    equip_ice_resistance = 0
    equip_damage_bonus_pct = 0
    equip_crit_bonus_pct = 0
    equip_grants_skill_id = None

    # Apply equipment stats
    from ..equipment.equipment import EquipmentLoadout, EquipStats

    loadout = state.equipment_loadout
    stats: EquipStats | None = None
    if isinstance(loadout, EquipmentLoadout):
        raw_stats = loadout.total_stats
        stats = raw_stats if isinstance(raw_stats, EquipStats) else None
        if stats is not None:
            equip_attack_bonus = stats.attack_bonus
            equip_defense = stats.defense
            equip_hp_bonus = stats.hp_bonus
            equip_shield_bonus = stats.shield_bonus
            equip_ap_bonus = stats.ap_bonus
            equip_program_power = stats.program_power
            equip_ice_resistance = stats.ice_resistance
            equip_damage_bonus_pct = stats.damage_bonus_pct
            equip_crit_bonus_pct = stats.crit_bonus_pct
            equip_grants_skill_id = stats.grants_skill_id

        # Apply bonuses to base stats
        base_hp = 100 + equip_hp_bonus
        base_max_ap = 6 + equip_ap_bonus

        # Add equipment-granted skill if any
        if equip_grants_skill_id is not None:
            granted = prog_registry.get(equip_grants_skill_id)
            if granted is not None and granted not in player_skills:
                player_skills.append(granted)

    player = Combatant(
        id="player",
        name="You",
        portrait="◉P◉",
        color=(0, 255, 0),
        hp=base_hp,
        max_hp=base_hp,
        ap=3 + equip_ap_bonus,  # Start with bonus AP
        max_ap=base_max_ap,
        auto_attack_damage=base_attack + equip_attack_bonus,
        skills=tuple(player_skills),
        team="player",
        # Apply equipment stats
        equip_attack_bonus=equip_attack_bonus,
        equip_defense=equip_defense,
        equip_hp_bonus=equip_hp_bonus,
        equip_shield_bonus=equip_shield_bonus,
        equip_ap_bonus=equip_ap_bonus,
        equip_program_power=equip_program_power,
        equip_ice_resistance=equip_ice_resistance,
        equip_damage_bonus_pct=equip_damage_bonus_pct,
        equip_crit_bonus_pct=equip_crit_bonus_pct,
        equip_grants_skill_id=equip_grants_skill_id,
    )

    # Build enemy combatant
    # ice_node.kind should be ICE, but we'll use a default if not
    ice_kind = "standard"  # Placeholder: extract from ice_node
    enemy = build_ice_enemy(ice_kind, ice_registry)
    return CombatState(player=player, enemy=enemy)
