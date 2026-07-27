from pathlib import Path

from typer.testing import CliRunner

from srd_cli.api import get_rules_api
from srd_cli.character_builder import CharacterBuilder, CharacterRequest
from srd_cli.character_store import CharacterStore
from srd_cli.cli import app


def _character(path: Path) -> Path:
    builder = CharacterBuilder(get_rules_api())
    hero = builder.build(
        CharacterRequest("Ada", "Fighter", "Human", "Soldier", "Savage Attacker")
    )
    return CharacterStore(builder, root=path).save(hero)


def test_combat_auto_is_byte_identical(tmp_path):
    character = _character(tmp_path)
    args = [
        "combat", "--character", str(character), "--monster", "Goblin Warrior",
        "--seed", "17", "--auto", "--json",
    ]
    first = CliRunner().invoke(app, args)
    second = CliRunner().invoke(app, args)
    assert first.exit_code == second.exit_code == 0
    assert first.stdout_bytes == second.stdout_bytes


def test_combat_interactive_prompts_for_action(tmp_path):
    result = CliRunner().invoke(
        app,
        [
            "combat", "--character", str(_character(tmp_path)),
            "--monster", "Goblin Warrior", "--seed", "7",
        ],
        input="1\n" * 100,
    )
    assert result.exit_code == 0
    assert "Action" in result.stdout
    assert "Result:" in result.stdout
