"""Deterministic initiative, turn ownership, and action-economy contracts."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from openrpg_cli.engine.rng import GameRNG

MAX_ACTORS = 256
MAX_ID = 128
MAX_VALUE = 1_000_000


def _id(value: str) -> None:
    if not isinstance(value, str) or not value or len(value) > MAX_ID:
        raise ValueError("invalid id")


@dataclass(frozen=True, slots=True)
class InitiativeEntry:
    actor_id: str
    team_id: str
    roll: int
    modifier: int
    total: int

    def __post_init__(self) -> None:
        _id(self.actor_id)
        _id(self.team_id)


@dataclass(frozen=True, slots=True)
class TurnOrder:
    entries: tuple[InitiativeEntry, ...]

    def __post_init__(self) -> None:
        if not self.entries or len(self.entries) > MAX_ACTORS:
            raise ValueError("invalid actor count")
        ids = [x.actor_id for x in self.entries]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate actor")

    @property
    def actor_ids(self) -> tuple[str, ...]:
        return tuple(x.actor_id for x in self.entries)


@dataclass(frozen=True, slots=True)
class SurpriseState:
    surprised_actor_ids: frozenset[str] = frozenset()
    consumed_actor_ids: frozenset[str] = frozenset()

    def is_surprised(self, actor_id: str) -> bool:
        return actor_id in self.surprised_actor_ids and actor_id not in self.consumed_actor_ids


@dataclass(frozen=True, slots=True)
class TurnState:
    order: TurnOrder
    index: int = 0
    round: int = 1
    surprise: SurpriseState = SurpriseState()

    def __post_init__(self) -> None:
        if not 0 <= self.index < len(self.order.entries) or self.round < 1:
            raise ValueError("invalid turn state")

    @property
    def current_actor_id(self) -> str:
        return self.order.entries[self.index].actor_id


@dataclass(frozen=True, slots=True)
class TurnTransition:
    accepted: bool
    reason: str | None
    before_actor_id: str
    after_actor_id: str
    before_round: int
    after_round: int
    srd_key: str = "srd-5.2.1:combat-the-order-of-combat"


def roll_initiative(
    actors: tuple[tuple[str, str, int], ...],
    teams: tuple[tuple[str, tuple[str, ...]], ...],
    rng: GameRNG,
    surprised_actor_ids: frozenset[str] = frozenset(),
) -> tuple[TurnState, GameRNG]:
    if not actors or len(actors) > MAX_ACTORS:
        raise ValueError("invalid actor count")
    actor_ids = [a[0] for a in actors]
    if len(actor_ids) != len(set(actor_ids)):
        raise ValueError("duplicate actor")
    team_map: dict[str, str] = {}
    for team_id, members in teams:
        _id(team_id)
        for member in members:
            if member in team_map:
                raise ValueError("duplicate team membership")
            team_map[member] = team_id
    if set(team_map) != set(actor_ids):
        raise ValueError("missing actor or team reference")
    if not surprised_actor_ids <= set(actor_ids):
        raise ValueError("unknown surprised actor")
    entries, next_rng = [], rng
    for actor_id, team_id, modifier in actors:
        _id(actor_id)
        _id(team_id)
        if (
            team_map.get(actor_id) != team_id
            or type(modifier) is not int
            or abs(modifier) > MAX_VALUE
        ):
            raise ValueError("invalid actor initiative")
        roll, next_rng = next_rng.die(20)
        entries.append(InitiativeEntry(actor_id, team_id, roll, modifier, roll + modifier))
    entries.sort(key=lambda x: (-x.total, -x.modifier, x.actor_id))
    return TurnState(
        TurnOrder(tuple(entries)), surprise=SurpriseState(surprised_actor_ids)
    ), next_rng


def require_owner(state: TurnState, actor_id: str) -> str | None:
    return None if actor_id == state.current_actor_id else "not_current_actor"


def end_turn(state: TurnState, actor_id: str) -> tuple[TurnState, TurnTransition]:
    reason = require_owner(state, actor_id)
    if reason:
        return state, TurnTransition(
            False, reason, state.current_actor_id, state.current_actor_id, state.round, state.round
        )
    surprise = state.surprise
    if surprise.is_surprised(actor_id):
        surprise = replace(surprise, consumed_actor_ids=surprise.consumed_actor_ids | {actor_id})
    index = (state.index + 1) % len(state.order.entries)
    round_number = state.round + (1 if index == 0 else 0)
    result = replace(state, index=index, round=round_number, surprise=surprise)
    return result, TurnTransition(
        True, None, actor_id, result.current_actor_id, state.round, round_number
    )


class BudgetKind(str, Enum):
    ACTION = "action"
    BONUS_ACTION = "bonus_action"
    REACTION = "reaction"
    MOVEMENT = "movement"
    INTERACTION = "interaction"


class TriggerKind(str, Enum):
    LEAVE_REACH = "leave_reach"
    READY = "ready"
    EXPLICIT = "explicit"


@dataclass(frozen=True, slots=True)
class ActionBudget:
    action: int = 1
    bonus_action: int = 1
    reaction: int = 1
    movement: int = 30
    interaction: int = 1

    def __post_init__(self) -> None:
        if any(
            type(x) is not int or not 0 <= x <= MAX_VALUE
            for x in (
                self.action,
                self.bonus_action,
                self.reaction,
                self.movement,
                self.interaction,
            )
        ):
            raise ValueError("invalid budget")


@dataclass(frozen=True, slots=True)
class ActionCost:
    action: int = 0
    bonus_action: int = 0
    reaction: int = 0
    movement: int = 0
    interaction: int = 0

    def __post_init__(self) -> None:
        ActionBudget(self.action, self.bonus_action, self.reaction, self.movement, self.interaction)


@dataclass(frozen=True, slots=True)
class TargetSpec:
    kinds: tuple[str, ...] = ()
    minimum: int = 0
    maximum: int = 0

    def __post_init__(self) -> None:
        if len(self.kinds) > 32 or not 0 <= self.minimum <= self.maximum <= 256:
            raise ValueError("invalid target spec")


@dataclass(frozen=True, slots=True)
class RangeSpec:
    minimum: int = 0
    maximum: int = 0
    unit: str = "feet"

    def __post_init__(self) -> None:
        if (
            type(self.minimum) is not int
            or type(self.maximum) is not int
            or not 0 <= self.minimum <= self.maximum <= MAX_VALUE
        ):
            raise ValueError("invalid range spec")


@dataclass(frozen=True, slots=True)
class LegalCommandSpec:
    command_id: str
    actor_id: str
    cost: ActionCost
    targets: TargetSpec
    range: RangeSpec
    prerequisites: tuple[str, ...] = ()
    legal: bool = True
    failure_reason: str | None = None
    srd_key: str = ""

    def __post_init__(self) -> None:
        _id(self.command_id)
        _id(self.actor_id)
        if len(self.prerequisites) > 64:
            raise ValueError("too many prerequisites")


def reset_budget(speed: int = 30) -> ActionBudget:
    return ActionBudget(movement=speed)


def spend_budget(
    budget: ActionBudget, cost: ActionCost, trigger: TriggerKind | None = None
) -> tuple[ActionBudget, str | None]:
    if cost.reaction and trigger is None:
        return budget, "reaction_requires_trigger"
    names = ("action", "bonus_action", "reaction", "movement", "interaction")
    for name in names:
        if getattr(cost, name) > getattr(budget, name):
            return budget, f"insufficient_{name}"
    return replace(budget, **{n: getattr(budget, n) - getattr(cost, n) for n in names}), None
