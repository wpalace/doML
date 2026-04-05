---
phase: 03-kickoff-interview
plan: 01
subsystem: workflow
tags: [doml, interview, duckdb, project-init, askuserquestion, project.md, config.json]

# Dependency graph
requires:
  - phase: 03-kickoff-interview
    plan: 02
    provides: scan_data_folder() and format_scan_report() callable from doml.data_scan
  - phase: 02-framework-skeleton
    provides: new-project.md skeleton with Phase 2 stubs at Steps 2 and 3

provides:
  - .claude/doml/workflows/new-project.md — Steps 2 and 3 fully implemented; workflow is end-to-end functional
  - Step 2: DuckDB scan of data/raw/ via scan_data_folder(), displayed before interview
  - Step 3: 8-question guided interview with ML type inference, time-factor detection, domain research offer, framing sentence confirmation
  - Atomic writes to PROJECT.md (all placeholders filled) and config.json (analysis_language, problem_type, time_factor, dataset.format)
  - Hard stop on missing/empty data/raw/ — no partial writes

affects:
  - Phase 4 Business Understanding (reads filled PROJECT.md as context)
  - Any phase that uses config.json analysis_language or problem_type fields
  - /doml-new-project user experience end-to-end

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "AskUserQuestion for all user-facing interview questions — renders TUI, handles text_mode fallback"
    - "Atomic write pattern: all answers collected before any file writes"
    - "doml.data_scan integration: scan_data_folder() → format_scan_report() → display before Q1"
    - "PROJECT_ROOT env var (REPR-02) for data/raw/ path resolution"
    - "SystemExit(1) on scan ValueError — hard stop, no partial writes"
    - "time_factor upgrade path: regression + time_factor=True → offer time_series reclassification"
    - "domain_research conditional: user opts in → summary appended to PROJECT.md Problem Framing section"

key-files:
  created: []
  modified:
    - .claude/doml/workflows/new-project.md

key-decisions:
  - "Step 2 calls doml.data_scan via Bash tool Python snippet — consistent with Phase 3 Plan 02 module interface"
  - "scan_results stored in memory between Step 2 and Step 3 — used for target column inference and dataset.format population"
  - "Framing sentence gating: PROJECT.md and config.json only written after user explicitly confirms the framing sentence (no partial writes)"
  - "domain_research_summary appended inline to Problem Framing section in PROJECT.md (no separate file)"
  - "config.json write: read full JSON → modify specific keys → write complete updated JSON (prevents partial write corruption)"

patterns-established:
  - "AskUserQuestion retry pattern: empty/whitespace response → retry once → fall back to plain-text prompt"
  - "Inference + confirm: Claude reasons over free-text Q1-Q5, proposes problem_type with explanation, user confirms or corrects"
  - "Time-factor upgrade: if time_factor=True and problem_type=regression → AskUserQuestion upgrade offer to time_series"
  - "Atomic output writes: all answers collected → framing sentence confirmed → PROJECT.md written → config.json written"

requirements-completed: [INTV-01, INTV-02, INTV-04, INTV-05]

# Metrics
duration: 25min
completed: 2026-04-05
---

# Phase 3 Plan 01: Kickoff Interview Workflow Summary

**Full /doml-new-project workflow implemented: DuckDB scan before interview, 8-question guided interview with ML type inference and atomic PROJECT.md + config.json writes**

## Performance

- **Duration:** 25 min
- **Started:** 2026-04-05T14:30:00Z
- **Completed:** 2026-04-05T14:55:00Z
- **Tasks:** 2 committed (Task 3 = human-verify checkpoint, not yet approved)
- **Files modified:** 1

## Accomplishments

- `new-project.md` Step 2 stub replaced with live DuckDB scan via `doml.data_scan.scan_data_folder()` — hard stop on empty/missing `data/raw/`, scan report displayed before any interview questions
- `new-project.md` Step 3 stub replaced with full 8-question guided interview: Q1-Q5 (business context + time factor), ML type inference with user confirm/correct, time-factor regression upgrade offer, domain research opt-in, language preference, framing sentence confirm
- Atomic write pattern enforced: PROJECT.md and config.json written only after framing sentence confirmed — no partial writes if interview interrupted
- INTV-01, INTV-02, INTV-04, INTV-05 requirements fulfilled in a single workflow file
- Steps 4 and 5 (planning artifact generation and summary display) preserved unchanged

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace Step 2 stub with DuckDB scan implementation** - `3c8d7f9` (feat)
2. **Task 2: Replace Step 3 stub with full guided kickoff interview** - `3eee52d` (feat)

_Task 3 is a human-verify checkpoint — not a code commit._

## Files Created/Modified

- `.claude/doml/workflows/new-project.md` — Steps 2 and 3 fully implemented; Step 1, 4, 5 unchanged

## Decisions Made

- **scan_results in memory between steps:** Step 2 stores `scan_results` list in agent memory so Step 3 can use it for target column inference (from column names) and dataset.format population in config.json. No temp file needed.
- **Framing sentence as the write gate:** The atomic write is gated on the user confirming the framing sentence (not just completing Q7). This ensures the most derived artifact (the framing) is correct before anything is written. Matches Decision 2 in 03-CONTEXT.md.
- **domain_research_summary appended inline:** Per Decision 1 in 03-CONTEXT.md, domain research summary is appended as a sub-section in PROJECT.md Problem Framing — not a separate file.
- **config.json write order:** PROJECT.md first, then config.json. If config.json write fails after PROJECT.md succeeds, state is technically partial — but this is a local planning tool and the user can re-run; full transactional atomicity not warranted here.

## Deviations from Plan

None — plan executed exactly as written. The Step 2 and Step 3 content was specified in the plan's `<action>` blocks and implemented verbatim with minor formatting choices within spec.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required. The workflow runs inside Claude Code using built-in tools (Bash, AskUserQuestion, Edit).

## Known Stubs

None. The workflow is fully implemented. The word "placeholder" appears in instructional context (telling Claude to use "the target variable" as a placeholder if the target column is ambiguous) — this is intentional guidance, not an unresolved stub.

## Checkpoint: Task 3 (human-verify) — Awaiting Approval

Task 3 is a blocking human-verify checkpoint. The workflow is implemented and committed. Human verification requires running `/doml-new-project` end-to-end in a test directory with a CSV file in `data/raw/`.

**How to verify:**
1. Create test directory: `mkdir -p /tmp/doml-test/data/raw && printf "id,value\n1,1.1\n2,2.2\n" > /tmp/doml-test/data/raw/sales.csv`
2. Run `/doml-new-project` from `/tmp/doml-test/` and walk through the interview
3. Confirm: DuckDB scan shows before Q1, all 5 questions asked, ML type inferred+confirmed, framing sentence shown
4. After confirming framing: check `.planning/PROJECT.md` (all placeholders filled, "We are trying to..." present) and `.planning/config.json` (analysis_language, problem_type, time_factor set)
5. Test error case: `rm /tmp/doml-test/data/raw/sales.csv` and run again — expect "No data files found" error, no `.planning/` changes

**Resume signal:** Type "approved" if end-to-end flow is correct, or describe what needs fixing.

## Next Phase Readiness

- `/doml-new-project` is functional end-to-end pending human checkpoint approval
- Phase 4 (Business Understanding notebook) can begin once PROJECT.md is confirmed fillable with real interview output
- `doml.data_scan` module (Plan 03-02) is successfully integrated
- No blockers

---
*Phase: 03-kickoff-interview*
*Completed: 2026-04-05*

## Self-Check: PASSED

- .claude/doml/workflows/new-project.md: FOUND
- .planning/phases/03-kickoff-interview/03-01-SUMMARY.md: FOUND
- Commit 3c8d7f9 (Task 1 feat): FOUND
- Commit 3eee52d (Task 2 feat): FOUND
