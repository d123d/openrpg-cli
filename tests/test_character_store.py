from __future__ import annotations

import json

import pytest

from openrpg_cli.api import get_rules_api
from openrpg_cli.character_builder import CharacterBuilder, CharacterRequest
from openrpg_cli.character_store import CharacterCodec, CharacterStore, CharacterValidationError


def character():
    return CharacterBuilder(get_rules_api()).build(CharacterRequest(
        "Éowyn", "Fighter", "Human", "Soldier", "Alert"))


def test_codec_round_trip_is_canonical():
    codec = CharacterCodec()
    payload = codec.encode(character())
    assert codec.encode(codec.decode(payload)) == payload
    assert payload.endswith(b"\n")


def test_schema_and_duplicate_keys_rejected():
    codec = CharacterCodec()
    with pytest.raises(ValueError, match="duplicate"):
        codec.decode(b'{"schema_version":1,"schema_version":1}')
    data = json.loads(codec.encode(character()))
    data["schema_version"] = 99
    with pytest.raises(ValueError, match="migration"):
        codec.decode(json.dumps(data).encode())


def test_store_round_trip_and_listing(tmp_path):
    store = CharacterStore(CharacterBuilder(get_rules_api()), root=tmp_path)
    path = store.save(character())
    assert path.name == "eowyn.json"
    assert store.load(path) == character()
    assert store.list()[0].name == "Éowyn"


def test_tampered_derived_is_rejected(tmp_path):
    store = CharacterStore(CharacterBuilder(get_rules_api()), root=tmp_path)
    path = store.save(character())
    data = json.loads(path.read_text(encoding="utf-8"))
    data["derived"]["armor_class"] = 99
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(CharacterValidationError, match="derived"):
        store.load(path)


def test_traversal_and_symlink_rejected(tmp_path):
    store = CharacterStore(CharacterBuilder(get_rules_api()), root=tmp_path)
    with pytest.raises(ValueError, match="name"):
        store.resolve_name("../escape")
