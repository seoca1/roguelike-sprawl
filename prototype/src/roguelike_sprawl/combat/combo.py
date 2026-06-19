"""Skill combo system for combat.

Players chain 3-7 skills within a time window (3.5s by default) for
cumulative bonuses:

  Stage 0 (1-2 hits): WARMUP     - no bonus
  Stage 1 (3 hits):   CHAIN       - +20% damage, "3x CHAIN!"
  Stage 2 (4 hits):   FLURRY      - +50% damage, +1 AP, "4x FLURRY!"
  Stage 3 (5 hits):   RAMPAGE     - +100% damage, +2 AP, "5x RAMPAGE!"
  Stage 4 (6+ hits):  ANNIHILATION - +200% damage, +3 AP, "6x ANNIHILATION!"

Features:
  - Window-based: combo resets after 3.5s without a hit
  - Per-stage visual: counter color escalates, screen shake on high stages
  - Stage-up cinematic: brief text callout on reaching new stage
  - End visual: "콤보 종료" with bonus summary
  - Integration: apply bonus damage/AP to skill resolution
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# ----------------------------------------------------------------------------
# Combo stage definitions
# ----------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ComboStage:
    """A stage in the combo progression.

    Activated when combo count reaches `min_count`. Provides:
    - Display label (e.g. "3x CHAIN!")
    - Damage bonus percentage
    - AP regen on hit
    - Screen shake intensity
    - Color for the counter display
    - Korean name for stage-up callout
    """

    index: int
    name: str
    name_ko: str
    min_count: int
    damage_bonus_pct: int
    ap_regen: int
    screen_shake: float
    color: tuple[int, int, int]
    label: str


# 5 combo stages
WARMUP = ComboStage(
    index=0,
    name="WARMUP",
    name_ko="웜업",
    min_count=1,
    damage_bonus_pct=0,
    ap_regen=0,
    screen_shake=0.0,
    color=(200, 200, 200),
    label="",
)

CHAIN = ComboStage(
    index=1,
    name="CHAIN",
    name_ko="연쇄",
    min_count=3,
    damage_bonus_pct=20,
    ap_regen=0,
    screen_shake=0.5,
    color=(100, 230, 130),
    label="CHAIN!",
)

FLURRY = ComboStage(
    index=2,
    name="FLURRY",
    name_ko="폭주",
    min_count=4,
    damage_bonus_pct=50,
    ap_regen=1,
    screen_shake=1.5,
    color=(255, 200, 80),
    label="FLURRY!",
)

RAMPAGE = ComboStage(
    index=3,
    name="RAMPAGE",
    name_ko="섬멸",
    min_count=5,
    damage_bonus_pct=100,
    ap_regen=2,
    screen_shake=2.5,
    color=(255, 100, 80),
    label="RAMPAGE!",
)

ANNIHILATION = ComboStage(
    index=4,
    name="ANNIHILATION",
    name_ko="초월",
    min_count=6,
    damage_bonus_pct=200,
    ap_regen=3,
    screen_shake=4.0,
    color=(255, 30, 30),
    label="ANNIHILATION!",
)

ALL_STAGES: tuple[ComboStage, ...] = (
    WARMUP,
    CHAIN,
    FLURRY,
    RAMPAGE,
    ANNIHILATION,
)


# ----------------------------------------------------------------------------
# Combo state
# ----------------------------------------------------------------------------


@dataclass(slots=True)
class CombatCombo:
    """Tracks the current combo in combat.

    Hits within `window_ms` of each other accumulate. Each hit
    increases the count; the current stage is the highest stage
    whose min_count is ≤ the count.
    """

    count: int = 0
    last_hit_ms: int = 0
    current_stage: ComboStage = WARMUP
    previous_stage: ComboStage = WARMUP
    # Visual state
    elapsed_ms: int = 0  # Time since last hit
    window_ms: int = 3500
    stage_up_pending: bool = False  # True for 1 frame when stage changes
    just_ended: bool = False  # True for 1 frame when combo ends
    # Stats
    total_damage_dealt: int = 0
    total_ap_gained: int = 0
    max_combo_reached: int = 0

    def register_hit(
        self,
        current_ms: int,
        damage_dealt: int = 0,
    ) -> ComboStage:
        """Register a hit; returns the (possibly new) current stage.

        If the window has expired, count resets to 1. Otherwise count
        increments. Stage changes trigger stage_up_pending.
        """
        if current_ms - self.last_hit_ms > self.window_ms:
            # Window expired — reset
            self.count = 1
        else:
            self.count += 1

        self.last_hit_ms = current_ms
        self.elapsed_ms = 0
        self.total_damage_dealt += damage_dealt
        self.max_combo_reached = max(self.max_combo_reached, self.count)

        # Update stage
        new_stage = self._stage_for_count(self.count)
        if new_stage.index > self.current_stage.index:
            self.previous_stage = self.current_stage
            self.current_stage = new_stage
            self.stage_up_pending = True
        else:
            self.stage_up_pending = False

        # Apply AP regen (cumulative across hits in the same stage)
        # Note: AP is given to the player, not stored in combo
        return new_stage

    def step(self, dt_ms: int) -> None:
        """Step the combo forward. Detect window expiry."""
        self.elapsed_ms += dt_ms
        # Clear one-shot flags
        if self.stage_up_pending:
            # stays True for 1 step
            pass
        # Window check
        if self.count > 0 and self.elapsed_ms > self.window_ms:
            # Combo ended
            self.just_ended = True
            self.count = 0
            self.current_stage = WARMUP
            self.previous_stage = WARMUP
            self.elapsed_ms = 0
        else:
            self.just_ended = False

    def consume_stage_up(self) -> ComboStage | None:
        """Consume stage_up flag. Returns the new stage if it was just raised."""
        if self.stage_up_pending:
            self.stage_up_pending = False
            return self.current_stage
        return None

    def consume_just_ended(self) -> bool:
        """Consume just_ended flag. Returns True if combo just ended."""
        if self.just_ended:
            self.just_ended = False
            return True
        return False

    def reset(self) -> None:
        """Reset the combo (e.g. on combat end)."""
        self.count = 0
        self.current_stage = WARMUP
        self.previous_stage = WARMUP
        self.elapsed_ms = 0
        self.stage_up_pending = False
        self.just_ended = False

    def _stage_for_count(self, count: int) -> ComboStage:
        """Get the highest stage whose min_count is ≤ count."""
        stage = WARMUP
        for s in ALL_STAGES:
            if count >= s.min_count:
                stage = s
        return stage

    @property
    def display_count(self) -> int:
        """Count to show in the UI (max 99)."""
        return min(self.count, 99)

    @property
    def display_label(self) -> str:
        """Full combo label e.g. '3x CHAIN!'."""
        if self.count < 2:
            return ""
        return f"{self.display_count}x {self.current_stage.label}"

    @property
    def window_progress(self) -> float:
        """0.0 to 1.0 progress through the combo window.

        Used to show a "draining" timer bar.
        """
        if self.count == 0 or self.window_ms == 0:
            return 0.0
        return min(1.0, self.elapsed_ms / self.window_ms)

    @property
    def window_remaining_pct(self) -> int:
        """0-100 percent of window remaining."""
        return int((1.0 - self.window_progress) * 100)

    def apply_damage_bonus(self, base_damage: int) -> int:
        """Apply the current stage's damage bonus to a base damage value."""
        bonus = base_damage * self.current_stage.damage_bonus_pct // 100
        return base_damage + bonus

    def get_ap_regen(self) -> int:
        """AP regen amount for the current stage."""
        return self.current_stage.ap_regen


# ----------------------------------------------------------------------------
# Combo visual state
# ----------------------------------------------------------------------------


@dataclass(slots=True)
class ComboVisual:
    """Visual state for the combo display.

    Drives the top-center combo counter and any stage-up cinematic.
    """

    counter_text: str = ""
    counter_color: tuple[int, int, int] = (200, 200, 200)
    counter_pulse_ms: int = 0  # Pulses when new hit registered
    counter_pulse_max_ms: int = 200
    # Stage-up cinematic
    stage_up_text: str = ""
    stage_up_color: tuple[int, int, int] = (200, 200, 200)
    stage_up_ms: int = 0
    stage_up_max_ms: int = 800
    # End cinematic
    end_text: str = ""
    end_ms: int = 0
    end_max_ms: int = 1500


def update_combo_visual(
    visual: ComboVisual,
    combo: CombatCombo,
) -> None:
    """Update the visual state from combo state."""
    visual.counter_text = combo.display_label
    visual.counter_color = combo.current_stage.color

    # Decay pulses
    if visual.counter_pulse_ms > 0:
        visual.counter_pulse_ms = max(0, visual.counter_pulse_ms - 16)
    if visual.stage_up_ms > 0:
        visual.stage_up_ms = max(0, visual.stage_up_ms - 16)
    if visual.end_ms > 0:
        visual.end_ms = max(0, visual.end_ms - 16)

    # Stage-up cinematic
    new_stage = combo.consume_stage_up()
    if new_stage is not None:
        visual.stage_up_text = f"▸ {new_stage.name_ko} 단계 돌입 ({new_stage.label})"
        visual.stage_up_color = new_stage.color
        visual.stage_up_ms = visual.stage_up_max_ms
        visual.counter_pulse_ms = visual.counter_pulse_max_ms

    # End cinematic
    if combo.consume_just_ended():
        max_combo = combo.max_combo_reached
        total_dmg = combo.total_damage_dealt
        visual.end_text = f"[ 콤보 종료 ]  최대 {max_combo} 히트, {total_dmg} 데미지"
        visual.end_ms = visual.end_max_ms
        visual.counter_text = ""
        visual.counter_pulse_ms = 0


# ----------------------------------------------------------------------------
# Combo display rendering
# ----------------------------------------------------------------------------


def render_combo_counter(visual: ComboVisual, width: int = 30) -> str:
    """Render the combo counter for top-center display.

    Returns the text to display. Empty if no active combo.
    """
    if not visual.counter_text:
        return ""

    # Pad to width for centering
    text = visual.counter_text
    pad = max(0, (width - len(text)) // 2)
    return " " * pad + text


def render_combo_stage_up(visual: ComboVisual) -> str:
    """Render the stage-up cinematic text (one-time callout)."""
    if visual.stage_up_ms <= 0:
        return ""
    return visual.stage_up_text


def render_combo_end(visual: ComboVisual) -> str:
    """Render the end cinematic text."""
    if visual.end_ms <= 0:
        return ""
    return visual.end_text


# ----------------------------------------------------------------------------
# High-level spawner
# ----------------------------------------------------------------------------


def spawn_combo_hit(
    combo: CombatCombo,
    visual: ComboVisual,
    current_ms: int,
    damage_dealt: int = 0,
) -> ComboStage:
    """Register a combo hit, update visual, return new stage.

    This is the main entry point. combat_view calls this on every
    successful player skill use.
    """
    new_stage = combo.register_hit(current_ms, damage_dealt)
    if new_stage.index > 0:
        visual.counter_pulse_ms = visual.counter_pulse_max_ms
    update_combo_visual(visual, combo)
    return new_stage


__all__ = [
    "ALL_STAGES",
    "ANNIHILATION",
    "CHAIN",
    "CombatCombo",
    "ComboStage",
    "ComboVisual",
    "FLURRY",
    "RAMPAGE",
    "WARMUP",
    "render_combo_counter",
    "render_combo_end",
    "render_combo_stage_up",
    "spawn_combo_hit",
    "update_combo_visual",
]
