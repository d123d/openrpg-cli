from openrpg_cli.rules.effects import CONDITION_REGISTRY, Condition, DurationKind, Effect, Phase, add_effect, advance


def test_registry_and_scheduler_order_idempotence() -> None:
    assert set(CONDITION_REGISTRY) == set(Condition)
    effect = Effect("b", "s", "t", Condition.BLINDED, 0, duration=DurationKind.FIXED, end_tick=1)
    state = add_effect((), effect)
    state, due = advance(state, 0, Phase.START)
    state2, repeated = advance(state, 0, Phase.START)
    assert [x.kind for x in due] == ["due"]
    assert repeated == ()
    assert state2 == state


def test_due_precedes_expiry() -> None:
    effect = Effect("a", "s", "t", Condition.POISONED, 0, end_tick=0, end_phase=Phase.START)
    state, transitions = advance((effect,), 0, Phase.START)
    assert state == ()
    assert [x.kind for x in transitions] == ["due", "expired"]
