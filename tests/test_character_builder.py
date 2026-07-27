from __future__ import annotations

import pytest

from srd_cli.api import get_rules_api
from srd_cli.character import AbilityScores, Character
from srd_cli.character_builder import CharacterBuilder, CharacterRequest, ChoiceError


def test_contracts_reject_invalid_values():
    with pytest.raises(ValueError, match="unknown"):
        AbilityScores.from_mapping({"str": 10, "dex": 10, "con": 10, "int": 10, "wis": 10, "cha": 10, "luck": 10})
    with pytest.raises(ValueError, match="integer"):
        AbilityScores(True, 10, 10, 10, 10, 10)


def request(**changes):
    values = dict(name="Ada", class_identity="Wizard", species_identity="Human",
                  background_identity="Sage", feat_identity="Magic Initiate")
    values.update(changes)
    return CharacterRequest(**values)


def test_choices_defaults_are_deterministic():
    builder = CharacterBuilder(get_rules_api())
    one = builder.build(request())
    assert one == builder.build(request())
    assert sorted(score for _, score in one.scores.items()) == [8, 10, 12, 13, 14, 15]


def test_choices_cover_all_base_classes():
    builder = CharacterBuilder(get_rules_api())
    for cls in builder.classes:
        assert isinstance(builder.build(request(class_identity=cls.name)), Character)


def test_suggestions_are_stable():
    with pytest.raises(ChoiceError, match=r"class.*Wizard"):
        CharacterBuilder(get_rules_api()).build(request(class_identity="Wizrd"))


def test_defaults_and_derived_stats():
    char = CharacterBuilder(get_rules_api()).build(request())
    assert char.level == 1
    assert char.derived.proficiency_bonus == 2
    assert char.derived.max_hp == 6 + char.derived.modifiers["con"]
    assert char.derived.spell_save_dc == 8 + 2 + char.derived.modifiers["int"]


def test_explicit_choices():
    scores = AbilityScores(8, 14, 13, 15, 12, 10)
    char = CharacterBuilder(get_rules_api()).build(request(scores=scores, spells=("Fire Bolt",)))
    assert char.scores == scores
    assert [spell.name for spell in char.spells] == ["Fire Bolt"]
