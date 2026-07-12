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


def test_start_combat_uses_node_ice_kind(data_dir: Path) -> None:
    """Regression: combat_view.start_combat must use ice_node.ice to pick
    the enemy, not hardcoded 'standard'. Pre-fix: every node spawned the
    same Standard ICE regardless of node.ice value.
    """
    from roguelike_sprawl.engine import combat_view
    from roguelike_sprawl.engine.state import AppState
    from roguelike_sprawl.matrix.node import IceKind, Node, NodeKind, ZoneDepth

    ice_reg = IceRegistry.load(data_dir / "combat" / "ice_types.json")
    prog_reg = ProgramRegistry.load(data_dir / "programs" / "programs.json")

    # Black ICE node → should spawn black enemy, not standard
    black_node = Node(
        id="ice_black_test",
        kind=NodeKind.ICE,
        label="Black ICE",
        zone=ZoneDepth.CORE,
        ice=IceKind.BLACK,
    )
    state = AppState()
    cs = combat_view.start_combat(state, black_node, prog_reg, ice_reg)
    assert "Black" in cs.enemy.name, f"Expected Black ICE, got {cs.enemy.name!r}"

    # Watchdog node → should spawn watchdog enemy
    watchdog_node = Node(
        id="ice_watchdog_test",
        kind=NodeKind.ICE,
        label="Watchdog",
        zone=ZoneDepth.MID,
        ice=IceKind.WATCHDOG,
    )
    state2 = AppState()
    cs2 = combat_view.start_combat(state2, watchdog_node, prog_reg, ice_reg)
    assert "Watchdog" in cs2.enemy.name, f"Expected Watchdog ICE, got {cs2.enemy.name!r}"


def test_all_mission_ice_ids_resolve(data_dir: Path) -> None:
    """Regression: every ``ice.<X>`` referenced by a mission must exist
    in the ICE registry. Pre-fix: 10 references (construct, boss,
    revelation, neuromancer, ai_whisper, surveillance, wintermute,
    zion_defense) silently failed at runtime — added in this session.
    """
    import json

    ice_reg = IceRegistry.load(data_dir / "combat" / "ice_types.json")
    with (data_dir / "missions" / "missions.json").open(encoding="utf-8") as f:
        missions = json.load(f)

    missing: list[str] = []
    for mid, m in missions.items():
        for obj in [m.get("primary_objective", {})] + m.get("secondary_objectives", []):
            enemy = obj.get("enemy", "")
            if enemy.startswith("ice."):
                ice_id = enemy[len("ice.") :]
                if ice_reg.get(ice_id) is None:
                    missing.append(f"{mid}: {enemy} (resolved {ice_id!r})")

    assert not missing, "Mission ICE references missing from registry:\n" + "\n".join(
        f"  {m}" for m in missing
    )


def test_ap_regen() -> None:
    p = build_default_player(max_hp=100, max_ap=6, programs=ProgramRegistry({}))
    p.ap = 0
    e = _enemy(max_hp=200, base_damage=0)
    state = CombatState(player=p, enemy=e, rng=random.Random(0))
    for _ in range(70):
        step_combat(state)
    assert p.ap >= 3


def test_vfx_overlay_no_afterimage() -> None:
    """Regression: hit flash must not leave afterimages when expired.

    Before fix: _draw_vfx_overlay only printed at sparse cells (x+y)%3==0,
    and console.print only set fg (not bg). After flash expired, the colored
    cells remained visible as ghost images (afterimages).

    After fix: _draw_vfx_overlay clears the entire region with bg=0 before
    drawing any effects, preventing afterimages.
    """
    import tcod.console

    from roguelike_sprawl.combat.effects import CombatEffects
    from roguelike_sprawl.engine.combat_view import _draw_vfx_overlay
    from roguelike_sprawl.engine.layout import Region, RegionId

    console = tcod.console.Console(30, 20)
    region = Region(id=RegionId.MAIN, x=5, y=3, w=20, h=14)

    # Phase 1: render with hit flash ACTIVE
    fx = CombatEffects()
    fx.hit_flash.trigger(color=(255, 255, 255), duration_ms=120)
    _draw_vfx_overlay(console, region, fx, 0, 0)

    # Count flash cells
    flash_count_active = sum(
        1
        for y in range(region.y, region.y + region.h)
        for x in range(region.x, region.x + region.w)
        if chr(console.ch[y, x]) == "█"
    )
    assert flash_count_active > 0, "Hit flash should render some cells"

    # Phase 2: advance time so flash expires, then re-render
    fx.step(200)  # 200ms > 120ms duration
    assert not fx.hit_flash.is_active, "Hit flash should be expired"

    _draw_vfx_overlay(console, region, fx, 0, 0)

    # Phase 3: verify no flash cells remain (afterimage bug is fixed)
    flash_count_after = sum(
        1
        for y in range(region.y, region.y + region.h)
        for x in range(region.x, region.x + region.w)
        if chr(console.ch[y, x]) == "█"
    )
    assert flash_count_after == 0, (
        f"Afterimage bug: {flash_count_after} flash cells remain after expiry. "
        "The overlay region should be cleared before re-drawing."
    )
