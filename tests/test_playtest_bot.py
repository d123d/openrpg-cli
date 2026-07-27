"""Bounded autonomous SRD combat playtests."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from openrpg_cli.api import get_rules_api
from openrpg_cli.character_builder import CharacterBuilder, CharacterRequest
from openrpg_cli.cli import app
from openrpg_cli.playtest_agent import CallableController
from openrpg_cli.playtest_bot import (
    PlaytestCase,
    run_playtest,
    run_playtest_matrix,
    write_playtest_artifacts,
)


def _fixture():
    api = get_rules_api()
    character = CharacterBuilder(api).build(
        CharacterRequest("Ada", "Fighter", "Human", "Soldier", "Savage Attacker")
    )
    creature = api.get_creature("Goblin Warrior")
    assert creature is not None
    return character, creature


def test_playtest_is_deterministic_and_observation_is_public():
    character, creature = _fixture()
    seen = []

    def choose(observation):
        seen.append(observation)
        return {"action": "1", "rationale": "exercise offered action"}

    first = run_playtest(
        character,
        creature,
        seed=17,
        controller=CallableController(choose, name="fixture-ai"),
    )
    second = run_playtest(
        character,
        creature,
        seed=17,
        controller=CallableController(
            lambda _: {"action": "1", "rationale": "exercise offered action"},
            name="fixture-ai",
        ),
    )
    assert first.ok
    assert first.outcome in {"victory", "defeat"}
    assert first.to_dict() == second.to_dict()
    assert seen
    assert seen[0].combat["player"]["name"] == "Ada"
    assert seen[0].schema_version == 2
    assert seen[0].situation_id == "combat-encounter"
    assert seen[0].character["name"] == "Ada"
    assert seen[0].legal_actions
    assert seen[0].legal_actions[0]["description"]
    assert seen[0].legal_actions[0]["target_ids"]
    assert not hasattr(seen[0], "session")
    assert first.transcript[0].action_source == "fixture-ai"


def test_invalid_controller_action_records_fallback_without_stopping_run():
    character, creature = _fixture()
    report = run_playtest(
        character,
        creature,
        seed=7,
        controller=CallableController(lambda _: "invented fireball", name="bad-ai"),
    )
    assert report.fallback_decisions > 0
    assert any(item.code == "controller-fallback" for item in report.findings)
    assert report.outcome in {"victory", "defeat"}


def test_playtest_artifacts_contain_evidence(tmp_path):
    report = run_playtest(*_fixture(), seed=11)
    log_path, report_path = write_playtest_artifacts(
        report,
        log_dir=tmp_path / "logs",
        report_dir=tmp_path / "reports",
    )
    payload = json.loads(log_path.read_text(encoding="utf-8"))
    markdown = report_path.read_text(encoding="utf-8")
    assert payload["seed"] == 11
    assert payload["transcript"]
    assert "## Findings" in markdown
    assert "RNG draws=" in markdown


def test_matrix_runner_replays_exact_mechanics_and_aggregates_coverage():
    character, creature = _fixture()
    report = run_playtest_matrix(
        (
            PlaytestCase(character, creature, 7),
            PlaytestCase(character, creature, 11),
        ),
    )
    assert report.ok
    assert len(report.runs) == 2
    assert not report.deterministic_failures
    assert sum(report.outcome_coverage.values()) == 2
    assert report.interaction_coverage["attack"] > 0


def test_playtest_cli_runs_default_agent_and_saves_artifacts(tmp_path):
    result = CliRunner().invoke(
        app,
        [
            "playtest",
            "--monster", "Goblin Warrior",
            "--seed", "17",
            "--log-dir", str(tmp_path / "logs"),
            "--report-dir", str(tmp_path / "reports"),
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert "PASS:" in result.stdout
    assert list((tmp_path / "logs").glob("*.json"))
    assert list((tmp_path / "reports").glob("*.md"))
