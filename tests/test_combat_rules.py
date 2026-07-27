from srd_cli.combat_rules import CombatRules
from srd_cli.normalized import NormalizedRepository


def test_combat_relationships_are_exhaustive():
    n = NormalizedRepository()
    rules = CombatRules(n)
    assert sum(len(v.traits) for v in rules.creatures) == len(n.load("CreatureTrait.json"))
    assert sum(len(v.actions) for v in rules.creatures) == len(n.load("CreatureAction.json"))
    assert sum(len(a.attacks) for v in rules.creatures for a in v.actions) == len(n.load("CreatureActionAttack.json"))
    assert sum(len(v.properties) for v in rules.weapons) == len(n.load("WeaponPropertyAssignment.json"))


def test_resolved_weapon_properties_and_exact_lookup():
    rules = CombatRules()
    battleaxe = rules.get_weapon("Battleaxe")
    assert battleaxe.properties
    assert all(item.property.name for item in battleaxe.properties)
    assert rules.get_creature("Goblin") is None
