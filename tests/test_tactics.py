# ruff: noqa: F403, F405
from srd_cli.rules.tactics import *  # noqa: F403, F405


def setup():
    s = SpatialState(("a", "b"), (RelativePosition("a", "b", RangeBand.NEAR),))
    return ActionBudget(), s


def test_grapple_shove_cost_and_failure():
    b, s = setup()
    result = grapple("a", "b", b, s, success=False)
    assert result.accepted and result.budget.action == 0 and result.grapple is None
    malformed = grapple("a", "b", b, s, size_difference=2)
    assert not malformed.accepted and malformed.budget == b
    shoved = shove("a", "b", ShoveMode.PRONE, b, s)
    assert shoved.conditions == ("prone",)


def test_opportunity_cover_visibility_underwater():
    b, s = setup()
    triggers = opportunity_triggers(s, "a", RangeBand.FAR, ("b",))
    assert len(triggers) == 1
    spent, reason = accept_opportunity(triggers[0], "b", b)
    assert reason is None and spent.reaction == 0
    assert opportunity_triggers(s, "a", RangeBand.FAR, ("b",), disengaged=True) == ()
    assert not tactical_modifier(CoverLevel.TOTAL).targetable
    assert tactical_modifier(environment=EnvironmentMode.UNDERWATER).disadvantage
