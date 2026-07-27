import pytest
from openrpg_cli.rules.spellcasting import (
    CastingState,
    concentration_save,
    slots_for,
    spend_slot,
    start_concentration,
)


def test_slots_spend_and_concentration():
    state = CastingState(slots_for({"wizard": (3, "full")}))
    assert state.slots == (4, 2)
    state = spend_slot(state, 1, 1)
    state, ended = start_concentration(state, "spell:a")
    assert ended is None and state.slots[0] == 3 and concentration_save(23) == 11
    with pytest.raises(ValueError):
        spend_slot(CastingState(()), 1, 1)
