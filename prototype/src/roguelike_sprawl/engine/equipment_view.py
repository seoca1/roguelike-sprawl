"""Equipment visualizer: shows player's character with equipped gear.

Renders an ASCII character with equipment overlay.
"""

from __future__ import annotations

import tcod.console

from ..equipment.equipment import (
    EquipmentLoadout,
    EquipSlot,
)
from .layout import Region, clear_region


def render_equipment_visualizer(
    console: tcod.console.Console,
    region: Region,
    loadout: EquipmentLoadout,
) -> None:
    """Render the player character with equipped gear.

    Shows:
    - ASCII character with equipment at each body slot
    - Total stats summary
    - Equipment list
    """
    clear_region(console, region)
    _draw_border(console, region)

    x = region.x + 2
    y = region.y + 1
    max_w = region.w - 4

    # Title
    console.print(x=x, y=y, string="═══ RIG ═══", fg=(100, 200, 255))
    y += 1

    # Draw character with equipment
    _draw_character_with_gear(console, x, y, loadout)
    y += 11  # Character takes ~10 rows

    # Stats summary
    y += 1
    _draw_total_stats(console, x, y, loadout, max_w)
    y += 8

    # Equipment list
    if y < region.y2 - 1:
        _draw_equipment_list(console, x, y, loadout, region, max_w)


def _draw_border(console: tcod.console.Console, region: Region) -> None:
    """Draw border around the visualizer."""
    fg = (60, 60, 80)
    console.print(x=region.x, y=region.y, string="+", fg=fg)
    console.print(x=region.x2, y=region.y, string="+", fg=fg)
    console.print(x=region.x, y=region.y2, string="+", fg=fg)
    console.print(x=region.x2, y=region.y2, string="+", fg=fg)
    for xi in range(region.x + 1, region.x2):
        console.print(x=xi, y=region.y, string="-", fg=fg)
        console.print(x=xi, y=region.y2, string="-", fg=fg)
    for yi in range(region.y + 1, region.y2):
        console.print(x=region.x, y=yi, string="|", fg=fg)
        console.print(x=region.x2, y=yi, string="|", fg=fg)


def _draw_character_with_gear(
    console: tcod.console.Console,
    x: int,
    y: int,
    loadout: EquipmentLoadout,
) -> None:
    """Draw a character silhouette with equipment at body slots.

    Layout:
            [H]      <- headware
             |
           [E][E]    <- eyeware
         [B]     [B] <- bodysuit
          \\   /
           [|]     <- hands (gloves)
           / \
          [B] [B]  <- boots
           |
        (core)    <- deck (back-mounted)
    """
    # Get equipment
    head = loadout.get(EquipSlot.HEADWARE)
    eyes = loadout.get(EquipSlot.EYEWARE)
    body = loadout.get(EquipSlot.BODYSUIT)
    gloves = loadout.get(EquipSlot.GLOVES)
    boots = loadout.get(EquipSlot.BOOTS)
    deck = loadout.get(EquipSlot.DECK)
    implant = loadout.get(EquipSlot.IMPLANT)
    trodes = loadout.get(EquipSlot.TRODES)

    # Row 0: Title
    # Row 1: Empty
    # Row 2: Headware
    head_glyph = head.ascii_glyph if head else " o "
    head_fg = head.ascii_color if head else (150, 150, 150)
    console.print(x=x + 5, y=y + 2, string=head_glyph, fg=head_fg)
    if head:
        console.print(x=x + 9, y=y + 2, string=f"  ← {head.tier.value}", fg=(120, 120, 120))

    # Row 3: Eyeware
    if eyes:
        eye_str = eyes.ascii_glyph
        eye_fg = eyes.ascii_color
        console.print(x=x + 4, y=y + 3, string=eye_str, fg=eye_fg)
        console.print(x=x + 4, y=y + 3, string="  ", fg=eye_fg)
    else:
        console.print(x=x + 5, y=y + 3, string=" o ", fg=(150, 150, 150))

    # Row 4: Torso (Bodysuit + Deck)
    body_glyph = body.ascii_glyph if body else "[|]"
    body_fg = body.ascii_color if body else (150, 150, 150)
    console.print(x=x + 4, y=y + 4, string="─", fg=body_fg)
    console.print(x=x + 5, y=y + 4, string=body_glyph, fg=body_fg)
    console.print(x=x + 9, y=y + 4, string="─", fg=body_fg)

    # Row 5: Belt/loincloth area
    belt_str = "═══════════"
    console.print(x=x + 3, y=y + 5, string=belt_str, fg=body_fg)

    # Row 6: Arms (Gloves)
    arm_left = "/"
    arm_right = "\\"
    console.print(x=x + 1, y=y + 6, string=arm_left, fg=(150, 150, 150))
    console.print(x=x + 12, y=y + 6, string=arm_right, fg=(150, 150, 150))

    # Row 7: Gloves
    if gloves:
        glove_glyph = gloves.ascii_glyph
        glove_fg = gloves.ascii_color
        console.print(x=x, y=y + 7, string=glove_glyph, fg=glove_fg)
        console.print(x=x + 12, y=y + 7, string=glove_glyph, fg=glove_fg)
    else:
        console.print(x=x, y=y + 7, string=" |", fg=(100, 100, 100))
        console.print(x=x + 12, y=y + 7, string="| ", fg=(100, 100, 100))

    # Row 8: Hips / Legs start
    leg_left = "/"
    leg_right = "\\"
    console.print(x=x + 5, y=y + 8, string=leg_left, fg=(150, 150, 150))
    console.print(x=x + 8, y=y + 8, string=leg_right, fg=(150, 150, 150))

    # Row 9: Legs
    console.print(x=x + 4, y=y + 9, string="|", fg=(150, 150, 150))
    console.print(x=x + 9, y=y + 9, string="|", fg=(150, 150, 150))

    # Row 10: Boots
    if boots:
        boot_glyph = boots.ascii_glyph
        boot_fg = boots.ascii_color
        console.print(x=x + 3, y=y + 10, string=boot_glyph, fg=boot_fg)
        console.print(x=x + 8, y=y + 10, string=boot_glyph, fg=boot_fg)
    else:
        console.print(x=x + 3, y=y + 10, string="[ ]", fg=(100, 100, 100))
        console.print(x=x + 8, y=y + 10, string="[ ]", fg=(100, 100, 100))

    # Right side indicators (deck, implant, trodes)
    if deck:
        console.print(x=x + 17, y=y + 3, string="[DECK]", fg=deck.ascii_color)
        console.print(x=x + 17, y=y + 4, string=deck.tier.value, fg=(150, 150, 150))
    if implant:
        console.print(x=x + 17, y=y + 6, string="[IMPL]", fg=implant.ascii_color)
    if trodes:
        console.print(x=x + 17, y=y + 8, string="[TROD]", fg=trodes.ascii_color)


def _draw_total_stats(
    console: tcod.console.Console,
    x: int,
    y: int,
    loadout: EquipmentLoadout,
    max_w: int,
) -> None:
    """Draw total stats from all equipped items."""
    stats = loadout.total_stats()

    console.print(x=x, y=y, string="─── STATS ───", fg=(100, 200, 255))
    y += 1

    if stats.attack_bonus > 0:
        console.print(x=x, y=y, string=f"ATK +{stats.attack_bonus}", fg=(255, 100, 100))
        y += 1
    if stats.crit_bonus_pct > 0:
        console.print(x=x, y=y, string=f"CRIT +{stats.crit_bonus_pct}%", fg=(255, 255, 0))
        y += 1
    if stats.damage_bonus_pct > 0:
        console.print(x=x, y=y, string=f"DMG +{stats.damage_bonus_pct}%", fg=(255, 150, 100))
        y += 1
    if stats.defense > 0:
        console.print(x=x, y=y, string=f"DEF +{stats.defense}", fg=(100, 200, 255))
        y += 1
    if stats.hp_bonus > 0:
        console.print(x=x, y=y, string=f"HP +{stats.hp_bonus}", fg=(255, 100, 100))
        y += 1
    if stats.shield_bonus > 0:
        console.print(x=x, y=y, string=f"SHIELD +{stats.shield_bonus}", fg=(100, 200, 255))
        y += 1
    if stats.ap_bonus > 0:
        console.print(x=x, y=y, string=f"AP +{stats.ap_bonus}", fg=(0, 255, 255))
        y += 1
    if stats.ap_regen_bonus_pct > 0:
        console.print(x=x, y=y, string=f"AP REGEN +{stats.ap_regen_bonus_pct}%", fg=(0, 255, 255))
        y += 1
    if stats.program_power > 0:
        console.print(x=x, y=y, string=f"PROG PWR +{stats.program_power}", fg=(200, 100, 255))
        y += 1
    if stats.ice_resistance > 0:
        console.print(x=x, y=y, string=f"ICE RES +{stats.ice_resistance}%", fg=(100, 255, 100))
        y += 1

    if not any(
        [
            stats.attack_bonus,
            stats.crit_bonus_pct,
            stats.damage_bonus_pct,
            stats.defense,
            stats.hp_bonus,
            stats.shield_bonus,
            stats.ap_bonus,
            stats.ap_regen_bonus_pct,
            stats.program_power,
            stats.ice_resistance,
        ]
    ):
        console.print(x=x, y=y, string="(no equipment)", fg=(100, 100, 100))


def _draw_equipment_list(
    console: tcod.console.Console,
    x: int,
    y: int,
    loadout: EquipmentLoadout,
    region: Region,
    max_w: int,
) -> None:
    """Draw the list of equipped items."""
    console.print(x=x, y=y, string="─── EQUIPPED ───", fg=(100, 200, 255))
    y += 1

    for slot, equipment in loadout.equipment.items():
        if y >= region.y2 - 1:
            break
        # Slot label
        slot_label = _slot_short_label(slot)
        # Equipment info
        line = f"  {slot_label}: {equipment.name}"
        # Color by tier
        tier_color = _tier_color(equipment.tier)
        console.print(x=x, y=y, string=line[:max_w], fg=tier_color)
        y += 1


def _slot_short_label(slot: EquipSlot) -> str:
    """Short label for a slot."""
    labels = {
        EquipSlot.DECK: "DECK",
        EquipSlot.HEADWARE: "HEAD",
        EquipSlot.EYEWARE: "EYES",
        EquipSlot.BODYSUIT: "BODY",
        EquipSlot.GLOVES: "HAND",
        EquipSlot.BOOTS: "FEET",
        EquipSlot.IMPLANT: "IMPL",
        EquipSlot.TRODES: "TROD",
    }
    return labels.get(slot, slot.value.upper())


def _tier_color(tier: object) -> tuple[int, int, int]:
    """Color by tier."""
    colors = {
        "T0": (150, 150, 150),
        "T1": (100, 200, 100),
        "T2": (100, 150, 255),
        "T3": (200, 100, 255),
        "T4": (255, 150, 0),
        "T5": (255, 50, 200),
    }
    return colors.get(str(getattr(tier, "value", tier)), (200, 200, 200))


