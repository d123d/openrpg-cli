from openrpg_cli.api import get_rules_api
from openrpg_cli.character_builder import CharacterBuilder, CharacterRequest
from openrpg_cli.combat_session import CombatSession
from openrpg_cli.interfaces.v1_compat import adapt_combat_result


def test_adapter_preserves_legacy_result_and_rng() -> None:
    api = get_rules_api()
    hero = CharacterBuilder(api).build(
        CharacterRequest("Ada", "Fighter", "Human", "Soldier", "Savage Attacker")
    )
    result = CombatSession(hero, api.get_creature("Goblin Warrior"), 41, api=api).run_auto()
    before = repr(result)
    _, rng, log = adapt_combat_result(result)
    assert repr(result) == before
    assert rng.draws == 0
    assert len(log.records) == len(result.events)
