from openrpg_cli.rules.vitality import DamageInstance, DamageType, Defenses, Vitality, apply_damage, apply_healing, apply_temporary_hp


def test_damage_order_and_temp_hp() -> None:
    state = Vitality(20, 20, 3)
    result = apply_damage(state, (DamageInstance(5, DamageType.FIRE),), Defenses(resistances=frozenset({DamageType.FIRE})))
    assert result.state.current_hp == 20
    assert result.state.temporary_hp == 1
    assert result.transitions[0].adjusted == 2


def test_healing_and_temp_do_not_stack() -> None:
    state = apply_temporary_hp(Vitality(10, 0, 4, 1, 2), 3)
    healed = apply_healing(state, 99)
    assert (healed.current_hp, healed.temporary_hp, healed.death_successes, healed.death_failures) == (10, 4, 0, 0)
