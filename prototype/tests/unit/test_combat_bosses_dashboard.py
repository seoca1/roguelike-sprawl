"""Tests for BOSS dashboard section in combat.html."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DASH = REPO_ROOT / "dashboard" / "combat.html"

ALL_BOSS_IDS = ["goliath_prime", "black_ice_lord", "watchdog_alpha"]
ALL_BOSS_NAMES = ["GOLIATH PRIME", "BLACK ICE LORD", "WATCHDOG ALPHA"]
ALL_BOSS_PHASES = {
    "goliath_prime": 4,
    "black_ice_lord": 3,
    "watchdog_alpha": 3,
}


def test_boss_section_exists() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert "BOSS ICE" in html
    assert "bosses.py" in html


@pytest.mark.parametrize("boss_id", ALL_BOSS_IDS)
def test_boss_id_listed(boss_id: str) -> None:
    html = DASH.read_text(encoding="utf-8").lower()
    # The id might appear in many forms: snake, kebab, title
    boss_id_lower = boss_id.lower()
    variants = [
        boss_id_lower,
        boss_id_lower.replace("_", " "),
        boss_id_lower.replace("_", "-"),
    ]
    assert any(v in html for v in variants), f"{boss_id} not in combat.html"


@pytest.mark.parametrize("boss_name", ALL_BOSS_NAMES)
def test_boss_name_listed(boss_name: str) -> None:
    html = DASH.read_text(encoding="utf-8")
    assert boss_name in html


def test_boss_grid_css_defined() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert ".boss-grid" in html
    assert ".boss-card" in html
    assert "goliath" in html
    assert "black" in html
    assert "watchdog" in html


def test_boss_phase_count_listed() -> None:
    html = DASH.read_text(encoding="utf-8")
    # P0, P1, P2, P3 for GOLIATH (4 phases)
    for phase_idx in range(3):
        assert f"P{phase_idx}" in html


def test_boss_special_abilities_listed() -> None:
    html = DASH.read_text(encoding="utf-8")
    # GOLIATH specials
    assert "ground_slam" in html
    assert "desperate_strike" in html
    # BLACK specials
    assert "glitch_burst" in html
    assert "corrupt_payload" in html
    # WATCHDOG specials
    assert "pack_howl" in html
    assert "alpha_strike" in html
