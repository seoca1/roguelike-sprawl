"""Death and restart system (Pillar 3: The Flatline).

When a player's HP hits 0 in combat (or other circumstances), they
"flatline" — a story moment, not just a game over. The death screen
shows the iconic X head (avatar flatline state) and offers:
- [ENTER] Jack out (return to hub, lose inventory, restart mission)
- [Q] Quit game

Death is not a hard reset — the player's grade, story progress, and
unlocked missions persist. Only the current run is lost.
"""

from __future__ import annotations

import tcod.console

from ..audio import sound_manager as _sm_module
from .settings_ui import get_volume
from .state import AppState, ScreenKind


def trigger_death(state: AppState, reason: str = "Combat") -> None:
    """Trigger player death (flatline).

    Args:
        state: App state.
        reason: Why the player died (shown in death screen).
    """
    state.is_dead = True
    state.death_reason = reason
    state.screen = ScreenKind.DEATH
    state.status_messages.append(f">>> FLATLINE: {reason}")
    state.status_messages.append(">>> Press ENTER to jack out")

    # Play defeat sound (if not already played)
    try:
        _sm_module.play("combat/defeat")
    except Exception:
        pass


def jack_out_to_hub(state: AppState) -> None:
    """Recover from death: return to hub, lose current run progress.

    Pillar 3 recovery: The player flatlines but doesn't lose everything.
    Inventory and credits from the current run are forfeited.
    Story progress and unlocked missions persist.
    """
    if not state.is_dead:
        return

    # Clear combat
    state.combat_state = None
    state.action_menu_open = False

    # Clear current matrix (start fresh)
    state.matrix = None
    state.current_node_id = None
    state.cyberspace_layouts = None
    state.server_subgraph = None
    state.in_server_browser = True
    state.selected_server_index = 0

    # Reset mission progress
    state.mission_progress = {}
    state.current_mission = None

    # Reset HP to full (respawn)
    state.player_hp = state.player_max_hp

    # Forfeit inventory (materials gathered this run)
    state.inventory = {}

    # Player is alive again
    state.is_dead = False
    state.death_reason = ""

    # Return to hub
    state.screen = ScreenKind.HUB
    state.status_messages.append(">>> Jacked out. Returning to hub...")
    state.status_messages.append(">>> Inventory lost. Grade preserved.")


def render_death_screen(
    console: tcod.console.Console,
    state: AppState,
) -> None:
    """Render the flatline (death) screen.

    Shows the X head (jockey avatar flatline state) and recovery options.
    """
    from ..avatar import build_avatar_state
    from ..avatar.renderer import render_avatar_lines
    from . import config as _engine_config

    SCREEN_WIDTH = _engine_config.SCREEN_WIDTH  # noqa: N806
    SCREEN_HEIGHT = _engine_config.SCREEN_HEIGHT  # noqa: N806

    console.clear(bg=(0, 0, 0))

    # Title
    title = "FLATLINE"
    console.print(
        x=(SCREEN_WIDTH - len(title)) // 2,
        y=4,
        string=title,
        fg=(140, 0, 0),
    )
    subtitle = "Static. Silence."
    console.print(
        x=(SCREEN_WIDTH - len(subtitle)) // 2,
        y=5,
        string=subtitle,
        fg=(80, 80, 80),
    )

    # Avatar (X head, flatline state)
    avatar_state = build_avatar_state(
        hp=0,
        max_hp=state.player_max_hp if state.player_max_hp > 0 else 100,
        ppl=state.player_ppl if state.player_ppl > 0 else 5,
        zdr=99,  # Always deadly
        deck_tier=3,
        wetware_tier=3,
        construct_id=None,  # Construct disappears at death
    )
    rendered = render_avatar_lines(avatar_state)
    avatar_x = (SCREEN_WIDTH - rendered.width) // 2
    avatar_y = 8
    # Frame
    console.print(
        x=avatar_x - 1,
        y=avatar_y - 1,
        string="=" * (rendered.width + 2),
        fg=(140, 0, 0),
    )
    for i, (text, color) in enumerate(rendered.lines):
        console.print(
            x=avatar_x,
            y=avatar_y + i,
            string=text,
            fg=color,
        )
    console.print(
        x=avatar_x - 1,
        y=avatar_y + len(rendered.lines),
        string="=" * (rendered.width + 2),
        fg=(140, 0, 0),
    )

    # Death reason
    reason_text = f"Cause: {state.death_reason}"
    console.print(
        x=(SCREEN_WIDTH - len(reason_text)) // 2,
        y=avatar_y + len(rendered.lines) + 3,
        string=reason_text,
        fg=(180, 80, 80),
    )

    # Options
    option1 = "[ENTER] Jack Out — Return to Hub"
    option2 = "[Q] Quit Game"
    console.print(
        x=(SCREEN_WIDTH - len(option1)) // 2,
        y=SCREEN_HEIGHT // 2 + 6,
        string=option1,
        fg=(200, 200, 200),
    )
    console.print(
        x=(SCREEN_WIDTH - len(option2)) // 2,
        y=SCREEN_HEIGHT // 2 + 8,
        string=option2,
        fg=(100, 100, 100),
    )

    # Volume indicator (bottom)
    vol_pct = int(get_volume() * 100)
    console.print(
        x=2,
        y=SCREEN_HEIGHT - 2,
        string=f"[M] mute  [+/-] vol: {vol_pct}%",
        fg=(80, 80, 80),
    )


def handle_death_input(
    event: tcod.event.Event,
    state: AppState,
) -> bool:
    """Handle input on the death screen. Returns False to quit."""
    import tcod.event

    if not isinstance(event, tcod.event.KeyDown):
        return True

    if event.sym is tcod.event.KeySym.Q:
        return False

    if event.sym in (tcod.event.KeySym.RETURN, tcod.event.KeySym.SPACE, tcod.event.KeySym.KP_ENTER):
        jack_out_to_hub(state)
        return True

    if event.sym is tcod.event.KeySym.M:
        muted = _sm_module.toggle_mute()
        label = "MUTED" if muted else "UNMUTED"
        state.status_messages.append(f">>> Audio {label}")
        return True

    # Volume controls
    if event.sym in (tcod.event.KeySym.EQUALS, tcod.event.KeySym.PLUS, tcod.event.KeySym.KP_PLUS):
        from .settings_ui import adjust_volume

        new_vol = adjust_volume(+0.1)
        state.status_messages.append(f">>> Volume: {int(new_vol * 100)}%")
        return True
    if event.sym in (tcod.event.KeySym.MINUS, tcod.event.KeySym.KP_MINUS):
        from .settings_ui import adjust_volume

        new_vol = adjust_volume(-0.1)
        state.status_messages.append(f">>> Volume: {int(new_vol * 100)}%")
        return True

    # Per-category sound toggles
    from ..audio.config import SoundCategory
    from .settings_ui import toggle_category

    category_by_key = {
        tcod.event.KeySym.T: SoundCategory.THEME,
        tcod.event.KeySym.E: SoundCategory.EVENTS,
        tcod.event.KeySym.K: SoundCategory.KEYS,
        tcod.event.KeySym.B: SoundCategory.COMBAT,
        tcod.event.KeySym.V: SoundCategory.MOVEMENT,
        tcod.event.KeySym.I: SoundCategory.ITEMS,
    }
    if event.sym in category_by_key:
        category = category_by_key[event.sym]
        new_state = toggle_category(category)
        label = "ON" if new_state else "OFF"
        state.status_messages.append(
            f">>> Sound category '{category.value}' toggled: {label}"
        )
        return True

    return True
