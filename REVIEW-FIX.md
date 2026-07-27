---
phase: v1.0-milestone
fixed_at: 2026-07-27T02:45:00Z
review_path: REVIEW.md
iteration: 2
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# OpenRPG CLI v1.0: Code Review Fix Report

## Fixed Issues

- **CR-01 / WR-01:** Shield separated from body armor, body armor selected deterministically, shield bonus applied once. Added shield-only, medium-plus-shield, heavy-plus-shield, unarmored, light-armor, and medium-Dex-cap regression matrix. Commit `3d86dc5`.
- **CR-02:** Shared guided builder now powers `play` and `character create`. Guided play displays legal equipment/spell choices and preserves stable defaults. Commit `706e968`.
- **CR-03:** Added `build` dev dependency, low/medium/high-CR seeded sessions, isolated wheel build/install, installed audit, manifest license/version, and bundled-data assertions. Commit `61b645b`.
- **CR-04:** Exact project-root `py -3.14 -m ruff check .` reports `All checks passed!`. Reviewer claim could not be reproduced.

## Verification

- `py -3.14 -m ruff check .` — PASS
- Release matrix passed before concurrent uncommitted content/playtest work appeared.
- Current shared tree pytest/audit blocked by concurrent untracked `Language.json`, `Size.json`, `SpellSchool.json` lacking manifest declarations plus unrelated playtest determinism failure. These files are outside this fix pass and were not reverted.

---

_Fixer: Codex (gsd-code-fixer)_
