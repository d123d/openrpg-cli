# SRD CLI Agent Rules

## Scope Lock

Bundled game content must come only from latest SRD 5.2.1.

Never add:

- published adventures or campaign settings
- Forgotten Realms, Greyhawk, Eberron, Critical Role, or other setting lore
- 5etools/third-party content outside Open5e `wizards-of-the-coast/srd-2024`
- SRD 5.1/2014 content
- custom monsters, spells, classes, species, feats, items, NPCs, or locations

Runtime user content may remain external. Do not bundle it.

## Data Updates

1. Verify latest SRD version at https://www.dndbeyond.com/srd.
2. Import only Open5e `data/v2/wizards-of-the-coast/srd-2024`.
3. Pin source commit in `scripts/build_manifest.py`.
4. Run `py -3.14 scripts/build_manifest.py`.
5. Run audit, tests, ruff.
6. Review diff for new tables, foreign document ids, attribution changes.

## Verification

```powershell
py -3.14 -m srd_cli audit
py -3.14 -m pytest -q
py -3.14 -m ruff check .
```

Python stays 3.11-compatible. Prefer stdlib. Content access stays read-only.

