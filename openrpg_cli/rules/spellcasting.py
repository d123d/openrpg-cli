"""Deterministic spell availability, slots, resources, concentration."""

from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Mapping

FULL_SLOTS = (
    (),
    (2,),
    (3,),
    (4, 2),
    (4, 3),
    (4, 3, 2),
    (4, 3, 3),
    (4, 3, 3, 1),
    (4, 3, 3, 2),
    (4, 3, 3, 3, 1),
    (4, 3, 3, 3, 2),
    (4, 3, 3, 3, 2, 1),
    (4, 3, 3, 3, 2, 1),
    (4, 3, 3, 3, 2, 1, 1),
    (4, 3, 3, 3, 2, 1, 1),
    (4, 3, 3, 3, 2, 1, 1, 1),
    (4, 3, 3, 3, 2, 1, 1, 1, 1),
    (4, 3, 3, 3, 3, 1, 1, 1, 1),
    (4, 3, 3, 3, 3, 2, 1, 1, 1),
    (4, 3, 3, 3, 3, 2, 2, 1, 1),
    (4, 3, 3, 3, 3, 2, 2, 1, 1),
)


@dataclass(frozen=True, slots=True)
class Resource:
    id: str
    source_key: str
    current: int
    maximum: int
    recharge: str


@dataclass(frozen=True, slots=True)
class CastingState:
    slots: tuple[int, ...]
    known: tuple[str, ...] = ()
    prepared: tuple[str, ...] = ()
    resources: tuple[Resource, ...] = ()
    concentration: str | None = None
    slot_maximum: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if not self.slot_maximum:
            object.__setattr__(self, "slot_maximum", self.slots)
        if len(self.slots) != len(self.slot_maximum):
            raise ValueError("slots: current/maximum shape mismatch")
        if any(
            current < 0 or current > maximum
            for current, maximum in zip(self.slots, self.slot_maximum)
        ):
            raise ValueError("slots: current outside maximum")


def multiclass_caster_level(class_levels: Mapping[str, tuple[int, str]]) -> int:
    total = 0
    for level, kind in class_levels.values():
        if not 0 <= level <= 20:
            raise ValueError("class level: invalid")
        total += (
            level
            if kind == "full"
            else level // 2
            if kind == "half"
            else level // 3
            if kind == "third"
            else 0
        )
    return min(total, 20)


def slots_for(class_levels: Mapping[str, tuple[int, str]]) -> tuple[int, ...]:
    return FULL_SLOTS[multiclass_caster_level(class_levels)]


def validate_spells(
    spell_keys: tuple[str, ...],
    spell_catalog: Mapping[str, object],
    class_keys: frozenset[str],
    max_spell_level: int,
) -> tuple[str, ...]:
    if len(spell_keys) != len(set(spell_keys)):
        raise ValueError("spells: duplicate")
    for key in spell_keys:
        spell = spell_catalog.get(key)
        if spell is None:
            raise ValueError(f"spells.{key}: unknown")
        data = getattr(spell, "data", spell)
        if int(data["level"]) > max_spell_level or not class_keys.intersection(data["classes"]):
            raise ValueError(f"spells.{key}: ineligible")
    return tuple(sorted(spell_keys))


def spend_slot(state: CastingState, spell_level: int, slot_level: int) -> CastingState:
    if spell_level == 0:
        return state
    if not 1 <= spell_level <= slot_level <= len(state.slots) or state.slots[slot_level - 1] <= 0:
        raise ValueError("slot: unavailable")
    slots = list(state.slots)
    slots[slot_level - 1] -= 1
    return replace(state, slots=tuple(slots))


def spend_resource(state: CastingState, resource_id: str, amount: int = 1) -> CastingState:
    if isinstance(amount, bool) or amount <= 0:
        raise ValueError("amount: positive integer required")
    found = False
    rows = []
    for r in state.resources:
        if r.id == resource_id:
            found = True
            if r.current < amount:
                raise ValueError("resource: insufficient")
            r = replace(r, current=r.current - amount)
        rows.append(r)
    if not found:
        raise ValueError("resource: unknown")
    return replace(state, resources=tuple(rows))


def start_concentration(state: CastingState, effect_id: str) -> tuple[CastingState, str | None]:
    if not effect_id:
        raise ValueError("effect_id: blank")
    return replace(state, concentration=effect_id), state.concentration


def concentration_save(dc_damage: int) -> int:
    if dc_damage < 0:
        raise ValueError("damage: negative")
    return max(10, dc_damage // 2)
