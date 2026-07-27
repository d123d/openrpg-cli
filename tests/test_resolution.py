from openrpg_cli.engine.rng import GameRNG
from openrpg_cli.rules.resolution import D20Test, Proficiency, TestKind, passive_score, resolve_contest, resolve_d20


def test_pipeline_expertise_and_cancelled_advantage() -> None:
    test = D20Test(TestKind.CHECK, 3, 2, Proficiency.EXPERTISE, (1,), ("help",), ("poison",), 10, "key")
    result, rng = resolve_d20(test, GameRNG(1))
    assert result.total == result.natural + 8
    assert result.dice == (result.natural,)
    assert rng.draws == 1


def test_contest_and_passive() -> None:
    test = D20Test(TestKind.CHECK, 2, advantage_sources=("help",))
    assert passive_score(test) == 17
    left, right, outcome, rng = resolve_contest(test, test, GameRNG(3))
    assert outcome in {-1, 0, 1}
    assert rng.draws == 4
    assert left.rng_draw_end == right.rng_draw_start
