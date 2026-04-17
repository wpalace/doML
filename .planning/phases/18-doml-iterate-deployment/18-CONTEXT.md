# Phase 18: doml-iterate-deployment — Context

**Gathered:** 2026-04-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement `doml-iterate-deployment`: a SKILL.md entry point and `iterate-deployment.md` workflow that detects the current deployment version, validates the leaderboard model hasn't changed, applies `--guidance` to configuration, routes to the appropriate target skill (deploy-cli / deploy-web / deploy-wasm), and regenerates the performance report for the new version.

This phase does NOT modify the deploy-model.md orchestrator, the target skills, or the performance report template — it builds a new iterate-specific workflow that delegates to those existing components.

**Requirements in scope:** ITER-01, ITER-02, ITER-03, ITER-04, ITER-05

</domain>

<decisions>
## Implementation Decisions

### Model Source and Validation

- **D-01: Leaderboard-match guard before iterating**
  - `iterate-deployment.md` re-reads `leaderboard.csv` (or `unsupervised_leaderboard.csv`) to find the current #1 model
  - Compares the leaderboard leader against the model recorded in the most recent `deployment_metadata.json` under `src/`
  - **Same model** → proceed with version bump
  - **Different model** → stop and display:
    ```
    The leaderboard leader has changed since your last deployment.
    Current leader: {new_model}
    Last deployed:  {old_model}

    Did you mean to deploy a new model?
    Run /doml-deploy-model to start a fresh deployment for {new_model}.
    ```
  - No silent auto-upgrade; user must make a deliberate choice to switch models

### Version Scanning

- **D-02: Scan src/ for highest existing vN, write to vN+1**
  - Matches the Phase 13 D-02 pattern (filesystem scan, not assumed)
  - Scans `src/<modelname>/v*/` directories and takes `max(N) + 1` as the new version
  - Before creating, prints: `"src/<modelname>/v2/ exists — iterating to v3/"` (or whichever version)
  - **New model (ITER-03)**: If the user explicitly passes `--model <different.pkl>`, the new folder is `src/<newmodelname>/v1/`; this is the only path where a different model is allowed in iterate-deployment

### Target Selection

- **D-03: --target flag to switch deployment target**
  - `iterate-deployment` accepts an optional `--target {cli|web|wasm}` flag
  - If omitted: re-uses the `target` field from the most recent `deployment_metadata.json` (same target as last deployment)
  - If provided: overrides the target for this iteration — supports the ITER-05 case of changing deployment target without a new model
  - New `deployment_metadata.json` is written with the (possibly updated) target

### Guidance

- **D-04: --guidance shapes deployment configuration**
  - `iterate-deployment` accepts `--guidance "<text>"` as a freeform string
  - Claude reads the guidance text and applies relevant configuration tweaks before invoking the target skill
  - Examples of what guidance can direct:
    - `"optimize for low latency"` → reduce worker threads, disable batch padding in web service
    - `"add batch endpoint"` → instruct deploy-web step to include a `/predict/batch` route
    - `"use quantized model"` → pass quantization flag to deploy-wasm
    - `"increase gunicorn workers"` → edit web service config
  - Guidance is also passed to the performance report narrative step so Claude's analysis reflects the intent
  - Running without `--guidance` is valid (ITER-05) — default is no config changes from prior version

### Workflow Structure

- **D-05: New standalone iterate-deployment.md**
  - `iterate-deployment.md` is a dedicated workflow separate from `deploy-model.md`
  - It handles iterate-specific logic: model validation guard, version scan, guidance application
  - It then delegates to the same existing target skills (`deploy-cli.md` / `deploy-web.md` / `deploy-wasm.md`) exactly as `deploy-model.md` does
  - After the target skill completes, it runs the same performance report step (Step 12 of `deploy-model.md`) — either by copying that step inline or referencing it directly
  - `deploy-model.md` is NOT modified by this phase

### No-New-Model Use Cases (ITER-05)

- **D-06: Three valid no-new-model scenarios**
  - Users can run `iterate-deployment` without changing the model for any of these reasons:
    1. **Config/guidance change**: same model, same target, different `--guidance` (e.g., tune inference settings)
    2. **Target change**: same model, different `--target` (e.g., re-deploy CLI build as web service)
    3. **Baseline refresh**: same model, same target, no guidance — re-runs the deployment and generates a fresh performance report (e.g., after updating Docker base image or dependency versions)
  - All three produce a new `vN+1/` directory with a fresh `deployment_report.ipynb` and HTML

### Claude's Discretion

- Exact argument parsing implementation (`--guidance` quoted string extraction via `sed`)
- Whether guidance application is a discrete workflow step or inline commentary before delegating to target skills
- Whether `deployment_metadata.json` includes a `guidance` field for traceability (recommended but not required)
- Port conflict handling if iterating on a web service while the previous version's container is still running (fail with clear error is acceptable)
- Whether the skill name slug in `src/` uses `model_name` directly from metadata or sanitizes it (same convention as deploy-model — Claude's discretion)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §ITER-01 through ITER-05 — all acceptance criteria for this phase

### Phase 13 — Version scaffolding pattern
- `.planning/phases/13-deployment-workflow-skeleton/13-CONTEXT.md` — D-02 (version scanning), D-05 (`deployment_metadata.json` fields)
- `.claude/doml/workflows/deploy-model.md` — structure to mirror for argument parsing, model resolution, and delegation to target skills

### Phase 14 — CLI target skill
- `.planning/phases/14-cli-binary-target/14-CONTEXT.md`
- `.claude/doml/workflows/deploy-cli.md` — invoked by iterate-deployment for CLI target

### Phase 15 — Web service target skill
- `.planning/phases/15-web-service-target/15-CONTEXT.md`
- `.claude/doml/workflows/deploy-web.md` — invoked by iterate-deployment for web target

### Phase 16 — ONNX/WASM target skill
- `.planning/phases/16-onnx-wasm-target/16-CONTEXT.md`
- `.claude/doml/workflows/deploy-wasm.md` — invoked by iterate-deployment for wasm target

### Phase 17 — Performance report step
- `.planning/phases/17-performance-report/17-CONTEXT.md` — D-03 (trigger placement in orchestrator), D-05 (target routing)
- `.claude/doml/workflows/deploy-model.md` Step 12 — the performance report step to replicate in iterate-deployment

### Existing iterate skill (modelling)
- `.claude/skills/doml-iterate/SKILL.md` — reference for argument pattern (`--guidance` / direction string) used in modelling iterate

</canonical_refs>
