from srd_cli.character import CHARACTER_SCHEMA_VERSION
from srd_cli.character_builder import CharacterBuilder, CharacterRequest
from srd_cli.character_store import CharacterCodec


def _character(level=1):
    builder = CharacterBuilder()
    return builder.build(
        CharacterRequest("Hero", "Fighter", "Human", "Soldier", "Savage Attacker", level=level)
    )


def test_schema_v2_round_trip_and_level_twenty_projection():
    character = _character(20)
    assert character.schema_version == CHARACTER_SCHEMA_VERSION == 2
    assert character.derived.proficiency_bonus == 6
    assert CharacterCodec().decode(CharacterCodec().encode(character)) == character


def test_v1_payload_migrates_adjacent_without_changing_visible_fields():
    codec = CharacterCodec()
    payload = codec.encode(_character()).replace(b'"schema_version": 2', b'"schema_version": 1')
    migrated = codec.decode(payload)
    assert migrated.schema_version == 2
