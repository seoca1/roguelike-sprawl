"""Tests for stage UI dashboard section in combat.html.

Validates that combat.html includes the new stage UI components:
- Stage avatars (5 unique icons)
- Timing bar (3 color tiers)
- Combo finishers (3 special moves)
- Full combo HUD preview
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DASH = REPO_ROOT / "dashboard" / "combat.html"

AVATAR_ICONS = ["◦", "⫶", "⚡", "☠", "✦"]
STAGE_NAMES = ["WARMUP", "CHAIN", "FLURRY", "RAMPAGE", "ANNIHILATION"]
FINISHER_IDS = ["quick_slash", "rampage_burst", "final_strike"]
FINISHER_ENGLISH_NAMES = ["QUICK SLASH", "RAMPAGE BURST", "FINAL STRIKE"]


def test_stage_ui_section_exists() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert "스테이지 UI" in html
    assert "Stage Avatar" in html
    assert "Timing Bar" in html
    assert "콤보 필살기" in html


@pytest.mark.parametrize("icon", AVATAR_ICONS)
def test_avatar_icon_present(icon: str) -> None:
    html = DASH.read_text(encoding="utf-8")
    assert icon in html


@pytest.mark.parametrize("name", STAGE_NAMES)
def test_avatar_stage_name_present(name: str) -> None:
    html = DASH.read_text(encoding="utf-8")
    assert name in html


def test_avatar_css_grid() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert ".avatar-grid" in html
    assert ".avatar-card" in html
    assert ".avatar-icon" in html
    assert ".avatar-frames" in html


def test_timing_bar_section() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert "타이밍 바" in html
    assert ".timing-demo" in html
    assert ".timing-row" in html
    # 3 color tiers
    for tier_class in ["timing-row", "timing-row.warn", "timing-row.urgent"]:
        assert tier_class in html


def test_timing_bar_3_tiers_in_css() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert "100%" in html
    assert "57%" in html or "70%" in html
    assert "20%" in html


@pytest.mark.parametrize("finisher_id", FINISHER_IDS)
def test_finisher_id_present(finisher_id: str) -> None:
    html = DASH.read_text(encoding="utf-8")
    # Some finishers may use snake_case, some use the English name
    # Just check that either the ID or the English name is present
    english_name = finisher_id.replace("_", " ").upper()
    assert finisher_id in html or english_name in html


@pytest.mark.parametrize("english_name", FINISHER_ENGLISH_NAMES)
def test_finisher_english_name_present(english_name: str) -> None:
    html = DASH.read_text(encoding="utf-8")
    assert english_name in html


def test_finisher_korean_names() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert "빠른 참격" in html
    assert "섬멸 폭발" in html
    assert "최후의 일격" in html


def test_finisher_damage_multipliers() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert "×2.0" in html
    assert "×3.0" in html
    assert "×5.0" in html


def test_finisher_cooldowns() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert "CD 5초" in html
    assert "CD 8초" in html
    assert "CD 12초" in html


def test_finisher_grid_css() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert ".finisher-grid" in html
    assert ".finisher-card" in html
    assert ".finisher-kr" in html


def test_hud_preview_section() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert "풀 콤보 HUD" in html or "실제 출력" in html
    assert ".hud-preview" in html
    assert ".hud-frame" in html


def test_hud_preview_examples() -> None:
    """3 example frames showing different stages."""
    html = DASH.read_text(encoding="utf-8")
    assert "FLURRY" in html
    assert "RAMPAGE" in html
    assert "ANNIHILATION" in html
    # Examples should include the counter text
    assert "4x FLURRY" in html
    assert "5x RAMPAGE" in html
    assert "6x ANNIHILATION" in html
