from openrpg_cli.dice import LegacyPythonRNG
from openrpg_cli.engine.rng import DeterministicRNG


def test_deterministic_rng_golden_vector() -> None:
    rng = DeterministicRNG(0)
    values = []
    states = []
    for _ in range(8):
        value, rng = rng.next_int(1, 20)
        values.append(value)
        states.append(rng.state)

    assert values == [8, 7, 14, 1, 4, 11, 10, 5]
    assert states == [
        1442695040888963407,
        1876011003808476466,
        11166244414315200793,
        7401132627792533940,
        7076646890315895283,
        10346034117385188870,
        1459328389850446429,
        6566661184467396264,
    ]
    assert rng.draws == 8


def test_legacy_python_rng_golden_vector() -> None:
    rng = LegacyPythonRNG(42)
    assert [rng.randint(1, 20) for _ in range(8)] == [4, 1, 9, 8, 8, 5, 4, 18]
    assert rng.draw_count == 8
