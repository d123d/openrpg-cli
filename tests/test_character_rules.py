from srd_cli.character_rules import CharacterRules
from srd_cli.normalized import NormalizedRepository


def test_character_relationships_are_exhaustive():
    n = NormalizedRepository()
    rules = CharacterRules(n)
    assert sum(len(v.features) for v in rules.classes) == len(n.load("ClassFeature.json"))
    assert sum(len(f.items) for v in rules.classes for f in v.features) == len(n.load("ClassFeatureItem.json"))
    assert sum(len(v.traits) for v in rules.species) == len(n.load("SpeciesTrait.json"))
    assert sum(len(v.benefits) for v in rules.backgrounds) == len(n.load("BackgroundBenefit.json"))
    assert sum(len(v.benefits) for v in rules.feats) == len(n.load("FeatBenefit.json"))
    assert sum(len(v.options) for v in rules.spells) == len(n.load("SpellCastingOption.json"))


def test_exact_lookup_and_nested_views():
    rules = CharacterRules()
    assert rules.get_class("Barbarian").features
    assert rules.get_class("barb") is None
    assert rules.get_species("Dwarf").traits
    assert rules.get_background("Acolyte").benefits

