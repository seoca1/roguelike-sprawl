"""Tests for skill combo dashboard section."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DASH = REPO_ROOT / "dashboard" / "combat.html"

REQUIRED_STAGES = ["WARMUP", "CHAIN", "FLURRY", "RAMPAGE", "ANNIHILATION"]
REQUIRED_KOREAN = ["웜업", "연쇄", "폭주", "섬멸", "초월"]
REQUIRED_LABELS = ["3x CHAIN!", "4x FLURRY!", "5x RAMPAGE!", "6x ANNIHILATION!"]


def test_combo_section_exists() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert "콤보 시스템" in html or "스킬 콤보" in html
    assert "combo.py" in html


@pytest.mark.parametrize("stage", REQUIRED_STAGES)
def test_stage_listed(stage: str) -> None:
    html = DASH.read_text(encoding="utf-8")
    assert stage in html, f"Stage {stage} not in combat dashboard"


@pytest.mark.parametrize("name", REQUIRED_KOREAN)
def test_korean_name_listed(name: str) -> None:
    html = DASH.read_text(encoding="utf-8")
    assert name in html, f"Korean name {name} not in combat dashboard"


@pytest.mark.parametrize("label", REQUIRED_LABELS)
def test_label_listed(label: str) -> None:
    html = DASH.read_text(encoding="utf-8")
    assert label in html, f"Label {label} not in combat dashboard"


def test_combo_window_text() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert "3.5초" in html
    assert "콤보 종료" in html


def test_damage_bonus_values() -> None:
    html = DASH.read_text(encoding="utf-8")
    # Check all damage bonus values
    assert "+0% DMG" in html
    assert "+20% DMG" in html
    assert "+50% DMG" in html
    assert "+100% DMG" in html
    assert "+200% DMG" in html


def test_ap_regen_values() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert "+1 AP" in html
    assert "+2 AP" in html
    assert "+3 AP" in html


def test_combo_grid_css() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert ".combo-grid" in html
    assert ".combo-stage" in html
    assert ".combo-label" in html


def test_per_stage_color_classes() -> None:
    html = DASH.read_text(encoding="utf-8")
    # All 5 stage CSS classes
    for stage in ("warmup", "chain", "flurry", "rampage", "annihilation"):
        assert f"combo-stage.{stage}" in html
