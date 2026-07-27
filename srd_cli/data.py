"""Read-only access to bundled SRD 5.2.1 data.

Data is vendored from the Open5e conversion of Wizards' SRD-only subtree.
This module deliberately has no adventure, campaign-setting, or third-party
content fallback.
"""

from __future__ import annotations

import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

DATA_ROOT = Path(__file__).resolve().parent / "data" / "srd521"
MANIFEST_PATH = DATA_ROOT / "manifest.json"
DOCUMENT_KEY = "srd-2024"

# Public categories. Supporting relationship tables remain searchable through
# their parent entities but stay out of the default browsing surface.
CATEGORY_TABLES: dict[str, tuple[str, ...]] = {
    "abilities": ("AbilityDescription.json",),
    "alignments": ("AlignmentDescription.json",),
    "armor": ("Armor.json",),
    "backgrounds": ("Background.json",),
    "classes": ("CharacterClass.json",),
    "conditions": ("ConditionDescription.json",),
    "creatures": ("Creature.json",),
    "creature-types": ("CreatureTypeDescription.json",),
    "damage-types": ("DamageTypeDescription.json",),
    "feats": ("Feat.json",),
    "items": ("Item.json", "MagicItem.json"),
    "languages": ("Language.json",),
    "rules": ("Rule.json", "RuleSet.json"),
    "services": ("Service.json", "Services.json"),
    "sizes": ("Size.json",),
    "skills": ("SkillDescription.json",),
    "species": ("Species.json",),
    "spells": ("Spell.json",),
    "spell-schools": ("SpellSchool.json",),
    "weapons": ("Weapon.json",),
}

_CATEGORY_ALIASES = {
    "ability": "abilities",
    "alignment": "alignments",
    "armors": "armor",
    "background": "backgrounds",
    "class": "classes",
    "condition": "conditions",
    "creature": "creatures",
    "monster": "creatures",
    "monsters": "creatures",
    "creature-type": "creature-types",
    "damage-type": "damage-types",
    "feat": "feats",
    "item": "items",
    "language": "languages",
    "rule": "rules",
    "service": "services",
    "size": "sizes",
    "skill": "skills",
    "specie": "species",
    "race": "species",
    "races": "species",
    "spell": "spells",
    "spell-school": "spell-schools",
    "weapon": "weapons",
}


def normalize(text: str) -> str:
    """Normalize names and primary keys for stable CLI matching."""
    text = text.strip().lower().replace("_", "-")
    text = re.sub(r"^srd-2024[-_]", "", text)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def category_name(value: str) -> str:
    key = normalize(value)
    key = _CATEGORY_ALIASES.get(key, key)
    if key not in CATEGORY_TABLES:
        choices = ", ".join(sorted(CATEGORY_TABLES))
        raise KeyError(f"unknown category {value!r}; choose: {choices}")
    return key


class SRDRepository:
    """Lazy, immutable view over bundled JSON tables."""

    def __init__(self, root: Path = DATA_ROOT) -> None:
        self.root = root

    @lru_cache(maxsize=None)
    def table(self, filename: str) -> tuple[dict[str, Any], ...]:
        path = self.root / filename
        if not path.is_file():
            raise FileNotFoundError(f"missing SRD table: {path}")
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError(f"SRD table must contain a JSON array: {filename}")
        return tuple(row for row in raw if isinstance(row, dict))

    @lru_cache(maxsize=1)
    def manifest(self) -> dict[str, Any]:
        if not (self.root / "manifest.json").is_file():
            raise FileNotFoundError(f"missing SRD manifest: {self.root / 'manifest.json'}")
        raw = json.loads((self.root / "manifest.json").read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("SRD manifest must contain a JSON object")
        return raw

    def categories(self) -> tuple[str, ...]:
        return tuple(sorted(CATEGORY_TABLES))

    def entries(self, category: str) -> list[dict[str, Any]]:
        key = category_name(category)
        entries: list[dict[str, Any]] = []
        for filename in CATEGORY_TABLES[key]:
            for row in self.table(filename):
                fields = dict(row.get("fields") or {})
                fields["_pk"] = str(row.get("pk") or "")
                fields["_table"] = filename
                entries.append(fields)
        return entries

    @staticmethod
    def entry_name(entry: dict[str, Any]) -> str:
        return str(
            entry.get("name")
            or entry.get("display_name")
            or entry.get("describes")
            or entry.get("_pk")
            or ""
        )

    def list_names(self, category: str) -> list[str]:
        return sorted(
            (self.entry_name(entry) for entry in self.entries(category)),
            key=str.casefold,
        )

    def find(self, category: str, query: str) -> dict[str, Any] | None:
        needle = normalize(query)
        entries = self.entries(category)
        for entry in entries:
            candidates = (self.entry_name(entry), str(entry.get("_pk") or ""))
            if any(normalize(value) == needle for value in candidates):
                return entry
        hits = [
            entry
            for entry in entries
            if needle in normalize(self.entry_name(entry))
            or needle in normalize(str(entry.get("_pk") or ""))
        ]
        return hits[0] if len(hits) == 1 else None

    def search(
        self,
        query: str,
        *,
        category: str | None = None,
        limit: int = 20,
    ) -> list[tuple[str, dict[str, Any]]]:
        needle = query.strip().casefold()
        if not needle:
            return []
        categories: Iterable[str]
        categories = (category_name(category),) if category else self.categories()
        hits: list[tuple[int, str, dict[str, Any]]] = []
        for current in categories:
            for entry in self.entries(current):
                name = self.entry_name(entry)
                haystack = " ".join(
                    str(value)
                    for key, value in entry.items()
                    if key not in {"_table"} and value is not None
                ).casefold()
                if needle not in haystack:
                    continue
                exact = normalize(name) == normalize(query)
                prefix = normalize(name).startswith(normalize(query))
                rank = 0 if exact else (1 if prefix else 2)
                hits.append((rank, current, entry))
        hits.sort(key=lambda hit: (hit[0], self.entry_name(hit[2]).casefold(), hit[1]))
        return [(current, entry) for _, current, entry in hits[: max(1, limit)]]

    def stats(self) -> dict[str, int]:
        return {category: len(self.entries(category)) for category in self.categories()}

    def verify(self) -> list[str]:
        """Return audit errors. Empty list means bundle matches manifest."""
        errors: list[str] = []
        manifest = self.manifest()
        declared = manifest.get("declared_files") or {}
        if not isinstance(declared, dict):
            return ["manifest declared_files must be an object"]

        actual_files = {path.name for path in self.root.glob("*.json")} - {"manifest.json"}
        declared_files = set(declared)
        for name in sorted(declared_files - actual_files):
            errors.append(f"missing declared file: {name}")
        for name in sorted(actual_files - declared_files):
            errors.append(f"undeclared JSON file: {name}")

        for name, expected in declared.items():
            path = self.root / name
            if not path.is_file():
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != expected.get("sha256"):
                errors.append(f"hash mismatch: {name}")
            try:
                rows = self.table(name)
            except (ValueError, json.JSONDecodeError) as exc:
                errors.append(f"invalid JSON table {name}: {exc}")
                continue
            if len(rows) != expected.get("record_count"):
                errors.append(
                    f"record count mismatch: {name} "
                    f"({len(rows)} != {expected.get('record_count')})"
                )
            for index, row in enumerate(rows):
                fields = row.get("fields") or {}
                document = fields.get("document")
                if document is not None and document != DOCUMENT_KEY:
                    errors.append(f"foreign document in {name}[{index}]: {document}")
                    break
        return errors


@lru_cache(maxsize=1)
def get_repository() -> SRDRepository:
    return SRDRepository()

