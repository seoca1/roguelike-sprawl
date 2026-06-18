"""Job board: loads missions and filters by grade (ADR-0008, ADR-0010, ADR-0017)."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

from ..matrix.node import ZoneDepth
from .mission import Mission, Objective, Rewards


class JobBoard:
    """The pool of available missions, filterable by player grade.

    Loads from ``missions.json`` (a flat dict of mission id -> mission data).
    Supports both the legacy format (ADR-0010) and the new structured
    format (ADR-0017).
    """

    __slots__ = ("_missions",)

    def __init__(self, missions: tuple[Mission, ...] = ()) -> None:
        self._missions = {m.id: m for m in missions}

    @classmethod
    def load(cls, path: Path) -> JobBoard:
        """Load a JobBoard from a JSON file.

        Missing or empty file yields an empty board (not an error).
        Malformed entries are skipped (caller can lint the data file).
        """
        if not path.exists():
            return cls()
        with path.open(encoding="utf-8") as f:
            raw: object = json.load(f)
        if not isinstance(raw, dict):
            return cls()
        missions: list[Mission] = []
        for value in raw.values():
            if not isinstance(value, dict):
                continue
            mission = _parse_mission(value)
            if mission is not None:
                missions.append(mission)
        return cls(tuple(missions))

    def add(self, mission: Mission) -> None:
        """Add or replace a mission by id."""
        self._missions[mission.id] = mission

    def get(self, mission_id: str) -> Mission | None:
        """Return a mission by id, or None if absent."""
        return self._missions.get(mission_id)

    def available_for(self, grade: int) -> tuple[Mission, ...]:
        """Return missions whose ``[grade_min, grade_max]`` includes ``grade``."""
        return tuple(m for m in self._missions.values() if m.grade_min <= grade <= m.grade_max)

    def __iter__(self) -> Iterator[Mission]:
        return iter(self._missions.values())

    def __len__(self) -> int:
        return len(self._missions)

    def __contains__(self, mission_id: object) -> bool:
        return isinstance(mission_id, str) and mission_id in self._missions

    def __repr__(self) -> str:
        return f"JobBoard({len(self._missions)} missions)"


def _parse_objective(raw: object) -> Objective | None:
    if not isinstance(raw, dict):
        return None
    try:
        tier_raw = raw.get("tier_level")
        tier_value: int | None = None
        if tier_raw is not None and not isinstance(tier_raw, bool):
            try:
                tier_value = int(tier_raw)
            except (TypeError, ValueError):
                tier_value = None
        count_raw = raw.get("count", 1)
        count_value: int = 1
        if count_raw is not None and not isinstance(count_raw, bool):
            try:
                count_value = int(count_raw)
            except (TypeError, ValueError):
                count_value = 1
        return Objective(
            type=str(raw.get("type", "")),
            count=count_value,
            material=_opt_str(raw.get("material")),
            enemy=_opt_str(raw.get("enemy")),
            data_id=_opt_str(raw.get("data_id")),
            item_type=_opt_str(raw.get("item_type")),
            tier_level=tier_value,
        )
    except (TypeError, ValueError):
        return None


def _parse_rewards(raw: object) -> Rewards | None:
    if not isinstance(raw, dict):
        return None
    credits_value = _opt_int(raw.get("credits"), 0) or 0
    materials_raw = raw.get("materials", {})
    materials: dict[str, int] = {}
    if isinstance(materials_raw, dict):
        for k, v in materials_raw.items():
            count = _opt_int(v, 0)
            if count is not None:
                materials[str(k)] = count
    return Rewards(credits=credits_value, materials=materials)


def _parse_mission(value: dict[str, object]) -> Mission | None:
    try:
        primary = _parse_objective(value.get("primary_objective"))
        secondary_raw = value.get("secondary_objectives", ())
        secondary: list[Objective] = []
        if isinstance(secondary_raw, list):
            for s in secondary_raw:
                obj = _parse_objective(s)
                if obj is not None:
                    secondary.append(obj)
        rewards = _parse_rewards(value.get("rewards"))

        if primary is None:
            obj_text = str(value.get("objective", ""))
            if obj_text:
                primary = Objective(type="extract_data", data_id=obj_text)
        if rewards is None:
            credits_value = _opt_int(value.get("reward_credits"), 0) or 0
            rewards = Rewards(credits=credits_value, materials={})

        return Mission(
            id=str(value["id"]),
            title=str(value["title"]),
            fixer=str(value["fixer"]),
            arc=_opt_int(value.get("arc"), 0) or 1,
            grade_min=_opt_int(value.get("grade_min"), 0) or 1,
            grade_max=_opt_int(value.get("grade_max"), 0) or 1,
            matrix_seed=_opt_int(value.get("matrix_seed"), 0) or 0,
            zone=ZoneDepth(str(value["zone"])),
            objective=str(value.get("objective", "")),
            reward_tier=_opt_int(value.get("reward_tier"), 1) or 1,
            reward_credits=rewards.credits,
            primary_objective=primary,
            secondary_objectives=tuple(secondary),
            rewards=rewards,
        )
    except (KeyError, TypeError, ValueError):
        return None


def _opt_int(value: object, default: int) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, (str, bytes, bytearray)):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _opt_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)
