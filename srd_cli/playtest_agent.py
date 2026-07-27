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
    """Public mechanical state sent to a playtest controller."""

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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)


@dataclass(frozen=True, slots=True)
class AgentAction:
    """One legal player action requested by a controller."""

    action: str
    rationale: str = ""
    controller: str = "external"

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
        return cls(action, result.rationale[:500], result.controller[:80])


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
        return AgentAction(action.action, action.rationale, controller)


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
        return AgentAction(action.action, action.rationale, controller)


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
