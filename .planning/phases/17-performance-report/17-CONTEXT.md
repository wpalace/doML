# Phase 17: Performance Report — Context

**Gathered:** 2026-04-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement `deployment_report.ipynb` as a notebook template and nbconvert pipeline — covering single/batch latency benchmarks, memory footprint, throughput projection, and a parity test that asserts the deployed endpoint matches in-memory model output. Generate `reports/deployment_report.html` with code hidden and a Claude API narrative summarising results.

This phase adds a final step to `deploy-model.md` (the orchestrator) so the report runs automatically after every deployment target completes. Phase 17 does NOT build any new deployment target.

**Requirements in scope:** PERF-01, PERF-02, PERF-03, PERF-04, PERF-05, PERF-06, PERF-07

</domain>

<decisions>
## Implementation Decisions

### ONNX/WASM Benchmarking

- **D-01: Python onnxruntime approximation for WASM target**
  - For the ONNX/WASM target, benchmark by running `model.onnx` via the Python `onnxruntime` package inside Docker
  - This approximates browser-side latency — the report notes clearly: "benchmarked via Python onnxruntime; browser performance may vary"
  - No Playwright or headless browser dependency
  - Parity test for WASM: run `model.onnx` via Python onnxruntime, compare outputs against `pipeline.predict()` in-memory — same tolerance rules as other targets (regression atol=1e-4; classification exact labels; clustering exact cluster IDs)

### Web Service Container Management

- **D-02: Auto-start/stop Docker container for web service benchmarking**
  - Notebook spins up the FastAPI container via `docker compose -f src/<modelname>/vN/docker-compose.serve.yml up -d`
  - Polls `GET /health` with a timeout (e.g., 30 s, 1 s intervals) before proceeding
  - Runs all latency and parity benchmarks against the live HTTP endpoint
  - Stops the container via `docker compose -f ... down` in a `finally` block so cleanup always happens
  - Single prediction: `POST /predict` with JSON body; batch: loop over rows (HTTP/1.1, no parallelism)

### Trigger Placement

- **D-03: Final step in deploy-model.md orchestrator**
  - `deploy-model.md` is updated to add a final step: after the target-specific skill (deploy-cli / deploy-web / deploy-wasm) completes, generate and execute `deployment_report.ipynb`
  - This guarantees the report runs for every target from a single maintenance point
  - The step reads `deployment_metadata.json` to know which target was deployed and routes benchmark logic accordingly

### Claude Narrative

- **D-04: Claude Code workflow injection (matches established DoML pattern)**
  - Claude writes the narrative in the `deploy-model.md` Step 12 workflow step, then injects it via an nbformat Python script — identical to the pattern used in all existing DoML workflows (BU, EDA, forecasting, anomaly detection)
  - No `anthropic` SDK call inside the notebook; no `anthropic` package required
  - Note: the original CONTEXT.md described "same anthropic SDK call used in other report phases" — this was inaccurate. The established pattern is workflow injection, not in-notebook SDK calls

### Target-Specific Routing

- **D-05: Notebook detects target from deployment_metadata.json**
  - At runtime, the notebook reads `deployment_metadata.json` to determine `target` (`cli`, `web`, or `wasm`)
  - Benchmark cells are conditional Python if/elif blocks: CLI cells run subprocess against the binary; web cells call HTTP to a pre-started service; WASM cells use Python onnxruntime
  - Web service container is started/stopped by the workflow (deploy-model.md Step 12), NOT inside the notebook — the notebook receives the endpoint URL and assumes it's running
  - A single `deployment_report.ipynb` template handles all three targets — no separate notebooks per target

### Data Source for Parity Test

- **D-06: Preprocessed test data from data/processed/**
  - Parity test reads `data/processed/preprocessed_*.csv` — the same schema the Pipeline expects
  - Uses the last 100 rows (or all rows if fewer than 100) as the test set
  - 100 rows is enough to surface prediction drift while keeping HTTP benchmark latency manageable
  - `feature_schema` from `deployment_metadata.json` determines column order/types passed to the endpoint

### Claude's Discretion

- Exact matplotlib/seaborn chart style for latency distribution plots (box plot or violin — either is fine)
- Whether batch latency is measured as wall-clock per-call or total time / N
- Whether `psutil` or `tracemalloc` is used for memory measurement (psutil process RSS delta is simpler and sufficient)
- Exact nbconvert CLI flags for code-hidden HTML conversion
- Whether the notebook uses `papermill`-style parameters or reads `deployment_metadata.json` directly at startup (direct read is fine)
- Port number handling if 8080 is already in use (fail with a clear error is acceptable)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §Performance Report — PERF-01 through PERF-07 define all acceptance criteria

### Phase 13 — Orchestrator and metadata
- `.planning/phases/13-deployment-workflow-skeleton/13-CONTEXT.md` — `deployment_metadata.json` fields and `deploy-model.md` structure; **Phase 17 adds a final step to this workflow**
- `.claude/doml/workflows/deploy-model.md` — must be updated to add report generation step after target skill completes

### Phase 14 — CLI target invocation
- `.planning/phases/14-cli-binary-target/14-CONTEXT.md` — D-02 (preprocessed schema input), D-04 (output JSON format); benchmark calls `dist/predict/predict` subprocess with JSON input

### Phase 15 — Web service invocation
- `.planning/phases/15-web-service-target/15-CONTEXT.md` — D-03 (Docker compose file, port 8080), D-02 (Pydantic model); benchmark posts to `POST /predict`
- `.claude/doml/workflows/deploy-web.md` — Docker compose setup and container startup pattern

### Phase 16 — ONNX model location
- `.planning/phases/16-onnx-wasm-target/16-CONTEXT.md` — D-02 (model.onnx written to `src/<modelname>/vN/model.onnx`), D-03 (categorical ordinal encoding for ONNX input)
- `.claude/doml/workflows/deploy-wasm.md` — ONNX conversion step and category_map structure

### Existing report pattern (Claude API narrative)
- `.claude/doml/templates/notebooks/business_understanding.ipynb` — reference for Claude API call pattern and nbconvert HTML generation in existing DoML notebooks

</canonical_refs>
