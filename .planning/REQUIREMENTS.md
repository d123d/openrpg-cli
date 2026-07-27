# Requirements: OpenRPG CLI v2.0 Complete Gameplay Systems

## Kernel and State

- [x] **KERN-01**: Versioned immutable game, actor, team, scene, encounter, clock, resource, and effect state.
- [x] **KERN-02**: Typed commands and events with canonical JSON codecs.
- [x] **KERN-03**: Deterministic reducer with explicit RNG and no interface-side mutation.
- [x] **KERN-04**: Append-only command/event log, replay, snapshot hash, save migration.
- [x] **KERN-05**: Runtime user-authored scene data separated from bundled SRD content.

## Universal Resolution

- [x] **RES-01**: Ability checks, saves, attacks, contests, passive scores, DCs.
- [x] **RES-02**: Proficiency, expertise, advantage/disadvantage, circumstantial modifiers.
- [x] **RES-03**: Typed damage/healing pipeline with criticals, resistances, immunities, vulnerabilities, temporary HP.
- [x] **RES-04**: Zero HP, unconscious, death saves, stabilization, defeat, recovery.
- [x] **RES-05**: All SRD conditions plus exhaustion and timed effect lifecycle.

## Turns, Actions, Space

- [x] **TURN-01**: N-actor initiative, teams, rounds, surprise, legal turn ownership.
- [x] **TURN-02**: Action, bonus action, reaction, movement, interaction budgets.
- [x] **TURN-03**: Attack, Magic, Dash, Disengage, Dodge, Help, Hide, Influence, Ready, Search, Study, Utilize.
- [x] **TURN-04**: Grapple, shove, opportunity attacks, cover, visibility, mounted/underwater modes.
- [x] **TURN-05**: Coordinate-free range bands plus optional grid positions, movement, areas, targets.

## Characters and Resources

- [ ] **CHAR-20**: Levels 1–20, XP/level advancement, subclasses, multiclass prerequisites.
- [ ] **CHAR-21**: Species/background/feat/class feature grants and choice graph.
- [ ] **CHAR-22**: Proficiencies, expertise, languages, tools, saves, skills.
- [ ] **CHAR-23**: Inventory, quantities, containers, currency, encumbrance, equipment, ammo, attunement.
- [ ] **CHAR-24**: Spell preparation/known spells, slots, concentration, class resources, recharge.
- [ ] **CHAR-25**: Short/long rest and recovery reset hooks.

## Spells, Creatures, Items

- [ ] **FX-01**: Declarative effect DSL: attack, save, damage, heal, condition, movement, area, repeat, summon, spend/recharge.
- [ ] **FX-02**: Structured adapters for SRD spells with explicit unsupported registry.
- [ ] **FX-03**: Creature actions, multiattack, recharge, traits, defenses, movement, reactions, spellcasting.
- [ ] **FX-04**: Weapons, armor, properties, magic items, services, tools.
- [ ] **FX-05**: Generated corpus coverage report; no silent fallback/invented mechanics.

## Encounter and Party

- [ ] **ENC-01**: Encounter create/edit/start/pause/resume/save/replay.
- [ ] **ENC-02**: Parties, rosters, roles, marching order, shared inventory/currency, group checks.
- [ ] **ENC-03**: Difficulty/XP budgeting, creature scaling inputs, objectives, waves, morale.
- [ ] **ENC-04**: Structured controllers for human, deterministic auto, and external agents.
- [ ] **ENC-05**: Scene transitions and consequence/outcome records.

## Scene and Activity Systems

- [ ] **SCENE-01**: Common scene contract with participants, clocks, resources, objectives, discoveries, choices, outcomes.
- [ ] **SCENE-02**: Combat encounter scene.
- [ ] **SCENE-03**: Social/influence/negotiation/relationship scene.
- [ ] **SCENE-04**: Exploration/travel/navigation/search/discovery scene.
- [ ] **SCENE-05**: Puzzle/investigation/lore/knowledge scene.
- [ ] **SCENE-06**: Challenge/hazard/trap/chase/survival scene.
- [ ] **SCENE-07**: Downtime/crafting/training/research/work/service scene.
- [ ] **SCENE-08**: Camping/rest/forage/watch/cook/slice-of-life scene.
- [ ] **SCENE-09**: Party/faction/reputation/stronghold/group activity scene.
- [ ] **SCENE-10**: Spiritual/rite/oath/devotion/omen activity scene.
- [ ] **SCENE-11**: Extensible custom activity schema without bundled non-SRD content.

## Interface and Quality

- [ ] **UX-01**: CLI create/inspect/run/act/save/resume/replay for every scene/activity type.
- [ ] **UX-02**: JSON interface exposes state, legal commands, events, and validation errors.
- [ ] **QA-01**: Property/state-machine tests and deterministic replay differential tests.
- [ ] **QA-02**: Golden SRD examples, corpus adapter coverage, fuzzed malformed commands/state.
- [ ] **QA-03**: Audit, tests, Ruff, wheel, isolated install, attribution/data gates remain green.
- [ ] **QA-04**: Documentation states exact supported/unsupported SRD mechanics.

## Traceability

| Requirement group | Phase |
|---|---|
| KERN-* | 5 |
| RES-* | 6 |
| TURN-* | 7 |
| CHAR-20..25 | 8 |
| FX-* | 9 |
| ENC-* | 10 |
| SCENE-01..06 | 11 |
| SCENE-07..11 | 12 |
| UX-*, QA-* | 13 |
