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
