"""General AI developer backend and player-experience catalog."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from srd_cli.cli import app
from srd_cli.dev import CapabilityStatus, ExperienceDomain, get_developer_backend


def test_catalog_covers_every_domain_with_linked_descriptions():
    backend = get_developer_backend()
    assert {item.domain for item in backend.situations} == set(ExperienceDomain)
    assert len({item.id for item in backend.actions}) == len(backend.actions)
    assert len({item.id for item in backend.situations}) == len(backend.situations)
    assert all(item.description.strip() for item in (*backend.actions, *backend.situations))
    known = {item.id for item in backend.actions}
    assert all(set(item.action_ids) <= known for item in backend.situations)


def test_coverage_distinguishes_implemented_planned_and_framework_truth():
    coverage = get_developer_backend().coverage()
    assert coverage["actions"] >= 50
    assert coverage["situations"] >= 25
    assert coverage["by_status"][CapabilityStatus.IMPLEMENTED.value]["actions"] > 0
    assert coverage["by_status"][CapabilityStatus.PLANNED.value]["actions"] > 0
    assert coverage["by_status"][CapabilityStatus.FRAMEWORK.value]["situations"] > 0


def test_search_and_situation_payload_include_player_context():
    backend = get_developer_backend()
    hits = backend.search("death")
    assert any(item["id"] == "death-save" for item in hits)
    payload = backend.situation_payload("combat-encounter")
    assert payload["player_goals"]
    assert payload["stakes"]
    assert {item["id"] for item in payload["actions"]} >= {"attack", "cast-magic", "dodge"}


def test_controller_prompt_guards_engine_authority_and_invention():
    prompt = get_developer_backend().controller_prompt("investigation-mystery")
    assert "Engine state and offered legal actions are authoritative" in prompt
    assert "Never invent" in prompt
    assert '"action"' in prompt


def test_decision_validation_resolves_index_label_and_single_target():
    backend = get_developer_backend()
    offered = (
        {
            "index": 1,
            "id": "sword",
            "label": "Longsword",
            "intent": "attack",
            "target_ids": ("goblin",),
        },
    )
    by_index = backend.validate_decision("1", offered)
    by_label = backend.validate_decision({"action": "Longsword"}, offered)
    assert by_index.valid and by_index.action_id == "sword"
    assert by_index.target_id == "goblin"
    assert by_label.valid
    assert not backend.validate_decision("invent fireball", offered).valid


def test_dev_cli_exposes_json_manifest_catalog_and_schemas():
    runner = CliRunner()
    manifest = runner.invoke(app, ["dev", "manifest"])
    actions = runner.invoke(app, ["dev", "actions", "--domain", "combat", "--json"])
    schemas = runner.invoke(app, ["dev", "schemas"])
    assert manifest.exit_code == actions.exit_code == schemas.exit_code == 0
    assert json.loads(manifest.stdout)["name"] == "srd-cli-developer-backend"
    assert any(item["id"] == "attack" for item in json.loads(actions.stdout))
    assert "observation" in json.loads(schemas.stdout)
