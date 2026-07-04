"""BOSS ICE definitions with multi-phase transitions.

BOSS ICE have:
- Multi-phase progression (3-4 phases triggered at HP thresholds)
- Longer intro sequence (3-5s with multi-line text)
- Multi-phase death sequence (12-15 frames)
- Phase transition effects (screen flash, name callout)
- Per-phase stat buffs (attack speed, damage, special abilities)
- Boss-specific dialogue lines (Korean)

Boss types (3 implemented):
  1. GOLIATH PRIME (goliath base) — earth-shattering, 4 phases
  2. BLACK ICE LORD (black base) — glitch chaos, 3 phases
  3. WATCHDOG ALPHA (watchdog base) — pack leader, 3 phases
"""

from __future__ import annotations

from dataclasses import dataclass

from .effects import (
    CinematicSequence,
    CombatEffects,
    IceType,
    spawn_hit_effects,
)
from .palette import GLITCH_COLOR

# ----------------------------------------------------------------------------
# Boss data structures
# ----------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class BossPhase:
    """A single phase of a BOSS fight.

    Activated when the BOSS's HP drops below `hp_threshold_pct` (0-100).
    Each phase has its own intro line and stat modifiers.
    """

    index: int
    name: str
    hp_threshold_pct: int  # 0-100, phase activates when HP% <= this
    intro_line: str  # Korean text shown on transition
    color: tuple[int, int, int]
    attack_bonus_pct: int = 0  # +X% attack vs previous phase
    speed_bonus_pct: int = 0  # +X% attack speed
    screen_shake_intensity: float = 0.0  # Shake on phase change
    special_ability: str | None = None  # e.g. "ground_slam", "glitch_burst"


@dataclass(frozen=True, slots=True)
class BossSpec:
    """A complete BOSS definition with all phases."""

    id: str
    name: str
    base_ice_type: IceType
    hp_multiplier: float  # 3-5x normal ICE
    attack_multiplier: float  # 1.5-2.5x
    defense_multiplier: float  # 1.2-2.0x
    phases: tuple[BossPhase, ...]  # Ordered high-to-low HP
    intro_lines: tuple[str, ...]  # Multi-line intro text
    death_lines: tuple[str, ...]  # Multi-line death text


# ----------------------------------------------------------------------------
# 3 BOSS definitions
# ----------------------------------------------------------------------------


GOLIATH_PRIME = BossSpec(
    id="goliath_prime",
    name="GOLIATH PRIME",
    base_ice_type=IceType.GOLIATH,
    hp_multiplier=4.0,
    attack_multiplier=2.0,
    defense_multiplier=1.8,
    intro_lines=(
        "[ 경고: GOLIATH PRIME ]",
        "▓▓▓ 보안 시스템 핵심 ▓▓▓",
        "최대 방어 프로토콜 가동",
        "·····",
        "출현.",
    ),
    phases=(
        BossPhase(
            index=0,
            name="정상",
            hp_threshold_pct=100,
            intro_line="",
            color=(150, 150, 170),
        ),
        BossPhase(
            index=1,
            name="경계",
            hp_threshold_pct=75,
            intro_line="▸ 방어 프로토콜 강화",
            color=(255, 180, 100),
            attack_bonus_pct=20,
            speed_bonus_pct=10,
            screen_shake_intensity=2.0,
        ),
        BossPhase(
            index=2,
            name="격노",
            hp_threshold_pct=50,
            intro_line="▸ 격노 상태 돌입",
            color=(255, 100, 100),
            attack_bonus_pct=40,
            speed_bonus_pct=20,
            screen_shake_intensity=3.0,
            special_ability="ground_slam",
        ),
        BossPhase(
            index=3,
            name="자폭",
            hp_threshold_pct=25,
            intro_line="▸ 자폭 시퀀스 시작",
            color=(255, 50, 50),
            attack_bonus_pct=80,
            speed_bonus_pct=40,
            screen_shake_intensity=4.5,
            special_ability="desperate_strike",
        ),
    ),
    death_lines=(
        "[ GOLIATH PRIME ]",
        "·····",
        "방어 프로토콜 해제.",
        "코어 노출.",
        "·····",
        "침묵.",
    ),
)

BLACK_ICE_LORD = BossSpec(
    id="black_ice_lord",
    name="BLACK ICE LORD",
    base_ice_type=IceType.BLACK,
    hp_multiplier=3.5,
    attack_multiplier=2.5,
    defense_multiplier=1.4,
    intro_lines=(
        "▓▓▓ 오류: ICE 권한 초과 ▓▓▓",
        "▓▓▓ BLACK ICE: 관리자 계정 ▓▓▓",
        "·····",
        "▒▒ 관리자 권한으로 시스템 장악 ▒▒",
        "나타남.",
    ),
    phases=(
        BossPhase(
            index=0,
            name="위장",
            hp_threshold_pct=100,
            intro_line="",
            color=(180, 180, 200),
        ),
        BossPhase(
            index=1,
            name="노출",
            hp_threshold_pct=66,
            intro_line="▸ 위장 해제 — 본체 노출",
            color=GLITCH_COLOR,
            attack_bonus_pct=30,
            screen_shake_intensity=1.5,
            special_ability="glitch_burst",
        ),
        BossPhase(
            index=2,
            name="붕괴",
            hp_threshold_pct=33,
            intro_line="▸ 코드 손상 — 무작위 공격",
            color=(255, 0, 100),
            attack_bonus_pct=60,
            speed_bonus_pct=30,
            screen_shake_intensity=3.0,
            special_ability="corrupt_payload",
        ),
    ),
    death_lines=(
        "[ERR] BLACK_ICE_LORD",
        "▓▓ 권한 박탈 ▓▓",
        "·····",
        "[연결 종료]",
    ),
)

WATCHDOG_ALPHA = BossSpec(
    id="watchdog_alpha",
    name="WATCHDOG ALPHA",
    base_ice_type=IceType.WATCHDOG,
    hp_multiplier=3.0,
    attack_multiplier=1.8,
    defense_multiplier=1.2,
    intro_lines=(
        "[ 경고: 추적자 ]",
        "·····",
        "WATCHDOG ALPHA 가 잠에서 깨어남.",
        "추적 시작.",
        "도망칠 수 없다.",
    ),
    phases=(
        BossPhase(
            index=0,
            name="추적",
            hp_threshold_pct=100,
            intro_line="",
            color=(200, 150, 100),
        ),
        BossPhase(
            index=1,
            name="분노",
            hp_threshold_pct=50,
            intro_line="▸ 무리 호출 — 공격 빈도 증가",
            color=(255, 100, 100),
            attack_bonus_pct=25,
            speed_bonus_pct=50,
            screen_shake_intensity=2.5,
            special_ability="pack_howl",
        ),
        BossPhase(
            index=2,
            name="집중",
            hp_threshold_pct=20,
            intro_line="▸ 마지막 추적 — 결정타",
            color=(255, 50, 50),
            attack_bonus_pct=100,
            speed_bonus_pct=20,
            screen_shake_intensity=3.5,
            special_ability="alpha_strike",
        ),
    ),
    death_lines=(
        "WATCHDOG ALPHA:",
        "·····",
        "...woof?",
        "[연결 종료]",
    ),
)

ALL_BOSSES: dict[str, BossSpec] = {
    GOLIATH_PRIME.id: GOLIATH_PRIME,
    BLACK_ICE_LORD.id: BLACK_ICE_LORD,
    WATCHDOG_ALPHA.id: WATCHDOG_ALPHA,
}


def is_boss(ice_id: str) -> bool:
    """Check if an ICE id refers to a BOSS."""
    return ice_id in ALL_BOSSES


def get_boss_spec(ice_id: str) -> BossSpec | None:
    """Get the BOSS spec for an id, or None if not a BOSS."""
    return ALL_BOSSES.get(ice_id)


def get_next_phase(spec: BossSpec, current_hp_pct: int) -> BossPhase | None:
    """Get the next phase to activate given the current HP percentage.

    A phase activates when current_hp_pct drops to or below its threshold.
    Returns None if no phase transition should occur.
    """
    # Phases are ordered high-to-low. Find the highest-index phase
    # whose threshold the HP has just crossed.
    for phase in reversed(spec.phases):
        if current_hp_pct <= phase.hp_threshold_pct:
            return phase
    return None


def apply_phase_buff(phase: BossPhase, base_attack: int, base_speed_ms: int) -> tuple[int, int]:
    """Apply a phase's stat buff to base attack and attack speed.

    Returns (new_attack, new_speed_ms).
    """
    new_attack = base_attack * (100 + phase.attack_bonus_pct) // 100
    new_speed = base_speed_ms * 100 // (100 + phase.speed_bonus_pct)
    return (new_attack, new_speed)


# ----------------------------------------------------------------------------
# Boss intro sequence (3-5 second multi-line)
# ----------------------------------------------------------------------------


def boss_intro_sequence(spec: BossSpec) -> CinematicSequence:
    """Long, multi-line intro for a BOSS.

    Each line is shown for 500-800ms with color matching the boss's
    primary element. Total duration: 3-5 seconds.
    """
    if spec.base_ice_type == IceType.GOLIATH:
        # Heavy, earth-shattering intro
        from .palette import ICE_GOLIATH_PALETTE

        color_palette = ICE_GOLIATH_PALETTE
    elif spec.base_ice_type == IceType.BLACK:
        # Glitchy, digital corruption intro
        from .palette import ICE_BLACK_PALETTE

        color_palette = ICE_BLACK_PALETTE
    else:  # WATCHDOG
        from .palette import ICE_WATCHDOG_PALETTE

        color_palette = ICE_WATCHDOG_PALETTE

    phases: list[tuple[str, tuple[int, int, int], int]] = []
    for i, line in enumerate(spec.intro_lines):
        color = color_palette[min(i, len(color_palette) - 1)]
        # First and last lines stay longer
        duration = 800 if (i == 0 or i == len(spec.intro_lines) - 1) else 500
        phases.append((line, color, duration))

    return CinematicSequence(name=f"boss_intro_{spec.id}", phases=tuple(phases))


# ----------------------------------------------------------------------------
# Boss phase transition
# ----------------------------------------------------------------------------


def boss_phase_transition(spec: BossSpec, new_phase: BossPhase) -> CinematicSequence:
    """Cinematic when the BOSS transitions to a new phase.

    Includes:
    - Screen flash
    - Name callout
    - Phase transition line
    - Special ability announcement
    """
    phases: list[tuple[str, tuple[int, int, int], int]] = []

    # Warning flash
    phases.append(("▒▒▒", (255, 255, 255), 80))
    phases.append(("▓▓▓", (255, 200, 0), 80))
    phases.append(("███", (255, 100, 0), 100))

    # Phase name
    phase_names = ["", "경계", "격노", "자폭", "최후"]
    phase_name = (
        phase_names[new_phase.index]
        if new_phase.index < len(phase_names)
        else f"PHASE {new_phase.index}"
    )
    phases.append((f"[ {spec.name} ]", new_phase.color, 300))
    phases.append((f"▸ {phase_name} 단계 돌입", new_phase.color, 600))

    # Special ability announcement
    if new_phase.special_ability is not None:
        ability_names = {
            "ground_slam": "▸ 지면 강타",
            "glitch_burst": "▸ 글리치 폭주",
            "corrupt_payload": "▸ 페이로드 오염",
            "desperate_strike": "▸ 자폭 강타",
            "pack_howl": "▸ 무리 외침",
            "alpha_strike": "▸ 알파 스트라이크",
        }
        ability_text = ability_names.get(
            new_phase.special_ability, f"▸ {new_phase.special_ability}"
        )
        phases.append((ability_text, (255, 100, 100), 700))

    # Final flash
    phases.append(("▓▓▓", (255, 255, 255), 100))
    phases.append(("···", (200, 200, 200), 200))

    return CinematicSequence(
        name=f"boss_phase_{spec.id}_{new_phase.index}",
        phases=tuple(phases),
    )


# ----------------------------------------------------------------------------
# Boss death sequence (12-15 frames)
# ----------------------------------------------------------------------------


def boss_death_sequence(spec: BossSpec) -> list[CinematicSequence]:
    """Multi-stage death sequence for a BOSS.

    Returns a list of CinematicSequences to play in sequence:
    1. Damage accumulation phase (3-4 frames)
    2. Critical failure (3-4 frames)
    3. Core exposure (2-3 frames)
    4. Final destruction (3-4 frames)
    5. Epilogue dialogue
    """
    dispatch = {
        IceType.GOLIATH: _goliath_death_sequence,
        IceType.BLACK:   _black_death_sequence,
    }
    handler = dispatch.get(spec.base_ice_type, _watchdog_death_sequence)
    return handler()


# ------------------------------------------------------------------
# Per-ICE-type death-sequence builders.  Each returns the four-stage
# CinematicSequence list for that ICE archetype.
# ------------------------------------------------------------------


def _goliath_death_sequence() -> list[CinematicSequence]:
    """Slow, heavy destruction with earthquake — corp-war-machine feel."""
    seq1 = CinematicSequence(
        name="goliath_dmg_phase",
        phases=(
            ("[X_X]", (255, 100, 100), 100),
            ("[X!X]", (255, 50, 50), 100),
            ("[#_#]", (200, 100, 100), 150),
            ("[╳_╳]", (200, 50, 50), 200),
        ),
    )
    seq2 = CinematicSequence(
        name="goliath_crit_fail",
        phases=(
            ("▓▓▓ 경고 ▓▓▓", (255, 200, 0), 300),
            ("코어 보호 실패", (255, 150, 0), 400),
            ("·····", (200, 100, 100), 300),
        ),
    )
    seq3 = CinematicSequence(
        name="goliath_core_exposure",
        phases=(
            ("[___]", (255, 100, 100), 200),
            ("[*_*]", (255, 200, 0), 250),
            ("[*█*]", (255, 255, 100), 300),
        ),
    )
    seq4 = CinematicSequence(
        name="goliath_final",
        phases=(
            ("[*█*]", (255, 255, 200), 150),
            ("[*▓*]", (200, 200, 100), 200),
            ("·····", (100, 100, 100), 300),
        ),
    )
    return [seq1, seq2, seq3, seq4]


def _black_death_sequence() -> list[CinematicSequence]:
    """Glitchy corruption, code collapse — ICE-controlled ICE."""
    seq1 = CinematicSequence(
        name="black_dmg_phase",
        phases=(
            (f"[{GLITCH_COLOR[0]}ERR]", (255, 100, 0), 100),
            ("[ERR]", (255, 0, 0), 100),
            (f"[{GLITCH_COLOR[0]}?????]", (200, 0, 200), 150),
            ("[▓▓▓▓▓]", (100, 100, 100), 200),
        ),
    )
    seq2 = CinematicSequence(
        name="black_crit_fail",
        phases=(
            ("▒ 권한 박탈 ▒", (255, 0, 100), 250),
            ("[연결 손상]", (200, 0, 100), 300),
            ("·····", (100, 0, 100), 250),
        ),
    )
    seq3 = CinematicSequence(
        name="black_core_exposure",
        phases=(
            ("[▒▒▒▒▒]", (80, 80, 80), 200),
            ("[░░░░░]", (60, 60, 60), 250),
            ("[_____]", (40, 40, 40), 300),
        ),
    )
    seq4 = CinematicSequence(
        name="black_final",
        phases=(
            ("[_____]", (40, 40, 40), 200),
            ("· · ·", (30, 30, 30), 300),
            ("[연결 종료]", (100, 100, 100), 400),
        ),
    )
    return [seq1, seq2, seq3, seq4]


def _watchdog_death_sequence() -> list[CinematicSequence]:
    """Predatory fall, final howl — default for non-archetype bosses."""
    seq1 = CinematicSequence(
        name="watchdog_dmg_phase",
        phases=(
            ("[X_O]", (220, 180, 100), 150),
            ("[X_X]", (200, 100, 100), 200),
            ("[X_X]", (150, 80, 80), 250),
        ),
    )
    seq2 = CinematicSequence(
        name="watchdog_crit_fail",
        phases=(
            ("...", (200, 150, 100), 200),
            ("...woof?", (200, 100, 100), 400),
            ("[system: target lost]", (180, 100, 100), 400),
        ),
    )
    seq3 = CinematicSequence(
        name="watchdog_core_exposure",
        phases=(
            ("[X_X]", (150, 80, 80), 200),
            ("[X·X]", (100, 60, 60), 250),
            ("[·_·]", (80, 40, 40), 300),
        ),
    )
    seq4 = CinematicSequence(
        name="watchdog_final",
        phases=(
            ("[·_·]", (60, 30, 30), 200),
            ("· · ·", (40, 20, 20), 400),
            ("[추적 종료]", (100, 100, 100), 400),
        ),
    )
    return [seq1, seq2, seq3, seq4]


# ----------------------------------------------------------------------------
# Boss epic dialogue
# ----------------------------------------------------------------------------


def boss_epilogue_lines(spec: BossSpec) -> tuple[str, ...]:
    """Return the BOSS's death dialogue."""
    return spec.death_lines


# ----------------------------------------------------------------------------
# High-level spawners
# ----------------------------------------------------------------------------


def spawn_boss_intro(effects: CombatEffects, spec: BossSpec) -> None:
    """Spawn the cinematic BOSS intro."""
    seq = boss_intro_sequence(spec)
    effects.cinematic = seq
    effects.slow_motion_ms = seq.total_duration_ms
    effects.shake.trigger(intensity=3.0, duration_ms=500)


def spawn_boss_phase_transition(
    effects: CombatEffects,
    spec: BossSpec,
    new_phase: BossPhase,
) -> None:
    """Spawn a phase transition cinematic."""
    seq = boss_phase_transition(spec, new_phase)
    effects.cinematic = seq
    effects.slow_motion_ms = 0  # No slow-mo for mid-fight
    effects.shake.trigger(intensity=new_phase.screen_shake_intensity, duration_ms=400)
    # Burst particles on transition
    spawn_hit_effects(
        effects,
        target_x=20.0,
        target_y=7.0,
        damage=0,
        effect_type="heavy_attack",
        is_crit=False,
        hit_color=new_phase.color,
    )


def spawn_boss_death(effects: CombatEffects, spec: BossSpec) -> None:
    """Spawn a multi-stage BOSS death sequence.

    Plays the first sequence immediately. The remaining sequences
    can be chained by re-calling this after the previous one finishes.
    """
    sequences = boss_death_sequence(spec)
    if sequences:
        first = sequences[0]
        # Modify the first to include the epilogue
        epilogue = boss_epilogue_lines(spec)
        combined_phases = list(first.phases)
        for line in epilogue:
            combined_phases.append((line, (200, 200, 200), 600))
        effects.cinematic = CinematicSequence(
            name=f"boss_death_{spec.id}",
            phases=tuple(combined_phases),
        )
        effects.slow_motion_ms = 0
        effects.shake.trigger(intensity=4.0, duration_ms=600)


__all__ = [
    "ALL_BOSSES",
    "BLACK_ICE_LORD",
    "BossPhase",
    "BossSpec",
    "GOLIATH_PRIME",
    "WATCHDOG_ALPHA",
    "apply_phase_buff",
    "boss_death_sequence",
    "boss_epilogue_lines",
    "boss_intro_sequence",
    "boss_phase_transition",
    "get_boss_spec",
    "get_next_phase",
    "is_boss",
    "spawn_boss_death",
    "spawn_boss_intro",
    "spawn_boss_phase_transition",
]
