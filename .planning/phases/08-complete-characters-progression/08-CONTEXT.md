# Phase 8: Complete Characters & Progression - Context

**Gathered:** 2026-07-26
**Status:** Ready for planning
**Mode:** Autonomous

## Boundary

Extend SRD characters through levels 1–20: advancement, subclasses, multiclass prerequisites, feature/choice grants, proficiencies, inventory/economy/encumbrance/equipment/ammo/attunement, spell preparation/slots/concentration/class resources, short/long rests. Integrate kernel/actions; preserve v1 schema migration.

## Decisions

- Derived stats are projections rebuilt from authoritative selections/state.
- Feature grants use typed effect/choice descriptors; no silent prose inference.
- Full all-class level tables generated from joined SRD features.
- Explicit unsupported feature mechanics registry permitted; structural grant/resource availability still complete.
- Inventory tracks quantities, currency, containers, equip slots, weight, ammo, attunement.
- Rest hooks deterministic and feature-owned.
- Save schema v2 migrates v1 characters losslessly.

## Deferred

Deep spell/monster effect execution belongs Phase 9.
