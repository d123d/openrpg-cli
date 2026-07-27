# ruff: noqa: F403, F405
from openrpg_cli.engine.rng import GameRNG
from openrpg_cli.rules.actions import *  # noqa: F403, F405
from openrpg_cli.rules.space import *  # noqa: F403, F405
from openrpg_cli.rules.turns import *  # noqa: F403, F405


def setup():
    order = TurnOrder((InitiativeEntry("a", "x", 10, 0, 10), InitiativeEntry("b", "y", 5, 0, 5)))
    return (
        TurnState(order),
        ActionBudget(),
        SpatialState(("a", "b"), (RelativePosition("a", "b", RangeBand.NEAR),)),
    )


def test_catalog_exact_and_actions():
    assert {x.value for x in CoreAction} == {
        "attack",
        "magic",
        "dash",
        "disengage",
        "dodge",
        "help",
        "hide",
        "influence",
        "ready",
        "search",
        "study",
        "utilize",
    }
    turn, budget, space = setup()
    out, rng = resolve_action(
        ActionRequest(CoreAction.ATTACK, "a", ("b",)),
        turn,
        budget,
        space,
        GameRNG(1),
        {"a": "x", "b": "y"},
    )
    assert out.accepted and out.budget.action == 0 and rng.draws == 0
    bad, _ = resolve_action(
        ActionRequest(CoreAction.ATTACK, "b", ("a",)), turn, budget, space, GameRNG(1)
    )
    assert not bad.accepted and bad.budget == budget


def test_ready_and_dash():
    turn, budget, space = setup()
    out, _ = resolve_action(
        ActionRequest(CoreAction.READY, "a", trigger=TriggerKind.LEAVE_REACH),
        turn,
        budget,
        space,
        GameRNG(2),
    )
    assert out.ready
    b, reason = trigger_ready(out.ready, TriggerKind.LEAVE_REACH, budget)
    assert reason is None and b.reaction == 0
    dash, _ = resolve_action(ActionRequest(CoreAction.DASH, "a"), turn, budget, space, GameRNG(2))
    assert dash.budget.movement == 60
