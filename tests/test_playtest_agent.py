"""External playtest controller contract."""

from __future__ import annotations

import sys

import pytest

from srd_cli.playtest_agent import (
    AgentAction,
    AgentObservation,
    ControllerError,
    CoverageController,
    SubprocessController,
)


def _observation() -> AgentObservation:
    return AgentObservation(
        schema_version=1,
        run_id="fixture",
        turn=3,
        combat={"round": 2},
        legal_actions=(
            {"index": 1, "kind": "weapon", "id": "sword", "label": "Sword"},
            {"index": 2, "kind": "spell", "id": "bolt", "label": "Bolt"},
        ),
    )


def test_agent_action_rejects_empty_multiline_and_oversized_values():
    assert AgentAction.parse({"action": " sword "}).action == "sword"
    with pytest.raises(ControllerError, match="empty"):
        AgentAction.parse("")
    with pytest.raises(ControllerError, match="one line"):
        AgentAction.parse("sword\nclaim victory")
    with pytest.raises(ControllerError, match="exceeds"):
        AgentAction.parse("x" * 201)


def test_coverage_controller_exercises_each_action_before_repeating():
    controller = CoverageController()
    first = controller.decide(_observation())
    second = controller.decide(_observation())
    third = controller.decide(_observation())
    assert [first.action, second.action, third.action] == ["sword", "bolt", "sword"]


def test_subprocess_controller_uses_strict_json_protocol():
    program = (
        "import json,sys; o=json.load(sys.stdin); "
        "print(json.dumps({'action':'2','rationale':str(o['turn'])}))"
    )
    controller = SubprocessController(
        [sys.executable, "-c", program],
        timeout=10,
        name="fixture-ai",
    )
    action = controller.decide(_observation())
    assert action.action == "2"
    assert action.rationale == "3"
    assert action.controller == "fixture-ai"


def test_structured_general_decision_and_v2_observation():
    action = AgentAction.parse({
        "action": "search",
        "target": "door",
        "parameters": {"method": "careful"},
        "confidence": 0.75,
        "expected_effect": "discover offered evidence",
    })
    assert action.target == "door"
    assert action.parameters["method"] == "careful"
    assert action.confidence == 0.75
    observation = AgentObservation(
        schema_version=2,
        run_id="general-fixture",
        turn=1,
        combat={},
        legal_actions=({"index": 1, "id": "search", "label": "Search"},),
        mode="investigation",
        situation_id="investigation-mystery",
        objectives=("find evidence",),
    )
    payload = observation.to_dict()
    assert payload["mode"] == "investigation"
    assert payload["situation_id"] == "investigation-mystery"


def test_structured_decision_rejects_bad_confidence_and_history_bounds():
    with pytest.raises(ControllerError, match="confidence"):
        AgentAction.parse({"action": "search", "confidence": 1.1})
    with pytest.raises(ValueError, match="history"):
        AgentObservation(2, "run", 1, {}, (), recent_actions=("x",) * 65)
