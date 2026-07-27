"""Regenerate deterministic integrity metadata for bundled SRD JSON tables."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "openrpg_cli" / "data" / "srd521"
OUTPUT = DATA / "manifest.json"

SOURCE_COMMIT = "d4276c586d79f2a27bf2b814aed151cf57605283"


def main() -> None:
    files: dict[str, dict[str, int | str]] = {}
    for path in sorted(DATA.glob("*.json")):
        if path.name == "manifest.json":
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            raise ValueError(f"{path.name} is not a JSON array")
        files[path.name] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "record_count": len(rows),
        }
    manifest = {
        "srd_document": "System Reference Document 5.2.1",
        "srd_version": "5.2.1",
        "srd_official_url": "https://www.dndbeyond.com/srd",
        "content_license": "CC-BY-4.0",
        "content_license_url": "https://creativecommons.org/licenses/by/4.0/legalcode",
        "source_repository": "https://github.com/open5e/open5e-api",
        "source_commit": SOURCE_COMMIT,
        "source_subtree": "data/v2/wizards-of-the-coast/srd-2024",
        "scope": (
            "Only JSON files from Open5e's Wizards of the Coast srd-2024 subtree. "
            "No srd-2014, third-party publisher, campaign setting, or adventure data."
        ),
        "declared_files": files,
    }
    OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(files)} files)")


if __name__ == "__main__":
    main()

