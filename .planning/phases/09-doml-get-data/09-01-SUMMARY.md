---
phase: 09-doml-get-data
plan: 01
subsystem: doml-skill
tags: [kaggle, curl, docker-cp, git-lfs, provenance, sha256, data-acquisition]

# Dependency graph
requires:
  - phase: 08-doml-crisp-dm-commands
    provides: established SKILL.md + workflow delegation pattern used here
provides:
  - doml-get-data skill (SKILL.md entry point + get-data.md workflow)
  - Kaggle dataset download via docker compose exec + docker cp
  - URL download via curl with ZIP extraction
  - SHA-256 provenance logging to data/raw/README.md
  - Kaggle env var slots in docker-compose.yml template
  - kaggle package in requirements.in for Docker image
  - data/raw/.stage/ excluded from git
affects: [doml-new-project, doml-data-understanding, 09-02]

# Tech tracking
tech-stack:
  added: [kaggle CLI (requirements.in), docker cp, sha256sum, git-lfs (graceful degrade)]
  patterns:
    - SKILL.md delegates to workflow via @execution_context reference
    - In-container staging via /tmp/doml-stage then docker cp (workaround for :ro mount)
    - Pre-run .stage/ cleanup prevents stale-data contamination across runs

key-files:
  created:
    - .claude/skills/doml-get-data/SKILL.md
    - .claude/doml/workflows/get-data.md
  modified:
    - .claude/doml/templates/docker-compose.yml
    - requirements.in
    - .gitignore

key-decisions:
  - "URL downloads run on host with curl (not docker compose exec) — no Kaggle auth needed, simpler flow"
  - "In-container staging uses /tmp/doml-stage (not data/raw/.stage/) — data/raw is :ro inside container"
  - "docker cp trailing /. is mandatory — without it, docker copies the directory itself not its contents"
  - "git-lfs check wraps entire LFS block — warn and continue if not installed (verified: not on this host)"
  - "Kaggle credential check runs inside container — env vars are set there, not on host"

patterns-established:
  - "Pattern: Docker exec staging — download to /tmp/doml-stage inside container, docker cp to host, clean up"
  - "Pattern: Pre-run cleanup — rm -rf .stage at start of each run to prevent stale file contamination"
  - "Pattern: Provenance append — echo blank line first, then heredoc to data/raw/README.md (never overwrite)"

requirements-completed: [CMD-14, DATA-01, DATA-02, DATA-04]

# Metrics
duration: 10min
completed: 2026-04-11
---

# Phase 9 Plan 01: doml-get-data Skill Summary

**doml-get-data SKILL.md + 8-step get-data.md workflow for Kaggle and URL dataset acquisition with SHA-256 provenance logging**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-04-11T07:01:00Z
- **Completed:** 2026-04-11T07:11:42Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Created `.claude/skills/doml-get-data/SKILL.md` following the established DoML skill pattern (name, argument-hint, allowed-tools, execution_context delegation)
- Created `.claude/doml/workflows/get-data.md` with 8 steps covering: argument parsing, Docker check, Kaggle flow (credential check + staged download + docker cp), URL flow (curl + ZIP extraction + format move), Git LFS setup, SHA-256 provenance computation, README.md append, and display summary
- Applied all 8 RESEARCH.md pitfall mitigations inline: docker cp `/.` suffix, nested ZIP extraction, `.stage/` pre-run cleanup, URL query-string filename stripping, container restart note in credential error, git-lfs graceful degrade, README.md blank-line guard before append, `head -1` for scaled-service container ID
- Updated docker-compose.yml template with `KAGGLE_USERNAME` and `KAGGLE_KEY` env var slots (empty default via `:-`)
- Added `kaggle` to `requirements.in` under a `# --- Data acquisition ---` section header
- Added `data/raw/.stage/` to `.gitignore` to prevent staging dir from entering git history

## Task Commits

Each task was committed atomically:

1. **Task 1: Create doml-get-data SKILL.md entry point** - `229f274` (feat)
2. **Task 2: Create get-data.md acquisition workflow** - `ef26c78` (feat)
3. **Task 3: Update config files** - `04ad094` (chore)

## Files Created/Modified

- `.claude/skills/doml-get-data/SKILL.md` - Skill entry point; delegates to get-data.md via @execution_context; accepts `kaggle owner/slug` or `url https://...` via $ARGUMENTS
- `.claude/doml/workflows/get-data.md` - 332-line full acquisition workflow with executable bash code blocks for each step
- `.claude/doml/templates/docker-compose.yml` - Added KAGGLE_USERNAME and KAGGLE_KEY env var slots after PROJECT_ROOT
- `requirements.in` - Added kaggle package in new Data acquisition section with pip-compile regeneration reminder
- `.gitignore` - Added data/raw/.stage/ immediately after the data/raw/* exclusion block

## Decisions Made

- URL downloads run on the host with `curl` rather than routing through `docker compose exec` — no Kaggle auth is needed for public URLs, and host-side download is simpler
- In-container staging uses `/tmp/doml-stage` (not `data/raw/.stage/`) because `data/raw/` is mounted `:ro` inside the container; `.stage/` on the host is for URL downloads only
- docker cp path must end with `/.` — without it, Docker copies the `doml-stage` directory itself (not its contents); this pitfall is documented with a warning comment in the workflow

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Known Stubs

None — this plan creates workflow markdown files (no data-flow stubs or placeholder UI).

## Threat Flags

None — no new network endpoints or trust boundaries introduced beyond what the threat model in the plan already covers (T-09-01 through T-09-07 applied as specified).

## Next Phase Readiness

- `doml-get-data` skill is complete and follows the established SKILL.md → workflow delegation pattern
- Plan 09-02 (new-project.md integration) can proceed — it will modify `new-project.md` Step 3 to invoke the get-data flow when `data/raw/` is empty
- After plan 09-02, run `docker compose run --rm jupyter pip-compile requirements.in` and `docker compose build` to include the kaggle package in the Docker image

---
*Phase: 09-doml-get-data*
*Completed: 2026-04-11*
