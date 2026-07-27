# ruff: noqa: F403, F405
from openrpg_cli.rules.space import *  # noqa: F403, F405
from openrpg_cli.rules.turns import *  # noqa: F403, F405


def test_move_targets_grid_parity():
    s = SpatialState(("a", "b"), (RelativePosition("a", "b", RangeBand.NEAR),))
    moved, t = move(s, "a", "b", RangeBand.FAR, 30)
    assert t.accepted and moved.band("a", "b") == RangeBand.FAR
    spec = TargetSpec(("enemy",), 1, 1)
    rng = RangeSpec(0, int(RangeBand.NEAR))
    assert resolve_targets(s, "a", ("b",), spec, rng, {"a": "x", "b": "y"}).accepted == ("b",)
    g = GridState((("a", GridPosition(0, 0)), ("b", GridPosition(6, 0))))
    assert grid_to_spatial(g).band("a", "b") == RangeBand.NEAR


def test_grid_rejects_occupancy():
    import pytest

    with pytest.raises(ValueError):
        GridState((("a", GridPosition(0, 0)), ("b", GridPosition(0, 0))))
