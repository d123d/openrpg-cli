# OpenRPG CLI Content Licenses

## Primary Content

### SRD 5.2.1 (D&D 2024)
- **License**: CC-BY-4.0
- **Source**: Open5e `wizards-of-the-coast/srd-2024` subtree
- **Commit**: `d4276c586d79f2a27bf2b814aed151cf57605283`
- **Tables**: All tables in `CATEGORY_TABLES` except those listed below
- **URL**: https://www.dndbeyond.com/srd

## Isolated Open-System Packs

| Packs | License | Pinned canonical/official corpus |
|---|---|---|
| Fate Core, Accelerated, Condensed | CC-BY-3.0 | `fate-srd/fate-srd-content` official-source copies |
| Dungeon World | CC-BY-3.0 | Author repository `Sagelt/Dungeon-World` |
| Forged in the Dark SRD | CC-BY-3.0 | Blades SRD text published from official SRD site |
| Cairn First Edition | CC-BY-SA-4.0 | `yochaigal/cairn` |

Each pack manifest records exact commit, upstream file path and SHA-256.
Each pack carries its own `LICENSE.md`, `NOTICE.md`, and `ATTRIBUTION.md`.
Cairn remains isolated so ShareAlike scope cannot be confused with other packs.

## Disabled Metadata Only

Pathfinder 2e, ACKS, Mothership, unverified Legacy SRD, and QuestWorlds are not
enabled or bundled. QuestWorlds source and ORC metadata are pinned, but its
upstream attribution asks for a reserved logo that this project's no-trademark
policy excludes. Registry entries contain no rules records and state the reason.

## Attribution

Each data file includes a `document` field identifying its source. The `info` command displays provenance. The `audit` command validates file allowlist and integrity.

Third-party content (Tome of Beasts, EN Publishing, Kobold Press) is explicitly excluded per project scope rules.
