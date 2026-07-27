# ruff: noqa: F403, F405
"""Tactical modifier and reaction hooks over shared Phase 7 contracts."""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from .space import *
from .turns import *


class CoverLevel(str, Enum):
    NONE = "none"
    HALF = "half"
    THREE_QUARTERS = "three_quarters"
    TOTAL = "total"


class VisibilityLevel(str, Enum):
    VISIBLE = "visible"
    OBSCURED = "obscured"
    HIDDEN = "hidden"
    UNSEEN = "unseen"


class EnvironmentMode(str, Enum):
    NORMAL = "normal"
    UNDERWATER = "underwater"


class ShoveMode(str, Enum):
    PRONE = "prone"
    PUSH = "push"


@dataclass(frozen=True, slots=True)
class TacticalModifier:
    ac_bonus: int = 0
    save_bonus: int = 0
    advantage: tuple[str, ...] = ()
    disadvantage: tuple[str, ...] = ()
    targetable: bool = True
    reason: str | None = None
    sources: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class GrappleState:
    grappler_id: str
    target_id: str


@dataclass(frozen=True, slots=True)
class MountState:
    rider_id: str
    mount_id: str
    controlled: bool = True


@dataclass(frozen=True, slots=True)
class OpportunityTrigger:
    reactor_id: str
    mover_id: str
    source_band: RangeBand
    destination_band: RangeBand
    srd_key: str = "srd-5.2.1:opportunity-attacks"


@dataclass(frozen=True, slots=True)
class TacticalResult:
    accepted: bool
    reason: str | None
    budget: ActionBudget
    spatial: SpatialState
    conditions: tuple[str, ...] = ()
    grapple: GrappleState | None = None


def grapple(
    actor_id: str,
    target_id: str,
    budget: ActionBudget,
    space: SpatialState,
    *,
    size_difference: int = 0,
    free_hand: bool = True,
    success: bool = True,
) -> TacticalResult:
    if abs(size_difference) > 1:
        return TacticalResult(False, "invalid_size", budget, space)
    if not free_hand:
        return TacticalResult(False, "free_hand_required", budget, space)
    if space.band(actor_id, target_id) > RangeBand.NEAR:
        return TacticalResult(False, "out_of_reach", budget, space)
    spent, reason = spend_budget(budget, ActionCost(action=1))
    if reason:
        return TacticalResult(False, reason, budget, space)
    return TacticalResult(
        True,
        None,
        spent,
        space,
        ("grappled",) if success else (),
        GrappleState(actor_id, target_id) if success else None,
    )


def shove(
    actor_id: str,
    target_id: str,
    mode: ShoveMode,
    budget: ActionBudget,
    space: SpatialState,
    *,
    size_difference: int = 0,
    success: bool = True,
) -> TacticalResult:
    if abs(size_difference) > 1:
        return TacticalResult(False, "invalid_size", budget, space)
    if space.band(actor_id, target_id) > RangeBand.NEAR:
        return TacticalResult(False, "out_of_reach", budget, space)
    spent, reason = spend_budget(budget, ActionCost(action=1))
    if reason:
        return TacticalResult(False, reason, budget, space)
    result = space
    conditions = ()
    if success and mode is ShoveMode.PRONE:
        conditions = ("prone",)
    elif success:
        result, _ = move(space, target_id, actor_id, RangeBand.FAR, 30)
    return TacticalResult(True, None, spent, result, conditions)


def opportunity_triggers(
    space: SpatialState,
    mover_id: str,
    destination: RangeBand,
    enemies: tuple[str, ...],
    *,
    visible: bool = True,
    disengaged: bool = False,
) -> tuple[OpportunityTrigger, ...]:
    if not visible or disengaged:
        return ()
    return tuple(
        OpportunityTrigger(x, mover_id, space.band(x, mover_id), destination)
        for x in sorted(enemies)
        if space.band(x, mover_id) <= RangeBand.NEAR and destination > RangeBand.NEAR
    )


def accept_opportunity(
    trigger: OpportunityTrigger, reactor_id: str, budget: ActionBudget
) -> tuple[ActionBudget, str | None]:
    if trigger.reactor_id != reactor_id:
        return budget, "wrong_reactor"
    return spend_budget(budget, ActionCost(reaction=1), TriggerKind.LEAVE_REACH)


def tactical_modifier(
    cover: CoverLevel = CoverLevel.NONE,
    visibility: VisibilityLevel = VisibilityLevel.VISIBLE,
    environment: EnvironmentMode = EnvironmentMode.NORMAL,
    *,
    weapon_supported: bool = True,
) -> TacticalModifier:
    if cover is CoverLevel.TOTAL:
        return TacticalModifier(targetable=False, reason="total_cover", sources=("cover",))
    ac = {CoverLevel.NONE: 0, CoverLevel.HALF: 2, CoverLevel.THREE_QUARTERS: 5}[cover]
    save = ac
    adv = ()
    dis = ()
    sources = []
    if cover is not CoverLevel.NONE:
        sources.append("cover")
    if visibility in {VisibilityLevel.HIDDEN, VisibilityLevel.UNSEEN}:
        dis = ("unseen_target",)
        sources.append("visibility")
    if environment is EnvironmentMode.UNDERWATER:
        sources.append("underwater")
        if not weapon_supported:
            return TacticalModifier(
                ac, save, adv, dis, False, "unsupported_underwater_equipment", tuple(sources)
            )
        dis += ("underwater_attack",)
    return TacticalModifier(ac, save, adv, dis, True, None, tuple(sources))
