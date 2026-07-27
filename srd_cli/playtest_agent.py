"""Provider-neutral controller contract for autonomous SRD combat playtests."""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Protocol, runtime_checkable


class ControllerError(RuntimeError):
    """A controller failed or returned an invalid action."""


@dataclass(frozen=True, slots=True)
class AgentObservation:
    """Versioned public state sent to a combat or general player controller."""

    schema_version: int
    run_id: str
    turn: int
    combat: dict[str, Any]
    legal_actions: tuple[dict[str, Any], ...]
    recent_actions: tuple[str, ...] = ()
    recent_events: tuple[dict[str, Any], ...] = ()
    objective: str = (
        "Play fairly, exercise legal actions, finish combat, and expose engine defects."
    )
    mode: str = "combat"
    situation_id: str = "combat-encounter"
    character: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    objectives: tuple[str, ...] = ()
    constraints: tuple[str, ...] = (
        "Choose one offered legal action.",
        "Never invent mechanics, rolls, outcomes, or state changes.",
    )

    def __post_init__(self) -> None:
        if self.schema_version not in (1, 2):
            raise ValueError("unsupported observation schema version")
        if not self.run_id or len(self.run_id) > 200:
            raise ValueError("run id length must be 1..200")
        if self.turn < 0 or self.turn > 1_000_000:
            raise ValueError("turn must be 0..1000000")
        if not self.mode or len(self.mode) > 80:
            raise ValueError("mode length must be 1..80")
        if len(self.legal_actions) > 256:
            raise ValueError("legal action count exceeds 256")
        if len(self.recent_actions) > 64 or len(self.recent_events) > 64:
            raise ValueError("recent history exceeds 64 entries")
        if len(self.objectives) > 32 or len(self.constraints) > 32:
            raise ValueError("objective or constraint count exceeds 32")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)


@dataclass(frozen=True, slots=True)
class AgentAction:
    """One structured player decision requested by a controller."""

    action: str
    rationale: str = ""
    controller: str = "external"
    target: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    confidence: float | None = None
    expected_effect: str = ""

    @classmethod
    def parse(cls, value: AgentAction | str | dict[str, Any]) -> AgentAction:
        if isinstance(value, cls):
            result = value
        elif isinstance(value, str):
            result = cls(action=value)
        elif isinstance(value, dict):
            result = cls(
                action=str(value.get("action") or ""),
                rationale=str(value.get("rationale") or ""),
                controller=str(value.get("controller") or "external"),
                target=str(value.get("target") or ""),
                parameters=dict(value.get("parameters") or {}),
                confidence=(
                    float(value["confidence"]) if value.get("confidence") is not None else None
                ),
                expected_effect=str(value.get("expected_effect") or ""),
            )
        else:
            raise ControllerError(f"unsupported controller result: {type(value).__name__}")
        action = result.action.strip()
        if not action:
            raise ControllerError("controller returned empty action")
        if "\n" in action or "\r" in action:
            raise ControllerError("controller action must be one line")
        if len(action) > 200:
            raise ControllerError("controller action exceeds 200 characters")
        target = result.target.strip()
        if "\n" in target or "\r" in target or len(target) > 200:
            raise ControllerError("controller target must be one bounded line")
        if len(result.parameters) > 32:
            raise ControllerError("controller parameters exceed 32 entries")
        confidence = result.confidence
        if confidence is not None and not 0.0 <= confidence <= 1.0:
            raise ControllerError("controller confidence must be 0..1")
        return cls(
            action,
            result.rationale[:500],
            result.controller[:80],
            target,
            dict(result.parameters),
            confidence,
            result.expected_effect[:500],
        )


@runtime_checkable
class AgentController(Protocol):
    """Any AI framework can implement this interface."""

    name: str

    def decide(self, observation: AgentObservation) -> AgentAction | str | dict[str, Any]:
        """Choose one offered action without inventing outcomes or mutating state."""


class CallableController:
    """Adapt a Python callback or SDK-backed agent."""

    def __init__(
        self,
        fn: Callable[[AgentObservation], AgentAction | str | dict[str, Any]],
        *,
        name: str = "callable",
    ) -> None:
        self.fn = fn
        self.name = name

    def decide(self, observation: AgentObservation) -> AgentAction:
        action = AgentAction.parse(self.fn(observation))
        controller = action.controller if action.controller != "external" else self.name
        return AgentAction(
            action.action, action.rationale, controller, action.target,
            action.parameters, action.confidence, action.expected_effect,
        )


class SubprocessController:
    """Invoke an external agent using one JSON document over stdin/stdout."""

    def __init__(
        self,
        command: list[str],
        *,
        timeout: int = 120,
        name: str = "subprocess",
    ) -> None:
        if not command:
            raise ValueError("command cannot be empty")
        if timeout < 1:
            raise ValueError("timeout must be positive")
        self.command = list(command)
        self.timeout = timeout
        self.name = name

    def decide(self, observation: AgentObservation) -> AgentAction:
        try:
            result = subprocess.run(
                self.command,
                input=observation.to_json(),
                text=True,
                capture_output=True,
                timeout=self.timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ControllerError(f"{self.name} failed: {exc}") from exc
        if result.returncode != 0:
            detail = result.stderr.strip()[-500:] or f"exit {result.returncode}"
            raise ControllerError(f"{self.name} failed: {detail}")
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ControllerError(f"{self.name} returned invalid JSON: {exc}") from exc
        action = AgentAction.parse(payload)
        controller = action.controller if action.controller != "external" else self.name
        return AgentAction(
            action.action, action.rationale, controller, action.target,
            action.parameters, action.confidence, action.expected_effect,
        )


@dataclass(slots=True)
class CoverageController:
    """Deterministic agent that exercises least-used legal actions first."""

    name: str = "coverage-v1"
    _counts: dict[str, int] = field(default_factory=dict, init=False, repr=False)

    def decide(self, observation: AgentObservation) -> AgentAction:
        if not observation.legal_actions:
            raise ControllerError("observation contains no legal actions")
        chosen = min(
            observation.legal_actions,
            key=lambda item: (self._counts.get(str(item["id"]), 0), int(item["index"])),
        )
        identity = str(chosen["id"])
        self._counts[identity] = self._counts.get(identity, 0) + 1
        return AgentAction(
            identity,
            f"exercise least-used legal action: {chosen['label']}",
            self.name,
        )
