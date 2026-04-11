---
phase: 09-doml-get-data
plan: 02
subsystem: doml-skill
tags: [doml-new-project, data-acquisition, ux-flow, empty-data, kaggle, curl]

# Dependency graph
requires:
  - phase: 09-doml-get-data
    plan: 01
    provides: get-data.md workflow for inline invocation reference
provides:
  - new-project.md Step 3 with EMPTY_DATA_DIR sentinel (exit code 2) instead of SystemExit(1)
  - new-project.md Step 3b — inline acquisition fallback with Get data now / Add files manually choice loop
affects: [doml-new-project]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Exit code sentinel pattern — EMPTY_DATA_DIR + SystemExit(2) distinguishes "empty" from "error" (exit 1) for agent-readable flow control
    - Inline workflow invocation — Step 3b invokes get-data.md steps inline without spawning a new command, then re-scans and loops

key-files:
  created: []
  modified:
    - .claude/doml/workflows/new-project.md

key-decisions:
  - "Empty data/raw/ is now a recoverable condition (exit 2 + loop) rather than a fatal error (exit 1)"
  - "EMPTY_DATA_DIR sentinel makes the empty-directory case machine-readable: agent checks output text + exit code, not just exit code"
  - "Loop continues until at least one supported file is present — never silently proceeds with empty data"

patterns-established:
  - "Pattern: Sentinel + exit code pairing — print a named sentinel string, then raise SystemExit(N) with a unique code, so the agent can distinguish cases without parsing human-readable error text"

requirements-completed: [DATA-03]

# Metrics
duration: 5min
completed: 2026-04-11
---

# Phase 9 Plan 02: new-project.md Empty-Data Fallback Summary

**new-project.md Step 3 now presents an inline Get data now / Add files manually choice loop instead of exiting with an error when data/raw/ is empty**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-04-11T07:15:00Z
- **Completed:** 2026-04-11T07:20:00Z
- **Tasks:** 1 (+ checkpoint)
- **Files modified:** 1

## Accomplishments

- Changed empty-files case in the Step 3 DuckDB scan from `SystemExit(1)` to `EMPTY_DATA_DIR` sentinel + `SystemExit(2)`, making it machine-distinguishable from fatal errors
- Updated Step 3 parse instructions to route exit code 2 + `EMPTY_DATA_DIR` to Step 3b instead of stopping
- Added Step 3b — Data acquisition fallback: AskUserQuestion with "Get data now" (invokes get-data.md inline) and "Add files manually" (instructions + confirm + re-scan) options; loops until files are present
- Left all exit-1 cases unchanged: directory not found, .xls format error, container not running all still stop with error

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace empty-data error exit in new-project.md Step 3 with inline choice loop** - `66d6e11` (feat)

## Files Created/Modified

- `.claude/doml/workflows/new-project.md` — Step 3 Python block: EMPTY_DATA_DIR sentinel + SystemExit(2); Step 3 parse instructions: exit-code routing table; Step 3b: new fallback subsection with acquisition loop

## Decisions Made

- EMPTY_DATA_DIR sentinel + SystemExit(2) pairing was chosen over parsing error text — more robust as a machine-readable signal
- "Get data now" invokes get-data.md Steps 1–8 inline (not as a separate command) so the interview flow stays within a single agent turn
- Loop enforces at least one file present before Step 4 begins — the loop only exits on successful re-scan, never silently

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Known Stubs

None — this plan modifies a workflow markdown file; no data-flow stubs or placeholder UI.

## Threat Flags

None — no new network endpoints or trust boundaries introduced. T-09-08 (infinite loop DoS) is mitigated by the AskUserQuestion gate: the loop only continues when the user explicitly re-confirms, never autonomously. T-09-09 and T-09-10 apply as specified in the threat model and are handled by the unchanged Step 3 .xls check and the get-data.md Step 1 validation respectively.

## Next Phase Readiness

- Phase 9 is complete: doml-get-data skill is registered, get-data.md workflow is implemented, and new-project.md integration is done
- After merging, run `docker compose run --rm jupyter pip-compile requirements.in && docker compose build` to include the kaggle package in the Docker image
- Human verification checkpoint follows — reviewer should confirm SKILL.md, get-data.md Steps and sentinels, config file changes, and new-project.md Step 3b

## Self-Check: PASSED

- FOUND: `.claude/doml/workflows/new-project.md`
- FOUND: `.planning/phases/09-doml-get-data/09-02-SUMMARY.md`
- FOUND: commit `66d6e11`

---
*Phase: 09-doml-get-data*
*Completed: 2026-04-11*
