# Phase 15: Web Service Target — Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Generate `app.py` (FastAPI with a dynamic Pydantic request model, `/predict`, `/health`, `/schema` endpoints, and a `/` form route), a Jinja2 prediction form template, `Dockerfile.serve`, and `docker-compose.serve.yml` — all written into `src/<modelname>/vN/`.

Phase 15 reads from `src/<modelname>/vN/deployment_metadata.json` (produced by Phase 13) and populates that directory with the web service artifacts. Running `docker compose -f src/<modelname>/vN/docker-compose.serve.yml up` must start the service with no manual setup.

**Requirements in scope:** WEB-01, WEB-02, WEB-03, WEB-04, WEB-05, WEB-06, WEB-07

</domain>

<decisions>
## Implementation Decisions

### Categorical Dropdown Source

- **D-01: Embed category values into `deployment_metadata.json` at deploy time**
  - When `doml-deploy-model` runs (Phase 13 / deploy-model.md workflow), scan `data/processed/preprocessed_*.csv` for unique values per categorical column
  - Store as `categories: ["EU", "NA", "APAC"]` (or `null` for numeric) in each `feature_schema` entry
  - `app.py` reads `deployment_metadata.json` at startup — no data directory mount needed at runtime
  - `docker-compose.serve.yml` does NOT mount `./data/` — the service is fully self-contained from `deployment_metadata.json`
  - Extended `feature_schema` entry shape: `{name, type, categories}` where `categories` is a list of strings for `object`-typed columns and `null` for numeric columns

  > **Impact on Phase 13 workflow:** `deploy-model.md` must be updated to include the category scan step before writing `deployment_metadata.json`. This is a backward-compatible extension — existing fields are unchanged.

### Pydantic Model Strategy

- **D-02: Dynamic `create_model()` at startup**
  - `app.py` is a single generated file that reads `deployment_metadata.json` at startup and calls `pydantic.create_model()` to build the request model
  - Type mapping: `int64` / `float64` → `float`; `object` → `str`; everything else → `str`
  - The generated `app.py` is the same template for every deployment — no hardcoded field definitions
  - Pydantic v2 compatible (`create_model` from `pydantic`)

### Docker Serve Base Image

- **D-03: `python:3.14-slim`**
  - `Dockerfile.serve` uses `python:3.14-slim` as base
  - A `requirements.serve.txt` is generated alongside `app.py` with pinned versions: `fastapi`, `uvicorn[standard]`, `scikit-learn`, `joblib`, `jinja2`, `pandas`, `numpy`
  - Service starts via: `CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]`
  - `docker-compose.serve.yml` maps host port 8080 → container port 8080

### Prediction Result Display

- **D-04: Formatted card with probability bars**
  - After `fetch()` returns, render a styled result card below the submit button
  - All problem types: show `Prediction: <value>` prominently
  - Classification only: also render a probability table — one row per class with a CSS bar (width = probability %) and the percentage label
  - Result card is injected into a `<div id="result">` placeholder via `innerHTML`; no page reload
  - Regression / clustering: show only the prediction value (no probability display)

### Claude's Discretion

- Exact CSS styling for the result card (minimal inline styles or a `<style>` block in the template)
- Whether the Jinja2 template is a separate `templates/index.html.j2` file or rendered as a Python string via `jinja2.Environment`
- Error handling wording for `/predict` validation errors (Pydantic will auto-generate 422 responses; no custom error UX required)
- Whether `GET /schema` returns `feature_schema` verbatim from `deployment_metadata.json` or restructures it (verbatim is fine)
- uvicorn worker count in `docker-compose.serve.yml` (single worker is fine for this use case)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §WEB — WEB-01 through WEB-07 define all acceptance criteria for this phase

### Phase 13 outputs
- `.planning/phases/13-deployment-workflow-skeleton/13-CONTEXT.md` — Phase 13 decisions; directory structure, `deployment_metadata.json` fields
- `.claude/doml/workflows/deploy-model.md` — produces `deployment_metadata.json`; **must be updated** to include category scan per D-01

### Phase 14 patterns
- `.planning/phases/14-cli-binary-target/14-CONTEXT.md` — D-02 (preprocessed-schema input), D-04 (classification label + probabilities); same conventions apply to web service
- `.claude/doml/workflows/deploy-cli.md` — reference for workflow step structure and `gsd-tools.cjs` commit pattern

### Prior phase patterns
- `.claude/doml/workflows/modelling.md` — sklearn Pipeline `.predict()` / `.predict_proba()` availability
- `.claude/skills/doml-deploy-cli/SKILL.md` — reference SKILL.md format for new `doml-deploy-web` skill

### Data contracts
- `src/<modelname>/vN/deployment_metadata.json` — fields: `model_file`, `model_name`, `target`, `build_date`, `version`, `feature_schema` (`[{name, type, categories}]` — `categories` added by this phase's D-01 requirement on deploy-model)
- `models/best_model.pkl` — sklearn Pipeline; accepts preprocessed-schema input
- `data/processed/preprocessed_*.csv` — read at deploy time only (for category extraction); NOT mounted at runtime

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `gsd-tools.cjs` commit helper — used by all doml workflows; same pattern applies
- `AskUserQuestion` pattern — all interactive doml commands follow the same header/options structure
- `docker compose exec jupyter` invocation — established pattern for running Python inside container (used in Phase 14 for PyInstaller build; Phase 15 uses it for category extraction during deploy)

### Established Patterns
- SKILL.md structure: `name`, `description`, `argument-hint`, `allowed-tools`, `<objective>`, `<execution_context>`, `<context>`, `<process>` — must match existing doml skill files exactly
- Workflow steps numbered with `### Step N —` header
- Config read via: `python3 -c "import json; c=json.load(open('.planning/config.json')); print(c.get('problem_type','regression'))"`

### Integration Points
- Reads from: `src/<modelname>/vN/deployment_metadata.json` (already written by Phase 13)
- Writes to: `src/<modelname>/vN/app.py`, `src/<modelname>/vN/requirements.serve.txt`, `src/<modelname>/vN/templates/index.html`, `src/<modelname>/vN/Dockerfile.serve`, `src/<modelname>/vN/docker-compose.serve.yml`
- Updates: `deploy-model.md` — adds category scan step before writing `deployment_metadata.json`
- Service port: 8080 (host and container)
- Does NOT invoke Docker for the generation step — all artifacts are written by the workflow directly; user runs `docker compose up` themselves

</code_context>

<specifics>
## Specific Ideas

- `feature_schema` category scan: run `docker compose exec jupyter python3 -c "..."` to read the preprocessed CSV inside the container where pandas is guaranteed available
- `app.py` startup: load `deployment_metadata.json` from the same directory as `app.py` using `Path(__file__).parent / 'deployment_metadata.json'` so the working directory doesn't matter
- Jinja2 template: render categoricals as `<select name="{name}">` with one `<option>` per category; render numerics as `<input type="number" name="{name}" step="any">`
- The `<div id="result">` should be empty initially; `fetch()` on form submit calls `POST /predict` with `Content-Type: application/json` and sets `innerHTML` on success or error
- For classification probability bars: use inline `style="width: {pct}%; background: #4f46e5; height: 12px;"` — no external CSS dependency
- `GET /schema` should include `example` values: read first row of `preprocessed_*.csv` at deploy time and embed into `deployment_metadata.json` as `example` per feature (same pattern as Phase 14 D-03 for `--help` values)

</specifics>

<deferred>
## Deferred Ideas

- Auth/security on the endpoint — no auth required for this phase; open service is acceptable for local/internal use
- Multi-worker uvicorn configuration — single worker is sufficient; scaling is out of scope for v1.4
- HTTPS / TLS termination — user responsibility via reverse proxy; not generated by this phase
- Windows/macOS Docker serve — Linux x86_64 container covers the v1.4 scope

</deferred>

---

*Phase: 15-web-service-target*
*Context gathered: 2026-04-16*
