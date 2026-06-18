"""Mission data model (ADR-0010, ADR-0017, story_skeleton.md)."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..matrix.node import ZoneDepth


@dataclass(frozen=True, slots=True)
class Objective:
    """A single mission objective (ADR-0017).

    ``type`` is one of:
        "extract_data", "collect_material", "deliver_material",
        "defeat", "craft_item", "hunt", "salvage".
    """

    type: str
    count: int = 1
    material: str | None = None
    enemy: str | None = None
    data_id: str | None = None
    item_type: str | None = None
    tier_level: int | None = None


@dataclass(frozen=True, slots=True)
class Rewards:
    """Mission completion rewards (ADR-0017)."""

    credits: int = 0
    materials: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Mission:
    """A single cyberspace run definition (ADR-0010, ADR-0017).

    Supports both the legacy fields (``objective``, ``reward_tier``,
    ``reward_credits``) and the new structured objectives / rewards
    introduced by ADR-0017.
    """

    id: str
    title: str
    fixer: str
    arc: int
    grade_min: int
    grade_max: int
    matrix_seed: int
    zone: ZoneDepth
    objective: str = ""
    reward_tier: int = 1
    reward_credits: int = 0
    primary_objective: Objective | None = None
    secondary_objectives: tuple[Objective, ...] = ()
    rewards: Rewards | None = None

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Mission id must be non-empty")
        if not 1 <= self.arc <= 5:
            raise ValueError(f"arc must be 1..5, got {self.arc}")
        if not 1 <= self.grade_min <= self.grade_max <= 5:
            raise ValueError(f"invalid grade range {self.grade_min}..{self.grade_max}")
        if not 1 <= self.reward_tier <= 5:
            raise ValueError(f"reward_tier must be 1..5, got {self.reward_tier}")
        if self.reward_credits < 0:
            raise ValueError("reward_credits must be >= 0")

    def primary_type(self) -> str:
        """Return the primary objective type, defaulting to 'extract_data'."""
        if self.primary_objective is not None:
            return self.primary_objective.type
        return "extract_data"

    def required_count(self) -> int:
        """Return how many items/events are required to complete primary objective."""
        if self.primary_objective is not None:
            return self.primary_objective.count
        return 1

    def check_completion(self, progress: dict[str, int]) -> bool:
        """Check if the mission is complete based on player progress.

        Args:
            progress: Dict of objective_type -> count.

        Returns:
            True if primary objective is satisfied.
        """
        if self.primary_objective is None:
            return False
        obj = self.primary_objective
        current = progress.get(obj.type, 0)
        return current >= obj.count

    def progress_pct(self, progress: dict[str, int]) -> float:
        """Return 0.0-1.0 progress toward primary objective."""
        required = self.required_count()
        if required <= 0:
            return 1.0
        if self.primary_objective is None:
            return 0.0
        current = progress.get(self.primary_objective.type, 0)
        return min(1.0, current / required)
