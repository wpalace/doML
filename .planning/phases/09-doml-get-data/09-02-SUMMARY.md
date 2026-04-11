---
phase: 09-doml-get-data
plan: 02
subsystem: doml-skill
tags: [new-project, data-acquisition, empty-data, sentinel, loop, kaggle, url]

# Dependency graph
requires:
  - phase: 09-doml-get-data
    plan: 01
    provides: get-data.md workflow invoked inline from new-project.md Step 3b
affects: [doml-new-project, 09-doml-get-data]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Sentinel exit-code pattern — exit 2 + EMPTY_DATA_DIR string distinguishes recoverable empty-dir from fatal errors (exit 1)
    - Inline workflow invocation — new-project.md Step 3b calls get-data.md steps directly without spawning a new command
    - Acquisition loop — AskUserQuestion repeats until re-scan finds files, never silently continues with empty data

key-files:
  created: []
  modified:
    - .claude/doml/workflows/new-project.md

key-decisions:
  - "EMPTY_DATA_DIR sentinel + exit code 2 chosen over modifying the scan script return value — lets the instruction layer distinguish recoverable (empty) from fatal (missing dir, .xls) without touching DuckDB scan logic"
  - "Step 3b added as a subsection immediately after the Python scan block — keeps linear reading order intact and avoids restructuring later steps"
  - "Loop-back is unconditional on still-empty re-scan — the interview cannot proceed without data, so the loop runs until files appear or the user exits Claude Code"

patterns-established:
  - "Pattern: Sentinel-exit distinction — use distinct exit codes (1 = fatal, 2 = recoverable) plus a parseable output token to let the agent layer branch without re-parsing error text"

requirements-completed: [DATA-03]

# Metrics
duration: 5min
completed: 2026-04-11
---

# Phase 9 Plan 02: new-project.md Empty-Data Fallback Summary

**new-project.md Step 3 now offers an inline "Get data now / Add files manually" acquisition loop instead of stopping with SystemExit(1) when data/raw/ is empty**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-04-11T07:14:00Z
- **Completed:** 2026-04-11T07:19:00Z
- **Tasks:** 1 auto + 1 human-verify checkpoint
- **Files modified:** 1

## Accomplishments

- Modified `.claude/doml/workflows/new-project.md` Step 3 to emit `EMPTY_DATA_DIR` sentinel + exit 2 (instead of SystemExit(1)) when `data/raw/` is empty
- Added Step 3b — Data acquisition fallback subsection with AskUserQuestion presenting "Get data now (Kaggle or URL)" and "Add files manually" options
- "Get data now" path invokes the full get-data.md workflow inline (Steps 1–8) then re-runs the scan
- "Add files manually" path displays format instructions, pauses for user confirmation, then re-runs the scan
- Loop repeats unconditionally if re-scan still finds no files — interview never proceeds with empty data
- `.xls` error and directory-not-found cases unchanged — still exit 1, still stop

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace empty-data error exit in new-project.md Step 3 with inline choice loop** - `66d6e11` (feat)

## Files Created/Modified

- `.claude/doml/workflows/new-project.md` - Step 3 Python scan updated to emit EMPTY_DATA_DIR + exit 2; Step 3b added with full acquisition fallback loop; parse instructions updated to distinguish exit codes 2 vs 1

## Decisions Made

- EMPTY_DATA_DIR sentinel + exit code 2 chosen to distinguish recoverable empty-dir from fatal errors without restructuring DuckDB scan logic
- Step 3b inserted immediately after the scan block to keep linear reading order
- Loop is unconditional — the interview cannot proceed without at least one valid file

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Known Stubs

None — this plan modifies a workflow markdown file; no data-flow stubs or placeholder UI.

## Threat Flags

None — T-09-08 (infinite loop DoS) is mitigated by the AskUserQuestion loop requiring explicit user action each iteration; T-09-09 and T-09-10 coverage inherited from Plan 01.

## Next Phase Readiness

- Phase 9 doml-get-data is fully complete: SKILL.md, get-data.md, config updates (Plan 01), and new-project.md integration (Plan 02)
- Run `docker compose run --rm jupyter pip-compile requirements.in && docker compose build` to include the `kaggle` package in the Docker image before using `/doml-get-data kaggle`
- No further blockers for downstream phases

---
*Phase: 09-doml-get-data*
*Completed: 2026-04-11*
