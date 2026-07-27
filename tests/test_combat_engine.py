from srd_cli.api import get_rules_api
from srd_cli.character import AbilityScores
from srd_cli.character_builder import CharacterBuilder, CharacterRequest
from srd_cli.combat import CombatEngine, CombatError


def hero():
    return CharacterBuilder(get_rules_api()).build(CharacterRequest(
        "Ada", "Fighter", "Human", "Soldier", "Savage Attacker",
        AbilityScores(15, 14, 13, 12, 10, 8), (), (),
    ))


def test_seeded_engine_and_invalid_action_atomic():
    creature = get_rules_api().get_creature("Goblin Warrior")
    one, two = CombatEngine(hero(), creature, 42), CombatEngine(hero(), creature, 42)
    assert one.state == two.state
    before = one.rng.to_dict()
    if one.state.active_actor == "player":
        try:
            one.act("player", "not-equipped")
        except CombatError:
            pass
        assert one.rng.to_dict() == before
