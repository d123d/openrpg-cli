from __future__ import annotations

import json

from typer.testing import CliRunner

from srd_cli.cli import app

runner = CliRunner()


def create_args(root):
    return ["character", "create", "--name", "Ada", "--class", "Wizard",
            "--species", "Human", "--background", "Sage", "--feat", "Magic Initiate",
            "--root", str(root)]


def test_create_headless_json(tmp_path):
    result = runner.invoke(app, create_args(tmp_path) + ["--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["identity"]["name"] == "Ada"
    assert (tmp_path / "ada.json").is_file()


def test_create_invalid_has_candidates(tmp_path):
    args = create_args(tmp_path)
    args[args.index("Wizard")] = "Wizrd"
    result = runner.invoke(app, args)
    assert result.exit_code == 2
    assert "Wizard" in result.output


def test_show_list_validate_workflow(tmp_path):
    assert runner.invoke(app, create_args(tmp_path)).exit_code == 0
    shown = runner.invoke(app, ["character", "show", "ada", "--root", str(tmp_path), "--json"])
    assert shown.exit_code == 0
    assert json.loads(shown.output)["identity"]["class"]["name"] == "Wizard"
    listed = runner.invoke(app, ["character", "list", "--root", str(tmp_path)])
    assert listed.exit_code == 0 and "Ada" in listed.output and "PASS" in listed.output
    valid = runner.invoke(app, ["character", "validate", "ada", "--root", str(tmp_path)])
    assert valid.exit_code == 0 and "PASS" in valid.output


def test_missing_and_tampered_fail_without_traceback(tmp_path):
    missing = runner.invoke(app, ["character", "show", "missing", "--root", str(tmp_path)])
    assert missing.exit_code == 2 and "Traceback" not in missing.output
    assert runner.invoke(app, create_args(tmp_path)).exit_code == 0
    path = tmp_path / "ada.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["derived"]["max_hp"] = 999
    path.write_text(json.dumps(data), encoding="utf-8")
    bad = runner.invoke(app, ["character", "validate", "ada", "--root", str(tmp_path)])
    assert bad.exit_code == 2 and "derived" in bad.output


def test_legacy_commands_smoke():
    for args in (["info"], ["categories"], ["list", "spells", "--limit", "1"],
                 ["show", "spells", "Fire Bolt"], ["search", "fire"], ["roll", "1d6", "--seed", "1"], ["audit"]):
        result = runner.invoke(app, args)
        assert result.exit_code == 0, (args, result.output)
