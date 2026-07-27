from typer.testing import CliRunner

from srd_cli import get_rules_api
from srd_cli.cli import app


def test_public_api_is_cached_and_complete():
    api = get_rules_api()
    assert api is get_rules_api()
    assert api.get_class("Barbarian")
    assert api.get_creature("Goblin Warrior")
    assert api.get_weapon("Battleaxe")
    assert api.get_spell("Fireball")
    assert api.get_class("barb") is None


def test_show_joined_and_json_compatibility():
    runner = CliRunner()
    joined = runner.invoke(app, ["show", "classes", "Barbarian"])
    assert joined.exit_code == 0
    assert "Features" in joined.stdout
    raw = runner.invoke(app, ["show", "classes", "Barbarian", "--json"])
    assert raw.exit_code == 0
    assert '"hit_dice"' in raw.stdout
    assert "Features" not in raw.stdout
