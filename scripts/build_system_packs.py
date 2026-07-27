"""Build small, license-audited rules packs from pinned primary-source corpora."""

from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "openrpg_cli" / "data" / "providers"
PACKS = [
    {
        "provider": "fate-srd",
        "id": "fate-core",
        "title": "Fate Core System SRD",
        "doc": "fate-core-srd",
        "repo": "https://github.com/fate-srd/fate-srd-content",
        "commit": "93ed848e723f31b4994b466b7241011ba24be885",
        "path": "source/fate-core-SRD.html",
        "source_sha256": "8f5b2987d6087b9d23dfd6f06406a47c9c7ec11b22528884c53e741f4ca55b6e",
        "license": "CC-BY-3.0",
        "authors": "Leonard Balsera, Brian Engard, Jeremy Keller, Ryan Macklin, Mike Olson, Clark Valentine, Amanda Valentine, Fred Hicks, and Rob Donoghue",
        "records": [
            {
                "name": "Fate dice check",
                "dice": "4dF",
                "procedure": "Roll four Fate dice, add relevant skill, compare total against opposition.",
                "outcomes": ["fail", "tie", "succeed", "succeed with style"],
            }
        ],
    },
    {
        "provider": "fate-srd",
        "id": "fate-accelerated",
        "title": "Fate Accelerated Edition SRD",
        "doc": "fate-accelerated-srd",
        "repo": "https://github.com/fate-srd/fate-srd-content",
        "commit": "93ed848e723f31b4994b466b7241011ba24be885",
        "path": "source/fate-accelerated-SRD.html",
        "source_sha256": "b78299a410c998a8db1745a306aabec15f7864a59c5001b67beea217b31bf461",
        "license": "CC-BY-3.0",
        "authors": "Leonard Balsera, Brian Engard, Jeremy Keller, Ryan Macklin, Mike Olson, Clark Valentine, Amanda Valentine, Fred Hicks, and Rob Donoghue",
        "records": [
            {
                "name": "Approach check",
                "dice": "4dF",
                "procedure": "Roll four Fate dice, add chosen approach, compare total against opposition.",
                "outcomes": ["fail", "tie", "succeed", "succeed with style"],
            }
        ],
    },
    {
        "provider": "fate-srd",
        "id": "fate-condensed",
        "title": "Fate Condensed SRD",
        "doc": "fate-condensed-srd",
        "repo": "https://github.com/fate-srd/fate-srd-content",
        "commit": "93ed848e723f31b4994b466b7241011ba24be885",
        "path": "source/Fate-Condensed-SRD-CC-BY.html",
        "source_sha256": "a563064d9a6a55e91dd912541068eff15b0176a2c18a1bd9b060b60dae330c4d",
        "license": "CC-BY-3.0",
        "authors": "PK Sullivan, Lara Turner, Fred Hicks, Richard Bellingham, Robert Hanz, and Sophie Lagacé",
        "records": [
            {
                "name": "Fate dice check",
                "dice": "4dF",
                "procedure": "Roll four Fate dice, add relevant skill, compare total against opposition.",
                "outcomes": ["fail", "tie", "succeed", "succeed with style"],
            }
        ],
    },
    {
        "provider": "dungeon-world",
        "id": "dungeon-world",
        "title": "Dungeon World",
        "doc": "dungeon-world-ccby",
        "repo": "https://github.com/Sagelt/Dungeon-World",
        "commit": "e67bd51c09d24518a7f989149b76094fbcc7fecc",
        "path": "text/Playing_the_Game.xml",
        "source_sha256": "4319f803ebd346ea8cd4cbef980e9267cc1975311ff5ba9d82002667202c30a0",
        "license": "CC-BY-3.0",
        "authors": "Sage LaTorra and Adam Koebel",
        "records": [
            {
                "name": "Move roll",
                "dice": "2d6 + modifier",
                "procedure": "When a move triggers, roll 2d6 and add stated modifier.",
                "outcomes": [
                    "10+: best outcome",
                    "7-9: success with compromise or cost",
                    "6-: trouble; mark XP",
                ],
            }
        ],
    },
    {
        "provider": "forged-in-the-dark",
        "id": "forged-in-the-dark-srd",
        "title": "Blades in the Dark SRD / Forged in the Dark",
        "doc": "blades-in-the-dark-srd",
        "repo": "https://github.com/amazingrando/blades-in-the-dark-srd-content",
        "commit": "f141ed2c4ed8061b6833a57e37a314a03e4166ce",
        "path": "Blades-in-the-Dark-SRD.md",
        "source_sha256": "81db12b33a8f701866d39234517e7561c129ae9c8efa35f5044eeb9763dd159d",
        "license": "CC-BY-3.0",
        "authors": "John Harper",
        "records": [
            {
                "name": "Action roll",
                "dice": "d6 pool; keep highest",
                "procedure": "Roll pool of six-sided dice and read highest; with zero dice roll two and keep lowest.",
                "outcomes": [
                    "multiple 6s: critical",
                    "6: full success",
                    "4-5: partial success",
                    "1-3: bad outcome",
                ],
            }
        ],
    },
    {
        "provider": "chaosium",
        "id": "questworlds-srd",
        "title": "QuestWorlds System Reference Document 0.97",
        "doc": "questworlds-srd-0.97",
        "repo": "https://github.com/ChaosiumInc/QuestWorlds",
        "commit": "5e57ff946c8488ac3a1cbd8f3867e0df22308e45",
        "path": "2.0_Basic_Mechanics.md",
        "source_sha256": "36b919859ed783c700f36e7fe2002ea38bba8d7ce214e1519adec615fb6f1f4d",
        "license": "ORC-1.0",
        "authors": "Moon Design Publications LLC",
        "enabled": False,
        "disabled_reason": (
            "Upstream attribution instructions require a reserved logo; project policy "
            "forbids bundling trademarks or art. Metadata only."
        ),
        "records": [],
    },
    {
        "provider": "cairn",
        "id": "cairn-first-edition",
        "title": "Cairn First Edition SRD",
        "doc": "cairn-first-edition-srd",
        "repo": "https://github.com/yochaigal/cairn",
        "commit": "3a76883edfebe1029f7dd33177ec5d68ab3b9b20",
        "path": "first-edition/cairn-srd.md",
        "source_sha256": "2c899eb56cb455cb1d3aad16e8c914a87d99d5d0c85b46130a009d5d0b0906de",
        "license": "CC-BY-SA-4.0",
        "authors": "Yochai Gal",
        "records": [
            {
                "name": "Saving throw",
                "dice": "d20 roll-under",
                "procedure": "Roll d20 equal to or under relevant ability score to save.",
                "outcomes": ["success", "failure"],
            },
            {
                "name": "Attack",
                "dice": "damage die",
                "procedure": "Attacks automatically hit; roll weapon damage and subtract armor before reducing hit protection.",
                "outcomes": ["damage"],
            },
        ],
    },
]
LICENSE_URLS = {
    "CC-BY-3.0": "https://creativecommons.org/licenses/by/3.0/",
    "CC-BY-SA-4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
    "ORC-1.0": "https://www.chaosium.com/orclicense/",
}


def write(pack: dict[str, object]) -> None:
    p = ROOT / str(pack["provider"]) / "packs" / str(pack["id"])
    p.mkdir(parents=True, exist_ok=True)
    doc = str(pack["doc"])
    rows = [
        {"model": "system.ResolutionRule", "pk": i, "fields": {"document": doc, **r}}
        for i, r in enumerate(pack["records"], 1)
    ]
    data_path = p / "ResolutionRule.json"
    if rows:
        data = json.dumps(rows, indent=2, ensure_ascii=False) + "\n"
        data_path.write_text(data, encoding="utf-8")
        declared_files = {
            data_path.name: {
                "sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
                "record_count": len(rows),
            }
        }
    else:
        data_path.unlink(missing_ok=True)
        declared_files = {}
    lic = str(pack["license"])
    url = LICENSE_URLS[lic]
    (p / "LICENSE.md").write_text(
        f"# Content license\n\nSPDX: `{lic}`\n\nLicense terms: {url}\n", encoding="utf-8"
    )
    (p / "NOTICE.md").write_text(
        f"# Notice\n\nMinimal rules records derived from `{pack['path']}` at pinned commit `{pack['commit']}`. No art, logos, trade dress, adventures, or setting material included. Upstream file SHA-256: `{pack['source_sha256']}`.\n",
        encoding="utf-8",
    )
    (p / "ATTRIBUTION.md").write_text(
        f"# Attribution\n\n**{pack['title']}** by {pack['authors']}. Source: {pack['repo']} at `{pack['commit']}` (`{pack['path']}`). Licensed under [{lic}]({url}). Changes: selected mechanics normalized into compact JSON; wording condensed. No endorsement implied.\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": 2,
        "pack_id": pack["id"],
        "system_id": pack["id"],
        "provider_id": pack["provider"],
        "title": pack["title"],
        "enabled": bool(pack.get("enabled", True)),
        "quarantined": not bool(pack.get("enabled", True)),
        "source_document_ids": [doc],
        "source_repository": pack["repo"],
        "source_commit": pack["commit"],
        "source_files": [{"path": pack["path"], "sha256": pack["source_sha256"]}],
        "license": {"id": lic, "url": url, "verified": True},
        "license_file": "LICENSE.md",
        "notice_file": "NOTICE.md",
        "attribution_file": "ATTRIBUTION.md",
        "allowlist": {"document_ids": [doc]},
        "scope": "Minimal system mechanics only; excludes trademarks, logos, art, trade dress, adventures, and setting corpus.",
        "declared_files": declared_files,
    }
    if pack.get("disabled_reason"):
        manifest["disabled_reason"] = pack["disabled_reason"]
    (p / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    for pack in PACKS:
        write(pack)
    print(f"Wrote {len(PACKS)} audited system packs")


if __name__ == "__main__":
    main()
