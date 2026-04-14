# Requirements: DoML — Do Machine Learning

**Defined:** 2026-04-04
**Updated:** 2026-04-14 — Milestone v1.4 Deployment
**Core Value:** A data scientist can drop a dataset into `/data`, answer a few questions, and get a fully reproducible, peer-reviewable ML analysis with stakeholder-ready summaries — without re-inventing the process each time.

---

## Milestone v1.4 Requirements — Deployment

### Deployment Workflow (DEPLOY)
- [ ] **DEPLOY-01**: User can run `doml-deploy-model` to deploy the #1 leaderboard model to a chosen target without specifying a model file
- [ ] **DEPLOY-02**: User can override the default model selection with a specific model file or leaderboard rank
- [ ] **DEPLOY-03**: User can choose a deployment target (CLI binary, web service, ONNX/WASM) at run time
- [ ] **DEPLOY-04**: Deployed artifacts are written to `src/<modelname>/v1/` with a `deployment_metadata.json` recording model file, target, build date, and feature schema
- [ ] **DEPLOY-05**: `model_metadata.json` is extended with a `model_name` field (derived from estimator class name if not present)

### CLI Target (CLI)
- [ ] **CLI-01**: User can run a self-contained binary (`dist/predict`) on a Linux machine with no Python installed
- [ ] **CLI-02**: Binary accepts a single prediction via `--input '{"feature": value}'` (JSON string) and prints result to stdout
- [ ] **CLI-03**: Binary accepts batch predictions via `--input data.csv` or `--input data.json` (file path)
- [ ] **CLI-04**: Binary accepts `--output <path>` to write batch results to a file instead of stdout
- [ ] **CLI-05**: `--help` displays the feature schema (names, types, example values) from `model_metadata.json`
- [ ] **CLI-06**: Binary exits with code 0 on success, 1 on input validation error, 2 on model error

### Web Service Target (WEB)
- [ ] **WEB-01**: User can start the inference service with `docker compose -f docker-compose.serve.yml up`
- [ ] **WEB-02**: `POST /predict` accepts a JSON body of feature values and returns a prediction response
- [ ] **WEB-03**: `GET /health` returns service status, model name, and version
- [ ] **WEB-04**: `GET /schema` returns the feature schema (names, types, example values)
- [ ] **WEB-05**: FastAPI auto-generates OpenAPI docs at `GET /docs`
- [ ] **WEB-06**: `GET /` serves an auto-generated HTML prediction form with one input per feature, typed from the feature schema (numeric inputs, dropdowns for categoricals derived from processed dataset)
- [ ] **WEB-07**: Submitting the prediction form returns the prediction result inline without a page reload

### ONNX/WASM Target (WASM)
- [ ] **WASM-01**: User receives a self-contained `index.html` that runs inference entirely in the browser with no server
- [ ] **WASM-02**: The page auto-generates a prediction form from the feature schema embedded in the HTML
- [ ] **WASM-03**: Submitting the form runs ONNX inference via onnxruntime-web and displays the result inline
- [ ] **WASM-04**: Workflow blocks WASM target for forecasting problem type and DBSCAN clustering with a clear message
- [ ] **WASM-05**: Workflow blocks WASM target if the converted `model.onnx` exceeds 20 MB, with a message suggesting the web service target

### Performance Report (PERF)
- [ ] **PERF-01**: `notebooks/deployment_report.ipynb` is generated after every deployment
- [ ] **PERF-02**: Report benchmarks single-prediction latency (mean ± std over 1000 runs)
- [ ] **PERF-03**: Report benchmarks batch prediction latency at 10, 100, 1000, and 10 000 rows
- [ ] **PERF-04**: Report includes a parity test: test set fed through the deployed endpoint (or binary) is asserted to match in-memory model output within tolerance (regression: atol=1e-4; classification: exact labels; clustering: exact cluster IDs)
- [ ] **PERF-05**: Report measures model load memory footprint and per-prediction memory delta
- [ ] **PERF-06**: Report projects throughput (requests/sec) from latency measurements
- [ ] **PERF-07**: `reports/deployment_report.html` is generated with code hidden and a Claude narrative summarising benchmark results

### Iteration (ITER)
- [ ] **ITER-01**: User can run `doml-iterate-deployment` to create a new deployment version without re-running `doml-deploy-model` from scratch
- [ ] **ITER-02**: Same model, new deployment version → artifacts written to `src/<modelname>/v<N+1>/` (version scanned from existing dirs, not assumed)
- [ ] **ITER-03**: Different/better model → artifacts written to `src/<newmodelname>/v1/` as a new model folder in `src/`
- [ ] **ITER-04**: `doml-iterate-deployment` accepts a `--guidance` parameter to shape the iteration direction
- [ ] **ITER-05**: User can run `doml-iterate-deployment` even when no new model is available (to tune inference performance, change deployment target, or adjust configuration)

---

## Future Requirements (deferred from v1.4)

- Streaming predictions (SSE/WebSocket)
- Multi-model A/B serving
- Cloud deployment configs (Kubernetes, AWS ECS, GCP Cloud Run)
- GPU inference support
- Windows/macOS CLI binaries (Linux only in v1.4, built in Docker)
- Progressive Web App manifest for ONNX page
- SHAP explanation in web UI
- Async batch endpoint (`POST /predict/batch` with job polling)

---

## Out of Scope

- **Dimensionality reduction deployment** — PCA/UMAP transforms not useful as standalone inference endpoints
- **ONNX/WASM for forecasting** — Prophet/ARIMA have no ONNX export path
- **ONNX/WASM for DBSCAN clustering** — DBSCAN has no ONNX export; KMeans only
- **AutoML re-training on prediction requests** — deployment is inference-only
- **Model registry integration** (MLflow, W&B) — DoML uses own model_metadata.json
- **API key auth / rate limiting** — infrastructure concern, out of scope for v1.4

---

## Traceability

| REQ-ID | Phase |
|--------|-------|
| DEPLOY-01 – DEPLOY-05 | Phase 13 |
| CLI-01 – CLI-06 | Phase 14 |
| WEB-01 – WEB-07 | Phase 15 |
| WASM-01 – WASM-05 | Phase 16 |
| PERF-01 – PERF-07 | Phase 17 |
| ITER-01 – ITER-05 | Phase 18 |
