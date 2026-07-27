from openrpg_cli.api import get_rules_api
from openrpg_cli.character import AbilityScores
from openrpg_cli.character_builder import CharacterBuilder, CharacterRequest
from openrpg_cli.combat_session import CombatSession, render_combat_json, render_transcript
from openrpg_cli.combat import CombatError
from dataclasses import replace
import pytest


def test_auto_output_is_byte_stable():
    hero = CharacterBuilder(get_rules_api()).build(CharacterRequest(
        "Ada", "Fighter", "Human", "Soldier", "Savage Attacker",
        AbilityScores(15, 14, 13, 12, 10, 8), (), ()))
    monster = get_rules_api().get_creature("Goblin Warrior")
    a = CombatSession(hero, monster, 7).run_auto()
    b = CombatSession(hero, monster, 7).run_auto()
    assert render_combat_json(a) == render_combat_json(b)
    assert render_transcript(a) == render_transcript(b)


def test_unarmed_is_always_legal_and_invalid_action_is_domain_error():
    hero = CharacterBuilder(get_rules_api()).build(CharacterRequest(
        "Ada", "Fighter", "Human", "Soldier", "Savage Attacker",
        AbilityScores(15, 14, 13, 12, 10, 8), (), ()))
    monster = get_rules_api().get_creature("Goblin Warrior")
    session = CombatSession(replace(hero, equipment=(), derived=replace(hero.derived, attacks=())), monster, 2)
    assert ("unarmed", "unarmed") in session.engine.legal_player_actions()
    if session.engine.state.active_actor == "player":
        with pytest.raises(CombatError):
            session.engine.act("player", "not-an-action")
