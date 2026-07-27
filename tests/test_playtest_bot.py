"""Bounded autonomous SRD combat playtests."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from srd_cli.api import get_rules_api
from srd_cli.character_builder import CharacterBuilder, CharacterRequest
from srd_cli.cli import app
from srd_cli.playtest_agent import CallableController
from srd_cli.playtest_bot import run_playtest, write_playtest_artifacts


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
    assert seen[0].legal_actions
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
