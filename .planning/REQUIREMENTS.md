# Requirements: SRD CLI v1.0

## Content Baseline

- [x] **SRD-01**: Bundle latest SRD 5.2.1 structured data only.
- [x] **SRD-02**: Exclude setting, adventure, third-party, and 2014 content.
- [x] **SRD-03**: Ship required CC-BY-4.0 attribution.
- [x] **SRD-04**: Pin transform source commit and subtree.
- [x] **AUD-01**: Verify allowlist, hashes, counts, and document ownership.
- [x] **CLI-01**: List, show, search, info, and audit commands.
- [x] **DICE-01**: Deterministic bounded dice roller.
- [x] **DEV-01**: pytest and ruff gates.

## Normalized Rules API

- [x] **API-01**: Typed core entity models.
- [x] **API-02**: Class features/items joins.
- [x] **API-03**: Species/background/feat benefit joins.
- [x] **API-04**: Creature action/attack/trait joins.
- [x] **API-05**: Weapon/property and spellcasting joins.
- [x] **API-06**: Complete relationship coverage tests.

## Character Engine

- [ ] **CHAR-01**: Guided and non-interactive character creation.
- [ ] **CHAR-02**: Deterministic derived statistics.
- [ ] **CHAR-03**: SRD-only choice validation and suggestions.
- [ ] **CHAR-04**: Versioned JSON save/load.
- [ ] **CHAR-05**: Character integrity validation.
- [ ] **CHAR-06**: Character sheet rendering.

## Combat and Play

- [ ] **COMBAT-01**: Initiative and turn loop.
- [ ] **COMBAT-02**: Weapon attacks, damage, critical hits, defeat.
- [ ] **COMBAT-03**: Spell attacks and save-based damage.
- [ ] **COMBAT-04**: Deterministic enemy SRD action selection.
- [ ] **COMBAT-05**: Reproducible transcript and headless auto mode.
- [ ] **PLAY-01**: Interactive create/load and encounter loop.
- [ ] **PLAY-02**: Install/package/smoke verification.

## Traceability

| Requirement | Phase |
|-------------|-------|
| SRD-01..04, AUD-01, CLI-01, DICE-01, DEV-01 | 1 |
| API-01..06 | 2 |
| CHAR-01..06 | 3 |
| COMBAT-01..05, PLAY-01..02 | 4 |

