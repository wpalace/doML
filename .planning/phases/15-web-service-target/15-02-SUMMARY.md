---
phase: 15-web-service-target
plan: "02"
subsystem: deploy
tags: [fastapi, deployment, web-service, jinja2, pydantic, docker]

# Dependency graph
requires:
  - phase: 15-web-service-target
    plan: "01"
    provides: deploy-model.md enriched with feature_schema categories/examples and problem_type
provides:
  - .claude/skills/doml-deploy-web/SKILL.md — /doml-deploy-web command entry point
  - .claude/doml/workflows/deploy-web.md — full 13-step web service generation workflow
affects:
  - Users running /doml-deploy-web get app.py, templates/index.html, requirements.serve.txt, Dockerfile.serve, docker-compose.serve.yml

# Tech tracking
tech-stack:
  added:
    - FastAPI (app.py template)
    - uvicorn (app.py template)
    - Jinja2 (templates/index.html)
    - pydantic create_model (dynamic request model)
  patterns:
    - "Dynamic Pydantic model via create_model() at app startup — no hardcoded field definitions"
    - "python3 heredoc file generation pattern — same as deploy-cli.md"
    - "Shell env-var temp file (/tmp/doml_web_meta.sh) for metadata extraction — same as deploy-cli.md"
    - "Jinja2 template with {% for feature %} loop — categoricals as <select>, numerics as <input type=number>"

key-files:
  created:
    - .claude/skills/doml-deploy-web/SKILL.md
    - .claude/doml/workflows/deploy-web.md
  modified: []

key-decisions:
  - "app.py uses pydantic.create_model() at startup from feature_schema — D-02 from CONTEXT.md"
  - "Dockerfile.serve uses python:3.14-slim — D-03 from CONTEXT.md"
  - "docker-compose.serve.yml maps host:8080 → container:8080 — D-03 from CONTEXT.md"
  - "Probability bars rendered inline via CSS width percent — D-04 from CONTEXT.md"
  - "No data/ mount in docker-compose.serve.yml — service self-contained from deployment_metadata.json (D-01)"
  - "Step 4 src/ mount check is informational-only (non-blocking) — web service builds from Dockerfile.serve independently"

patterns-established:
  - "deploy-web.md follows identical 13-step header pattern as deploy-cli.md (10 steps)"
  - "SKILL.md structure matches doml-deploy-model/SKILL.md exactly: name, description, argument-hint, allowed-tools, objective, execution_context, context, process"

requirements-completed:
  - WEB-01
  - WEB-02
  - WEB-03
  - WEB-04
  - WEB-05
  - WEB-06
  - WEB-07

# Metrics
duration: 10min
completed: 2026-04-16
---

# Phase 15 Plan 02: Web Service Target — deploy-web.md and SKILL.md Summary

**FastAPI web service generator: SKILL.md entry point + 13-step deploy-web.md workflow that writes app.py (dynamic Pydantic model), Jinja2 prediction form, requirements.serve.txt, Dockerfile.serve, and docker-compose.serve.yml into src/<modelname>/vN/**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-04-16T07:57:00Z
- **Completed:** 2026-04-16T08:07:00Z
- **Tasks:** 2
- **Files created:** 2

## Accomplishments

- `/doml-deploy-web` registered as a doml skill — SKILL.md routes to deploy-web.md with correct frontmatter, argument-hint, and 10-item objective
- `deploy-web.md` written with all 13 steps: deployment directory discovery, metadata extraction, model copy, app.py generation (dynamic Pydantic model with type mapping int64/float64→float, object→str), Jinja2 template generation (categoricals as `<select>`, numerics as `<input type=number>`, inline-fetch JS, probability bars), requirements.serve.txt with pinned deps, Dockerfile.serve (python:3.14-slim, copies model.pkl + deployment_metadata.json), docker-compose.serve.yml (port 8080), metadata update, STATE.md update, confirmation output
- All UI-SPEC.md values honored: system-ui font, #4f46e5 accent, #111827 text, #f9fafb background, 600px max-width card, 6px border-radius

## Task Commits

1. **Task 1: Create SKILL.md entry point for /doml-deploy-web** - `a4e0639` (feat)
2. **Task 2: Write deploy-web.md — full 13-step web service generation workflow** - `733b69e` (feat)

## Files Created/Modified

- `.claude/skills/doml-deploy-web/SKILL.md` — /doml-deploy-web skill entry point, routes to deploy-web.md
- `.claude/doml/workflows/deploy-web.md` — full 13-step workflow generating all 5 web service artifacts

## Decisions Made

- `pydantic.create_model()` at app startup (D-02): type mapping int64/float64 → float, object → str, fallback → str
- `python:3.14-slim` Dockerfile base (D-03): matches CONTEXT.md decision
- Port 8080 for both host and container (D-03): no port conflicts with Jupyter on 8888
- Probability bars via inline CSS `width: ${pct}%` with `background: #4f46e5` (D-04)
- No `./data/` mount in docker-compose.serve.yml (D-01): service reads categories from deployment_metadata.json at startup only

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None — all generated file content is template-driven with runtime data; no hardcoded placeholder values.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `/doml-deploy-web` is a fully registered and functional skill
- `deploy-web.md` generates all 5 web service artifacts from `deployment_metadata.json` produced by Phase 13 + Plan 01
- Users run `docker compose -f src/<modelname>/vN/docker-compose.serve.yml up --build` to start the service
- Service exposes GET /, POST /predict, GET /health, GET /schema, GET /docs on port 8080
- No blockers for next phase or user testing

---
*Phase: 15-web-service-target*
*Completed: 2026-04-16*
