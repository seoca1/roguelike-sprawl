"""Tests for hub panel data loading (P2 #12).

The Hub 4-panel layout (Avatar / Materials / Recipes / Job Board) was
loading hardcoded placeholder data. These tests verify the new
data-driven loaders with graceful fallback when JSON files are missing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from roguelike_sprawl.engine import config as _engine_config
from roguelike_sprawl.engine import hub


@pytest.fixture
def crafting_data_dir() -> Path:
    return _engine_config.DATA_DIR / "crafting"


class TestLoadMaterialsData:
    def test_loads_from_real_file(self, crafting_data_dir: Path) -> None:
        if not (crafting_data_dir / "materials.json").exists():
            pytest.skip("crafting/materials.json not in this checkout")
        data = hub._load_materials_data()
        assert len(data) >= 3
        for name, have, need in data:
            assert isinstance(name, str)
            assert name
            assert have == 0  # placeholder default; real value from inventory
            assert isinstance(need, int)
            assert need > 0

    def test_fallback_when_file_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Point to a directory without materials.json.
        fake_dir = Path("/nonexistent/path/for/test")
        monkeypatch.setattr(hub, "_engine_config", type("cfg", (), {"DATA_DIR": fake_dir})())
        data = hub._load_materials_data()
        assert data == hub._PLACEHOLDER_MATERIALS
        assert len(data) == 5

    def test_fallback_when_file_malformed(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        crafting = tmp_path / "crafting"
        crafting.mkdir()
        (crafting / "materials.json").write_text("{not json", encoding="utf-8")
        monkeypatch.setattr(hub, "_engine_config", type("cfg", (), {"DATA_DIR": tmp_path})())
        data = hub._load_materials_data()
        assert data == hub._PLACEHOLDER_MATERIALS


class TestLoadRecipesData:
    def test_loads_from_real_file(self, crafting_data_dir: Path) -> None:
        if not (crafting_data_dir / "recipes.json").exists():
            pytest.skip("crafting/recipes.json not in this checkout")
        data = hub._load_recipes_data()
        assert len(data) >= 3
        for name, glyph, ready in data:
            assert isinstance(name, str)
            assert name
            assert isinstance(glyph, str)
            assert glyph
            assert isinstance(ready, bool)

    def test_fallback_when_file_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fake_dir = Path("/nonexistent/path/for/test")
        monkeypatch.setattr(hub, "_engine_config", type("cfg", (), {"DATA_DIR": fake_dir})())
        data = hub._load_recipes_data()
        assert data == hub._PLACEHOLDER_RECIPES
        assert len(data) == 5

    def test_fallback_when_file_malformed(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        crafting = tmp_path / "crafting"
        crafting.mkdir()
        (crafting / "recipes.json").write_text("not valid json", encoding="utf-8")
        monkeypatch.setattr(hub, "_engine_config", type("cfg", (), {"DATA_DIR": tmp_path})())
        data = hub._load_recipes_data()
        assert data == hub._PLACEHOLDER_RECIPES


class TestMaterialInventoryLookup:
    def test_inventory_lookup_uses_snake_case_key(self) -> None:
        from roguelike_sprawl.engine.state import AppState

        state = AppState()
        state.inventory = {"ice_shard": 7, "data_fragment": 3, "unrelated": 99}

        # Material names in data → inventory keys (via _MATERIAL_NAME_TO_INV).
        have_ice = state.inventory.get(hub._MATERIAL_NAME_TO_INV.get("ICE Shard", "ice_shard"), 0)
        have_data = state.inventory.get(
            hub._MATERIAL_NAME_TO_INV.get("Data Fragment", "data_fragment"), 0
        )
        assert have_ice == 7
        assert have_data == 3
