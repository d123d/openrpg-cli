"""Dice roller. Explicit RNG only — no hidden random.seed side effects.

RNG resume uses Python Random.getstate/setstate so save→load continues the
exact same roll stream (not the broken random() advance trick).
"""

from __future__ import annotations

import os
import re
import random
from dataclasses import dataclass, field
from typing import Any, Literal

Advantage = Literal["normal", "advantage", "disadvantage"]

_DICE_TERM = re.compile(r"^(\d+)d(\d+)(?:k([hl])(\d+))?$", re.IGNORECASE)
_FLAT = re.compile(r"^\d+$")
# ai-realms / WorldOS-style bounds (pathological expression guard)
_MAX_DICE = 1000
_MAX_SIDES = 1000
_MAX_EXPRESSION_CHARS = 4096


@dataclass
class RollGroup:
    count: int
    sides: int
    rolls: list[int]
    dropped: list[int]
    total: int


@dataclass
class RollResult:
    expression: str
    groups: list[RollGroup]
    modifier: int
    total: int

    def summary(self) -> str:
        parts: list[str] = []
        for g in self.groups:
            body = f"{g.count}d{g.sides}=[{','.join(map(str, g.rolls))}]"
            if g.dropped:
                body += f" drop[{','.join(map(str, g.dropped))}]"
            parts.append(body)
        mod = f"{self.modifier:+d}" if self.modifier else ""
        return f"{self.expression} -> {' + '.join(parts)}{mod} = **{self.total}**"


@dataclass
class D20Roll:
    dice: list[int]
    natural: int
    modifier: int
    total: int
    advantage: Advantage
    is_nat20: bool
    is_nat1: bool

    def summary(self) -> str:
        adv = f" ({self.advantage})" if self.advantage != "normal" else ""
        dice_s = ",".join(map(str, self.dice))
        tag = " CRIT" if self.is_nat20 else (" FUMBLE" if self.is_nat1 else "")
        return f"d20{adv} [{dice_s}]{self.modifier:+d} = **{self.total}**{tag}"


@dataclass
class LegacyPythonRNG:
    """Seeded RNG with faithful save/restore via getstate/setstate.

    Set ``OPENRPG_CLI_RNG_TRACE=1`` to log every draw to stderr for
    determinism verification (DET-01).
    """

    seed: int
    draw_count: int = 0
    # Serialized random.Random.getstate() — list form is JSON-safe
    state: list[Any] | None = None
    _rng: random.Random = field(init=False, repr=False)
    _trace: list[str] = field(default_factory=list, repr=False)
    _trace_enabled: bool = field(
        default_factory=lambda: os.environ.get("OPENRPG_CLI_RNG_TRACE", "").strip() == "1",
        repr=False,
    )

    def __post_init__(self) -> None:
        self._rng = random.Random()
        if self.state is not None:
            # Restore exact stream position
            self._rng.setstate(_list_to_state(self.state))
        else:
            self._rng.seed(self.seed)
            # Legacy path: old saves only had draw_count. Burn that many d20 draws
            # to approximate the stream position (exact only if every draw was 1d20;
            # new saves carry full state and skip this).
            for _ in range(self.draw_count):
                self._rng.randint(1, 20)
        self._capture_state()

    def _capture_state(self) -> None:
        self.state = _state_to_list(self._rng.getstate())

    def randint(self, a: int, b: int, tag: str = "") -> int:
        self.draw_count += 1
        val = self._rng.randint(a, b)
        if self._trace_enabled:
            self._trace.append(f"#{self.draw_count} randint({a},{b})={val}  [{tag}]")
        self._capture_state()
        return val

    def snapshot(self) -> dict:
        """Capture stream position for rollback. Cheap — no object copy."""
        return {"draw_count": self.draw_count, "state": self.state}

    def restore(self, snap: dict) -> None:
        """Rewind to a `snapshot()`, discarding any draws made since."""
        self.draw_count = int(snap["draw_count"])
        self.state = snap["state"]
        if self.state is not None:
            self._rng.setstate(_list_to_state(self.state))

    def trace(self) -> list[str]:
        """Return the ordered list of RNG draws (empty if tracing was off)."""
        return list(self._trace)

    def trace_dump(self) -> str:
        """Dump full trace as a string, one draw per line."""
        return "\n".join(self._trace) if self._trace else "(no RNG trace — set OPENRPG_CLI_RNG_TRACE=1)"

    def to_dict(self) -> dict:
        return {
            "seed": self.seed,
            "draw_count": self.draw_count,
            "state": self.state,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LegacyPythonRNG":
        return cls(
            seed=int(data["seed"]),
            draw_count=int(data.get("draw_count", 0)),
            state=data.get("state"),
        )


def _state_to_list(state: tuple) -> list[Any]:
    """JSON-serialize random.getstate() (version, internal tuple, gauss)."""
    version, internal, gauss = state
    return [version, list(internal), gauss]


def _list_to_state(data: list[Any]) -> tuple:
    version, internal, gauss = data[0], data[1], data[2]
    return (version, tuple(internal), gauss)


def roll_die(rng: LegacyPythonRNG, sides: int) -> int:
    if sides < 2:
        raise ValueError(f"die sides must be >= 2, got {sides}")
    return rng.randint(1, sides)


def _parse_expression(expression: str) -> tuple[list[int], list[str]]:
    """Split '2d6+3-1d4' into signs [1, -1] and terms ['2d6', '1d4']."""
    expr = expression.strip().replace(" ", "")
    if not expr:
        raise ValueError("empty dice expression")
    tokens = re.split(r"([+-])", expr)
    if tokens[0] == "":
        raise ValueError(f"invalid dice expression: {expression!r}")
    signs: list[int] = [1]
    terms: list[str] = [tokens[0]]
    i = 1
    while i < len(tokens):
        signs.append(1 if tokens[i] == "+" else -1)
        terms.append(tokens[i + 1] if i + 1 < len(tokens) else "")
        i += 2
    return signs, terms


def _split_damage_expr(expression: str) -> tuple[str, int]:
    """Split '2d6+3' into dice part '2d6' and flat modifier 3 for crit rules."""
    signs, terms = _parse_expression(expression)
    dice_parts: list[str] = []
    modifier = 0
    for sign, term in zip(signs, terms):
        if not term:
            continue
        if _DICE_TERM.match(term):
            if not dice_parts:
                dice_parts.append(("-" if sign < 0 else "") + term)
            else:
                dice_parts.append(("+" if sign > 0 else "-") + term)
        elif _FLAT.match(term):
            modifier += sign * int(term)
        else:
            raise ValueError(f"invalid dice term: {term!r}")
    dice_only = "".join(dice_parts) if dice_parts else "0"
    return dice_only, modifier


def roll(rng: LegacyPythonRNG, expression: str) -> RollResult:
    expr = expression.strip().replace(" ", "")
    if not expr:
        raise ValueError("empty dice expression")
    if len(expr) > _MAX_EXPRESSION_CHARS:
        raise ValueError("dice expression too long")

    signs, terms = _parse_expression(expression)

    groups: list[RollGroup] = []
    modifier = 0
    total = 0
    for sign, term in zip(signs, terms):
        if not term:
            raise ValueError(f"invalid dice expression: {expression!r}")
        m = _DICE_TERM.match(term)
        if m:
            count, sides = int(m.group(1)), int(m.group(2))
            if not (1 <= count <= _MAX_DICE):
                raise ValueError(f"dice count out of bounds: {count}")
            if not (2 <= sides <= _MAX_SIDES):
                raise ValueError(f"dice sides out of bounds: {sides}")
            rolls = [roll_die(rng, sides) for _ in range(count)]
            dropped: list[int] = []
            if m.group(3):
                keep = int(m.group(4))
                if not (1 <= keep <= count):
                    raise ValueError(f"keep count out of bounds: {keep}")
                reverse = m.group(3).lower() == "h"
                ordered = sorted(rolls, reverse=reverse)
                kept, dropped = ordered[:keep], ordered[keep:]
                group_total = sum(kept)
            else:
                group_total = sum(rolls)
            groups.append(
                RollGroup(
                    count=count,
                    sides=sides,
                    rolls=rolls,
                    dropped=dropped,
                    total=group_total,
                )
            )
            total += sign * group_total
        elif _FLAT.match(term):
            val = int(term)
            modifier += sign * val
            total += sign * val
        else:
            raise ValueError(f"invalid dice term: {term!r} in {expression!r}")
    return RollResult(expression=expression, groups=groups, modifier=modifier, total=total)


def roll_damage_with_crit(rng: LegacyPythonRNG, expression: str, critical: bool) -> RollResult:
    """5e crit: roll weapon/spell dice twice, apply modifier once."""
    if not critical:
        return roll(rng, expression)
    dice_only, modifier = _split_damage_expr(expression)
    if dice_only in ("0", ""):
        # flat-only — no dice to double
        return RollResult(
            expression=f"{expression} (crit, no dice)",
            groups=[],
            modifier=modifier,
            total=modifier,
        )
    first = roll(rng, dice_only)
    second = roll(rng, dice_only)
    total = first.total + second.total + modifier
    return RollResult(
        expression=f"{expression} (crit dice x2)",
        groups=first.groups + second.groups,
        modifier=modifier,
        total=total,
    )


def roll_d20(rng: LegacyPythonRNG, modifier: int = 0, advantage: Advantage = "normal") -> D20Roll:
    n = 2 if advantage in ("advantage", "disadvantage") else 1
    dice = [roll_die(rng, 20) for _ in range(n)]
    if advantage == "advantage":
        natural = max(dice)
    elif advantage == "disadvantage":
        natural = min(dice)
    else:
        natural = dice[0]
    return D20Roll(
        dice=dice,
        natural=natural,
        modifier=modifier,
        total=natural + modifier,
        advantage=advantage,
        is_nat20=natural == 20,
        is_nat1=natural == 1,
    )


# Deprecated v1 compatibility export. New code imports LegacyPythonRNG.
GameRNG = LegacyPythonRNG
