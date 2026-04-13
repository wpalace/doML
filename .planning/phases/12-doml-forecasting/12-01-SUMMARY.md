---
phase: 12-doml-forecasting
plan: "01"
subsystem: forecasting
tags: [time-series, forecasting, pmdarima, arima, prophet, lightgbm, xgboost, skill, workflow]

requires:
  - phase: 10-doml-anomaly-detection
    provides: standalone skill pattern (SKILL.md + workflow .md + Docker exec + HTML report)
  - phase: 11-unified-doml-iterate
    provides: unified iterate pattern confirming skill structure conventions

provides:
  - doml-forecasting skill entry point (.claude/skills/doml-forecasting/SKILL.md)
  - forecasting.md 11-step orchestration workflow (.claude/doml/workflows/forecasting.md)
  - pmdarima dependency declaration in requirements.in
  - FORE-04 deferral documented in ROADMAP.md Phase 12

affects:
  - 12-02-doml-forecasting (notebook template uses SKILL.md and workflow as execution harness)
  - future-milestone-4 (FORE-04 forecast actuals tracking deferred here)

tech-stack:
  added:
    - pmdarima (auto_arima for ARIMA/SARIMA order selection — added to requirements.in)
  patterns:
    - "Standalone skill pattern: SKILL.md frontmatter + execution_context -> workflow .md"
    - "time_factor early-exit gate: read config.json TIME_FACTOR, stop with clear message if false"
    - "Required argument validation: --horizon and --target both required, clear error if absent"
    - "Parameter injection via /tmp Python script: never shell-interpolate user-supplied column names or guidance"
    - "SECURITY comment in workflow documenting injection prevention for all user-supplied args"

key-files:
  created:
    - .claude/skills/doml-forecasting/SKILL.md
    - .claude/doml/workflows/forecasting.md
  modified:
    - requirements.in (pmdarima added after prophet line)

key-decisions:
  - "FORE-04 (forecast actuals tracking) deferred to Milestone 4 — requires multi-session state management out of scope for Phase 12"
  - "ROADMAP.md Phase 12 section was pre-populated by phase planning; Task 3 content already satisfied — no modification needed"
  - "pmdarima placed in requirements.in after prophet, before Visualization block — logical grouping by domain"

patterns-established:
  - "Forecasting skill: /doml-forecasting --horizon N --target COLUMN [optional flags] — required args differ from other skills"
  - "time_factor gate: forecasting skill exits early with actionable message when time_factor=false"
  - "900s Docker timeout for forecasting (vs 600s for anomaly detection) — 6 models take more time"

requirements-completed: [CMD-16, FORE-04]

duration: 8min
completed: 2026-04-13
---

# Phase 12 Plan 01: doml-forecasting Skill + Workflow Summary

**doml-forecasting skill with 11-step forecasting.md workflow, time_factor guard, required --horizon/--target validation, injection-safe parameter injection, and pmdarima dependency**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-04-13T08:00:00Z
- **Completed:** 2026-04-13T08:07:16Z
- **Tasks:** 3 (Tasks 1 and 2 produced commits; Task 3 was a no-op — content pre-populated)
- **Files modified:** 3

## Accomplishments

- Created `.claude/skills/doml-forecasting/SKILL.md` with correct frontmatter (name, argument-hint, allowed-tools, execution_context) mirroring the anomaly-detection pattern
- Created `.claude/doml/workflows/forecasting.md` — 362-line 11-step workflow with time_factor early-exit (CMD-16), required --horizon/--target argument validation, injection-safe parameter passing via /tmp Python scripts, 900s Docker execution timeout, and leaderboard/HTML verification
- Added `pmdarima` to `requirements.in` for auto_arima() ARIMA/SARIMA order selection

## Task Commits

Each task was committed atomically:

1. **Task 1: Create SKILL.md entry point for doml-forecasting** - `65bfcaa` (feat)
2. **Task 2: Create forecasting.md workflow and add pmdarima to requirements.in** - `a7ebba6` (feat)
3. **Task 3: Document FORE-04 deferral** - no commit (ROADMAP.md content was pre-populated by the phase planning process; all acceptance criteria already satisfied)

## Files Created/Modified

- `.claude/skills/doml-forecasting/SKILL.md` — Skill entry point: frontmatter with name/description/argument-hint/allowed-tools, 7-step objective, execution_context -> forecasting.md
- `.claude/doml/workflows/forecasting.md` — 11-step orchestration workflow: state validation, time_factor guard, --horizon/--target required arg parsing, processed-file resolution, notebook copy + param injection, Docker exec 900s, narrative insertion, HTML report + checks, leaderboard verification, STATE.md update
- `requirements.in` — pmdarima added after prophet line in the ML stack section

## Decisions Made

- ROADMAP.md Phase 12 section was already complete when Task 3 ran — the phase planning process had pre-populated it with the plan list, FORE-04 deferral note, and Milestone 4 reference. No modification was necessary; all acceptance criteria passed on first check.
- pmdarima is grouped after prophet in requirements.in with a `# --- Time series forecasting ---` comment block for clarity.
- SECURITY comment in forecasting.md Step 3 and Step 9 explicitly calls out that TARGET, REGRESSORS, and GUIDANCE must never be shell-interpolated — mitigates T-12-01, T-12-02, T-12-03 from the threat model.

## Deviations from Plan

### Task 3 — Pre-populated content (no Rule triggered)

- **Found during:** Task 3 (Document FORE-04 deferral)
- **Situation:** ROADMAP.md Phase 12 section was fully pre-populated by the phase planning process (commit `9495107`). All four acceptance criteria already passed: FORE-04 deferral text present, 12-01-PLAN.md and 12-02-PLAN.md listed, Milestone 4 referenced.
- **Action:** No modifications made to ROADMAP.md. Task verified as satisfied.
- **Impact:** None — this is an optimization, not a gap.

---

**Total deviations:** 0 auto-fixed (0 rule triggers). One no-op task due to pre-populated content.
**Impact on plan:** All three tasks satisfied. No scope creep.

## Issues Encountered

None.

## User Setup Required

After this plan, the analyst must regenerate pinned dependencies and rebuild the Docker image
before using `/doml-forecasting`:

```bash
docker compose run --rm jupyter pip-compile requirements.in
docker compose build
```

This is required because `pmdarima` was added to `requirements.in` but `requirements.txt` has
not yet been regenerated. The forecasting notebook (plan 12-02) depends on `pmdarima` being
installed in the container.

## Next Phase Readiness

- **Plan 12-02** (forecasting.ipynb notebook template) can now proceed — the skill entry point and workflow are in place as the execution harness.
- The notebook template must define a `PARAMS` cell containing `HORIZON = None` for the Step 6 injection script to locate and replace.
- No blockers for plan 12-02.

---

*Phase: 12-doml-forecasting*
*Completed: 2026-04-13*
