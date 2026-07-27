"""Discovery, selection, and license-boundary audits for bundled system packs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

PACKS_ROOT = Path(__file__).resolve().parent / "data" / "providers"


@dataclass(frozen=True)
class SystemPack:
    """One independently licensed data pack."""

    root: Path
    manifest: dict[str, Any]

    @property
    def pack_id(self) -> str:
        return str(self.manifest["pack_id"])

    @property
    def system_id(self) -> str:
        return str(self.manifest["system_id"])

    @property
    def enabled(self) -> bool:
        return bool(self.manifest.get("enabled"))

    def audit(self) -> list[str]:
        errors: list[str] = []
        required = ("pack_id", "system_id", "provider_id", "source_document_ids", "license")
        for key in required:
            if not self.manifest.get(key):
                errors.append(f"{self.pack_id}: missing manifest field {key}")
        for key in ("notice_file", "attribution_file"):
            filename = self.manifest.get(key)
            if not filename or not (self.root / str(filename)).is_file():
                errors.append(f"{self.pack_id}: missing {key}")
        if self.manifest.get("quarantined") and self.enabled:
            errors.append(f"{self.pack_id}: quarantined pack cannot be enabled")

        allowed = set(self.manifest.get("allowlist", {}).get("document_ids", []))
        sources = set(self.manifest.get("source_document_ids", []))
        if not sources or allowed != sources:
            errors.append(f"{self.pack_id}: document allowlist must equal source_document_ids")

        declared = self.manifest.get("declared_files", {})
        actual = {path.name for path in self.root.glob("*.json")} - {"manifest.json"}
        if set(declared) != actual:
            errors.append(f"{self.pack_id}: declared JSON files differ from pack contents")
        for name, metadata in declared.items():
            path = self.root / name
            if not path.is_file():
                continue
            if hashlib.sha256(path.read_bytes()).hexdigest() != metadata.get("sha256"):
                errors.append(f"{self.pack_id}: hash mismatch: {name}")
                continue
            rows = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(rows, list) or len(rows) != metadata.get("record_count"):
                errors.append(f"{self.pack_id}: record count mismatch: {name}")
                continue
            for index, row in enumerate(rows):
                document = (row.get("fields") or {}).get("document")
                if document is not None and document not in allowed:
                    errors.append(
                        f"{self.pack_id}: foreign document in {name}[{index}]: {document}"
                    )
                    break
        return errors


class SystemRegistry:
    """Registry preserving pack namespaces; selection never merges pack data."""

    def __init__(self, root: Path = PACKS_ROOT) -> None:
        self.root = root

    def packs(self, *, include_disabled: bool = True) -> tuple[SystemPack, ...]:
        found: list[SystemPack] = []
        for path in sorted(self.root.glob("*/packs/*/manifest.json")):
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                pack = SystemPack(path.parent, raw)
                if include_disabled or pack.enabled:
                    found.append(pack)
        return tuple(found)

    def get(self, identity: str, *, allow_disabled: bool = False) -> SystemPack:
        matches = [
            pack
            for pack in self.packs()
            if identity in {pack.pack_id, pack.system_id}
        ]
        if len(matches) != 1:
            raise KeyError(f"unknown or ambiguous system pack: {identity}")
        pack = matches[0]
        if not pack.enabled and not allow_disabled:
            raise PermissionError(f"system pack is disabled/quarantined: {pack.pack_id}")
        return pack

    def select(self, identities: Iterable[str]) -> tuple[SystemPack, ...]:
        """Select packs as separate namespaces, rejecting duplicate pack ids."""
        selected = tuple(self.get(identity) for identity in identities)
        if len({pack.pack_id for pack in selected}) != len(selected):
            raise ValueError("duplicate system pack selection")
        return selected

    def audit(self) -> dict[str, list[str]]:
        return {pack.pack_id: pack.audit() for pack in self.packs()}


def get_system_registry() -> SystemRegistry:
    return SystemRegistry()
