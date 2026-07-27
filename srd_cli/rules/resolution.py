"""Pure deterministic d20 resolution."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from srd_cli.engine.rng import GameRNG

LIMIT = 1_000_000


class TestKind(str, Enum):
    CHECK = "check"
    SAVE = "save"
    ATTACK = "attack"


class Proficiency(str, Enum):
    NONE = "none"
    PROFICIENT = "proficient"
    EXPERTISE = "expertise"


@dataclass(frozen=True, slots=True)
class D20Test:
    kind: TestKind
    ability_modifier: int = 0
    proficiency_bonus: int = 0
    proficiency: Proficiency = Proficiency.NONE
    circumstantial_modifiers: tuple[int, ...] = ()
    advantage_sources: tuple[str, ...] = ()
    disadvantage_sources: tuple[str, ...] = ()
    target: int | None = None
    srd_key: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.kind, TestKind) or not isinstance(self.proficiency, Proficiency):
            raise ValueError("invalid test kind or proficiency")
        values = (self.ability_modifier, self.proficiency_bonus, *self.circumstantial_modifiers)
        if len(self.circumstantial_modifiers) > 64 or any(
            type(v) is not int or abs(v) > LIMIT for v in values
        ):
            raise ValueError("invalid modifier collection")
        if self.target is not None and (
            type(self.target) is not int or not 0 <= self.target <= LIMIT
        ):
            raise ValueError("invalid target")


@dataclass(frozen=True, slots=True)
class D20Result:
    kind: TestKind
    dice: tuple[int, ...]
    natural: int
    ability_modifier: int
    proficiency_modifier: int
    circumstantial_modifiers: tuple[int, ...]
    total: int
    target: int | None
    success: bool | None
    natural_20: bool
    natural_1: bool
    automatic_attack_hit: bool
    automatic_attack_miss: bool
    rng_draw_start: int
    rng_draw_end: int
    srd_key: str


def _modifier(test: D20Test) -> tuple[int, int]:
    multiplier = {Proficiency.NONE: 0, Proficiency.PROFICIENT: 1, Proficiency.EXPERTISE: 2}[
        test.proficiency
    ]
    prof = test.proficiency_bonus * multiplier
    return test.ability_modifier + prof + sum(test.circumstantial_modifiers), prof


def resolve_d20(test: D20Test, rng: GameRNG) -> tuple[D20Result, GameRNG]:
    advantage = bool(test.advantage_sources)
    disadvantage = bool(test.disadvantage_sources)
    count = 1 if advantage == disadvantage else 2
    rolls: list[int] = []
    next_rng = rng
    for _ in range(count):
        roll, next_rng = next_rng.die(20)
        rolls.append(roll)
    natural = (
        max(rolls)
        if advantage and not disadvantage
        else min(rolls)
        if disadvantage and not advantage
        else rolls[0]
    )
    modifier, prof = _modifier(test)
    total = natural + modifier
    success = None if test.target is None else total >= test.target
    auto_hit = test.kind is TestKind.ATTACK and natural == 20
    auto_miss = test.kind is TestKind.ATTACK and natural == 1
    if auto_hit:
        success = True
    elif auto_miss:
        success = False
    return D20Result(
        test.kind,
        tuple(rolls),
        natural,
        test.ability_modifier,
        prof,
        test.circumstantial_modifiers,
        total,
        test.target,
        success,
        natural == 20,
        natural == 1,
        auto_hit,
        auto_miss,
        rng.draws,
        next_rng.draws,
        test.srd_key,
    ), next_rng


def resolve_contest(
    left: D20Test, right: D20Test, rng: GameRNG
) -> tuple[D20Result, D20Result, int, GameRNG]:
    a, rng = resolve_d20(left, rng)
    b, rng = resolve_d20(right, rng)
    return a, b, (1 if a.total > b.total else -1 if a.total < b.total else 0), rng


def passive_score(test: D20Test) -> int:
    modifier, _ = _modifier(test)
    adjustment = (
        5
        if test.advantage_sources and not test.disadvantage_sources
        else -5
        if test.disadvantage_sources and not test.advantage_sources
        else 0
    )
    return 10 + modifier + adjustment
