"""Tests for combat VFX dashboard section (5-Layer system).

Validates that combat.html includes the new VFX visualization section
covering all 5 layers.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DASH = REPO_ROOT / "dashboard" / "combat.html"

REQUIRED_LAYERS: list[tuple[str, str]] = [
    ("Layer 1", "히트 플래시"),
    ("Layer 2", "15 스킬"),
    ("Layer 3", "ICE 타입"),
    ("Layer 4", "상태이상"),
    ("Layer 5", "시네마틱"),
]

REQUIRED_VFX_TERMS = [
    "히트 플래시",
    "플로팅 숫자",
    "히트 파티클",
    "스크린 셰이크",
    "ATTACK",
    "HEAVY_ATTACK",
    "PIERCE",
    "MULTI_HIT",
    "DOT",
    "SHIELD",
    "HEAL",
    "STUN",
    "LIFESTEAL",
    "COUNTER",
    "DETECT",
    "standard",
    "watchdog",
    "goliath",
    "black",
    "construct",
    "RAMPAGE",
    "콤보 카운터",
    "글리치",
    "슬로모션",
    "effects.py",
]


def test_combat_dashboard_exists() -> None:
    assert DASH.exists(), f"Combat dashboard not found at {DASH}"


LAYER_INDICES = list(range(len(REQUIRED_LAYERS)))


@pytest.mark.parametrize("layer_idx", LAYER_INDICES)
def test_layer_present(layer_idx: int) -> None:
    layer_id, layer_name = REQUIRED_LAYERS[layer_idx]
    html = DASH.read_text(encoding="utf-8")
    assert layer_id in html, f"Layer {layer_id} not in combat dashboard"
    assert layer_name in html, f"Layer {layer_name} description not in combat dashboard"


@pytest.mark.parametrize("term", REQUIRED_VFX_TERMS)
def test_vfx_term_present(term: str) -> None:
    html = DASH.read_text(encoding="utf-8")
    assert term in html, f"VFX term '{term}' not in combat dashboard"


def test_vfx_grid_css_defined() -> None:
    html = DASH.read_text(encoding="utf-8")
    assert ".vfx-grid" in html
    assert ".vfx-card" in html
    # Per-layer colors
    assert "layer1" in html
    assert "layer2" in html
    assert "layer3" in html
    assert "layer4" in html
    assert "layer5" in html
