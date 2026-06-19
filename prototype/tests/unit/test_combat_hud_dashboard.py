"""Tests for combat HUD dashboard section."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DASH = REPO_ROOT / "dashboard" / "combat.html"

REQUIRED_SECTIONS = [
    "HP 바",
    "카메라 연출",
    "HUD",
    "hud.py",
    "2단 HP",
    "AlertLevel",
    "보스 페이즈",
    "데미지",
    "힐 플래시",
    "Vignette",
    "Desaturation",
    "CRITICAL",
    "P0",
    "P1",
    "P2",
    "P3",
    "CombatHUD",
    "take_damage",
    "heal",
    "set_boss_phase",
]


def test_hud_section_exists() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert "HP 바" in html
    assert "hud.py" in html


@pytest.mark.parametrize("term", REQUIRED_SECTIONS)
def test_hud_term_present(term: str) -> None:
    html = DASH.read_text(encoding="utf-8")
    assert term in html, f"HUD term '{term}' not in combat.html"


def test_hud_grid_css_defined() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert ".hud-grid" in html
    assert ".hud-card" in html
    assert ".hud-table" in html


def test_bar_demo_html() -> None:
    """The bar demo should show 2-tier HP/shield visual."""
    html = DASH.read_text(encoding="utf-8")
    assert ".bar-demo" in html
    assert "hp-low" in html
    assert "hp-crit" in html
    assert "shield" in html
    # Block characters
    assert "█" in html
    assert "▓" in html
    assert "░" in html
