"""Combat visual effects system.

Provides ASCII animations, particles, screen shake, status icons,
and cinematic effects for combat. Pure ASCII rendering per ADR-0002.

Layer architecture:
  Layer 1: Hit feedback (flash, floating numbers, particles, shake)
  Layer 2: Skill animations (15 unique effects, 5-15 frames each)
  Layer 3: ICE-type specific (5 ICE types, unique intro/death)
  Layer 4: Status effect icons (persistent)
  Layer 5: Cinematic intro/finish (slow-mo, glitch, combo counter)
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# ASCII palette for combat effects. Colors use tcod conventions.
# All colors are now centralized in palette.py.
from .palette import (  # noqa: E402
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


class IceType(StrEnum):
    """ICE enemy types with unique visual effects."""

    STANDARD = "standard"
    WATCHDOG = "watchdog"
    GOLIATH = "goliath"
    BLACK = "black"
    CONSTRUCT = "construct"


class StatusIcon(StrEnum):
    """Status effect icons shown next to combatants."""

    POISON = "P"
    BURN = "B"
    STUN = "S"
    SHIELD = "❖"
    BUFF = "↑"
    DEBUFF = "↓"
    REGEN = "+"
    DOT = "•"


# ----------------------------------------------------------------------------
# Animation primitives
# ----------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AnimationFrame:
    """A single frame in an animation.

    Attributes:
        text: The ASCII art or symbol for this frame.
        color: RGB tuple for tcod rendering.
        duration_ms: How long this frame shows.
        offset: (dx, dy) position offset from the spawn point.
    """

    text: str
    color: tuple[int, int, int] = DEFAULT_COLOR
    duration_ms: int = 80
    offset: tuple[int, int] = (0, 0)


@dataclass(slots=True)
class Animation:
    """A multi-frame animation that plays once and completes.

    Use `step()` to advance; use `current_frame` to render; use
    `is_finished` to know when to remove.
    """

    frames: tuple[AnimationFrame, ...]
    elapsed_ms: int = 0
    _current_index: int = 0

    def step(self, dt_ms: int) -> None:
        """Advance animation by dt_ms milliseconds."""
        if self.is_finished:
            return
        self.elapsed_ms += dt_ms
        # Advance frames until we find one that covers elapsed_ms
        cumulative = 0
        for i, frame in enumerate(self.frames):
            cumulative += frame.duration_ms
            if self.elapsed_ms < cumulative:
                self._current_index = i
                return
        # Past the end
        self._current_index = len(self.frames) - 1

    @property
    def current_frame(self) -> AnimationFrame | None:
        """The frame to render this tick, or None if finished."""
        if self.is_finished:
            return None
        return self.frames[self._current_index]

    @property
    def is_finished(self) -> bool:
        """True when all frames have been displayed."""
        return self.elapsed_ms >= self.total_duration_ms

    @property
    def total_duration_ms(self) -> int:
        """Total animation duration."""
        return sum(f.duration_ms for f in self.frames)

    def progress(self) -> float:
        """0.0 to 1.0 progress through the animation."""
        total = self.total_duration_ms
        if total == 0:
            return 1.0
        return min(1.0, self.elapsed_ms / total)


# ----------------------------------------------------------------------------
# Particle system
# ----------------------------------------------------------------------------


@dataclass(slots=True)
class Particle:
    """A single particle in the particle system.

    Particles fly outward from a spawn point, fall/rise, and fade.
    Used for hit sparks, blood splatter, healing sparkles, etc.
    """

    x: float
    y: float
    vx: float  # velocity x (units per second)
    vy: float  # velocity y
    char: str
    color: tuple[int, int, int]
    life_ms: int = 0
    max_life_ms: int = 400
    gravity: float = 0.0  # y-acceleration per second

    def step(self, dt_ms: int) -> None:
        """Advance particle by dt_ms."""
        dt_s = dt_ms / 1000.0
        self.x += self.vx * dt_s
        self.y += self.vy * dt_s
        self.vy += self.gravity * dt_s
        self.life_ms += dt_ms

    @property
    def is_alive(self) -> bool:
        return self.life_ms < self.max_life_ms

    @property
    def alpha(self) -> float:
        """0.0 to 1.0 fade-out multiplier."""
        if self.max_life_ms == 0:
            return 0.0
        return max(0.0, 1.0 - self.life_ms / self.max_life_ms)


@dataclass(slots=True)
class ParticleSystem:
    """Container for all active particles."""

    particles: list[Particle] = field(default_factory=list)

    def spawn(self, particle: Particle) -> None:
        self.particles.append(particle)

    def spawn_burst(
        self,
        x: float,
        y: float,
        chars: tuple[str, ...] = ("*", "+", "x", "·"),
        color: tuple[int, int, int] = DAMAGE_COLOR,
        count: int = 6,
        speed: float = 30.0,
        life_ms: int = 400,
        spread: float = math.tau,
    ) -> None:
        """Spawn `count` particles in a burst pattern."""
        for _ in range(count):
            angle = random.uniform(0, spread)
            v = speed * random.uniform(0.6, 1.0)
            self.particles.append(
                Particle(
                    x=x,
                    y=y,
                    vx=math.cos(angle) * v,
                    vy=math.sin(angle) * v - v * 0.3,  # bias upward
                    char=random.choice(chars),
                    color=color,
                    max_life_ms=life_ms,
                    gravity=80.0,
                )
            )

    def spawn_upward(
        self,
        x: float,
        y: float,
        chars: tuple[str, ...] = ("+", "✚", "✿"),
        color: tuple[int, int, int] = HEAL_COLOR,
        count: int = 4,
        life_ms: int = 600,
    ) -> None:
        """Spawn particles rising upward (for healing/buffs)."""
        for _ in range(count):
            self.particles.append(
                Particle(
                    x=x + random.uniform(-0.5, 0.5),
                    y=y,
                    vx=random.uniform(-8.0, 8.0),
                    vy=-random.uniform(15.0, 30.0),
                    char=random.choice(chars),
                    color=color,
                    max_life_ms=life_ms,
                    gravity=-10.0,
                )
            )

    def step(self, dt_ms: int) -> None:
        for p in self.particles:
            p.step(dt_ms)
        self.particles = [p for p in self.particles if p.is_alive]

    def clear(self) -> None:
        self.particles.clear()


# ----------------------------------------------------------------------------
# Screen shake
# ----------------------------------------------------------------------------


@dataclass(slots=True)
class ScreenShake:
    """Camera shake state.

    On each step, returns (dx, dy) integer offset to apply to the
    whole render. Intensity decays over time.
    """

    intensity: float = 0.0
    duration_ms: int = 0
    elapsed_ms: int = 0

    def trigger(self, intensity: float, duration_ms: int) -> None:
        """Start a new shake; replaces any existing shake."""
        self.intensity = max(self.intensity, intensity)
        self.duration_ms = max(self.duration_ms, duration_ms)
        self.elapsed_ms = 0

    def step(self, dt_ms: int) -> None:
        if self.intensity <= 0:
            return
        self.elapsed_ms += dt_ms
        if self.elapsed_ms >= self.duration_ms:
            self.intensity = 0.0
            self.duration_ms = 0
            self.elapsed_ms = 0

    def offset(self) -> tuple[int, int]:
        """Current shake offset (dx, dy). Returns (0, 0) if no shake."""
        if self.intensity <= 0 or self.duration_ms <= 0:
            return (0, 0)
        # Decay factor: 1.0 at start, 0.0 at end
        decay = 1.0 - (self.elapsed_ms / self.duration_ms)
        magnitude = self.intensity * decay
        # Random jitter
        dx = int(random.uniform(-magnitude, magnitude))
        dy = int(random.uniform(-magnitude, magnitude))
        return (dx, dy)


# ----------------------------------------------------------------------------
# Floating damage numbers
# ----------------------------------------------------------------------------


@dataclass(slots=True)
class FloatingNumber:
    """A floating damage/heal number that rises and fades."""

    x: float
    y: float
    value: int
    color: tuple[int, int, int]
    life_ms: int = 0
    max_life_ms: int = 800
    is_crit: bool = False

    def step(self, dt_ms: int) -> None:
        self.life_ms += dt_ms
        # Float upward over time
        self.y -= 0.03 * dt_ms

    @property
    def is_alive(self) -> bool:
        return self.life_ms < self.max_life_ms

    @property
    def text(self) -> str:
        prefix = "!" if self.is_crit else ""
        return f"{prefix}{self.value}{prefix}"

    @property
    def alpha(self) -> float:
        if self.max_life_ms == 0:
            return 0.0
        return max(0.0, 1.0 - self.life_ms / self.max_life_ms)


# ----------------------------------------------------------------------------
# Hit flash
# ----------------------------------------------------------------------------


@dataclass(slots=True)
class HitFlash:
    """Brief flash on a target tile after a hit."""

    duration_ms: int = 0
    elapsed_ms: int = 0
    color: tuple[int, int, int] = (255, 255, 255)

    def trigger(
        self, color: tuple[int, int, int] = (255, 255, 255), duration_ms: int = 120
    ) -> None:
        self.color = color
        self.duration_ms = duration_ms
        self.elapsed_ms = 0

    def step(self, dt_ms: int) -> None:
        if self.duration_ms > 0:
            self.elapsed_ms += dt_ms

    @property
    def is_active(self) -> bool:
        return self.elapsed_ms < self.duration_ms

    @property
    def alpha(self) -> float:
        if self.duration_ms == 0:
            return 0.0
        return max(0.0, 1.0 - self.elapsed_ms / self.duration_ms)


# ----------------------------------------------------------------------------
# Cinematic intro / death sequences
# ----------------------------------------------------------------------------


@dataclass(slots=True)
class CinematicSequence:
    """A scripted multi-phase cinematic (intro, death, critical).

    Each phase is a (text, color, duration_ms) tuple. The sequence
    advances through phases automatically.
    """

    name: str
    phases: tuple[tuple[str, tuple[int, int, int], int], ...]
    elapsed_ms: int = 0
    _phase_index: int = 0

    def step(self, dt_ms: int) -> None:
        if self.is_finished:
            return
        self.elapsed_ms += dt_ms

    @property
    def current_phase(self) -> tuple[str, tuple[int, int, int], int] | None:
        if self.is_finished:
            return None
        cumulative = 0
        for phase in self.phases:
            cumulative += phase[2]
            if self.elapsed_ms < cumulative:
                return phase
        return None

    @property
    def is_finished(self) -> bool:
        return self.elapsed_ms >= self.total_duration_ms

    @property
    def total_duration_ms(self) -> int:
        return sum(p[2] for p in self.phases)


# ----------------------------------------------------------------------------
# Combo counter
# ----------------------------------------------------------------------------


@dataclass(slots=True)
class ComboCounter:
    """Tracks consecutive hits within a short window.

    Combo decays after a short pause (combo_window_ms).
    """

    count: int = 0
    last_hit_ms: int = 0
    combo_window_ms: int = 2500

    def register_hit(self, current_ms: int) -> int:
        """Register a hit; returns new combo count."""
        if current_ms - self.last_hit_ms > self.combo_window_ms:
            self.count = 1
        else:
            self.count += 1
        self.last_hit_ms = current_ms
        return self.count

    def reset(self) -> None:
        self.count = 0
        self.last_hit_ms = 0

    @property
    def label(self) -> str:
        """Display label, e.g. '3x HIT!'."""
        if self.count < 2:
            return ""
        if self.count >= 5:
            return f"{self.count}x RAMPAGE!"
        return f"{self.count}x HIT!"


# ----------------------------------------------------------------------------
# Skill effect animations (Layer 2)
# ----------------------------------------------------------------------------


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
    cinematic: CinematicSequence | None = None
    combo: ComboCounter = field(default_factory=ComboCounter)
    slow_motion_ms: int = 0  # When > 0, time runs at half speed

    def step(self, dt_ms: int) -> None:
        """Step all effects forward by dt_ms."""
        # Apply slow motion
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
    "spawn_hit_effects",
    "spawn_ice_death",
    "spawn_ice_intro",
    "spawn_status_icon",
    "stun_animation",
    "buff_animation",
]
