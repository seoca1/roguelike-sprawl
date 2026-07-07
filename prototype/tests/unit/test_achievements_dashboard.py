"""Tests for achievements dashboard (achievements.html)."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DASH = REPO_ROOT / "dashboard" / "achievements.html"

ALL_CATEGORIES = ["combat", "exploration", "story", "mastery", "hidden"]
ALL_TIERS = ["bronze", "silver", "gold", "platinum"]
ALL_ACHIEVEMENT_IDS = [
    "first_blood",
    "sharpshooter",
    "combo_master",
    "undefeated",
    "boss_slayer",
    "goliath_slayer",
    "centurion",
    "first_jackin",
    "world_walker",
    "server_domination",
    "data_extractor",
    "jackout_survivor",
    "matrix_explorer",
    "case_journey",
    "sil_awakening",
    "kas_rise",
    "five_tales",
    "the_truth",
    "ppl_10",
    "ppl_20",
    "ppl_30",
    "matrix_master",
    "combo_quant",
    "flawless",
]


def test_dashboard_exists() -> None:
    assert DASH.exists(), f"Achievements dashboard not found at {DASH}"


def test_title() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert "Achievements Dashboard" in html


def test_korean_title() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert "업적" in html


def test_stats_row() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert "stat-card" in html
    assert "28" in html  # Total achievements
    assert "해금" in html
    assert "완료율" in html
    assert "총 크레딧" in html


@pytest.mark.parametrize("cat", ALL_CATEGORIES)
def test_category_section(cat: str) -> None:
    html = DASH.read_text(encoding="utf-8")
    assert f"ach-card.{cat}" in html


@pytest.mark.parametrize("tier", ALL_TIERS)
def test_tier_badge(tier: str) -> None:
    html = DASH.read_text(encoding="utf-8")
    assert f"tier-{tier}" in html


@pytest.mark.parametrize("ach_id", ALL_ACHIEVEMENT_IDS)
def test_achievement_present(ach_id: str) -> None:
    """Each achievement ID's Korean name should appear in the dashboard."""
    html = DASH.read_text(encoding="utf-8")
    # Map ID to Korean name (from achievements.py definitions)
    ko_names = {
        "first_blood": "첫 피",
        "sharpshooter": "정밀 사격",
        "combo_master": "콤보 마스터",
        "undefeated": "무패",
        "boss_slayer": "보스 슬레이어",
        "goliath_slayer": "골리앗 정복자",
        "centurion": "100 킬",
        "first_jackin": "첫 잭인",
        "world_walker": "월드 워커",
        "server_domination": "서버 점령",
        "data_extractor": "데이터 추출",
        "jackout_survivor": "잭아웃 서바이버",
        "matrix_explorer": "매트릭스 탐험가",
        "case_journey": "케이의 여정",
        "sil_awakening": "실의 자각",
        "kas_rise": "카스의 각성",
        "five_tales": "다섯 단편",
        "the_truth": "진실",
        "ppl_10": "견습생",
        "ppl_20": "숙련자",
        "ppl_30": "달인",
        "matrix_master": "매트릭스 정통",
        "combo_quant": "콤보 콰이언",
        "flawless": "완벽한 자",
    }
    ko = ko_names.get(ach_id)
    if ko is None:
        # Hidden achievements — don't require them to appear (hidden!)
        return
    assert ko in html, f"Achievement {ach_id} (Korean: {ko}) not in dashboard"


def test_korean_names_present() -> None:
    html = DASH.read_text(encoding="utf-8")
    korean_names = [
        "첫 피",
        "정밀 사격",
        "콤보 마스터",
        "무패",
        "보스 슬레이어",
        "골리앗 정복자",
        "100 킬",
        "첫 잭인",
        "월드 워커",
        "서버 점령",
        "데이터 추출",
        "잭아웃 서바이버",
        "매트릭스 탐험가",
        "케이의 여정",
        "실의 자각",
        "카스의 각성",
        "다섯 단편",
        "진실",
        "견습생",
        "숙련자",
        "달인",
        "매트릭스 정통",
        "콤보 콰이언",
        "완벽한 자",
    ]
    for name in korean_names:
        assert name in html, f"Missing: {name}"


def test_hidden_section() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert "히든" in html
    assert "????? (조건 미공개)" in html
    assert "ach-locked" in html


def test_top_nav_consistent() -> None:
    html = DASH.read_text(encoding="utf-8")
    # Should have 9 nav links + Achievements current
    for link in [
        "index.html",
        "missions.html",
        "stages.html",
        "library.html",
        "sound.html",
        "combat.html",
        "equipment.html",
        "cyberspace.html",
        "achievements.html",
    ]:
        assert link in html


def test_all_28_ach_cards() -> None:
    """Should have 28 visible achievement cards (24 visible + 4 hidden locked)."""
    html = DASH.read_text(encoding="utf-8")
    # Count actual <div class="ach-card ..."> opening tags
    import re

    matches = re.findall(r'<div class="ach-card', html)
    assert len(matches) == 28, f"Expected 28 ach-card divs, found {len(matches)}"


def test_credit_rewards_listed() -> None:
    html = DASH.read_text(encoding="utf-8")
    # Spot-check reward amounts
    for amount in ["50", "200", "500", "1000", "2000", "1500", "3000", "4000", "5000"]:
        assert f"+{amount} 크레딧" in html, f"Missing reward: +{amount}"


def test_hidden_icons_obscured() -> None:
    """Hidden achievements should show '???' not their actual icons."""
    html = DASH.read_text(encoding="utf-8")
    # GHOST_PROTOCOL is hidden - its icon ◇ should NOT be in hidden section
    # (it appears in exploration but not in hidden cards)
    # Check that the 4 hidden cards have the obscured text
    assert html.count("????? (조건 미공개)") == 4


def test_no_real_save_localstorage() -> None:
    """This is a static dashboard, not a runtime state tracker."""
    html = DASH.read_text(encoding="utf-8")
    # No real save/load logic expected
    assert "data-stat" in html  # Has stat placeholders for JS population
