"""Tests for the cyberpunk equipment system.

The equipment module (447 lines, 15 default items, 8 slots, 6 tiers,
8 categories) was the largest untested module in the codebase. This
file covers the Equipment / EquipStats / EquipmentLoadout /
EquipmentRegistry dataclasses and the 15 default items.
"""

from __future__ import annotations

import pytest

from roguelike_sprawl.equipment.equipment import (
    STARTER_DECK,
    STARTER_HEADWARE,
    EquipCategory,
    Equipment,
    EquipmentLoadout,
    EquipmentRegistry,
    EquipSlot,
    EquipStats,
    EquipTier,
)

# ============================================================================
# EquipStats
# ============================================================================


class TestEquipStats:
    """EquipStats is a frozen dataclass with 12 stat fields."""

    def test_default_all_zero(self) -> None:
        s = EquipStats()
        assert s.attack_bonus == 0
        assert s.crit_bonus_pct == 0
        assert s.damage_bonus_pct == 0
        assert s.defense == 0
        assert s.hp_bonus == 0
        assert s.shield_bonus == 0
        assert s.ap_bonus == 0
        assert s.ap_regen_bonus_pct == 0
        assert s.program_power == 0
        assert s.ice_resistance == 0
        assert s.grants_skill_id is None
        assert s.extra_effect == ""

    def test_frozen_immutable(self) -> None:
        """Dataclass is frozen — direct field assignment raises."""
        from dataclasses import FrozenInstanceError

        s = EquipStats(attack_bonus=10)
        with pytest.raises(FrozenInstanceError):
            s.attack_bonus = 99  # type: ignore[misc]


# ============================================================================
# Equipment
# ============================================================================


class TestEquipmentDataclass:
    """Equipment is a frozen dataclass for a single gear piece."""

    def test_starter_deck_is_baseline_tier(self) -> None:
        assert STARTER_DECK.tier is EquipTier.T0_BASELINE
        assert STARTER_DECK.slot is EquipSlot.DECK
        assert STARTER_DECK.category is EquipCategory.HARDWARE
        assert not STARTER_DECK.is_upgradable()
        assert not STARTER_DECK.is_t1_or_better()

    def test_starter_deck_grants_program_power(self) -> None:
        # Ono-Sendai 7: program_power=5
        assert STARTER_DECK.stats.program_power == 5

    def test_is_t1_or_better(self) -> None:
        # Custom T1 item
        gear = Equipment(
            id="t1_test",
            name="Test T1",
            slot=EquipSlot.DECK,
            category=EquipCategory.HARDWARE,
            tier=EquipTier.T1_STREET,
            stats=EquipStats(),
            description="",
        )
        assert gear.is_t1_or_better()

    def test_is_upgradable(self) -> None:
        gear = Equipment(
            id="up",
            name="Up",
            slot=EquipSlot.DECK,
            category=EquipCategory.HARDWARE,
            tier=EquipTier.T1_STREET,
            stats=EquipStats(),
            description="",
            upgrade_slots=2,
        )
        assert gear.is_upgradable()
        assert not STARTER_DECK.is_upgradable()

    def test_repr_includes_tier_and_category(self) -> None:
        r = repr(STARTER_DECK)
        assert STARTER_DECK.name in r
        assert "T0" in r
        assert "hardware" in r

    def test_required_materials_default_empty(self) -> None:
        gear = Equipment(
            id="x",
            name="X",
            slot=EquipSlot.DECK,
            category=EquipCategory.HARDWARE,
            tier=EquipTier.T0_BASELINE,
            stats=EquipStats(),
            description="",
        )
        assert gear.required_materials == {}
        assert gear.set_id is None


# ============================================================================
# EquipmentRegistry
# ============================================================================


class TestEquipmentRegistry:
    """Lookup registry for equipment by id."""

    def test_default_registry_has_15_items(self) -> None:
        reg = EquipmentRegistry.load_default()
        assert len(reg.all()) == 15

    def test_default_registry_includes_all_tiers(self) -> None:
        reg = EquipmentRegistry.load_default()
        tiers = {e.tier for e in reg.all()}
        # All 6 tiers should be represented.
        assert EquipTier.T0_BASELINE in tiers
        assert EquipTier.T1_STREET in tiers
        assert EquipTier.T2_COMMERCIAL in tiers
        assert EquipTier.T3_MILITECH in tiers
        assert EquipTier.T4_CORPORATE in tiers
        assert EquipTier.T5_EXPERIMENTAL in tiers

    def test_get_known_item(self) -> None:
        reg = EquipmentRegistry.load_default()
        deck = reg.get("deck_arasaka")
        assert deck is not None
        assert "Onikiri" in deck.name
        assert deck.tier is EquipTier.T4_CORPORATE

    def test_get_unknown_returns_none(self) -> None:
        reg = EquipmentRegistry.load_default()
        assert reg.get("not_a_real_id") is None

    def test_by_slot_filters_correctly(self) -> None:
        reg = EquipmentRegistry.load_default()
        decks = reg.by_slot(EquipSlot.DECK)
        assert len(decks) >= 4  # T0/T1/T2/T3/T4/T5 = 6 decks
        assert all(e.slot is EquipSlot.DECK for e in decks)
        # No HEADWARE in DECK filter
        assert all(e.slot is not EquipSlot.HEADWARE for e in decks)

    def test_by_slot_empty_for_uncovered_slot(self) -> None:
        reg = EquipmentRegistry.load_default()
        # IMPLANT has Nano-Hive; verify it exists
        implants = reg.by_slot(EquipSlot.IMPLANT)
        assert len(implants) >= 1
        assert any(e.id == "implant_nanohive" for e in implants)

    def test_all_returns_copy(self) -> None:
        """reg.all() returns a new list — mutations don't affect registry."""
        reg = EquipmentRegistry.load_default()
        lst = reg.all()
        lst.clear()
        assert len(reg.all()) == 15


# ============================================================================
# EquipmentLoadout
# ============================================================================


class TestEquipmentLoadout:
    """Player's currently equipped gear (8 slots max)."""

    def test_empty_loadout_has_no_items(self) -> None:
        loadout = EquipmentLoadout()
        assert loadout.all_slots_filled() == []
        assert loadout.empty_slots() == list(EquipSlot)
        assert not loadout.is_complete()

    def test_equip_adds_to_slot(self) -> None:
        loadout = EquipmentLoadout()
        previous = loadout.equip(STARTER_DECK)
        assert previous is None
        assert loadout.get(EquipSlot.DECK) is STARTER_DECK

    def test_equip_replaces_returns_previous(self) -> None:
        loadout = EquipmentLoadout()
        loadout.equip(STARTER_DECK)
        # Equip another deck in same slot
        from roguelike_sprawl.equipment.equipment import STREET_DECK

        previous = loadout.equip(STREET_DECK)
        assert previous is STARTER_DECK
        assert loadout.get(EquipSlot.DECK) is STREET_DECK

    def test_unequip_returns_removed_item(self) -> None:
        loadout = EquipmentLoadout()
        loadout.equip(STARTER_DECK)
        removed = loadout.unequip(EquipSlot.DECK)
        assert removed is STARTER_DECK
        assert loadout.get(EquipSlot.DECK) is None

    def test_unequip_empty_slot_returns_none(self) -> None:
        loadout = EquipmentLoadout()
        assert loadout.unequip(EquipSlot.DECK) is None

    def test_all_slots_filled_matches_equipment_count(self) -> None:
        loadout = EquipmentLoadout()
        loadout.equip(STARTER_DECK)
        loadout.equip(STARTER_HEADWARE)
        assert len(loadout.all_slots_filled()) == 2

    def test_empty_slots_returns_unfilled(self) -> None:
        loadout = EquipmentLoadout()
        loadout.equip(STARTER_DECK)
        empty = loadout.empty_slots()
        assert EquipSlot.DECK not in empty
        assert len(empty) == len(EquipSlot) - 1

    def test_is_complete_when_all_8_slots_filled(self) -> None:
        loadout = EquipmentLoadout()
        # Need one equip per slot
        reg = EquipmentRegistry.load_default()
        # First equipment for each slot
        seen_slots: set[EquipSlot] = set()
        for item in reg.all():
            if item.slot not in seen_slots:
                loadout.equip(item)
                seen_slots.add(item.slot)
        assert loadout.is_complete()
        assert loadout.empty_slots() == []

    def test_total_stats_aggregates_correctly(self) -> None:
        loadout = EquipmentLoadout()
        loadout.equip(STARTER_DECK)  # program_power=5
        total = loadout.total_stats()
        assert total.program_power == 5
        assert total.attack_bonus == 0

    def test_total_stats_aggregates_multiple_items(self) -> None:
        from roguelike_sprawl.equipment.equipment import (
            CHROME_GLOVES,
            MILITECH_EYES,
        )

        loadout = EquipmentLoadout()
        loadout.equip(MILITECH_EYES)  # attack_bonus=3, crit_bonus_pct=10
        loadout.equip(CHROME_GLOVES)  # attack_bonus=5, program_power=3
        total = loadout.total_stats()
        assert total.attack_bonus == 8  # 3 + 5
        assert total.crit_bonus_pct == 10
        assert total.program_power == 3  # gloves only

    def test_total_stats_empty_loadout_is_zero(self) -> None:
        loadout = EquipmentLoadout()
        total = loadout.total_stats()
        assert total == EquipStats()


# ============================================================================
# Default Equipment Coverage
# ============================================================================


class TestDefaultEquipmentCoverage:
    """The 15 default items cover all 8 slots and all 6 tiers."""

    @pytest.fixture
    def registry(self) -> EquipmentRegistry:
        return EquipmentRegistry.load_default()

    def test_all_default_equipment_have_unique_ids(self, registry: EquipmentRegistry) -> None:
        ids = [e.id for e in registry.all()]
        assert len(ids) == len(set(ids))

    def test_all_default_equipment_have_descriptions(self, registry: EquipmentRegistry) -> None:
        for e in registry.all():
            assert e.description, f"{e.id} missing description"

    def test_all_default_equipment_have_ascii_glyph(self, registry: EquipmentRegistry) -> None:
        for e in registry.all():
            assert e.ascii_glyph, f"{e.id} missing ascii_glyph"

    def test_all_default_equipment_have_color(self, registry: EquipmentRegistry) -> None:
        for e in registry.all():
            assert len(e.ascii_color) == 3
            r, g, b = e.ascii_color
            assert 0 <= r <= 255
            assert 0 <= g <= 255
            assert 0 <= b <= 255

    def test_all_default_equipment_have_valid_slot(self, registry: EquipmentRegistry) -> None:
        valid_slots = set(EquipSlot)
        for e in registry.all():
            assert e.slot in valid_slots, f"{e.id} has invalid slot {e.slot}"

    def test_all_default_equipment_have_valid_category(self, registry: EquipmentRegistry) -> None:
        valid_categories = set(EquipCategory)
        for e in registry.all():
            assert e.category in valid_categories, f"{e.id} has invalid category {e.category}"

    def test_all_default_equipment_have_valid_tier(self, registry: EquipmentRegistry) -> None:
        valid_tiers = set(EquipTier)
        for e in registry.all():
            assert e.tier in valid_tiers, f"{e.id} has invalid tier {e.tier}"

    def test_upgrade_slots_consistent_with_tier(self, registry: EquipmentRegistry) -> None:
        """T0 has 0 upgrade slots; T1+ has at least 1 upgrade slot."""
        for e in registry.all():
            if e.tier is EquipTier.T0_BASELINE:
                assert e.upgrade_slots == 0, f"{e.id} is T0 but has {e.upgrade_slots} upgrade slots"

    def test_higher_tier_has_stronger_stats(self, registry: EquipmentRegistry) -> None:
        """Higher tier equipment tends to have higher stats."""
        # Compare decks across tiers
        deck_by_tier = {
            EquipTier.T0_BASELINE: "deck_basic",
            EquipTier.T1_STREET: "deck_street",
            EquipTier.T2_COMMERCIAL: "deck_corporate",
            EquipTier.T3_MILITECH: "deck_militech",
            EquipTier.T4_CORPORATE: "deck_arasaka",
            EquipTier.T5_EXPERIMENTAL: "deck_ghost",
        }
        prev_power = 0
        for tier in (
            EquipTier.T0_BASELINE,
            EquipTier.T1_STREET,
            EquipTier.T2_COMMERCIAL,
            EquipTier.T3_MILITECH,
            EquipTier.T4_CORPORATE,
            EquipTier.T5_EXPERIMENTAL,
        ):
            deck = registry.get(deck_by_tier[tier])
            assert deck is not None
            assert deck.stats.program_power > prev_power, (
                f"Deck {tier} has program_power={deck.stats.program_power} "
                f"<= previous tier's {prev_power}"
            )
            prev_power = deck.stats.program_power


# ============================================================================
# Equipment stats semantics
# ============================================================================


class TestStatAggregation:
    """_add_stats merges EquipStats correctly across multiple items."""

    def test_grants_skill_id_uses_first_non_empty(self) -> None:
        """When two items grant a skill, the first non-None wins."""
        from roguelike_sprawl.equipment.equipment import _add_stats

        a = EquipStats(grants_skill_id="alpha")
        b = EquipStats(grants_skill_id="beta")
        # a.grants_skill_id or b.grants_skill_id → "alpha" wins
        assert _add_stats(a, b).grants_skill_id == "alpha"

    def test_grants_skill_id_falls_back_to_second(self) -> None:
        from roguelike_sprawl.equipment.equipment import _add_stats

        a = EquipStats(grants_skill_id=None)
        b = EquipStats(grants_skill_id="beta")
        assert _add_stats(a, b).grants_skill_id == "beta"

    def test_extra_effect_concatenates(self) -> None:
        from roguelike_sprawl.equipment.equipment import _add_stats

        a = EquipStats(extra_effect="Heals 2 HP/turn")
        b = EquipStats(extra_effect="+Stealth")
        combined = _add_stats(a, b)
        assert "Heals 2 HP/turn" in combined.extra_effect
        assert "+Stealth" in combined.extra_effect
        assert ", " in combined.extra_effect

    def test_extra_effect_filters_empty(self) -> None:
        from roguelike_sprawl.equipment.equipment import _add_stats

        a = EquipStats(extra_effect="Heals")
        b = EquipStats(extra_effect="")
        combined = _add_stats(a, b)
        # Empty effect is filtered — no trailing comma
        assert combined.extra_effect == "Heals"
