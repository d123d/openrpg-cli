from typer.testing import CliRunner

from srd_cli.cli import app


def test_play_guides_creation_creature_and_actions(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    result = CliRunner().invoke(
        app,
        ["play", "--seed", "7"],
        input=(
            "create\nAda\nFighter\nHuman\nSoldier\nSavage Attacker\nn\n"
            "Goblin Warrior\n" + "1\n" * 100
        ),
    )
    assert result.exit_code == 0
    assert "Creature choices:" in result.stdout
    assert "Action" in result.stdout
    assert "Result:" in result.stdout
