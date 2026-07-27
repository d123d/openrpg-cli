"""Canonical JSON codec and safe filesystem store for characters."""

from __future__ import annotations

import json
import os
import re
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from srd_cli.character import (
    ABILITIES, CHARACTER_SCHEMA_VERSION, AbilityScores, AttackSummary, Character,
    ChoiceRecord, DerivedStats, EntityRef,
)
from srd_cli.character_builder import CharacterBuilder, CharacterRequest

MAX_CHARACTER_BYTES = 1_000_000


class CharacterValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    path: str
    message: str


@dataclass(frozen=True, slots=True)
class CharacterMetadata:
    name: str
    class_name: str
    species_name: str
    path: Path
    valid: bool
    error: str | None = None


def character_mapping(c: Character) -> dict[str, Any]:
    def ref(x):
        return {"pk": x.pk, "name": x.name}
    return {
        "schema_version": c.schema_version,
        "identity": {
            "name": c.name, "level": c.level, "class": ref(c.class_ref),
            "species": ref(c.species_ref), "background": ref(c.background_ref),
            "feat": ref(c.feat_ref),
        },
        "scores": {key: value for key, value in c.scores.items()},
        "equipment": [ref(x) for x in c.equipment],
        "spells": [ref(x) for x in c.spells],
        "choices": [{"field": x.field, "values": list(x.values)} for x in c.choices],
        "derived": {
            "modifiers": dict(c.derived.modifiers),
            "proficiency_bonus": c.derived.proficiency_bonus,
            "max_hp": c.derived.max_hp, "current_hp": c.derived.current_hp,
            "armor_class": c.derived.armor_class, "saves": dict(c.derived.saves),
            "skills": dict(c.derived.skills),
            "attacks": [{
                "weapon": ref(x.weapon), "ability": x.ability,
                "attack_bonus": x.attack_bonus, "damage": x.damage,
            } for x in c.derived.attacks],
            "spellcasting_ability": c.derived.spellcasting_ability,
            "spell_attack_bonus": c.derived.spell_attack_bonus,
            "spell_save_dc": c.derived.spell_save_dc,
        },
    }


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"$: duplicate key {key!r}")
        result[key] = value
    return result


def _expect_map(value, path, keys):
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected object")
    extra, missing = sorted(set(value) - set(keys)), sorted(set(keys) - set(value))
    if extra or missing:
        raise ValueError(f"{path}: extra={extra}, missing={missing}")
    return value


def _int(value, path):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{path}: expected integer")
    return value


def _str(value, path):
    if not isinstance(value, str):
        raise ValueError(f"{path}: expected string")
    return value


def _ref(value, path):
    obj = _expect_map(value, path, ("pk", "name"))
    return EntityRef(_str(obj["pk"], path + ".pk"), _str(obj["name"], path + ".name"))


class CharacterCodec:
    def encode(self, character: Character) -> bytes:
        return (json.dumps(character_mapping(character), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")

    def decode(self, payload: bytes) -> Character:
        if len(payload) > MAX_CHARACTER_BYTES:
            raise ValueError(f"$: file exceeds {MAX_CHARACTER_BYTES} bytes")
        try:
            root = json.loads(payload.decode("utf-8"), object_pairs_hook=_pairs)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"$: malformed JSON: {exc}") from exc
        root = _expect_map(root, "$", ("schema_version", "identity", "scores", "equipment", "spells", "choices", "derived"))
        version = _int(root["schema_version"], "$.schema_version")
        if version != CHARACTER_SCHEMA_VERSION:
            raise ValueError(f"$.schema_version: {version} requires migration; supported={CHARACTER_SCHEMA_VERSION}")
        identity = _expect_map(root["identity"], "$.identity", ("name", "level", "class", "species", "background", "feat"))
        scores_obj = _expect_map(root["scores"], "$.scores", ABILITIES)
        scores = AbilityScores.from_mapping({key: _int(scores_obj[key], f"$.scores.{key}") for key in ABILITIES})
        def refs(value, path):
            if not isinstance(value, list):
                raise ValueError(f"{path}: expected array")
            return tuple(_ref(x, f"{path}[{i}]") for i, x in enumerate(value))
        choices = []
        if not isinstance(root["choices"], list):
            raise ValueError("$.choices: expected array")
        for i, value in enumerate(root["choices"]):
            obj = _expect_map(value, f"$.choices[{i}]", ("field", "values"))
            if not isinstance(obj["values"], list) or not all(isinstance(x, str) for x in obj["values"]):
                raise ValueError(f"$.choices[{i}].values: expected string array")
            choices.append(ChoiceRecord(_str(obj["field"], f"$.choices[{i}].field"), tuple(obj["values"])))
        d = _expect_map(root["derived"], "$.derived", (
            "modifiers", "proficiency_bonus", "max_hp", "current_hp", "armor_class",
            "saves", "skills", "attacks", "spellcasting_ability", "spell_attack_bonus", "spell_save_dc",
        ))
        def int_map(value, path):
            if not isinstance(value, dict) or not all(isinstance(k, str) for k in value):
                raise ValueError(f"{path}: expected object")
            return {k: _int(v, f"{path}.{k}") for k, v in value.items()}
        attacks = []
        if not isinstance(d["attacks"], list):
            raise ValueError("$.derived.attacks: expected array")
        for i, value in enumerate(d["attacks"]):
            obj = _expect_map(value, f"$.derived.attacks[{i}]", ("weapon", "ability", "attack_bonus", "damage"))
            attacks.append(AttackSummary(_ref(obj["weapon"], f"$.derived.attacks[{i}].weapon"), _str(obj["ability"], "ability"), _int(obj["attack_bonus"], "attack_bonus"), _str(obj["damage"], "damage")))
        def nullable_int(value, path):
            return None if value is None else _int(value, path)
        casting = d["spellcasting_ability"]
        if casting is not None and not isinstance(casting, str):
            raise ValueError("$.derived.spellcasting_ability: expected string or null")
        derived = DerivedStats(
            int_map(d["modifiers"], "$.derived.modifiers"), _int(d["proficiency_bonus"], "$.derived.proficiency_bonus"),
            _int(d["max_hp"], "$.derived.max_hp"), _int(d["current_hp"], "$.derived.current_hp"),
            _int(d["armor_class"], "$.derived.armor_class"), int_map(d["saves"], "$.derived.saves"),
            int_map(d["skills"], "$.derived.skills"), tuple(attacks), casting,
            nullable_int(d["spell_attack_bonus"], "$.derived.spell_attack_bonus"),
            nullable_int(d["spell_save_dc"], "$.derived.spell_save_dc"),
        )
        return Character(
            _str(identity["name"], "$.identity.name"), _ref(identity["class"], "$.identity.class"),
            _ref(identity["species"], "$.identity.species"), _ref(identity["background"], "$.identity.background"),
            _ref(identity["feat"], "$.identity.feat"), scores, refs(root["equipment"], "$.equipment"),
            refs(root["spells"], "$.spells"), tuple(choices), derived,
            _int(identity["level"], "$.identity.level"), version,
        )


def validate_character(character: Character, builder: CharacterBuilder) -> tuple[ValidationIssue, ...]:
    try:
        rebuilt = builder.build(CharacterRequest(
            character.name, character.class_ref.pk, character.species_ref.pk,
            character.background_ref.pk, character.feat_ref.pk, character.scores,
            tuple(x.pk for x in character.equipment), tuple(x.pk for x in character.spells),
            character.level,
        ))
    except ValueError as exc:
        return (ValidationIssue("$.references", str(exc)),)
    issues = []
    for path, stored, current in (
        ("$.identity", (character.class_ref, character.species_ref, character.background_ref, character.feat_ref),
         (rebuilt.class_ref, rebuilt.species_ref, rebuilt.background_ref, rebuilt.feat_ref)),
        ("$.equipment", character.equipment, rebuilt.equipment),
        ("$.spells", character.spells, rebuilt.spells),
        ("$.choices", character.choices, rebuilt.choices),
        ("$.derived", character.derived, rebuilt.derived),
    ):
        if stored != current:
            issues.append(ValidationIssue(path, "stored value differs from SRD rebuild"))
    return tuple(issues)


class CharacterStore:
    def __init__(self, builder: CharacterBuilder, root: Path | None = None) -> None:
        self.builder = builder
        self.root = Path(root) if root is not None else Path.home() / ".srd-cli" / "characters"
        self.codec = CharacterCodec()

    def resolve_name(self, name: str) -> Path:
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", name):
            raise ValueError("name: invalid character filename")
        filename = name if name.endswith(".json") else f"{name}.json"
        return self.root / filename

    @staticmethod
    def _slug(name: str) -> str:
        text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().casefold()
        slug = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
        if not slug:
            raise ValueError("name: cannot produce safe filename")
        return slug[:100]

    def save(self, character: Character, path: Path | None = None, *, overwrite: bool = False) -> Path:
        target = Path(path) if path is not None else self.root / f"{self._slug(character.name)}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            raise ValueError("path: refusing symlink target")
        if target.exists() and not overwrite:
            raise FileExistsError(str(target))
        payload = self.codec.encode(character)
        fd, temp_name = tempfile.mkstemp(prefix=".character-", dir=target.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, target)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
        return target

    def load(self, path: Path | str) -> Character:
        source = Path(path)
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"path: not a regular character file: {source}")
        with source.open("rb") as stream:
            payload = stream.read(MAX_CHARACTER_BYTES + 1)
        character = self.codec.decode(payload)
        issues = validate_character(character, self.builder)
        if issues:
            raise CharacterValidationError("; ".join(f"{x.path}: {x.message}" for x in issues))
        return character

    def list(self) -> tuple[CharacterMetadata, ...]:
        if not self.root.exists():
            return ()
        rows = []
        for path in sorted(self.root.glob("*.json"), key=lambda p: p.name.casefold()):
            if path.is_symlink() or not path.is_file():
                continue
            try:
                char = self.load(path)
                rows.append(CharacterMetadata(char.name, char.class_ref.name, char.species_ref.name, path, True))
            except (OSError, ValueError) as exc:
                rows.append(CharacterMetadata(path.stem, "", "", path, False, str(exc)))
        return tuple(rows)
