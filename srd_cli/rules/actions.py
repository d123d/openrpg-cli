# ruff: noqa: F403, F405
"""Closed SRD 5.2.1 core action catalog."""

from __future__ import annotations
from dataclasses import dataclass, replace
from enum import Enum
from srd_cli.engine.rng import GameRNG
from .resolution import D20Test, D20Result, resolve_d20
from .space import SpatialState, TargetResolution, resolve_targets
from .turns import *


class CoreAction(str, Enum):
    ATTACK = "attack"
    MAGIC = "magic"
    DASH = "dash"
    DISENGAGE = "disengage"
    DODGE = "dodge"
    HELP = "help"
    HIDE = "hide"
    INFLUENCE = "influence"
    READY = "ready"
    SEARCH = "search"
    STUDY = "study"
    UTILIZE = "utilize"


@dataclass(frozen=True, slots=True)
class ActionRequest:
    action: CoreAction
    actor_id: str
    target_ids: tuple[str, ...] = ()
    test: D20Test | None = None
    trigger: TriggerKind | None = None
    structured_effect_id: str | None = None

    def __post_init__(self):
        if len(self.target_ids) > 256 or len(set(self.target_ids)) != len(self.target_ids):
            raise ValueError("invalid targets")


@dataclass(frozen=True, slots=True)
class ReadyState:
    actor_id: str
    trigger: TriggerKind
    action: CoreAction


@dataclass(frozen=True, slots=True)
class ActionOutcome:
    accepted: bool
    reason: str | None
    action: CoreAction
    actor_id: str
    budget: ActionBudget
    targets: TargetResolution | None = None
    test_result: D20Result | None = None
    statuses: tuple[str, ...] = ()
    ready: ReadyState | None = None
    srd_key: str = "srd-5.2.1:actions"


def command_spec(
    action: CoreAction, actor_id: str, turn: TurnState, budget: ActionBudget
) -> LegalCommandSpec:
    reason = require_owner(turn, actor_id)
    cost = ActionCost(action=1)
    target = TargetSpec(
        ("single",),
        0
        if action in {CoreAction.DASH, CoreAction.DODGE, CoreAction.DISENGAGE, CoreAction.READY}
        else 1,
        1,
    )
    if not reason:
        _, reason = spend_budget(budget, cost)
    return LegalCommandSpec(
        action.value,
        actor_id,
        cost,
        target,
        RangeSpec(0, 1),
        (),
        reason is None,
        reason,
        f"srd-5.2.1:action:{action.value}",
    )


def legal_commands(
    actor_id: str, turn: TurnState, budget: ActionBudget
) -> tuple[LegalCommandSpec, ...]:
    return tuple(command_spec(x, actor_id, turn, budget) for x in CoreAction)


def resolve_action(
    req: ActionRequest,
    turn: TurnState,
    budget: ActionBudget,
    space: SpatialState,
    rng: GameRNG,
    teams: dict[str, str] | None = None,
) -> tuple[ActionOutcome, GameRNG]:
    spec = command_spec(req.action, req.actor_id, turn, budget)
    if not spec.legal:
        return ActionOutcome(False, spec.failure_reason, req.action, req.actor_id, budget), rng
    targets = None
    if spec.targets.minimum:
        targets = resolve_targets(
            space, req.actor_id, req.target_ids, spec.targets, spec.range, teams
        )
        if len(targets.accepted) < spec.targets.minimum:
            return ActionOutcome(
                False, "invalid_targets", req.action, req.actor_id, budget, targets
            ), rng
    if (
        req.action in {CoreAction.MAGIC, CoreAction.UTILIZE}
        and not req.structured_effect_id
        and req.test is None
    ):
        return ActionOutcome(
            False, "structured_effect_required", req.action, req.actor_id, budget, targets
        ), rng
    spent, reason = spend_budget(budget, spec.cost)
    if reason:
        return ActionOutcome(False, reason, req.action, req.actor_id, budget, targets), rng
    statuses = []
    if req.action is CoreAction.DASH:
        spent = replace(spent, movement=min(MAX_VALUE, spent.movement + budget.movement))
    if req.action in {CoreAction.DISENGAGE, CoreAction.DODGE, CoreAction.HELP, CoreAction.HIDE}:
        statuses.append(req.action.value)
    ready = (
        ReadyState(req.actor_id, req.trigger, CoreAction.ATTACK)
        if req.action is CoreAction.READY and req.trigger
        else None
    )
    if req.action is CoreAction.READY and ready is None:
        return ActionOutcome(
            False, "ready_trigger_required", req.action, req.actor_id, budget, targets
        ), rng
    result = None
    next_rng = rng
    if req.test is not None:
        result, next_rng = resolve_d20(req.test, rng)
    return ActionOutcome(
        True, None, req.action, req.actor_id, spent, targets, result, tuple(statuses), ready
    ), next_rng


def trigger_ready(
    ready: ReadyState, trigger: TriggerKind, budget: ActionBudget
) -> tuple[ActionBudget, str | None]:
    if ready.trigger is not trigger:
        return budget, "trigger_mismatch"
    return spend_budget(budget, ActionCost(reaction=1), trigger)
