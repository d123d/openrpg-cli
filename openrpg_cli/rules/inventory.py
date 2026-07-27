"""Immutable inventory, currency, equipment, ammunition, attunement rules."""

from __future__ import annotations
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
from types import MappingProxyType
from typing import Mapping

DENOMINATIONS = MappingProxyType({"cp": 1, "sp": 10, "ep": 50, "gp": 100, "pp": 1000})


@dataclass(frozen=True, slots=True)
class ItemSpec:
    key: str
    weight: Decimal = Decimal(0)
    slots: tuple[str, ...] = ()
    ammunition_type: str | None = None
    requires_attunement: bool = False


@dataclass(frozen=True, slots=True)
class Stack:
    id: str
    item_key: str
    quantity: int
    container_id: str | None = None


@dataclass(frozen=True, slots=True)
class Inventory:
    stacks: tuple[Stack, ...] = ()
    currency_cp: int = 0
    equipped: tuple[tuple[str, str], ...] = ()
    attuned: tuple[str, ...] = ()


def _validate(state: Inventory, specs: Mapping[str, ItemSpec]) -> None:
    if state.currency_cp < 0:
        raise ValueError("currency: negative")
    ids = {s.id for s in state.stacks}
    if len(ids) != len(state.stacks) or len(ids) > 4096:
        raise ValueError("stacks: duplicate/too many")
    for s in state.stacks:
        if s.item_key not in specs or isinstance(s.quantity, bool) or s.quantity <= 0:
            raise ValueError(f"stacks.{s.id}: invalid")
        seen = {s.id}
        parent = s.container_id
        for _ in range(32):
            if parent is None:
                break
            if parent in seen or parent not in ids:
                raise ValueError(f"stacks.{s.id}.container: cyclic/missing")
            seen.add(parent)
            parent = next(x.container_id for x in state.stacks if x.id == parent)
        else:
            raise ValueError("containers: depth exceeded")
    for slot, stack_id in state.equipped:
        if (
            stack_id not in ids
            or slot not in specs[next(x.item_key for x in state.stacks if x.id == stack_id)].slots
        ):
            raise ValueError(f"equipped.{slot}: incompatible")
    if len(set(slot for slot, _ in state.equipped)) != len(state.equipped):
        raise ValueError("equipped: slot conflict")
    if len(state.attuned) > 3 or len(set(state.attuned)) != len(state.attuned):
        raise ValueError("attuned: invalid")


def add(state: Inventory, stack: Stack, specs: Mapping[str, ItemSpec]) -> Inventory:
    out = replace(state, stacks=tuple(sorted(state.stacks + (stack,), key=lambda x: x.id)))
    _validate(out, specs)
    return out


def remove(
    state: Inventory, stack_id: str, quantity: int, specs: Mapping[str, ItemSpec]
) -> Inventory:
    if isinstance(quantity, bool) or quantity <= 0:
        raise ValueError("quantity: positive integer required")
    old = next((x for x in state.stacks if x.id == stack_id), None)
    if old is None or old.quantity < quantity:
        raise ValueError("quantity: insufficient")
    rows = tuple(x for x in state.stacks if x.id != stack_id)
    if old.quantity > quantity:
        rows += (replace(old, quantity=old.quantity - quantity),)
    out = replace(
        state,
        stacks=tuple(sorted(rows, key=lambda x: x.id)),
        equipped=tuple(x for x in state.equipped if x[1] != stack_id),
        attuned=tuple(x for x in state.attuned if x != stack_id),
    )
    _validate(out, specs)
    return out


def transfer_currency(
    state: Inventory, amount: int, denomination: str, *, debit: bool = False
) -> Inventory:
    if denomination not in DENOMINATIONS or isinstance(amount, bool) or amount < 0:
        raise ValueError("currency: invalid")
    delta = amount * DENOMINATIONS[denomination] * (-1 if debit else 1)
    if state.currency_cp + delta < 0:
        raise ValueError("currency: insufficient")
    return replace(state, currency_cp=state.currency_cp + delta)


def carried_weight(state: Inventory, specs: Mapping[str, ItemSpec]) -> Decimal:
    _validate(state, specs)
    try:
        return sum((specs[x.item_key].weight * x.quantity for x in state.stacks), Decimal(0))
    except InvalidOperation as exc:
        raise ValueError("weight: invalid decimal") from exc


def encumbrance(state: Inventory, specs: Mapping[str, ItemSpec], strength: int) -> str:
    if isinstance(strength, bool) or not 1 <= strength <= 30:
        raise ValueError("strength: expected 1..30")
    weight = carried_weight(state, specs)
    return (
        "heavily_encumbered"
        if weight > strength * 10
        else "encumbered"
        if weight > strength * 5
        else "normal"
    )


def equip(
    state: Inventory,
    stack_id: str,
    slot: str,
    specs: Mapping[str, ItemSpec],
    proficiencies: frozenset[str],
) -> Inventory:
    stack = next((x for x in state.stacks if x.id == stack_id), None)
    if stack is None or stack.item_key not in proficiencies:
        raise ValueError("equip: ownership/proficiency required")
    out = replace(state, equipped=tuple(sorted(state.equipped + ((slot, stack_id),))))
    _validate(out, specs)
    return out


def attune(
    state: Inventory, stack_id: str, specs: Mapping[str, ItemSpec], *, eligible: bool = True
) -> Inventory:
    stack = next((x for x in state.stacks if x.id == stack_id), None)
    if stack is None or not specs[stack.item_key].requires_attunement or not eligible:
        raise ValueError("attune: illegal")
    out = replace(state, attuned=tuple(sorted(state.attuned + (stack_id,))))
    _validate(out, specs)
    return out


def consume_ammunition(
    state: Inventory, ammo_type: str, specs: Mapping[str, ItemSpec]
) -> Inventory:
    stack = next((x for x in state.stacks if specs[x.item_key].ammunition_type == ammo_type), None)
    if stack is None:
        raise ValueError("ammunition: unavailable")
    return remove(state, stack.id, 1, specs)
