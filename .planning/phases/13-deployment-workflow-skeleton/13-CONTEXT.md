# Phase 13: Deployment Workflow Skeleton — Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement `doml-deploy-model`: a SKILL.md entry point and `deploy-model.md` workflow that handles model resolution, interactive target selection, versioned `src/<modelname>/vN/` directory creation, `deployment_metadata.json` writing, and `model_name` extension to `model_metadata.json`.

This phase does NOT build any deployment target (CLI binary, web service, ONNX/WASM). Those are Phases 14–16. Phase 13 ends after scaffolding the output directory and writing metadata — leaving the directory ready for the target-specific phase to populate.

**Requirements in scope:** DEPLOY-01, DEPLOY-02, DEPLOY-03, DEPLOY-04, DEPLOY-05

</domain>

<decisions>
## Implementation Decisions

### Target Selection

- **D-01: No `--target` flag — always interactive**
  - Target selection is always via AskUserQuestion menu (CLI binary / Web service / ONNX/WASM)
  - No `--target` flag on the command — every invocation prompts the user interactively
  - Rationale: keeps the interface simple and consistent with the guided interview style of other doml commands

### Collision Handling

- **D-02: Auto-increment version with announcement**
  - When `src/<modelname>/v1/` already exists, the workflow scans for the highest existing `vN` directory and writes to `vN+1`
  - Before creating the new directory, print: `"src/<modelname>/v1/ exists — deploying to v2/"` (or whichever version)
  - No confirmation pause — just announce and continue
  - Version scanning is from the filesystem, not assumed (matches ITER-02 pattern in doml-iterate)

### Model Resolution

- **D-03: Leaderboard-based #1 model resolution (default)**
  - Reads `models/leaderboard.csv` (supervised) or `models/unsupervised_leaderboard.csv` (unsupervised/clustering) to find the top-ranked model
  - `--model <file>` flag overrides the default and uses the specified model file directly (DEPLOY-02)
  - If no leaderboard file and no `--model` flag: stop with a message directing the user to run `/doml-modelling` first

- **D-04: `model_name` derivation (DEPLOY-05)**
  - Check if `model_metadata.json` already has a `model_name` field (it does for all runs using the current templates)
  - If missing (older project or unsupervised run): load the `.pkl` artifact, call `type(model).__name__`, and add `model_name` to the JSON
  - Write the updated `model_metadata.json` in-place — no other fields modified

### Skeleton Output

- **D-05: Directory + metadata only — no stub files**
  - Phase 13 creates `src/<modelname>/vN/` and writes `deployment_metadata.json` inside it
  - No placeholder `predict.py`, `Dockerfile`, or HTML stubs — those are Phase 14/15/16 responsibilities
  - `deployment_metadata.json` fields: `model_file`, `target`, `build_date`, `feature_schema` (from `model_metadata.json`), `model_name`, `version`

### Claude's Discretion

- Exact format of the `model_name` slug used as the directory name (e.g., `XGBRegressor` → `xgb_regressor` vs `xgboost_regressor`) — lowercase + underscores is fine
- Whether to use `model_name` from metadata directly or sanitize it for filesystem safety (strip spaces/parens)
- Step ordering within the workflow (validation before or after target selection)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §DEPLOY — DEPLOY-01 through DEPLOY-05 define all acceptance criteria for this phase

### Prior phase patterns
- `.claude/doml/workflows/modelling.md` — leaderboard resolution and `model_metadata.json` write pattern
- `.claude/doml/workflows/iterate.md` — version scanning pattern (`vN+1` logic, filesystem scan not assumed)
- `.claude/skills/doml-modelling/SKILL.md` — reference skill structure for SKILL.md format

### Data contracts
- `models/leaderboard.csv` — supervised ranking source (`model` column = model name)
- `models/unsupervised_leaderboard.csv` — unsupervised ranking source
- `models/model_metadata.json` — existing fields: `model_name`, `feature_names`, `problem_type`, `training_date`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `gsd-tools.cjs` commit helper — used by all other doml workflows for committing artifacts; use same pattern
- `AskUserQuestion` pattern — all interactive doml commands use it; follow the same header/options structure

### Established Patterns
- SKILL.md structure: `name`, `description`, `argument-hint`, `allowed-tools`, `<objective>`, `<execution_context>`, `<context>`, `<process>` — must match existing doml skill files exactly
- Workflow steps numbered with `### Step N —` header
- Config read via: `python3 -c "import json; c=json.load(open('.planning/config.json')); print(c.get('problem_type','regression'))"`
- Leaderboard read: DuckDB or pandas inside `docker compose exec jupyter` bash snippet
- State update at end of workflow using `gsd-tools.cjs state record-session`

### Integration Points
- Reads from: `models/leaderboard.csv` or `models/unsupervised_leaderboard.csv`, `models/model_metadata.json`, `models/best_model.pkl` (for class name fallback), `.planning/config.json`
- Writes to: `src/<modelname>/vN/deployment_metadata.json`, `models/model_metadata.json` (model_name field addition only)
- Does NOT invoke Docker — metadata operations are pure file I/O handled by the workflow (no notebook execution)

</code_context>

<specifics>
## Specific Ideas

- The `model_name` used as directory slug should be sanitized: strip parentheses, replace spaces with underscores, lowercase (e.g., `"XGBoost (tuned)"` → `xgboost_tuned` or just `xgboost`)
- The interactive target menu labels should match REQUIREMENTS.md language exactly: "CLI binary", "Web service (FastAPI + Docker)", "ONNX/WASM page"
- `deployment_metadata.json` should embed `feature_schema` as the full list of `{name, type}` objects (not just names) to give downstream target phases everything they need

</specifics>

<deferred>
## Deferred Ideas

- **Problem type scope edge cases** — clustering (unsupervised_leaderboard) and forecasting leaderboard resolution not explicitly discussed; Claude should handle via config.json routing as per existing patterns
- **`--model` override UI** — DEPLOY-02 requires flag support; discussion focused on the interactive case; flag implementation is straightforward, left to planner

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 13-deployment-workflow-skeleton*
*Context gathered: 2026-04-14*
