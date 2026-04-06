---
phase: 03-kickoff-interview
plan: 01
subsystem: workflow
tags: [doml, interview, duckdb, project-init, askuserquestion, project.md, config.json, docker]

# Dependency graph
requires:
  - phase: 03-kickoff-interview
    plan: 02
    provides: scan_data_folder() and format_scan_report() callable from doml.data_scan
  - phase: 02-framework-skeleton
    provides: new-project.md skeleton with Phase 2 stubs at Steps 2 and 3

provides:
  - .claude/doml/workflows/new-project.md — Steps 2 through 5 fully implemented; workflow is end-to-end functional
  - Step 2 (Docker setup): checks for existing docker-compose.yml, asks permission, copies 4 templates (docker-compose.yml, Dockerfile, requirements.txt, requirements.in)
  - Step 3: DuckDB scan of data/raw/ via scan_data_folder() run inside container via `docker compose exec jupyter python -c "..."`, displayed before interview
  - Step 4: 8-question guided interview with ML type inference, time-factor detection, domain research offer, framing sentence confirmation
  - Step 5: Atomic writes to PROJECT.md (all placeholders filled) and config.json (analysis_language, problem_type, time_factor, dataset.format)
  - Hard stop on missing/empty data/raw/ — no partial writes

affects:
  - Phase 4 Business Understanding (reads filled PROJECT.md as context)
  - Any phase that uses config.json analysis_language or problem_type fields
  - /doml-new-project user experience end-to-end
  - Docker setup (docker-compose.yml, Dockerfile, requirements.txt templates)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "AskUserQuestion for all user-facing interview questions — renders TUI, handles text_mode fallback"
    - "Atomic write pattern: all answers collected before any file writes"
    - "doml.data_scan integration via docker compose exec — no local Python assumed"
    - "PROJECT_ROOT env var (REPR-02) for data/raw/ path resolution"
    - "SystemExit(1) on scan ValueError — hard stop, no partial writes"
    - "time_factor upgrade path: regression + time_factor=True → offer time_series reclassification"
    - "domain_research conditional: user opts in → summary appended to PROJECT.md Problem Framing section"
    - "Docker setup gate: check for existing docker-compose.yml before copying templates"

key-files:
  created:
    - .claude/doml/templates/Dockerfile
    - .claude/doml/templates/requirements.in
    - .claude/doml/templates/requirements.txt
  modified:
    - .claude/doml/workflows/new-project.md
    - .claude/doml/templates/docker-compose.yml

key-decisions:
  - "Docker setup added as Step 2 (steps renumbered: Docker=2, Scan=3, Interview=4, Artifacts=5, Summary=6)"
  - "Scan runs via docker compose exec jupyter python -c — no local Python dependency"
  - "CHOWN_HOME/CHOWN_HOME_OPTS removed from docker-compose templates — caused container crash on :ro mounts"
  - "Step 2 calls doml.data_scan via docker compose exec — consistent with container-first architecture"
  - "scan_results stored in memory between steps — used for target column inference and dataset.format"
  - "Framing sentence gating: PROJECT.md and config.json only written after user confirms the framing sentence"
  - "domain_research_summary appended inline to Problem Framing section in PROJECT.md (no separate file)"
  - "config.json write: read full JSON → modify specific keys → write complete updated JSON"

patterns-established:
  - "AskUserQuestion retry pattern: empty/whitespace response → retry once → fall back to plain-text prompt"
  - "Inference + confirm: Claude reasons over free-text Q1-Q5, proposes problem_type with explanation, user confirms or corrects"
  - "Time-factor upgrade: if time_factor=True and problem_type=regression → AskUserQuestion upgrade offer to time_series"
  - "Atomic output writes: all answers collected → framing sentence confirmed → PROJECT.md written → config.json written"
  - "Docker-first scan: all Python execution routed through docker compose exec, not local interpreter"

requirements-completed: [INTV-01, INTV-02, INTV-04, INTV-05]

# Metrics
duration: 45min
completed: 2026-04-05
---

# Phase 3 Plan 01: Kickoff Interview Workflow Summary

**Full /doml-new-project workflow implemented: Docker setup gate, DuckDB scan via container exec, 8-question guided interview with ML type inference, and atomic PROJECT.md + config.json writes — verified end-to-end in ~/source/dtest**

## Performance

- **Duration:** 45 min (including post-checkpoint fixes)
- **Started:** 2026-04-05T14:30:00Z
- **Completed:** 2026-04-05
- **Tasks:** 2 planned + 3 deviation commits (Docker step, template fixes, CHOWN_HOME fix)
- **Files modified:** 5

## Accomplishments

- `new-project.md` Step 2 stub replaced with live DuckDB scan via `doml.data_scan.scan_data_folder()` — hard stop on empty/missing `data/raw/`, scan report displayed before any interview questions
- `new-project.md` Step 3 stub replaced with full 8-question guided interview: Q1-Q5 (business context + time factor), ML type inference with user confirm/correct, time-factor regression upgrade offer, domain research opt-in, language preference, framing sentence confirm
- Docker setup step added (Step 2 in final numbering) — copies 4 templates on first run, checks for existing setup, asks permission before overwriting
- Scan execution moved inside container (`docker compose exec jupyter python -c "..."`) — no local Python dependency
- `CHOWN_HOME` / `CHOWN_HOME_OPTS` env vars removed from docker-compose templates — they crashed containers when `data/raw` is mounted `:ro`
- Atomic write pattern enforced: PROJECT.md and config.json written only after framing sentence confirmed
- INTV-01, INTV-02, INTV-04, INTV-05 requirements fulfilled; verified end-to-end in ~/source/dtest

## Task Commits

Each planned task was committed atomically:

1. **Task 1: Replace Step 2 stub with DuckDB scan implementation** - `3c8d7f9` (feat)
2. **Task 2: Replace Step 3 stub with full guided kickoff interview** - `3eee52d` (feat)

Post-checkpoint deviation fixes:

3. **Deviation: Add Docker setup step + fix scan to run in container** - `b44f97a` (feat)
4. **Deviation: Add Dockerfile/requirements templates; copy all 4 files on docker setup** - `4274545` (fix)
5. **Deviation: Remove CHOWN_HOME vars from docker-compose templates** - `f2ad9e5` (fix)

## Files Created/Modified

- `.claude/doml/workflows/new-project.md` — Steps renumbered (Docker=2, Scan=3, Interview=4, Artifacts=5, Summary=6); scan runs in container
- `.claude/doml/templates/docker-compose.yml` — CHOWN_HOME/CHOWN_HOME_OPTS removed
- `.claude/doml/templates/Dockerfile` — new template created for docker setup step
- `.claude/doml/templates/requirements.in` — new template created for docker setup step
- `.claude/doml/templates/requirements.txt` — new template created for docker setup step

## Decisions Made

- **Docker setup added as a workflow step:** During end-to-end testing it became clear the workflow needed to bootstrap Docker before scanning data. Step 2 checks for an existing `docker-compose.yml`, asks permission before overwriting, and copies all 4 templates (docker-compose.yml, Dockerfile, requirements.txt, requirements.in).
- **Steps renumbered:** Docker=2, Scan=3, Interview=4, Artifacts=5, Summary=6. Avoids cramming Docker into an existing step.
- **Scan via docker compose exec:** Running `python -c "..."` locally fails when the user has no local Python or when doml package is only installed in the container. Routing through `docker compose exec jupyter` is consistent with the container-first architecture.
- **CHOWN_HOME removed:** The env vars caused the Jupyter container to crash when `data/raw` or `data/external` are mounted read-only (`:ro`). Removed from both the template and the checked-in `docker-compose.yml`. This is a correctness fix — CHOWN_HOME is only relevant when running as a non-root user without pre-chowned volumes, and the `:ro` mount makes it fail.
- **scan_results in memory between steps:** Step 3 stores `scan_results` list so Step 4 can use it for target column inference and dataset.format population. No temp file needed.
- **Framing sentence as the write gate:** Atomic write is gated on user confirming the framing sentence (not just completing Q7). Matches Decision 2 in 03-CONTEXT.md.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Docker setup step added as Step 2**
- **Found during:** Task 3 (human-verify checkpoint — end-to-end test)
- **Issue:** Workflow assumed Docker was already running. New users running `/doml-new-project` in a fresh directory have no docker-compose.yml and no running container — the scan step would immediately fail.
- **Fix:** Added Step 2 (Docker setup): checks for existing `docker-compose.yml`, asks permission, copies 4 templates. Steps 3-6 renumbered accordingly.
- **Files modified:** `.claude/doml/workflows/new-project.md`, `.claude/doml/templates/docker-compose.yml`, `.claude/doml/templates/Dockerfile`, `.claude/doml/templates/requirements.in`, `.claude/doml/templates/requirements.txt`
- **Verification:** End-to-end test in ~/source/dtest passed
- **Committed in:** `b44f97a`, `4274545`

**2. [Rule 1 - Bug] Scan moved to run inside container via docker compose exec**
- **Found during:** Docker setup deviation (above)
- **Issue:** Step 3 originally ran `python -c "..."` locally. This fails without a local Python + doml install, and contradicts the container-first architecture.
- **Fix:** Changed scan Python snippet to run via `docker compose exec jupyter python -c "..."`.
- **Files modified:** `.claude/doml/workflows/new-project.md`
- **Committed in:** `b44f97a`

**3. [Rule 1 - Bug] CHOWN_HOME/CHOWN_HOME_OPTS removed from docker-compose templates**
- **Found during:** Docker setup deviation — container crash on :ro mounts
- **Issue:** `CHOWN_HOME: "yes"` and `CHOWN_HOME_OPTS: "--from=root"` caused the Jupyter container to crash when `data/raw` or `data/external` are mounted `:ro`. The chown operation attempts to traverse and modify the mount, which fails on read-only volumes.
- **Fix:** Removed both env vars from `.claude/doml/templates/docker-compose.yml` and `docker-compose.yml`.
- **Files modified:** `.claude/doml/templates/docker-compose.yml`, `docker-compose.yml` (root)
- **Committed in:** `f2ad9e5`

---

**Total deviations:** 3 auto-fixed (1 missing critical, 2 bugs)
**Impact on plan:** All fixes were necessary for the workflow to function correctly in a real user environment. No scope creep — Docker setup is required infrastructure for the scan step to work.

## Issues Encountered

- Container crash on first run due to CHOWN_HOME + :ro mount conflict — diagnosed and fixed before end-to-end test completed.
- scan_data_folder needed to run inside the container, not locally — scan step rewritten to use `docker compose exec jupyter`.

## User Setup Required

None — the Docker setup step in the workflow handles bootstrapping automatically. No manual configuration steps required beyond running `/doml-new-project`.

## Known Stubs

None. The workflow is fully implemented and verified end-to-end.

## Next Phase Readiness

- `/doml-new-project` is functional end-to-end — verified in ~/source/dtest
- Phase 4 (Business Understanding notebook) can begin: PROJECT.md is confirmed fillable with real interview output
- `doml.data_scan` module (Plan 03-02) is integrated and exercised through the container
- Docker templates (Dockerfile, requirements.txt, requirements.in) are in place for new projects
- No blockers

---
*Phase: 03-kickoff-interview*
*Completed: 2026-04-05*

## Self-Check: PASSED

- .claude/doml/workflows/new-project.md: FOUND
- .claude/doml/templates/Dockerfile: FOUND
- .claude/doml/templates/requirements.in: FOUND
- .claude/doml/templates/requirements.txt: FOUND
- .planning/phases/03-kickoff-interview/03-01-SUMMARY.md: FOUND
- Commit 3c8d7f9 (Task 1 feat): FOUND
- Commit 3eee52d (Task 2 feat): FOUND
- Commit b44f97a (Docker setup deviation): FOUND
- Commit 4274545 (templates deviation): FOUND
- Commit f2ad9e5 (CHOWN_HOME fix): FOUND
