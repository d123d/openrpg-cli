from dataclasses import FrozenInstanceError

import pytest

from srd_cli.normalized import NormalizedRepository, TABLE_CATALOG


def test_catalog_matches_manifest_and_loads_deterministically():
    source = NormalizedRepository()
    assert set(TABLE_CATALOG) == set(source.repository.manifest()["declared_files"])
    assert len(TABLE_CATALOG) == 37
    first = source.load("Creature.json")
    assert first == source.load("Creature.json")
    assert tuple(x.pk for x in first) == tuple(sorted(x.pk for x in first))


def test_models_and_nested_fields_are_immutable():
    entity = NormalizedRepository().load("Spell.json")[0]
    with pytest.raises(FrozenInstanceError):
        entity.pk = "changed"
    with pytest.raises(TypeError):
        entity.data["name"] = "changed"

