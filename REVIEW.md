---
phase: v1.0-milestone
reviewed: 2026-07-26T20:30:00Z
depth: deep
files_reviewed: 7
files_reviewed_list:
  - srd_cli/character_builder.py
  - srd_cli/cli.py
  - srd_cli/combat.py
  - srd_cli/combat_session.py
  - tests/test_character_builder.py
  - tests/test_combat_cli.py
  - tests/test_play_cli.py
findings:
  critical: 4
  warning: 1
  info: 0
  total: 5
status: issues_found
---

# SRD CLI v1.0: Code Re-review Report

**Reviewed:** 2026-07-26T20:30:00Z
**Depth:** deep
**Range:** `393ab3d..0c9cf2b`
**Status:** issues_found

## Summary

Fix range closes CR-01, CR-02, CR-05, WR-01, and WR-02. Audit passes. Pytest reports 44 passed. Four release blockers remain: shield-only AC is catastrophically wrong, guided creation still omits equipment/spell choices, promised release verification remains incomplete, Ruff fails with 47 errors.

## Critical Issues

### CR-01 [BLOCKER]: Shield is treated as base armor, producing AC 4

**File:** `srd_cli/character_builder.py:193-206`
**Issue:** Code takes `armor_rows[0]` as worn base armor. For Druid starting package, only matching armor row is Shield (`ac_base=2`), so code sets AC to 2 then adds another +2 because Shield is present. Default Druid AC becomes 4 instead of unarmored `10 + Dex + 2 shield` (13 for generated default). More generally, row ordering can select Shield before real armor. Combat correctness remains broken.
**Fix:** Partition shield from body armor. Choose exactly one legal body-armor row, derive its base/Dex cap or use unarmored fallback, then add shield bonus once.

### CR-02 [BLOCKER]: `play` creation still omits guided equipment and spell choices

**File:** `srd_cli/cli.py:123-131`
**Issue:** Create path still passes `None, (), ()` directly. User receives no legal equipment/spell choice menus, contrary to Phase 4 requirement that play reuse complete guided character workflow and Phase 3 requirement that guided and non-interactive creation be equal first-class modes.
**Fix:** Reuse one shared guided creation function used by `character create`; expose stable legal equipment/spell choices and defaults before building.

### CR-03 [BLOCKER]: Release verification matrix remains incomplete

**File:** `tests/test_release_smoke.py:1-11`
**Issue:** New combat/play tests cover basic interactive and byte-stable happy paths, but release smoke is unchanged. It still runs from source tree, does not build/install wheel into isolated target, does not verify bundled license/data, and does not exercise low/medium/high CR encounters. `python -m build` also cannot run in current project environment (`No module named build`). Phase 4 PLAY-02 gate remains unproved.
**Fix:** Add isolated wheel build/install smoke with attribution/data assertions and parameterized CR-band seeded combats. Add `build` to dev dependencies/environment and run exact release matrix.

### CR-04 [BLOCKER]: Required Ruff gate still fails

**File:** `pyproject.toml:26-29`
**Issue:** `python -m ruff check .` now reports 47 errors. DEV-01 and Phase 4 Task 3 require a clean Ruff gate. New changes added import-order failures while existing B008, TRY004, UP035, B019, and other violations remain.
**Fix:** Correct applicable lint findings, use `Annotated` Typer declarations or documented B008 config, configure only intentional project exceptions, then enforce clean Ruff in release workflow.

## Warnings

### WR-01 [WARNING]: New tests still miss shield/base-armor derivation

**File:** `tests/test_character_builder.py:24-70`
**Issue:** Added all-class legal-action and thrown-weapon coverage successfully catches prior defects, but no test asserts armor plus shield, shield-only, unarmored, or Dex-cap behavior. Default Druid AC 4 passed all 44 tests.
**Fix:** Add explicit cases for shield-only Druid, medium armor + shield Cleric, heavy armor + shield Paladin, unarmored class, and medium-armor Dex cap.

## Closed Findings

- Original CR-01: default characters now receive class-derived weapons and supported default spells; all 12 base classes expose legal actions.
- Original CR-02: `combat` now branches between auto and prompted player turns.
- Original CR-05: thrown weapons no longer automatically use Dexterity; regression test added.
- Original WR-01: unsupported spell adapters are converted to `CombatError`.
- Original WR-02: rules API is injected through combat session/engine.
- Original WR-03: combat/play CLI coverage exists, though release and armor gaps remain.

---

_Reviewed: 2026-07-26T20:30:00Z_
_Reviewer: Codex (gsd-code-reviewer)_
_Depth: deep_
