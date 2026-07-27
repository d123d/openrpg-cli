"""Stable developer API for AI agents, capability discovery, and decision validation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from functools import lru_cache
from typing import Any, Iterable

from .catalog import (
    ACTIONS,
    SITUATIONS,
    ActionDescriptor,
    CapabilityStatus,
    ExperienceDomain,
    SituationDescriptor,
)

MAX_QUERY_LENGTH = 200
MAX_LEGAL_ACTIONS = 256


def _plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class DecisionValidation:
    valid: bool
    action_id: str = ""
    target_id: str = ""
    reason: str = ""


class DeveloperBackend:
    """Read-only catalog and validation backend for human or AI clients."""

    def __init__(
        self,
        actions: Iterable[ActionDescriptor] = ACTIONS,
        situations: Iterable[SituationDescriptor] = SITUATIONS,
    ) -> None:
        self.actions = tuple(actions)
        self.situations = tuple(situations)
        self._actions = {item.id: item for item in self.actions}
        self._situations = {item.id: item for item in self.situations}
        self._validate_catalog()

    def _validate_catalog(self) -> None:
        if len(self._actions) != len(self.actions):
            raise ValueError("duplicate action id")
        if len(self._situations) != len(self.situations):
            raise ValueError("duplicate situation id")
        known = set(self._actions)
        for item in (*self.actions, *self.situations):
            if not item.id or len(item.id) > 80 or not item.description.strip():
                raise ValueError(f"invalid descriptor: {item.id!r}")
        for situation in self.situations:
            missing = set(situation.action_ids) - known
            if missing:
                raise ValueError(f"{situation.id}: unknown actions: {sorted(missing)}")
        covered = {item.domain for item in self.situations}
        missing_domains = set(ExperienceDomain) - covered
        if missing_domains:
            raise ValueError(f"domains without situations: {sorted(x.value for x in missing_domains)}")

    def manifest(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "name": "openrpg-cli-developer-backend",
            "content_scope": "SRD 5.2.1 plus labeled generic runtime frameworks",
            "truth_order": [
                "engine state and events",
                "legal action contracts",
                "SRD structured data",
                "rendered descriptions",
                "AI rationale",
            ],
            "limits": {
                "max_query_length": MAX_QUERY_LENGTH,
                "max_legal_actions": MAX_LEGAL_ACTIONS,
            },
            "domains": [item.value for item in ExperienceDomain],
            "action_count": len(self.actions),
            "situation_count": len(self.situations),
        }

    def list_actions(
        self,
        *,
        domain: ExperienceDomain | str | None = None,
        status: CapabilityStatus | str | None = None,
    ) -> tuple[ActionDescriptor, ...]:
        domain_value = ExperienceDomain(domain) if domain is not None else None
        status_value = CapabilityStatus(status) if status is not None else None
        return tuple(
            item for item in self.actions
            if (domain_value is None or domain_value in item.domains)
            and (status_value is None or status_value == item.status)
        )

    def list_situations(
        self,
        *,
        domain: ExperienceDomain | str | None = None,
        status: CapabilityStatus | str | None = None,
    ) -> tuple[SituationDescriptor, ...]:
        domain_value = ExperienceDomain(domain) if domain is not None else None
        status_value = CapabilityStatus(status) if status is not None else None
        return tuple(
            item for item in self.situations
            if (domain_value is None or domain_value == item.domain)
            and (status_value is None or status_value == item.status)
        )

    def get(self, identity: str) -> ActionDescriptor | SituationDescriptor | None:
        return self._actions.get(identity) or self._situations.get(identity)

    def search(self, query: str, *, limit: int = 20) -> tuple[dict[str, Any], ...]:
        needle = query.strip().casefold()
        if not needle or len(needle) > MAX_QUERY_LENGTH:
            raise ValueError(f"query length must be 1..{MAX_QUERY_LENGTH}")
        if not 1 <= limit <= 200:
            raise ValueError("limit must be 1..200")
        found = []
        for kind, values in (("action", self.actions), ("situation", self.situations)):
            for item in values:
                text = " ".join(str(value) for value in asdict(item).values()).casefold()
                if needle in text:
                    score = 0 if needle in item.id.casefold() else (
                        1 if needle in item.title.casefold() else 2
                    )
                    found.append((score, item.id, _plain({"kind": kind, **asdict(item)})))
        return tuple(item[2] for item in sorted(found, key=lambda x: (x[0], x[1]))[:limit])

    def coverage(self) -> dict[str, Any]:
        by_status = {
            status.value: {
                "actions": sum(item.status == status for item in self.actions),
                "situations": sum(item.status == status for item in self.situations),
            }
            for status in CapabilityStatus
        }
        by_domain = {
            domain.value: {
                "actions": sum(domain in item.domains for item in self.actions),
                "situations": sum(item.domain == domain for item in self.situations),
            }
            for domain in ExperienceDomain
        }
        return {
            "actions": len(self.actions),
            "situations": len(self.situations),
            "by_status": by_status,
            "by_domain": by_domain,
            "implemented_or_partial_actions": sum(
                item.status in {CapabilityStatus.IMPLEMENTED, CapabilityStatus.PARTIAL}
                for item in self.actions
            ),
            "framework_or_planned_actions": sum(
                item.status in {CapabilityStatus.FRAMEWORK, CapabilityStatus.PLANNED}
                for item in self.actions
            ),
        }

    def situation_payload(self, identity: str) -> dict[str, Any]:
        situation = self._situations.get(identity)
        if situation is None:
            raise ValueError(f"unknown situation: {identity}")
        return {
            **_plain(asdict(situation)),
            "actions": [_plain(asdict(self._actions[action_id])) for action_id in situation.action_ids],
        }

    def controller_prompt(self, situation_id: str) -> str:
        payload = self.situation_payload(situation_id)
        action_lines = "\n".join(
            f"- {item['id']}: {item['description']} "
            f"[status={item['status']}; authority={item['authority']}]"
            for item in payload["actions"]
        )
        return (
            "You are a fair OpenRPG CLI player agent. Engine state and offered legal actions are "
            "authoritative. Choose exactly one offered action. Never invent rolls, outcomes, "
            "items, abilities, targets, lore, or state changes. Prefer progress, survival, "
            "party safety, broad mechanic coverage, and non-repetition.\n\n"
            f"Situation: {payload['title']}\n{payload['description']}\n"
            f"Goals: {', '.join(payload['player_goals'])}\n"
            f"Stakes: {', '.join(payload['stakes'])}\n"
            f"Known interaction vocabulary:\n{action_lines}\n\n"
            "Return JSON only: "
            '{"action":"offered id, exact label, or index","target":"offered target if required",'
            '"rationale":"brief reason","confidence":0.0}'
        )

    def validate_decision(
        self,
        decision: str | dict[str, Any],
        legal_actions: Iterable[dict[str, Any]],
    ) -> DecisionValidation:
        offered = tuple(legal_actions)
        if not 1 <= len(offered) <= MAX_LEGAL_ACTIONS:
            return DecisionValidation(False, reason="legal action count outside bounds")
        if isinstance(decision, str):
            action, target = decision.strip(), ""
        elif isinstance(decision, dict):
            action = str(decision.get("action") or "").strip()
            target = str(decision.get("target") or "").strip()
        else:
            return DecisionValidation(False, reason="decision must be string or object")
        if not action or len(action) > 200 or "\n" in action or "\r" in action:
            return DecisionValidation(False, reason="action must be one non-empty bounded line")
        needle = action.casefold()
        if needle.isdigit():
            matches = [item for item in offered if int(item.get("index", -1)) == int(needle)]
        else:
            matches = [
                item for item in offered
                if needle in {
                    str(item.get("id", "")).casefold(),
                    str(item.get("label", "")).casefold(),
                    str(item.get("intent", "")).casefold(),
                }
            ]
        if len(matches) != 1:
            return DecisionValidation(False, reason="action is not exactly one offered option")
        selected = matches[0]
        targets = tuple(str(value) for value in selected.get("target_ids", ()))
        if targets and target and target not in targets:
            return DecisionValidation(False, reason="target is not one offered target")
        if len(targets) > 1 and not target:
            return DecisionValidation(False, reason="decision requires one offered target")
        resolved_target = target or (targets[0] if len(targets) == 1 else "")
        return DecisionValidation(True, str(selected.get("id", "")), resolved_target)

    def schemas(self) -> dict[str, Any]:
        return {
            "observation": {
                "required": ["schema_version", "run_id", "turn", "mode", "legal_actions"],
                "optional": [
                    "situation_id", "character", "context", "objectives", "constraints",
                    "recent_actions", "recent_events",
                ],
            },
            "decision": {
                "required": ["action"],
                "optional": ["target", "parameters", "rationale", "confidence", "expected_effect"],
                "forbidden": ["roll", "damage", "outcome", "state_mutation"],
            },
        }


@lru_cache(maxsize=1)
def get_developer_backend() -> DeveloperBackend:
    return DeveloperBackend()
