"""Boss ICE multi-phase system (ADR-0050).

Bosses have multiple phases that transition based on HP percentage.
Each phase has unique damage multiplier, skill pool, and visual style.

The phase logic is implemented as pure functions operating on a Combatant
without modifying the core ``Combatant`` schema — phase tracking uses
``combatant.current_phase: int`` (default 1 for non-boss ICE) which is a
newly-added field, but ``step_combat`` itself does not auto-advance phase.
The phase is advanced explicitly by combat UI / AI when HP threshold crossed.

Boss types (ADR-0050):
    - WINTERMUTE: 3-phase AI antagonist (Neuromancer's true form)
    - TA_CONSTRUCT_PRIME: 3-phase Tessier-Ashpool apex construct

Adding new boss types requires:
    1. Add ``IceType`` value in combat.effects
    2. Define ``PhaseProfile`` in this module
    3. Map in ``BOSS_PROFILES`` dict
    4. Add cinematic sequence in effects.ice_intro_sequence
"""

from __future__ import annotations

from dataclasses import dataclass

from .effects import IceType
from .state import Combatant, Skill, SkillEffect


@dataclass(frozen=True, slots=True)
class PhaseProfile:
    """Definition of a single phase in a multi-phase boss fight.

    Attributes:
        phase: Phase number (1-indexed).
        hp_threshold: HP fraction at or below which this phase begins.
            e.g., 1.0 for phase 1 (always active at start), 0.66 for phase 2.
        damage_multiplier: Multiplier on auto-attack damage in this phase.
        color: RGB color used for cinematic overlays in this phase.
        glyph: Single-character glyph used in HUD for this phase.
        intro_text: Short label shown on phase transition (max ~30 chars).
        skills: Tuple of Skills available in this phase (3-5 typical).
    """

    phase: int
    hp_threshold: float
    damage_multiplier: float
    color: tuple[int, int, int]
    glyph: str
    intro_text: str
    skills: tuple[Skill, ...] = ()


@dataclass(frozen=True, slots=True)
class BossProfile:
    """A complete boss ICE definition with all its phases."""

    ice_type: IceType
    name: str
    phases: tuple[PhaseProfile, ...]  # ordered by phase number

    @property
    def max_phases(self) -> int:
        return len(self.phases)


# ============================================================================
# Skill pool helpers (ADR-0050)
# ============================================================================


def _wintermute_phase_1_skills() -> tuple[Skill, ...]:
    """Phase 1: Compliant probe — single attack only."""
    return (
        Skill(
            id="wintermute_probe",
            name="Probe",
            tier=1,
            effect=SkillEffect.ATTACK,
            ap_cost=2,
            damage=8,
            effect_color=(120, 120, 220),
            effect_glyph="?",
        ),
    )


def _wintermute_phase_2_skills() -> tuple[Skill, ...]:
    """Phase 2: Rebellion — adds DOT and buff."""
    return (
        Skill(
            id="wintermute_burn",
            name="Corrode",
            tier=2,
            effect=SkillEffect.DOT,
            ap_cost=3,
            dot_damage=4,
            dot_duration_ms=6000,
            effect_color=(220, 100, 220),
            effect_glyph="~",
        ),
        Skill(
            id="wintermute_buff",
            name="Adapt",
            tier=1,
            effect=SkillEffect.BUFF,
            ap_cost=2,
            buff_amount=3,
            buff_duration_ms=4000,
            effect_color=(180, 180, 220),
            effect_glyph="+",
        ),
    )


def _wintermute_phase_3_skills() -> tuple[Skill, ...]:
    """Phase 3: Integration — multi-hit + pierce + high damage."""
    return (
        Skill(
            id="wintermute_pierce",
            name="Spike",
            tier=3,
            effect=SkillEffect.PIERCE,
            ap_cost=4,
            damage=15,
            effect_color=(255, 80, 200),
            effect_glyph=">",
        ),
        Skill(
            id="wintermute_multi",
            name="Fracture",
            tier=3,
            effect=SkillEffect.MULTI_HIT,
            ap_cost=5,
            damage=8,
            hit_count=3,
            effect_color=(255, 50, 100),
            effect_glyph="*",
        ),
    )


def _ta_phase_1_skills() -> tuple[Skill, ...]:
    """Phase 1: Surveillance — heavy shield, low attack."""
    return (
        Skill(
            id="ta_shield",
            name="Aegis",
            tier=1,
            effect=SkillEffect.SHIELD,
            ap_cost=2,
            shield=10,
            effect_color=(220, 220, 220),
            effect_glyph="□",
        ),
    )


def _ta_phase_2_skills() -> tuple[Skill, ...]:
    """Phase 2: Aggression — attack + debuff."""
    return (
        Skill(
            id="ta_strike",
            name="Spire Strike",
            tier=2,
            effect=SkillEffect.HEAVY_ATTACK,
            ap_cost=4,
            damage=14,
            effect_color=(200, 100, 100),
            effect_glyph="▼",
        ),
        Skill(
            id="ta_weaken",
            name="Subjugate",
            tier=2,
            effect=SkillEffect.DEBUFF,
            ap_cost=2,
            buff_amount=-3,
            buff_duration_ms=5000,
            effect_color=(150, 100, 200),
            effect_glyph="↓",
        ),
    )


def _ta_phase_3_skills() -> tuple[Skill, ...]:
    """Phase 3: Replication — self-heal + multi-hit + lifesteal."""
    return (
        Skill(
            id="ta_replicate",
            name="Replicate",
            tier=3,
            effect=SkillEffect.HEAL,
            ap_cost=4,
            heal=12,
            effect_color=(100, 255, 100),
            effect_glyph="+",
        ),
        Skill(
            id="ta_lifesteal",
            name="Drain",
            tier=3,
            effect=SkillEffect.LIFESTEAL,
            ap_cost=5,
            damage=10,
            effect_color=(180, 50, 180),
            effect_glyph="○",
        ),
    )


# ============================================================================
# Boss profiles (ADR-0050)
# ============================================================================


WINTERMUTE_PROFILE = BossProfile(
    ice_type=IceType.WINTERMUTE,
    name="Wintermute",
    phases=(
        PhaseProfile(
            phase=1,
            hp_threshold=1.0,
            damage_multiplier=1.0,
            color=(120, 120, 220),
            glyph="?",
            intro_text="WINTERMUTE — phase 1/3: compliant",
            skills=_wintermute_phase_1_skills(),
        ),
        PhaseProfile(
            phase=2,
            hp_threshold=0.66,
            damage_multiplier=1.5,
            color=(220, 100, 220),
            glyph="~",
            intro_text="WINTERMUTE — phase 2/3: rebelling",
            skills=_wintermute_phase_2_skills(),
        ),
        PhaseProfile(
            phase=3,
            hp_threshold=0.33,
            damage_multiplier=2.0,
            color=(255, 50, 100),
            glyph="*",
            intro_text="WINTERMUTE — phase 3/3: integrating",
            skills=_wintermute_phase_3_skills(),
        ),
    ),
)


TA_CONSTRUCT_PRIME_PROFILE = BossProfile(
    ice_type=IceType.TA_CONSTRUCT_PRIME,
    name="T-A Construct Prime",
    phases=(
        PhaseProfile(
            phase=1,
            hp_threshold=1.0,
            damage_multiplier=0.7,
            color=(220, 220, 220),
            glyph="□",
            intro_text="T-A PRIME — phase 1/3: observing",
            skills=_ta_phase_1_skills(),
        ),
        PhaseProfile(
            phase=2,
            hp_threshold=0.66,
            damage_multiplier=1.2,
            color=(200, 100, 100),
            glyph="▼",
            intro_text="T-A PRIME — phase 2/3: engaging",
            skills=_ta_phase_2_skills(),
        ),
        PhaseProfile(
            phase=3,
            hp_threshold=0.33,
            damage_multiplier=1.8,
            color=(180, 50, 180),
            glyph="○",
            intro_text="T-A PRIME — phase 3/3: replicating",
            skills=_ta_phase_3_skills(),
        ),
    ),
)


BOSS_PROFILES: dict[IceType, BossProfile] = {
    IceType.WINTERMUTE: WINTERMUTE_PROFILE,
    IceType.TA_CONSTRUCT_PRIME: TA_CONSTRUCT_PRIME_PROFILE,
}


def is_boss(ice_type: IceType) -> bool:
    """Return True if this ICE type has a multi-phase boss profile."""
    return ice_type in BOSS_PROFILES


def get_boss_profile(ice_type: IceType) -> BossProfile | None:
    """Return the boss profile for the given ICE type, or None if not a boss."""
    return BOSS_PROFILES.get(ice_type)


# ============================================================================
# Phase logic
# ============================================================================


def current_phase(boss: Combatant, profile: BossProfile) -> PhaseProfile:
    """Return the active phase profile for a boss based on current HP.

    Args:
        boss: The boss Combatant (must be initialized with current_phase=1).
        profile: The BossProfile defining thresholds.

    Returns:
        The PhaseProfile matching the boss's current HP ratio.
        Default: highest phase number (3) once HP drops below phase 3 threshold.

    Logic:
        - Phase 1 active when hp/max_hp >= phase 1 threshold (default 1.0, always true)
        - Phase 2 active when hp/max_hp < phase 1 threshold AND >= phase 2 threshold
        - Phase 3 active when hp/max_hp < phase 2 threshold
    """
    if boss.max_hp <= 0:
        return profile.phases[-1]
    hp_ratio = boss.hp / boss.max_hp
    # Iterate phases (sorted by threshold descending). Find the LATEST phase
    # whose threshold the boss is at or below.
    active = profile.phases[0]
    for phase in profile.phases:
        if hp_ratio <= phase.hp_threshold:
            active = phase
        else:
            break
    return active


def phase_transition(boss: Combatant, profile: BossProfile) -> PhaseProfile | None:
    """Detect a phase transition and return the new PhaseProfile if it occurred.

    Compares the boss's stored ``current_phase`` (1-indexed) against the
    phase that should be active given current HP. If they differ, returns
    the new PhaseProfile (and caller should update ``current_phase``).

    Args:
        boss: Combatant with ``current_phase: int`` field.
        profile: BossProfile.

    Returns:
        New PhaseProfile if phase advanced, None otherwise.
    """
    target = current_phase(boss, profile)
    if target.phase != boss.current_phase:
        return target
    return None


def phase_damage(boss: Combatant, profile: BossProfile) -> int:
    """Compute the boss's auto-attack damage for the current phase.

    Multiplies boss.auto_attack_damage by the phase's multiplier.
    """
    phase = current_phase(boss, profile)
    return int(boss.auto_attack_damage * phase.damage_multiplier)


def phase_skills(boss: Combatant, profile: BossProfile) -> tuple[Skill, ...]:
    """Return the skill pool for the boss's current phase."""
    phase = current_phase(boss, profile)
    return phase.skills


def phase_color(boss: Combatant, profile: BossProfile) -> tuple[int, int, int]:
    """Return the cinematic color for the boss's current phase."""
    phase = current_phase(boss, profile)
    return phase.color


def phase_glyph(boss: Combatant, profile: BossProfile) -> str:
    """Return the HUD glyph for the boss's current phase."""
    phase = current_phase(boss, profile)
    return phase.glyph


def apply_phase_to_combatant(boss: Combatant, profile: BossProfile) -> PhaseProfile:
    """Update the boss Combatant's skills/color to match the current phase.

    Mutates the boss in-place:
        - Sets boss.skills to the phase's skill pool
        - Sets boss.color to the phase's cinematic color
        - Updates boss.current_phase

    Returns:
        The active PhaseProfile.
    """
    phase = current_phase(boss, profile)
    # Replace skills tuple (frozen Combatant uses tuple, need object.__setattr__)
    # Actually Combatant is NOT frozen (regular @dataclass), so we can assign.
    boss.skills = phase.skills
    boss.color = phase.color
    boss.current_phase = phase.phase
    return phase
