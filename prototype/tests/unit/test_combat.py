"""Tests for the combat model and simulator (ADR-0003)."""

from __future__ import annotations

import random
from pathlib import Path

from roguelike_sprawl.combat import (
    Combatant,
    CombatState,
    IceRegistry,
    ProgramRegistry,
    build_default_player,
    build_ice_enemy,
    step_combat,
    use_skill,
)
from roguelike_sprawl.combat.state import AUTO_ATTACK_INTERVAL_MS, Skill, SkillEffect


def _enemy(max_hp: int, base_damage: int) -> Combatant:
    return Combatant(
        id="enemy",
        name="Test",
        portrait="▲ICE▲",
        color=(255, 0, 255),
        hp=max_hp,
        max_hp=max_hp,
        ap=0,
        max_ap=0,
        auto_attack_damage=base_damage,
        team="enemy",
    )


def test_combatant_creation() -> None:
    p = build_default_player(max_hp=100, max_ap=6, programs=ProgramRegistry({}))
    assert p.hp == 100
    assert p.max_hp == 100
    assert p.ap == 6
    assert p.team == "player"
    assert p.is_alive()


def test_combatant_take_damage() -> None:
    p = build_default_player(max_hp=50, max_ap=6, programs=ProgramRegistry({}))
    p.hp = 30
    assert p.is_alive()
    p.hp = 0
    assert not p.is_alive()


def test_step_combat_auto_attack() -> None:
    p = build_default_player(max_hp=100, max_ap=6, programs=ProgramRegistry({}))
    p.auto_attack_damage = 10
    e = _enemy(max_hp=80, base_damage=0)
    state = CombatState(player=p, enemy=e, rng=random.Random(0))
    for _ in range(AUTO_ATTACK_INTERVAL_MS // 100):
        step_combat(state)
    assert e.hp < 80
    assert "You hit" in state.log[-1] or len(state.log) > 0


def test_step_combat_enemy_attack() -> None:
    p = build_default_player(max_hp=100, max_ap=6, programs=ProgramRegistry({}))
    p.auto_attack_damage = 0
    e = _enemy(max_hp=80, base_damage=5)
    state = CombatState(player=p, enemy=e, rng=random.Random(0))
    for _ in range(AUTO_ATTACK_INTERVAL_MS // 100):
        step_combat(state)
    assert p.hp < 100
    assert any("Test hits you" in line for line in state.log)


def test_use_skill_attack() -> None:
    p = build_default_player(max_hp=100, max_ap=6, programs=ProgramRegistry({}))
    skill = Skill(
        id="goliath",
        name="Goliath",
        tier=3,
        effect=SkillEffect.ATTACK,
        ap_cost=3,
        damage=25,
    )
    p.skills = (skill,)
    e = _enemy(max_hp=80, base_damage=0)
    state = CombatState(player=p, enemy=e, rng=random.Random(0))
    used = use_skill(state, skill)
    assert used
    assert p.ap == 3
    # Damage has 80-120% variance
    assert 50 <= e.hp <= 60  # 25 dmg ±20% = 20-30
    assert "Goliath" in state.log[-1]


def test_use_skill_insufficient_ap() -> None:
    p = build_default_player(max_hp=100, max_ap=2, programs=ProgramRegistry({}))
    skill = Skill(id="goliath", name="Goliath", tier=3, effect="attack", ap_cost=3, damage=25)
    p.skills = (skill,)
    e = _enemy(max_hp=80, base_damage=0)
    state = CombatState(player=p, enemy=e, rng=random.Random(0))
    used = use_skill(state, skill)
    assert not used
    assert p.ap == 2
    assert e.hp == 80


def test_use_skill_shield() -> None:
    p = build_default_player(max_hp=100, max_ap=6, programs=ProgramRegistry({}))
    skill = Skill(
        id="wisp",
        name="Wisp",
        tier=1,
        effect=SkillEffect.SHIELD,
        ap_cost=2,
        shield=1,
    )
    p.skills = (skill,)
    e = _enemy(max_hp=80, base_damage=0)
    state = CombatState(player=p, enemy=e, rng=random.Random(0))
    use_skill(state, skill)
    assert state.shield == 1


def test_shield_absorbs_damage() -> None:
    p = build_default_player(max_hp=100, max_ap=6, programs=ProgramRegistry({}))
    e = _enemy(max_hp=80, base_damage=5)
    state = CombatState(player=p, enemy=e, rng=random.Random(0))
    state.shield = 10
    for _ in range(AUTO_ATTACK_INTERVAL_MS // 100):
        step_combat(state)
    # Shield reduced (exact amount varies due to 80-120% damage variance)
    assert state.shield < 10  # Some shield absorbed
    assert p.hp == 100  # Player took no damage (all absorbed)


def test_victory_condition() -> None:
    p = build_default_player(max_hp=100, max_ap=6, programs=ProgramRegistry({}))
    p.auto_attack_damage = 100
    e = _enemy(max_hp=10, base_damage=0)
    state = CombatState(player=p, enemy=e, rng=random.Random(0))
    for _ in range(AUTO_ATTACK_INTERVAL_MS // 100):
        step_combat(state)
    assert state.finished
    assert state.outcome == "victory"


def test_defeat_condition() -> None:
    p = build_default_player(max_hp=10, max_ap=0, programs=ProgramRegistry({}))
    p.auto_attack_damage = 0
    e = _enemy(max_hp=80, base_damage=100)
    state = CombatState(player=p, enemy=e, rng=random.Random(0))
    for _ in range(AUTO_ATTACK_INTERVAL_MS // 100):
        step_combat(state)
    assert state.finished
    assert state.outcome == "defeat"


def test_step_combat_after_finished_no_op() -> None:
    p = build_default_player(max_hp=10, max_ap=0, programs=ProgramRegistry({}))
    p.auto_attack_damage = 0
    e = _enemy(max_hp=1, base_damage=100)
    state = CombatState(player=p, enemy=e, rng=random.Random(0))
    for _ in range(AUTO_ATTACK_INTERVAL_MS // 100):
        step_combat(state)
    assert state.finished
    enemy_hp_before = e.hp
    tick_before = state.tick_ms
    step_combat(state)
    assert e.hp == enemy_hp_before
    assert state.tick_ms == tick_before


def test_program_registry_loads(data_dir: Path) -> None:
    reg = ProgramRegistry.load(data_dir / "programs" / "programs.json")
    assert len(reg) >= 3
    wisp = reg.get("wisp")
    assert wisp is not None
    # Effect should be a valid SkillEffect enum
    assert wisp.effect in SkillEffect
    assert wisp.shield >= 0


def test_ice_registry_loads(data_dir: Path) -> None:
    reg = IceRegistry.load(data_dir / "combat" / "ice_types.json")
    assert "standard" in reg
    assert "black" in reg
    standard = reg.get("standard")
    assert standard is not None
    assert int(standard["hp_base"]) == 80


def test_build_ice_enemy(data_dir: Path) -> None:
    ice = IceRegistry.load(data_dir / "combat" / "ice_types.json")
    e = build_ice_enemy("standard", ice)
    assert e.name == "ICE — Standard"
    assert e.hp == 80
    assert e.team == "enemy"


def test_build_ice_enemy_scaled(data_dir: Path) -> None:
    ice = IceRegistry.load(data_dir / "combat" / "ice_types.json")
    e_g1 = build_ice_enemy("standard", ice, player_grade=1)
    assert e_g1.hp == 80
    e_g3 = build_ice_enemy("standard", ice, player_grade=3)
    assert e_g3.hp == 80 + (15 * 2)
    e_g5 = build_ice_enemy("standard", ice, player_grade=5)
    assert e_g5.hp == 80 + (15 * 4)


def test_log_capped_at_6() -> None:
    p = build_default_player(max_hp=100, max_ap=6, programs=ProgramRegistry({}))
    p.skills = (Skill(id="g", name="G", tier=1, effect="attack", ap_cost=1, damage=1),)
    e = _enemy(max_hp=80, base_damage=0)
    state = CombatState(player=p, enemy=e, rng=random.Random(0))
    for _ in range(10):
        use_skill(state, p.skills[0])
    assert len(state.log) <= 6


def test_construct_data_shape(data_dir: Path) -> None:
    ice = IceRegistry.load(data_dir / "combat" / "ice_types.json")
    for ice_id in ("standard", "watchdog", "black", "goliath", "dixie"):
        data = ice.get(ice_id)
        assert data is not None
        assert "hp_base" in data
        assert "dmg_base" in data
        assert int(data["hp_base"]) > 0
        assert int(data["dmg_base"]) >= 0


def test_ap_regen() -> None:
    p = build_default_player(max_hp=100, max_ap=6, programs=ProgramRegistry({}))
    p.ap = 0
    e = _enemy(max_hp=200, base_damage=0)
    state = CombatState(player=p, enemy=e, rng=random.Random(0))
    for _ in range(70):
        step_combat(state)
    assert p.ap >= 3
