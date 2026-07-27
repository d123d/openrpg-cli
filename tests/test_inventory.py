from decimal import Decimal
import pytest
from srd_cli.rules.inventory import Inventory, ItemSpec, Stack, add, attune, carried_weight, consume_ammunition, equip

def test_inventory_conservation_equipment_ammo_attunement():
    specs = {"bow": ItemSpec("bow", Decimal("2"), ("hands",)),
             "arrow": ItemSpec("arrow", Decimal(".05"), ammunition_type="arrow"),
             "ring": ItemSpec("ring", requires_attunement=True)}
    state = Inventory()
    for stack in (Stack("b", "bow", 1), Stack("a", "arrow", 2), Stack("r", "ring", 1)):
        state = add(state, stack, specs)
    assert carried_weight(state, specs) == Decimal("2.10")
    state = equip(state, "b", "hands", specs, frozenset({"bow"}))
    state = consume_ammunition(state, "arrow", specs)
    state = attune(state, "r", specs)
    assert next(x for x in state.stacks if x.id == "a").quantity == 1
    with pytest.raises(ValueError): attune(state, "r", specs)
