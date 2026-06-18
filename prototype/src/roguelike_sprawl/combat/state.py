"""Combat state model (ADR-0003, RT-MS).

Pure-data combat primitives: ``Combatant``, ``Skill``, ``CombatState``.
A deterministic ``step_combat`` advances the simulation by one tick and
returns the events that occurred (damage, skill use, etc.).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal

TICK_MS = 100  # 10 FPS — sufficient for the simulator
AUTO_ATTACK_INTERVAL_MS = 2000  # 1 attack / 2s (ADR-0003)
AP_REGEN_INTERVAL_MS = 2000  # 1 AP / 2s

# Damage variance: ±20% randomization
DAMAGE_VARIANCE_MIN = 0.8
DAMAGE_VARIANCE_MAX = 1.2

# Critical hit: 15% chance, 2x damage
CRIT_CHANCE = 0.15
CRIT_MULTIPLIER = 2.0


class SkillEffect(StrEnum):
    """Types of skill effects in combat."""

    ATTACK = "attack"  # Direct damage
    HEAVY_ATTACK = "heavy_attack"  # Big damage, slow
    PIERCE = "pierce"  # Damage that ignores shield
    MULTI_HIT = "multi_hit"  # Hit 2-3 times
    DOT = "dot"  # Damage over time (burn, virus)
    SHIELD = "shield"  # Absorb damage
    REGEN = "regen"  # Heal over time
    HEAL = "heal"  # Instant heal
    BUFF = "buff"  # Increase attack power
    DEBUFF = "debuff"  # Reduce enemy attack
    DETECT = "detect"  # Reveal info
    STUN = "stun"  # Stun enemy (skip their attack)
    COUNTER = "counter"  # Reflect damage back
    LIFESTEAL = "lifesteal"  # Heal from damage dealt
    POISON = "poison"  # DOT that scales


@dataclass(frozen=True, slots=True)
class Skill:
    """A menu skill (ADR-0003) with extended effects."""

    id: str
    name: str
    tier: int
    effect: SkillEffect
    ap_cost: int
    damage: int = 0  # Base damage
    shield: int = 0  # Shield amount
    heal: int = 0  # Heal amount
    dot_damage: int = 0  # Per-tick damage
    dot_duration_ms: int = 0  # How long DoT lasts
    buff_amount: int = 0  # +damage or +defense
    buff_duration_ms: int = 0  # Buff duration
    stun_duration_ms: int = 0  # Stun duration
    hit_count: int = 1  # For multi-hit
    cooldown_ms: int = 0
    crit_bonus: float = 0.0  # Extra crit chance
    # Visual effect for the skill
    effect_color: tuple[int, int, int] = (255, 255, 255)
    effect_glyph: str = "*"


@dataclass
class StatusEffect:
    """An active status effect on a combatant."""

    effect_id: str  # "burn", "shield", "weak", etc
    remaining_ms: int
    # Per-tick effects
    dot_damage: int = 0  # damage per tick
    heal_per_tick: int = 0  # heal per tick
    attack_bonus: int = 0  # +attack
    defense_bonus: int = 0  # +defense (reduces dmg)
    # Special flags
    is_stunned: bool = False
    is_shield: bool = False  # absorbs damage before HP


@dataclass
class Combatant:
    """A combat participant (player or ICE)."""

    id: str
    name: str
    portrait: str
    color: tuple[int, int, int]
    hp: int
    max_hp: int
    ap: int = 0
    max_ap: int = 6
    auto_attack_damage: int = 5
    skills: tuple[Skill, ...] = ()
    team: Literal["player", "enemy"] = "enemy"
    # Active status effects
    statuses: list[StatusEffect] = field(default_factory=list)
    # Base stats (modified by buffs)
    base_attack: int = 0  # Set from auto_attack_damage
    base_defense: int = 0  # Flat damage reduction
    # Equipment bonuses (from equipped gear)
    equip_attack_bonus: int = 0
    equip_defense: int = 0
    equip_hp_bonus: int = 0
    equip_shield_bonus: int = 0
    equip_ap_bonus: int = 0
    equip_program_power: int = 0
    equip_ice_resistance: int = 0
    equip_damage_bonus_pct: int = 0
    equip_crit_bonus_pct: int = 0
    equip_grants_skill_id: str | None = None

    def is_alive(self) -> bool:
        return self.hp > 0

    def is_stunned(self) -> bool:
        return any(s.is_stunned for s in self.statuses)

    def get_attack_bonus(self) -> int:
        # Buffs + equipment
        buffs = sum(s.attack_bonus for s in self.statuses)
        return buffs + self.equip_attack_bonus

    def get_defense_bonus(self) -> int:
        # Buffs + equipment
        buffs = sum(s.defense_bonus for s in self.statuses)
        return buffs + self.equip_defense

    def get_total_attack(self) -> int:
        return self.auto_attack_damage + self.get_attack_bonus()

    def get_ice_resistance_pct(self) -> int:
        return self.equip_ice_resistance

    def get_crit_bonus_pct(self) -> int:
        return self.equip_crit_bonus_pct

    def get_damage_bonus_pct(self) -> int:
        return self.equip_damage_bonus_pct

    def get_program_power(self) -> int:
        return self.equip_program_power

    def get_total_shield_bonus(self) -> int:
        return self.equip_shield_bonus

    def get_total_ap_bonus(self) -> int:
        return self.equip_ap_bonus

    def get_total_hp_bonus(self) -> int:
        return self.equip_hp_bonus

    def get_total_shield(self) -> int:
        return sum(
            s.remaining_ms // TICK_MS * 0 + s.dot_damage + s.attack_bonus
            for s in self.statuses
            if s.is_shield
        )


@dataclass
class CombatState:
    """Live combat simulation state."""

    player: Combatant
    enemy: Combatant
    tick_ms: int = 0
    last_player_attack_ms: int = -AUTO_ATTACK_INTERVAL_MS
    last_enemy_attack_ms: int = -AUTO_ATTACK_INTERVAL_MS
    last_ap_regen_ms: int = 0
    shield: int = 0
    log: list[str] = field(default_factory=list)
    rng: random.Random = field(default_factory=random.Random)
    finished: bool = False
    outcome: Literal["ongoing", "victory", "defeat"] = "ongoing"
    last_skill_used: Skill | None = None
    # Skill cooldowns: skill_id -> remaining ms
    skill_cooldowns: dict[str, int] = field(default_factory=dict)
    # Last event for visual effects
    last_event: str = ""  # "player_attack", "skill_fire", etc
    last_event_color: tuple[int, int, int] = (255, 255, 255)
    last_event_tick: int = 0  # when it happened
    # Combo counter (consecutive attacks)
    player_combo: int = 0
    enemy_combo: int = 0

    def push(self, msg: str) -> None:
        """Append an event to the action log (capped at 6 lines)."""
        self.log.append(msg)
        if len(self.log) > 6:
            self.log.pop(0)


def _calculate_damage(
    state: CombatState,
    base_damage: int,
    attacker: Combatant,
    defender: Combatant,
    can_crit: bool = True,
) -> tuple[int, bool]:
    """Calculate final damage with variance, crit, and defense."""
    # Damage variance: ±20%
    variance = state.rng.uniform(DAMAGE_VARIANCE_MIN, DAMAGE_VARIANCE_MAX)
    dmg = int(base_damage * variance)

    # Add attacker's attack bonus
    dmg += attacker.get_attack_bonus()

    # Apply defender's defense
    dmg = max(0, dmg - defender.get_defense_bonus())

    # Crit check
    is_crit = False
    if can_crit:
        crit_chance = CRIT_CHANCE
        # Check skill crit bonus
        if state.last_skill_used and state.last_skill_used.crit_bonus > 0:
            crit_chance += state.last_skill_used.crit_bonus
        if state.rng.random() < crit_chance:
            dmg = int(dmg * CRIT_MULTIPLIER)
            is_crit = True

    return max(1, dmg), is_crit


def _apply_damage(
    state: CombatState,
    target: Combatant,
    amount: int,
    bypass_shield: bool = False,
) -> int:
    """Apply damage to target, handling shield. Returns damage actually applied."""
    if bypass_shield:
        target.hp = max(0, target.hp - amount)
        return amount

    absorbed = min(state.shield, amount)
    applied = amount - absorbed
    state.shield = max(0, state.shield - amount)
    target.hp = max(0, target.hp - applied)
    return applied


def _tick_status_effects(state: CombatState, target: Combatant) -> list[str]:
    """Process status effects for one tick. Returns list of log messages."""
    messages: list[str] = []
    for status in list(target.statuses):
        status.remaining_ms = max(0, status.remaining_ms - TICK_MS)
        # Apply per-tick effects
        if status.dot_damage > 0 and status.remaining_ms > 0:
            target.hp = max(0, target.hp - status.dot_damage)
            messages.append(f"{status.effect_id} burns {target.name} for {status.dot_damage}")
        if status.heal_per_tick > 0 and status.remaining_ms > 0:
            target.hp = min(target.max_hp, target.hp + status.heal_per_tick)
        if status.remaining_ms <= 0:
            target.statuses.remove(status)
    return messages


def step_combat(state: CombatState) -> None:
    """Advance ``state`` by one tick (TICK_MS).

    Mutates ``state`` in place: applies auto-attacks, regenerates AP,
    resolves end conditions. Events are appended to ``state.log``.
    """
    if state.finished:
        return
    state.tick_ms += TICK_MS

    # Tick down status effects (DoT, HoT, etc)
    player_msgs = _tick_status_effects(state, state.player)
    enemy_msgs = _tick_status_effects(state, state.enemy)
    for msg in player_msgs + enemy_msgs:
        state.push(msg)

    # Reduce skill cooldowns
    for skill_id in list(state.skill_cooldowns.keys()):
        state.skill_cooldowns[skill_id] = max(0, state.skill_cooldowns[skill_id] - TICK_MS)
        if state.skill_cooldowns[skill_id] <= 0:
            del state.skill_cooldowns[skill_id]

    # AP regen
    if state.tick_ms - state.last_ap_regen_ms >= AP_REGEN_INTERVAL_MS:
        if state.player.ap < state.player.max_ap:
            state.player.ap = min(state.player.max_ap, state.player.ap + 1)
            state.last_ap_regen_ms = state.tick_ms

    # Auto-attack: player (skip if stunned)
    if state.tick_ms - state.last_player_attack_ms >= AUTO_ATTACK_INTERVAL_MS:
        if not state.player.is_stunned():
            base_dmg = state.player.auto_attack_damage
            dmg, is_crit = _calculate_damage(state, base_dmg, state.player, state.enemy)
            applied = _apply_damage(state, state.enemy, dmg)
            state.last_player_attack_ms = state.tick_ms
            state.last_event = "player_attack"
            state.last_event_color = (200, 200, 200)
            state.last_event_tick = state.tick_ms

            crit_text = " CRITICAL HIT!" if is_crit else ""
            state.push(f"You strike {state.enemy.name} for {applied} damage.{crit_text}")
            state.player_combo += 1
        else:
            state.push("You are stunned and cannot attack!")
            state.last_player_attack_ms = state.tick_ms

    # Auto-attack: enemy (with shield absorption, skip if stunned)
    if state.tick_ms - state.last_enemy_attack_ms >= AUTO_ATTACK_INTERVAL_MS:
        if not state.enemy.is_stunned():
            base_dmg = state.enemy.auto_attack_damage
            dmg, is_crit = _calculate_damage(state, base_dmg, state.enemy, state.player)
            absorbed = min(state.shield, dmg)
            applied = dmg - absorbed
            state.shield = max(0, state.shield - dmg)
            state.player.hp = max(0, state.player.hp - applied)
            state.last_enemy_attack_ms = state.tick_ms
            state.last_event = "enemy_attack"
            state.last_event_color = (255, 100, 100)
            state.last_event_tick = state.tick_ms

            crit_text = " CRITICAL HIT!" if is_crit else ""
            if absorbed > 0:
                state.push(
                    f"{state.enemy.name} hits you for {applied} dmg (shield absorbed {absorbed}).{crit_text}"
                )
            else:
                state.push(f"{state.enemy.name} hits you for {applied} damage.{crit_text}")
            state.enemy_combo += 1
        else:
            state.push(f"{state.enemy.name} is stunned and cannot attack!")
            state.last_enemy_attack_ms = state.tick_ms

    # Reset combo if attack was dodged/stunned
    # End conditions
    if state.enemy.hp <= 0:
        state.finished = True
        state.outcome = "victory"
    elif state.player.hp <= 0:
        state.finished = True
        state.outcome = "defeat"


def use_skill(state: CombatState, skill: Skill) -> bool:
    """Apply a player skill. Returns True if the skill was used."""
    if state.finished:
        return False
    if skill.ap_cost > state.player.ap:
        return False
    # Check cooldown
    if state.skill_cooldowns.get(skill.id, 0) > 0:
        return False

    state.player.ap -= skill.ap_cost
    state.last_skill_used = skill

    # Set cooldown
    if skill.cooldown_ms > 0:
        state.skill_cooldowns[skill.id] = skill.cooldown_ms

    # Apply effect
    if skill.effect == SkillEffect.ATTACK:
        dmg, is_crit = _calculate_damage(state, skill.damage, state.player, state.enemy)
        applied = _apply_damage(state, state.enemy, dmg)
        crit_text = " [CRITICAL!]" if is_crit else ""
        state.last_event = "skill_attack"
        state.last_event_color = skill.effect_color
        state.last_event_tick = state.tick_ms
        state.push(f">> {skill.name}! {applied} damage to {state.enemy.name}.{crit_text}")

    elif skill.effect == SkillEffect.HEAVY_ATTACK:
        # Bigger damage, ignores variance
        dmg, is_crit = _calculate_damage(state, skill.damage, state.player, state.enemy)
        applied = _apply_damage(state, state.enemy, dmg)
        crit_text = " [DEVASTATING!]" if is_crit else ""
        state.last_event = "heavy_attack"
        state.last_event_color = skill.effect_color
        state.last_event_tick = state.tick_ms
        state.push(f">> {skill.name} SMASH! {applied} damage!{crit_text}")

    elif skill.effect == SkillEffect.PIERCE:
        # Damage bypasses shield
        dmg, is_crit = _calculate_damage(state, skill.damage, state.player, state.enemy)
        applied = _apply_damage(state, state.enemy, dmg, bypass_shield=True)
        crit_text = " [PIERCING!]" if is_crit else ""
        state.last_event = "pierce"
        state.last_event_color = skill.effect_color
        state.last_event_tick = state.tick_ms
        state.push(f">> {skill.name} pierces through! {applied} damage.{crit_text}")

    elif skill.effect == SkillEffect.MULTI_HIT:
        # Hit multiple times
        hits = skill.hit_count
        total_dmg = 0
        crit_hit = False
        for _ in range(hits):
            dmg, is_crit = _calculate_damage(
                state, skill.damage, state.player, state.enemy, can_crit=False
            )
            applied = _apply_damage(state, state.enemy, dmg)
            total_dmg += applied
            if is_crit:
                crit_hit = True
        crit_text = " [ALL CRITS!]" if crit_hit else ""
        state.last_event = "multi_hit"
        state.last_event_color = skill.effect_color
        state.last_event_tick = state.tick_ms
        state.push(f">> {skill.name} strikes {hits} times! Total: {total_dmg} damage.{crit_text}")

    elif skill.effect == SkillEffect.DOT or skill.effect == SkillEffect.POISON:
        # Direct damage + DoT
        dmg, is_crit = _calculate_damage(state, skill.damage, state.player, state.enemy)
        applied = _apply_damage(state, state.enemy, dmg)
        # Add DoT status
        state.enemy.statuses.append(
            StatusEffect(
                effect_id="burn",
                remaining_ms=skill.dot_duration_ms,
                dot_damage=skill.dot_damage,
            )
        )
        state.last_event = "dot"
        state.last_event_color = skill.effect_color
        state.last_event_tick = state.tick_ms
        state.push(
            f">> {skill.name}: {applied} damage + burn ({skill.dot_damage}/s for {skill.dot_duration_ms // 1000}s)!"
        )

    elif skill.effect == SkillEffect.SHIELD:
        # Add shield status
        state.shield += skill.shield
        state.last_event = "shield"
        state.last_event_color = skill.effect_color
        state.last_event_tick = state.tick_ms
        state.push(f">> {skill.name}: +{skill.shield} shield! (Total: {state.shield})")

    elif skill.effect == SkillEffect.HEAL:
        # Instant heal
        healed = min(skill.heal, state.player.max_hp - state.player.hp)
        state.player.hp = min(state.player.max_hp, state.player.hp + skill.heal)
        state.last_event = "heal"
        state.last_event_color = skill.effect_color
        state.last_event_tick = state.tick_ms
        state.push(f">> {skill.name}: +{healed} HP restored!")

    elif skill.effect == SkillEffect.REGEN:
        # Add HoT status
        state.player.statuses.append(
            StatusEffect(
                effect_id="regen",
                remaining_ms=skill.buff_duration_ms,
                heal_per_tick=max(1, skill.heal // 10),
            )
        )
        state.last_event = "regen"
        state.last_event_color = skill.effect_color
        state.last_event_tick = state.tick_ms
        state.push(f">> {skill.name}: regen active ({skill.heal // 10}/s)")

    elif skill.effect == SkillEffect.BUFF:
        # Self buff (attack +X)
        state.player.statuses.append(
            StatusEffect(
                effect_id="powered",
                remaining_ms=skill.buff_duration_ms,
                attack_bonus=skill.buff_amount,
            )
        )
        state.last_event = "buff"
        state.last_event_color = skill.effect_color
        state.last_event_tick = state.tick_ms
        state.push(f">> {skill.name}: +{skill.buff_amount} attack power!")

    elif skill.effect == SkillEffect.DEBUFF:
        # Enemy debuff (attack -X)
        state.enemy.statuses.append(
            StatusEffect(
                effect_id="weakened",
                remaining_ms=skill.buff_duration_ms,
                attack_bonus=-skill.buff_amount,
            )
        )
        state.last_event = "debuff"
        state.last_event_color = skill.effect_color
        state.last_event_tick = state.tick_ms
        state.push(f">> {skill.name}: {state.enemy.name} weakened (-{skill.buff_amount} attack)!")

    elif skill.effect == SkillEffect.STUN:
        # Stun enemy
        state.enemy.statuses.append(
            StatusEffect(
                effect_id="stun",
                remaining_ms=skill.stun_duration_ms,
                is_stunned=True,
            )
        )
        state.last_event = "stun"
        state.last_event_color = skill.effect_color
        state.last_event_tick = state.tick_ms
        state.push(
            f">> {skill.name}: {state.enemy.name} stunned for {skill.stun_duration_ms // 1000}s!"
        )

    elif skill.effect == SkillEffect.DETECT:
        # Reveal info
        state.push(
            f">> {skill.name}: {state.enemy.name} HP {state.enemy.hp}/{state.enemy.max_hp} | AP {state.enemy.ap}/{state.enemy.max_ap}"
        )

    elif skill.effect == SkillEffect.LIFESTEAL:
        # Damage + heal
        dmg, is_crit = _calculate_damage(state, skill.damage, state.player, state.enemy)
        applied = _apply_damage(state, state.enemy, dmg)
        healed = applied // 2
        state.player.hp = min(state.player.max_hp, state.player.hp + healed)
        state.last_event = "lifesteal"
        state.last_event_color = skill.effect_color
        state.last_event_tick = state.tick_ms
        state.push(f">> {skill.name}: {applied} damage, drained {healed} HP!")

    else:
        state.push(f">> {skill.name}: used.")

    # Re-check end
    if state.enemy.hp <= 0:
        state.finished = True
        state.outcome = "victory"

    return True
