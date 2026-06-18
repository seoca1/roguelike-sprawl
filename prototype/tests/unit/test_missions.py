"""Tests for missions and the job board (ADR-0010, ADR-0008)."""

from __future__ import annotations

from pathlib import Path

from roguelike_sprawl.matrix.node import ZoneDepth
from roguelike_sprawl.missions import JobBoard, Mission


def test_mission_creation() -> None:
    m = Mission(
        id="first_jack",
        title="First Jack",
        fixer="finn",
        arc=1,
        grade_min=1,
        grade_max=1,
        objective="Extract the demo file.",
        matrix_seed=42,
        zone=ZoneDepth.SURFACE,
        reward_tier=1,
        reward_credits=500,
    )
    assert m.id == "first_jack"
    assert m.arc == 1
    assert m.zone is ZoneDepth.SURFACE


def test_mission_invalid_grade_range() -> None:
    import pytest

    with pytest.raises(ValueError, match="grade"):
        Mission(
            id="x",
            title="X",
            fixer="finn",
            arc=1,
            grade_min=3,
            grade_max=2,
            objective="x",
            matrix_seed=1,
            zone=ZoneDepth.SURFACE,
            reward_tier=1,
            reward_credits=0,
        )


def test_job_board_empty() -> None:
    board = JobBoard()
    assert len(board) == 0
    assert board.available_for(grade=1) == ()


def test_job_board_load_missing_file(tmp_path: Path) -> None:
    board = JobBoard.load(tmp_path / "missing.json")
    assert len(board) == 0


def test_job_board_load_real_file(data_dir: Path) -> None:
    board = JobBoard.load(data_dir / "missions" / "missions.json")
    assert len(board) >= 2
    first = board.get("first_jack")
    assert first is not None
    assert first.fixer == "finn"
    assert first.zone is ZoneDepth.SURFACE


def test_job_board_available_for_filters_by_grade(data_dir: Path) -> None:
    board = JobBoard.load(data_dir / "missions" / "missions.json")
    g1 = board.available_for(grade=1)
    assert all(m.grade_min <= 1 <= m.grade_max for m in g1)
    g5 = board.available_for(grade=5)
    # No grade-5 mission defined yet
    assert all(m.grade_min <= 5 <= m.grade_max for m in g5)


def test_job_board_add_and_get() -> None:
    board = JobBoard()
    m = Mission(
        id="x",
        title="X",
        fixer="finn",
        arc=1,
        grade_min=1,
        grade_max=3,
        objective="x",
        matrix_seed=1,
        zone=ZoneDepth.SURFACE,
        reward_tier=1,
        reward_credits=0,
    )
    board.add(m)
    assert board.get("x") is m
    assert "x" in board
    assert "missing" not in board
