from srd_cli.api import get_rules_api
from srd_cli.character import AbilityScores
from srd_cli.character_builder import CharacterBuilder, CharacterRequest
from srd_cli.combat_session import CombatSession, render_combat_json, render_transcript


def test_auto_output_is_byte_stable():
    hero = CharacterBuilder(get_rules_api()).build(CharacterRequest(
        "Ada", "Fighter", "Human", "Soldier", "Savage Attacker",
        AbilityScores(15, 14, 13, 12, 10, 8), (), ()))
    monster = get_rules_api().get_creature("Goblin Warrior")
    a = CombatSession(hero, monster, 7).run_auto()
    b = CombatSession(hero, monster, 7).run_auto()
    assert render_combat_json(a) == render_combat_json(b)
    assert render_transcript(a) == render_transcript(b)
