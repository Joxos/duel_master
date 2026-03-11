import pytest

from duel_engine.battle import BattleFlow, DamageStep, DamageStepMachine


def test_damage_step_enum_contains_required_sub_steps():
    assert [step.name for step in DamageStep] == ["START", "CALC", "RESPONSE", "END"]


def test_damage_step_machine_advances_in_order():
    machine = DamageStepMachine()

    assert machine.current_step == DamageStep.START
    assert machine.advance_step() == DamageStep.CALC
    assert machine.advance_step() == DamageStep.RESPONSE
    assert machine.advance_step() == DamageStep.END


def test_damage_step_machine_rejects_advance_beyond_end():
    machine = DamageStepMachine(current_step=DamageStep.END)

    with pytest.raises(ValueError):
        machine.advance_step()


def test_damage_step_restrictions_allow_quick_only_in_response():
    machine = DamageStepMachine()

    assert not machine.can_activate("quick", DamageStep.START)
    assert not machine.can_activate("quick", DamageStep.CALC)
    assert machine.can_activate("quick", DamageStep.RESPONSE)
    assert not machine.can_activate("quick", DamageStep.END)


def test_damage_step_restrictions_allow_mandatory_trigger_in_all_sub_steps():
    machine = DamageStepMachine()

    assert all(machine.can_activate("mandatory_trigger", step) for step in DamageStep)


def test_declare_attack_resets_damage_step_and_stores_combatants():
    flow = BattleFlow(player_life_points={"p1": 8000, "p2": 8000})
    flow.damage_step_machine.advance_step()

    attacker = {"controller": "p1", "attack": 1900}
    defender = {"controller": "p2", "attack": 1500}
    flow.declare_attack(attacker=attacker, defender=defender)

    assert flow.attacker == attacker
    assert flow.defender == defender
    assert flow.damage_step_machine.current_step == DamageStep.START


def test_calculate_damage_for_monster_battle_assigns_difference_to_loser():
    flow = BattleFlow(player_life_points={"p1": 8000, "p2": 8000})
    flow.declare_attack(
        attacker={"controller": "p1", "attack": 1800},
        defender={"controller": "p2", "attack": 1200},
    )

    damage = flow.calculate_damage()

    assert damage == {"p1": 0, "p2": 600}


def test_calculate_damage_direct_attack_hits_defending_player_lp():
    flow = BattleFlow(player_life_points={"p1": 8000, "p2": 8000})
    flow.declare_attack(attacker={"controller": "p1", "attack": 2500}, defender=None)

    damage = flow.calculate_damage()

    assert damage == {"p1": 0, "p2": 2500}


def test_resolve_battle_applies_pending_damage_to_life_points():
    flow = BattleFlow(player_life_points={"p1": 8000, "p2": 8000})
    flow.declare_attack(
        attacker={"controller": "p1", "attack": 3000},
        defender={"controller": "p2", "attack": 1000},
    )
    flow.calculate_damage()

    life_points = flow.resolve_battle()

    assert life_points == {"p1": 8000, "p2": 6000}
    assert flow.pending_damage is None


def test_resolve_battle_requires_prior_damage_calculation():
    flow = BattleFlow(player_life_points={"p1": 8000, "p2": 8000})
    flow.declare_attack(attacker={"controller": "p1", "attack": 1000}, defender=None)

    with pytest.raises(ValueError):
        flow.resolve_battle()
