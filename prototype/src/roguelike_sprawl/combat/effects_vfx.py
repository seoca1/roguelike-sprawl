"""Combat visual effects — animation and sequence logic (ADR-0112 module split).

Extracted from combat/effects.py to reduce the module below the
1000+ LOC threshold per ADR-0110. Provides the 5-Layer VFX system
+ Boss themes per ADR-0050:

  Layer 1: Hit feedback (HitFlash, FloatingNumber, particles, shake)
  Layer 2: Skill animations (15 unique effects, 5-15 frames each)
  Layer 3: ICE-type specific (5 ICE types, unique intro/death)
  Layer 4: Status effect icons (persistent)
  Layer 5: Cinematic intro/finish (slow-mo, glitch, combo counter)

Data classes (IceType, StatusIcon, Animation, AnimationFrame,
Particle, ParticleSystem, ScreenShake, FloatingNumber, HitFlash,
ScreenFlash, CinematicSequence, ComboCounter) remain in
combat/effects.py for backward compatibility.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field

from .effects import (
    Animation,
    AnimationFrame,
    CinematicSequence,
    ComboCounter,
    FloatingNumber,
    HitFlash,
    IceType,
    Particle,
    ParticleSystem,
    ScreenFlash,
    ScreenShake,
    StatusIcon,
)
from .palette import (
    BUFF_COLOR,
    CRIT_COLOR,
    DAMAGE_COLOR,
    DEBUFF_COLOR,
    DEFAULT_COLOR,
    GLITCH_COLOR,
    HEAL_COLOR,
    ICE_BREAK_COLOR,
    SHIELD_COLOR,
    STUN_COLOR,
)


def attack_animation(damage: int = 0) -> Animation:
    """ATTACK: a forward strike with target flash."""
    return Animation(
        frames=(
            AnimationFrame("[\u003d\u003e", DAMAGE_COLOR, 60),
            AnimationFrame("[==\u003e", DAMAGE_COLOR, 60),
            AnimationFrame("[===\u003e", CRIT_COLOR, 80),
            AnimationFrame("[===\u003e", (255, 255, 255), 60),  # flash
            AnimationFrame("[===\u003e", DEFAULT_COLOR, 80),
        )
    )


def heavy_attack_animation() -> Animation:
    """HEAVY_ATTACK: charge, slam, screen shake trigger."""
    return Animation(
        frames=(
            AnimationFrame("[\u003c\u003d", BUFF_COLOR, 200),  # charge
            AnimationFrame("[\u003c\u003d\u003d", BUFF_COLOR, 150),
            AnimationFrame("[\u003c\u003d\u003d\u003d", (255, 200, 50), 200),  # windup peak
            AnimationFrame("[\u003c\u003c\u003c\u003c", (255, 100, 0), 80),  # slam
            AnimationFrame("[\u002a\u003c\u003c\u003c\u002a", ICE_BREAK_COLOR, 120),  # impact
            AnimationFrame("·[\u003c\u003c\u003c\u003c]·", (150, 150, 200), 150),  # shockwave
        )
    )


def pierce_animation() -> Animation:
    """PIERCE: arrow passes through target."""
    return Animation(
        frames=(
            AnimationFrame("-----\u003e", (200, 200, 100), 60),
            AnimationFrame("----==\u003e", (255, 200, 100), 60),
            AnimationFrame("----==\u003e", (255, 255, 255), 50),  # flash
            AnimationFrame("----==\u003e", (200, 200, 100), 60),
            AnimationFrame("-----\u003e", (150, 150, 100), 80),
        )
    )


def multi_hit_animation() -> Animation:
    """MULTI_HIT: 3 quick strikes."""
    return Animation(
        frames=(
            AnimationFrame("[\u003e", DAMAGE_COLOR, 50),
            AnimationFrame("[\u003e", (255, 255, 255), 30),
            AnimationFrame("[\u003e\u003e", DAMAGE_COLOR, 50),
            AnimationFrame("[\u003e\u003e", (255, 255, 255), 30),
            AnimationFrame("[\u003e\u003e\u003e", DAMAGE_COLOR, 50),
            AnimationFrame("[\u003e\u003e\u003e", (255, 200, 100), 80),
        )
    )


def dot_animation() -> Animation:
    """DOT/POISON: toxic particles around target."""
    return Animation(
        frames=(
            AnimationFrame("(\u2022\u002a\u2022)", (180, 100, 200), 100),
            AnimationFrame("(\u2022\u2022\u2022)", (200, 80, 220), 100),
            AnimationFrame("·\u2022\u2022\u2022·", (180, 100, 200), 100),
            AnimationFrame("(\u2022\u2022\u2022)", (160, 80, 200), 100),
            AnimationFrame("(\u2022\u002a\u2022)", (140, 60, 180), 150),
        )
    )


def shield_animation() -> Animation:
    """SHIELD: hexagonal shield pattern around self."""
    return Animation(
        frames=(
            AnimationFrame("·❖·", SHIELD_COLOR, 100),
            AnimationFrame("❖❖❖", (180, 230, 255), 100),
            AnimationFrame("❖●❖", (255, 255, 255), 80),
            AnimationFrame("❖❖❖", SHIELD_COLOR, 100),
            AnimationFrame("·❖·", (100, 180, 230), 150),
        )
    )


def heal_animation() -> Animation:
    """HEAL: rising plus signs."""
    return Animation(
        frames=(
            AnimationFrame("·+·", HEAL_COLOR, 100),
            AnimationFrame("·✚·", (120, 255, 150), 100),
            AnimationFrame("·❀·", (200, 255, 220), 100),
            AnimationFrame("+✚❀", (150, 255, 180), 100),
            AnimationFrame("✚❀✚", (100, 255, 150), 150),
        )
    )


def regen_animation() -> Animation:
    """REGEN: gentle pulse of plus signs."""
    return Animation(
        frames=(
            AnimationFrame("·+·", (120, 200, 150), 150),
            AnimationFrame("·+·", (150, 220, 170), 150),
            AnimationFrame("·+·", (120, 200, 150), 150),
        )
    )


def buff_animation() -> Animation:
    """BUFF: upward arrow burst."""
    return Animation(
        frames=(
            AnimationFrame("·↑·", BUFF_COLOR, 100),
            AnimationFrame("·⇈·", (255, 240, 150), 100),
            AnimationFrame("↑↑↑", (255, 255, 200), 100),
            AnimationFrame("·⇈·", BUFF_COLOR, 100),
            AnimationFrame("·↑·", (200, 180, 100), 150),
        )
    )


def debuff_animation() -> Animation:
    """DEBUFF: downward arrow."""
    return Animation(
        frames=(
            AnimationFrame("·↓·", DEBUFF_COLOR, 100),
            AnimationFrame("·⇊·", (230, 130, 255), 100),
            AnimationFrame("↓↓↓", (200, 100, 255), 100),
            AnimationFrame("·⇊·", DEBUFF_COLOR, 100),
            AnimationFrame("·↓·", (150, 80, 200), 150),
        )
    )


def stun_animation() -> Animation:
    """STUN: stars spinning around target."""
    return Animation(
        frames=(
            AnimationFrame("✦\u00b7✦", STUN_COLOR, 80),
            AnimationFrame("·✦\u00b7", (255, 255, 150), 80),
            AnimationFrame("✦\u00b7✦", (255, 230, 100), 80),
            AnimationFrame("·✦\u00b7", (255, 200, 50), 80),
            AnimationFrame("✦\u00b7✦", STUN_COLOR, 100),
        )
    )


def counter_animation() -> Animation:
    """COUNTER: shield bash returning damage."""
    return Animation(
        frames=(
            AnimationFrame("❖\u003c", SHIELD_COLOR, 80),
            AnimationFrame("❖\u003c\u003c", (200, 230, 255), 80),
            AnimationFrame("❖✦\u003c", (255, 255, 255), 60),
            AnimationFrame("\u003c❖✦", DAMAGE_COLOR, 80),
            AnimationFrame("·❖·", (150, 200, 230), 120),
        )
    )


def lifesteal_animation() -> Animation:
    """LIFESTEAL: red line from target to self."""
    return Animation(
        frames=(
            AnimationFrame("~~\u003e", DAMAGE_COLOR, 80),
            AnimationFrame("~~=\u003e", (200, 100, 100), 80),
            AnimationFrame("~~==\u003e", (180, 80, 80), 80),
            AnimationFrame("·✦·", HEAL_COLOR, 100),
            AnimationFrame("·+·", (150, 255, 180), 150),
        )
    )


def detect_animation() -> Animation:
    """DETECT: scanning reticle."""
    return Animation(
        frames=(
            AnimationFrame("[·]", (100, 200, 255), 100),
            AnimationFrame("[\u003c·\u003e]", (150, 220, 255), 100),
            AnimationFrame("[\u003c·\u003e]", (200, 240, 255), 100),
            AnimationFrame("[\u003c!\u003e]", (255, 255, 100), 100),
            AnimationFrame("[·]", (100, 200, 255), 150),
        )
    )


# Effect → animation factory
SKILL_EFFECT_ANIMATIONS: dict[str, Callable[[], Animation]] = {
    "attack": attack_animation,
    "heavy_attack": heavy_attack_animation,
    "pierce": pierce_animation,
    "multi_hit": multi_hit_animation,
    "dot": dot_animation,
    "poison": dot_animation,
    "shield": shield_animation,
    "heal": heal_animation,
    "regen": regen_animation,
    "buff": buff_animation,
    "debuff": debuff_animation,
    "stun": stun_animation,
    "counter": counter_animation,
    "lifesteal": lifesteal_animation,
    "detect": detect_animation,
}


def get_animation_for_effect(effect: str) -> Animation:
    """Get the animation for a SkillEffect name."""
    factory = SKILL_EFFECT_ANIMATIONS.get(effect, attack_animation)
    return factory()


# ----------------------------------------------------------------------------
# ICE-type specific effects (Layer 3)
# ----------------------------------------------------------------------------


def ice_intro_sequence(ice_type: IceType, name: str) -> CinematicSequence:
    """A scripted intro sequence unique to each ICE type."""
    if ice_type == IceType.STANDARD:
        return CinematicSequence(
            name="standard_intro",
            phases=(
                (f"[ {name} ]", (180, 180, 200), 300),
                (f"[\u00b7 {name} \u00b7]", (200, 200, 220), 250),
                (f"\u00b7· {name} ·\u00b7", (220, 220, 240), 200),
                (f"\u00b7· {name} ·\u00b7", (240, 240, 255), 800),
            ),
        )
    if ice_type == IceType.WATCHDOG:
        return CinematicSequence(
            name="watchdog_intro",
            phases=(
                ("[ grrr... ]", (200, 150, 100), 250),
                (f"[ {name} ]", (220, 170, 100), 200),
                ("WOOF!", (255, 100, 100), 120),
                (f"·{name}·", (255, 150, 100), 200),
                (f"·{name}·", (255, 200, 100), 800),
            ),
        )
    if ice_type == IceType.GOLIATH:
        return CinematicSequence(
            name="goliath_intro",
            phases=(
                ("...", (100, 100, 120), 300),
                (f"[ {name} ]", (150, 150, 170), 200),
                (f"[ {name} ]", (200, 100, 100), 100),
                (f"\u00b7·[{name}]·\u00b7", (255, 80, 80), 100),
                (f"\u00b7·[{name}]·\u00b7", (255, 50, 50), 1000),
            ),
        )
    if ice_type == IceType.BLACK:
        return CinematicSequence(
            name="black_intro",
            phases=(
                ("\u00b7▓▓▓\u00b7", (200, 200, 200), 200),
                ("\u00b7█▓█▓█\u00b7", (180, 180, 180), 150),
                ("▓█▓▓█▓", (160, 160, 160), 150),
                (f"[{name}]", GLITCH_COLOR, 100),
                (f"[{name}]", (100, 100, 100), 100),
                (f"[{name}]", (200, 0, 200), 100),
                (f"[{name}]", (80, 80, 80), 1200),
            ),
        )
    # ADR-0050: Boss ICE multi-phase intros (BEFORE construct fall-through)
    if ice_type == IceType.WINTERMUTE:
        return CinematicSequence(
            name="wintermute_intro",
            phases=(
                ("...", (80, 80, 120), 300),
                ("·?·", (100, 100, 150), 200),
                (f"[ {name} ]", (120, 120, 220), 300),
                (f"[ {name} ]", (140, 140, 240), 200),
                (f"[ {name} ]", (160, 160, 255), 800),
                ("PHASE 1/3: COMPLIANT", (120, 120, 220), 600),
            ),
        )
    if ice_type == IceType.TA_CONSTRUCT_PRIME:
        return CinematicSequence(
            name="ta_construct_prime_intro",
            phases=(
                ("·[ ⚙ ]·", (150, 150, 180), 200),
                ("·[ ⚙⚙ ]·", (180, 180, 200), 200),
                (f"[ {name} ]", (200, 200, 220), 300),
                (f"[ {name} ]", (220, 220, 240), 300),
                (f"[ {name} ]", (240, 240, 255), 800),
                ("PHASE 1/3: OBSERVING", (220, 220, 220), 600),
            ),
        )
    # construct
    return CinematicSequence(
        name="construct_intro",
        phases=(
            ("·[ ⚙ ]·", (150, 150, 180), 200),
            ("·[ ⚙ ]·", (180, 180, 200), 150),
            ("[ ⚙⚙⚙ ]", (200, 200, 220), 200),
            (f"[ {name} ]", (220, 220, 240), 250),
            (f"[ {name} ]", (240, 240, 255), 1000),
        ),
    )


def boss_phase_transition_sequence(
    ice_type: IceType, phase: int, total_phases: int = 3
) -> CinematicSequence:
    """Cinematic for a boss transitioning to a new phase.

    Args:
        ice_type: The boss's IceType (WINTERMUTE or TA_CONSTRUCT_PRIME).
        phase: The new phase number (2 or 3).
        total_phases: Total phases (default 3).
    """
    if ice_type == IceType.WINTERMUTE:
        # Glitchy pink/purple
        if phase == 2:
            return CinematicSequence(
                name="wintermute_phase_2_transition",
                phases=(
                    ("▓▓▓", (200, 200, 200), 100),
                    ("▓█▓█▓", (220, 100, 220), 100),
                    ("[ ADAPTING ]", (220, 100, 220), 300),
                    (f"PHASE {phase}/{total_phases}: REBELLING", (220, 100, 220), 600),
                    (f"PHASE {phase}/{total_phases}: REBELLING", (255, 50, 200), 600),
                ),
            )
        # phase 3
        return CinematicSequence(
            name="wintermute_phase_3_transition",
            phases=(
                ("█▓█▓█", (200, 200, 200), 100),
                ("▓█▓▓█▓", (255, 50, 100), 100),
                ("[ INTEGRATING ]", (255, 50, 100), 300),
                (f"PHASE {phase}/{total_phases}: INTEGRATING", (255, 50, 100), 600),
                (f"PHASE {phase}/{total_phases}: INTEGRATING", (255, 0, 50), 800),
            ),
        )
    if ice_type == IceType.TA_CONSTRUCT_PRIME:
        if phase == 2:
            return CinematicSequence(
                name="ta_construct_prime_phase_2_transition",
                phases=(
                    ("⚙⚙⚙", (220, 220, 220), 200),
                    ("⚙REPLICATING⚙", (200, 100, 100), 300),
                    (f"PHASE {phase}/{total_phases}: ENGAGING", (200, 100, 100), 600),
                    (f"PHASE {phase}/{total_phases}: ENGAGING", (255, 50, 50), 600),
                ),
            )
        return CinematicSequence(
            name="ta_construct_prime_phase_3_transition",
            phases=(
                ("⚙⚙⚙", (220, 220, 220), 200),
                ("⚙OVERRIDING⚙", (180, 50, 180), 300),
                (f"PHASE {phase}/{total_phases}: REPLICATING", (180, 50, 180), 600),
                (f"PHASE {phase}/{total_phases}: REPLICATING", (220, 0, 220), 800),
            ),
        )
    # Unknown boss — generic
    return CinematicSequence(
        name=f"{ice_type.value}_phase_{phase}_transition",
        phases=(
            (f"PHASE {phase}/{total_phases}", (200, 200, 200), 600),
            (f"PHASE {phase}/{total_phases}", (240, 240, 240), 600),
        ),
    )
    # Generic boss fall-through


def ice_death_sequence(ice_type: IceType) -> CinematicSequence:
    """A scripted death sequence unique to each ICE type."""
    if ice_type == IceType.STANDARD:
        return CinematicSequence(
            name="standard_death",
            phases=(
                ("[X_X]", DAMAGE_COLOR, 100),
                ("[>_>]", (200, 100, 100), 100),
                ("[X_X]", (150, 150, 150), 100),
                ("\u00b7[\u00b7]\u00b7", (200, 200, 200), 150),
                ("\u00b7 · \u00b7", (180, 180, 180), 200),
            ),
        )
    if ice_type == IceType.WATCHDOG:
        return CinematicSequence(
            name="watchdog_death",
            phases=(
                ("woof...?", (220, 180, 100), 200),
                ("[X_O]", (200, 150, 100), 150),
                ("[X_X]", (180, 100, 100), 150),
                ("[X_X]", (150, 80, 80), 200),
                ("\u00b7 · \u00b7", (200, 200, 200), 300),
            ),
        )
    if ice_type == IceType.GOLIATH:
        return CinematicSequence(
            name="goliath_death",
            phases=(
                ("[X_X]", (255, 100, 100), 100),
                ("[X!X]", (255, 50, 50), 100),
                ("[#_#]", (200, 100, 100), 150),
                ("\u00b7[\u00b7]\u00b7", (200, 200, 200), 200),
                ("\u00b7 · \u00b7", (180, 180, 180), 300),
            ),
        )
    if ice_type == IceType.BLACK:
        return CinematicSequence(
            name="black_death",
            phases=(
                (f"[{GLITCH_COLOR}]", GLITCH_COLOR, 100),
                ("[ERR]", (255, 0, 0), 100),
                ("[___]", (100, 100, 100), 100),
                ("[XXX]", (80, 80, 80), 150),
                ("\u00b7 · \u00b7", (200, 200, 200), 300),
            ),
        )
    # construct
    if ice_type == IceType.WINTERMUTE:
        return CinematicSequence(
            name="wintermute_death",
            phases=(
                ("[▓▓▓]", (200, 100, 220), 100),
                ("[???]", (255, 50, 200), 100),
                ("[XXX]", (200, 50, 100), 150),
                ("·▓▓▓·", (100, 100, 100), 200),
                ("· · ·", (200, 200, 200), 300),
            ),
        )
    if ice_type == IceType.TA_CONSTRUCT_PRIME:
        return CinematicSequence(
            name="ta_construct_prime_death",
            phases=(
                ("[⚙⚙⚙]", (200, 100, 100), 100),
                ("[⚠⚠⚠]", (180, 50, 180), 100),
                ("[___]", (150, 150, 150), 150),
                ("·[ ]·", (180, 180, 180), 200),
                ("· · ·", (200, 200, 200), 300),
            ),
        )
    return CinematicSequence(
        name="construct_death",
        phases=(
            ("[⚙X⚙]", (255, 100, 100), 100),
            ("[⚠⚠⚠]", (255, 200, 100), 100),
            ("[___]", (200, 200, 200), 150),
            ("\u00b7[ ]\u00b7", (180, 180, 180), 200),
            ("\u00b7 · \u00b7", (200, 200, 200), 300),
        ),
    )


# ----------------------------------------------------------------------------
# Critical hit effect (Layer 5)
# ----------------------------------------------------------------------------


def critical_hit_animation() -> Animation:
    """A multi-frame critical hit sequence with glitch."""
    return Animation(
        frames=(
            AnimationFrame("!·!", (255, 100, 100), 60),
            AnimationFrame("!!", (255, 50, 50), 60),
            AnimationFrame("·!·", (255, 200, 100), 60),
            AnimationFrame("!", (255, 255, 0), 80),
            AnimationFrame("!", (200, 200, 0), 100),
        )
    )


# ----------------------------------------------------------------------------
# Combat effects container
# ----------------------------------------------------------------------------


@dataclass(slots=True)
class CombatEffects:
    """Container for all active combat visual effects.

    One instance lives in AppState. combat_view.py reads it to render
    overlays and steps it each frame.
    """

    animations: list[Animation] = field(default_factory=list)
    particles: ParticleSystem = field(default_factory=ParticleSystem)
    shake: ScreenShake = field(default_factory=ScreenShake)
    floating_numbers: list[FloatingNumber] = field(default_factory=list)
    hit_flash: HitFlash = field(default_factory=HitFlash)
    screen_flash: ScreenFlash = field(default_factory=ScreenFlash)
    cinematic: CinematicSequence | None = None
    combo: ComboCounter = field(default_factory=ComboCounter)
    slow_motion_ms: int = 0  # When > 0, time runs at half speed

    def step(self, dt_ms: int) -> None:
        """Step all effects forward by dt_ms."""
        if self.slow_motion_ms > 0:
            dt_ms = dt_ms // 2
            self.slow_motion_ms = max(0, self.slow_motion_ms - 16)
        for anim in self.animations:
            anim.step(dt_ms)
        self.animations = [a for a in self.animations if not a.is_finished]
        self.particles.step(dt_ms)
        for fn in self.floating_numbers:
            fn.step(dt_ms)
        self.floating_numbers = [f for f in self.floating_numbers if f.is_alive]
        self.shake.step(dt_ms)
        self.hit_flash.step(dt_ms)
        self.screen_flash.step(dt_ms)
        if self.cinematic is not None:
            self.cinematic.step(dt_ms)
            if self.cinematic.is_finished:
                self.cinematic = None

    def clear(self) -> None:
        """Reset all effects (e.g. on combat end)."""
        self.animations.clear()
        self.particles.clear()
        self.floating_numbers.clear()
        self.shake = ScreenShake()
        self.hit_flash = HitFlash()
        self.screen_flash = ScreenFlash()
        self.cinematic = None
        self.combo.reset()
        self.slow_motion_ms = 0

    def has_active_effects(self) -> bool:
        """True if any effect is currently rendering."""
        return bool(
            self.animations
            or self.particles.particles
            or self.floating_numbers
            or self.shake.intensity > 0
            or self.hit_flash.is_active
            or self.screen_flash.is_active
            or self.cinematic is not None
        )


# ----------------------------------------------------------------------------
# Effect spawners (high-level API for combat_view)
# ----------------------------------------------------------------------------


def spawn_hit_effects(
    effects: CombatEffects,
    target_x: float,
    target_y: float,
    damage: int,
    *,
    effect_type: str = "attack",
    is_crit: bool = False,
    hit_color: tuple[int, int, int] | None = None,
) -> None:
    """Spawn a complete hit effect package: animation, particles, number, flash, shake.

    This is the high-level entry point called from combat_view when a
    skill resolves. It triggers all Layer 1+2 visuals for one hit.
    """
    # Layer 2: skill animation
    effects.animations.append(get_animation_for_effect(effect_type))

    # Layer 1: particles
    if is_crit:
        effects.particles.spawn_burst(
            target_x,
            target_y,
            chars=("✦", "★", "*", "✧"),
            color=CRIT_COLOR,
            count=10,
            speed=50.0,
        )
    elif effect_type in ("heal", "regen"):
        effects.particles.spawn_upward(target_x, target_y, color=HEAL_COLOR)
    elif effect_type in ("dot", "poison"):
        effects.particles.spawn_burst(
            target_x,
            target_y,
            chars=("•", "○", "◌"),
            color=(180, 100, 220),
            count=6,
            speed=20.0,
        )
    else:
        effects.particles.spawn_burst(
            target_x,
            target_y,
            chars=("*", "+", "x", "·", "✦"),
            color=DAMAGE_COLOR,
            count=6,
            speed=30.0,
        )

    # Layer 1: floating number
    if damage > 0:
        color = hit_color or (CRIT_COLOR if is_crit else DAMAGE_COLOR)
        effects.floating_numbers.append(
            FloatingNumber(
                x=target_x,
                y=target_y - 1.0,
                value=damage,
                color=color,
                is_crit=is_crit,
            )
        )

    # Layer 1: hit flash
    flash_color = (255, 255, 255) if is_crit else (255, 220, 100)
    effects.hit_flash.trigger(color=flash_color, duration_ms=120)

    # Layer 1: screen shake (only for big hits)
    if is_crit or effect_type in ("heavy_attack", "multi_hit"):
        effects.shake.trigger(intensity=2.5, duration_ms=200)
    elif effect_type in ("attack", "pierce"):
        effects.shake.trigger(intensity=1.0, duration_ms=80)


def spawn_ice_intro(effects: CombatEffects, ice_type: IceType, name: str) -> None:
    """Spawn a cinematic intro for an ICE type."""
    effects.cinematic = ice_intro_sequence(ice_type, name)
    effects.slow_motion_ms = effects.cinematic.total_duration_ms


def spawn_ice_death(effects: CombatEffects, ice_type: IceType) -> None:
    """Spawn a cinematic death for an ICE type."""
    effects.cinematic = ice_death_sequence(ice_type)
    effects.slow_motion_ms = 0  # No slow-mo for death
    effects.shake.trigger(intensity=2.0, duration_ms=250)


def spawn_critical(effects: CombatEffects, x: float, y: float, damage: int) -> None:
    """Spawn a critical hit effect package."""
    effects.animations.append(critical_hit_animation())
    effects.particles.spawn_burst(x, y, chars=("✦", "★"), color=CRIT_COLOR, count=12, speed=60.0)
    effects.floating_numbers.append(
        FloatingNumber(x=x, y=y - 1.0, value=damage, color=CRIT_COLOR, is_crit=True)
    )
    effects.hit_flash.trigger(color=(255, 255, 200), duration_ms=150)
    effects.shake.trigger(intensity=3.5, duration_ms=250)
    effects.slow_motion_ms = 250  # 250ms of slow-mo


def spawn_status_icon(combatant: object, status: StatusIcon) -> None:
    """Attach a status icon to a combatant. (Placeholder for HUD integration.)"""
    # In a full implementation this would push to a list on the combatant
    # or set a flag. combat_view reads the list to display icons.
    if not hasattr(combatant, "status_icons"):
        combatant.status_icons = []  # type: ignore[attr-defined]
    if status not in combatant.status_icons:  # type: ignore[attr-defined]
        combatant.status_icons.append(status)  # type: ignore[attr-defined]


# ----------------------------------------------------------------------------
# Matrix / dungeon VFX (ADR-0060 Phase 1.5)
#
# These provide the cyberspace atmosphere that the simplified NetHack-style
# map no longer carries. The map renders pure gameplay UI; cyberspace is
# layered as effects.
# ----------------------------------------------------------------------------


def spawn_jackin_glitch(effects: CombatEffects) -> None:
    """Spawn a one-shot 'jack-in' glitch VFX (Phase 1.5)."""
    effects.particles.spawn_burst(
        x=0.0,
        y=0.0,
        chars=("\u2593", "\u2592", "\u2591", "+", "\u00b7", "/", "\\"),
        color=(120, 220, 220),
        count=18,
        speed=45.0,
        life_ms=500,
        spread=math.tau,
    )
    effects.particles.spawn_burst(
        x=0.0,
        y=0.0,
        chars=("\u2592", "*", "+"),
        color=(220, 100, 220),
        count=8,
        speed=30.0,
        life_ms=300,
        spread=math.tau,
    )
    effects.shake.trigger(intensity=80, duration_ms=180)
    effects.hit_flash.trigger(color=(120, 220, 220), duration_ms=120)
    effects.cinematic = CinematicSequence(
        name="jackin",
        phases=(
            (">> JACKING IN...", (120, 220, 220), 180),
            (">> SCANNING HOST...", (220, 180, 100), 180),
            (">> CYBERSPACE LOADED", (180, 220, 120), 220),
        ),
    )


def spawn_room_flash(
    effects: CombatEffects,
    color: tuple[int, int, int] = (180, 180, 100),
) -> None:
    """Spawn a short color flash on room transition (Phase 1.5)."""
    effects.hit_flash.trigger(color=color, duration_ms=80)
    effects.particles.spawn_burst(
        x=1.0,
        y=1.0,
        chars=("\u00b7", "+", "\u00b7"),
        color=color,
        count=4,
        speed=10.0,
        life_ms=160,
        spread=math.pi,
    )


def spawn_aoe_screen_flash(
    effects: CombatEffects,
    color: tuple[int, int, int] = (255, 80, 80),
    duration_ms: int = 280,
) -> None:
    """Spawn a full-screen flash for AoE damage events (ADR-0125 follow-up).

    Triggers ScreenFlash (full-viewport, distinct from tile-level HitFlash),
    paired with screen shake for impact.
    """
    effects.screen_flash.trigger(color=color, duration_ms=duration_ms)
    effects.shake.trigger(intensity=0.6, duration_ms=duration_ms)


def spawn_data_acquired(effects: CombatEffects, x: float = 0.0, y: float = 0.0) -> None:
    """Spawn a 'data fragment recovered' VFX on DATA room pickup (Phase 1.5)."""
    effects.particles.spawn_burst(
        x=x,
        y=y,
        chars=("$", "\u00b7", "+", "\u00b7"),
        color=(255, 215, 0),
        count=14,
        speed=40.0,
        life_ms=500,
        spread=math.tau,
    )
    effects.hit_flash.trigger(color=(255, 215, 0), duration_ms=120)
    effects.cinematic = CinematicSequence(
        name="data_acquired",
        phases=(
            (">> DATA FRAGMENT RECOVERED", (255, 215, 0), 280),
            ("+ CREDITS + REPUTATION", (220, 220, 180), 200),
        ),
    )


def spawn_jackout_whiteout(effects: CombatEffects) -> None:
    """Spawn a 'jack-out' whiteout VFX on EXIT room (Phase 1.5)."""
    effects.hit_flash.trigger(color=(255, 255, 255), duration_ms=260)
    effects.particles.spawn_burst(
        x=0.0,
        y=0.0,
        chars=("\u00b7", "+", "\u00b7"),
        color=(220, 220, 220),
        count=10,
        speed=20.0,
        life_ms=400,
        spread=math.tau,
    )
    effects.cinematic = CinematicSequence(
        name="jackout",
        phases=(
            (">> JACKING OUT...", (220, 220, 220), 220),
            (">> CONNECTION SEVERED", (180, 180, 220), 220),
            (">> MATRIX CLOSED", (140, 140, 180), 200),
        ),
    )


__all__ = [
    "Animation",
    "AnimationFrame",
    "CinematicSequence",
    "CombatEffects",
    "ComboCounter",
    "FloatingNumber",
    "HitFlash",
    "IceType",
    "Particle",
    "ParticleSystem",
    "ScreenShake",
    "StatusIcon",
    "attack_animation",
    "counter_animation",
    "critical_hit_animation",
    "debuff_animation",
    "detect_animation",
    "dot_animation",
    "get_animation_for_effect",
    "heal_animation",
    "heavy_attack_animation",
    "ice_death_sequence",
    "ice_intro_sequence",
    "lifesteal_animation",
    "multi_hit_animation",
    "pierce_animation",
    "regen_animation",
    "shield_animation",
    "spawn_critical",
    "spawn_data_acquired",
    "spawn_hit_effects",
    "spawn_ice_death",
    "spawn_ice_intro",
    "spawn_jackin_glitch",
    "spawn_jackout_whiteout",
    "spawn_room_flash",
    "spawn_status_icon",
    "stun_animation",
    "buff_animation",
]
