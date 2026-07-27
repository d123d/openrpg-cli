# Phase 6: Universal Resolution & Effects - Context

**Gathered:** 2026-07-26
**Status:** Ready for planning
**Mode:** Autonomous

## Boundary

Implement universal mechanical resolvers atop Phase 5 kernel: d20 checks/saves/attacks/contests/passives; modifier/proficiency/expertise/advantage pipeline; damage/healing/temp HP/defenses; zero HP/death/recovery; all bundled conditions and timed effects. No turn/action economy yet.

## Decisions

- Pure typed rule functions emit commands/events; no CLI/domain mutation.
- Explicit SRD citations/keys in adapters and golden tests.
- Advantage/disadvantage cancel; multiple sources do not stack.
- Damage order and rounding encoded once; typed damage instances.
- Effect scheduler uses deterministic phases/ticks without assuming combat turns.
- Condition mechanics manually encoded from bundled definitions; unsupported clauses explicit.
- Preserve v1 combat via adapters and differential tests.

## Deferred

Initiative/action budgets/space belong Phase 7.
