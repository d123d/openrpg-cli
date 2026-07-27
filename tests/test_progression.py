import pytest
from openrpg_cli.rules.progression import (
    build_progressions,
    level_for_xp,
    proficiency_bonus,
    validate_advancement,
)


def test_all_base_progressions_are_complete_and_stable():
    rows = build_progressions()
    assert len(rows) == 12
    assert all(len(row.levels) == 20 for row in rows.values())
    assert build_progressions() == rows


def test_advancement_contracts():
    assert level_for_xp(300) == 2
    assert proficiency_bonus(20) == 6
    validate_advancement(1, 2, xp=300)
    with pytest.raises(ValueError):
        validate_advancement(1, 3, milestone=True)
