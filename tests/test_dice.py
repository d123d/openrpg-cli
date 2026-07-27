import pytest

from srd_cli.dice import GameRNG, roll


def test_seeded_roll_is_repeatable() -> None:
    first = roll(GameRNG(seed=42), "4d6kh3")
    second = roll(GameRNG(seed=42), "4d6kh3")
    assert first.total == second.total
    assert first.groups[0].rolls == second.groups[0].rolls


@pytest.mark.parametrize("expression", ["", "0d6", "1d1", "1001d6", "1d1001"])
def test_invalid_rolls_rejected(expression: str) -> None:
    with pytest.raises(ValueError):
        roll(GameRNG(seed=1), expression)

