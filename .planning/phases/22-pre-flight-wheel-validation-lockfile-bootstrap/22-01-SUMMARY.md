---
phase: 22-pre-flight-wheel-validation-lockfile-bootstrap
plan: 01
subsystem: infra
tags: [duckdb, ydata-profiling, eda, nbformat, requirements, template]

# Dependency graph
requires:
  - phase: v1.5 milestone (baseline)
    provides: existing template requirements.in/.txt and EDA notebook with ydata-profiling pin
provides:
  - Template requirements.in without ydata-profiling top-level dep
  - Template requirements.txt with ydata-profiling==4.18.1 pin removed
  - EDA Python notebook template with DuckDB SUMMARIZE summary cell (cell index 5)
affects: [22-02 (root requirements cleanup), 22-03 (lockfile regen via uv), 23 (full lockfile regen)]

# Tech tracking
tech-stack:
  added: []
  removed: [ydata-profiling]
  patterns:
    - DuckDB SUMMARIZE as canonical schema-and-stats summary in EDA templates
    - nbformat-safe JSON edits via inline python3 script (preserves cell metadata)

key-files:
  created: []
  modified:
    - .claude/doml/templates/requirements.in
    - .claude/doml/templates/requirements.txt
    - .claude/doml/templates/notebooks/data_understanding_python.ipynb

key-decisions:
  - "D-22-09: ydata-profiling dropped entirely from DoML template (deferred since Phase 01-04 due to pkg_resources issue under conda Python 3.13; scope ~4 MB transitive dep removal)"
  - "D-22-10: SUMMARIZE-driven cell replaces implicit profiling role; aligns with CLAUDE.md DuckDB-first rule"
  - "D-22-11: Transitive deps (visions/multimethod/phik/imagehash/wordcloud) NOT removed in this plan — they fall out naturally when Phase 23 regenerates the lockfile via uv pip-compile"
  - "D-22-18 commit 1: verbatim message 'chore: drop ydata-profiling from template + replace EDA profiling cell'"

patterns-established:
  - "Template-first deprecation: drop deps in .claude/doml/templates/ before touching root files (root cleanup deferred to plan 22-02)"
  - "Inline nbformat edits via python3 heredoc — never hand-edit notebook JSON; always normalize via json.loads/dumps"

requirements-completed: [PY-03]

# Metrics
duration: 29min
completed: 2026-04-30
---

# Phase 22 Plan 01: Pre-Flight Wheel Validation & Lockfile Bootstrap — ydata-profiling drop Summary

**Dropped ydata-profiling from the DoML project template and replaced its implicit profiling role with a DuckDB SUMMARIZE cell in the Python EDA notebook (3 files, 1 chore commit, scope-isolated to .claude/ templates).**

## Performance

- **Duration:** ~29 min
- **Started:** 2026-04-30T22:04:46Z
- **Completed:** 2026-04-30T22:33:49Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Removed `ydata-profiling` from `.claude/doml/templates/requirements.in` (line 31) — `# --- Visualization / profiling ---` section header and `plotly` retained
- Removed `ydata-profiling==4.18.1` pin from `.claude/doml/templates/requirements.txt` (line 130) — transitive deps left untouched per D-22-11 (Phase 23 will sweep them via uv lockfile regen)
- Inserted new DuckDB SUMMARIZE code cell in `data_understanding_python.ipynb` at cell index 5 (between the `def get_read_fn` helper at index 4 and the existing numeric-stats cell at index 6) — cell count went from 26 → 27
- Notebook source now contains zero `ydata`/`ProfileReport` references (case-insensitive verified)
- Single chore commit `1a7708b` lands the three template files atomically with the verbatim D-22-18 message

## Task Commits

1. **Task 1: Drop ydata-profiling from template requirements.in and requirements.txt** — included in commit `1a7708b` (chore)
2. **Task 2: Add DuckDB SUMMARIZE cell to data_understanding_python.ipynb** — included in commit `1a7708b` (chore)
3. **Task 3: Single chore commit (D-22-18 commit 1)** — `1a7708b` (chore)

_Note: All three tasks land in a single commit per the plan's D-22-18 commit-1 contract._

**Commit:** `1a7708b6ccab90c79331fb397ec18f74183e8a26` — `chore: drop ydata-profiling from template + replace EDA profiling cell`

## Files Created/Modified

- `.claude/doml/templates/requirements.in` — removed line 31 `ydata-profiling`; line count 41 → 40
- `.claude/doml/templates/requirements.txt` — removed line 130 `ydata-profiling==4.18.1`; line count 134 → 133
- `.claude/doml/templates/notebooks/data_understanding_python.ipynb` — inserted SUMMARIZE cell at index 5; cell count 26 → 27 (insertions: 20, deletions: 1 on file-level diff due to nbformat re-indenting)

### SUMMARIZE Cell Insertion Position

| Index | Type | Source (truncated) |
|-------|------|--------------------|
| 3 | markdown | `## 1. Data Profiling …` |
| 4 | code | `import duckdb …` (defines `get_read_fn`, runs DESCRIBE + null counts) |
| **5** | **code (NEW)** | `# DuckDB SUMMARIZE — canonical schema-and-stats summary per file …` |
| 6 | code | `NUMERIC_TYPES = {…}` (numeric MIN/MAX/AVG/STDDEV/MEDIAN per file) |
| 7 | code | `for path in files: … string_cols …` (categorical analysis) |

This ordering ensures `get_read_fn` and `files` are both in scope when SUMMARIZE runs; the SUMMARIZE cell groups with the existing "## 1. Data Profiling" section before flow continues to "## 2. Load Data for Statistical Analysis" at index 8.

## Decisions Made

- **D-22-09 / D-22-11 (template-only scope):** Only the explicit `ydata-profiling` lines were removed. Transitive deps (`visions`, `multimethod`, `phik`, `imagehash`, `wordcloud`) remain in `requirements.txt` as Phase 23 will regenerate the lockfile end-to-end with uv `--generate-hashes`.
- **D-22-10 (SUMMARIZE placement):** The new SUMMARIZE cell sits AFTER the helper-defining cell (index 4) so that `get_read_fn` and `files` are pre-defined; sits BEFORE the numeric-stats cell (index 6) so the new cell joins the "Data Profiling" section semantically rather than appearing between sections.
- **Comment hygiene:** Dropped a parenthetical "(replaces ydata-profiling)" from the SUMMARIZE cell comment so the verification block's stricter `grep -rn "ydata-profiling" .claude/` returns 0 matches.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed historical "(replaces ydata-profiling)" parenthetical from SUMMARIZE cell comment**
- **Found during:** Task 2 acceptance verification
- **Issue:** Plan's `<action>` template suggested the comment `# DuckDB SUMMARIZE — canonical schema-and-stats summary per file (replaces ydata-profiling)`, but the plan's `<verify>` block (and the `<verification>` block at end of plan) requires `grep -rn "ydata-profiling" .claude/` to return 0 matches. The historical parenthetical violated that contract.
- **Fix:** Trimmed the comment to `# DuckDB SUMMARIZE — canonical schema-and-stats summary per file`. SUMMARIZE behaviour and column docstring (`Returns: column_name, …`) preserved.
- **Files modified:** `.claude/doml/templates/notebooks/data_understanding_python.ipynb` (cell index 5)
- **Verification:** `grep -rn "ydata_profiling\|ydata-profiling\|ProfileReport" .claude/` returns exit 1 (no matches); `python3 -c "… 'ydata' not in src.lower() …"` passes.
- **Committed in:** `1a7708b` (single chore commit)

---

**Total deviations:** 1 auto-fixed (1 bug — verification contract enforcement)
**Impact on plan:** Cosmetic correction to honor the plan's stricter verification block. No scope creep, no architectural change.

## Issues Encountered

- Worktree branch was created from commit `d5e299f` (v1.5 archive) instead of the phase 22 base `45bd25d`. Working tree was clean, so a `git reset --hard 45bd25d…` advanced the branch to the correct base before any edits. No work lost; no upstream impact.
- nbformat `MissingIDFieldWarning` emitted on validation — pre-existing condition (template was authored without v4.5 cell IDs); not in this plan's scope per the deviation-rules SCOPE BOUNDARY. Logged here only; no fix attempted.

## User Setup Required

None — template-only changes; downstream `/doml-new-project` runs will pick up the new templates automatically. No env vars, no dashboard config.

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| (none) | — | Plan touches templates only; no new network/auth/file-access surface introduced. T-22-01-01 (nbformat tampering) mitigated via `nbformat.read` validation in acceptance criteria. T-22-01-02 (template requirements files) carries `accept` disposition per the plan's threat register. |

## Next Phase Readiness

- Plan 22-02 (root requirements cleanup) can proceed: the template side is now ydata-free, so root `requirements.in`/`requirements.txt` removals will not regress the template behaviour.
- Plan 22-03 (lockfile regen via uv) can proceed: dropping the explicit pin from the template lockfile is the prerequisite for Phase 23's full uv-based regeneration.
- The SUMMARIZE cell is wire-ready for the next `/doml-data-understanding` run; no notebook smoke run was performed in this plan (out of scope — papermill execution belongs to phase verification, not template edits).

## Self-Check

- [x] `.claude/doml/templates/requirements.in` exists, no `ydata-profiling` (verified via grep exit 1)
- [x] `.claude/doml/templates/requirements.txt` exists, no `ydata-profiling==4.18.1` pin (verified via grep exit 1)
- [x] `.claude/doml/templates/notebooks/data_understanding_python.ipynb` exists, contains `SUMMARIZE`, no `ydata`/`ProfileReport` (verified via python json scan)
- [x] Notebook is valid nbformat v4 (verified via `nbformat.read`)
- [x] Cell count is 27 (was 26, +1)
- [x] Commit `1a7708b6ccab90c79331fb397ec18f74183e8a26` exists in `git log` with the verbatim D-22-18 message
- [x] Commit touches exactly 3 files (no root files, no Dockerfile, no planning docs)
- [x] Working tree clean for plan-scoped files

## Self-Check: PASSED

---
*Phase: 22-pre-flight-wheel-validation-lockfile-bootstrap*
*Completed: 2026-04-30*
