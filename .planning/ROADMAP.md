# Roadmap: DoML — Do Machine Learning

## Milestones

- 🚧 **Milestone 1 — Foundation + EDA** — Phases 1–5 (in progress)
- 📋 **Milestone 2 — Modelling + Forecasting** — Phases 6–9 (planned)

## Overview

Milestone 1 delivers a fully installable DoML framework: a Docker-based Jupyter environment, planning artifact templates, four framework commands, a guided kickoff interview, and complete Business Understanding and Data Understanding phase workflows producing reproducible notebooks and HTML stakeholder reports. Milestone 2 extends the framework with Data Modelling (all traditional ML problem types) and optional Forecasting for time series.

---

## 🚧 Milestone 1 — Foundation + EDA (In Progress)

**Milestone Goal:** A data scientist can run `/doml-new-project`, answer guided questions, start Docker, and produce a reproducible Business Understanding notebook and a Data Understanding EDA notebook with stakeholder HTML reports — on any CSV, Parquet, or Excel dataset.

## Phases

- [ ] **Phase 1: Infrastructure & Docker** — Scaffold project structure, generate Docker environment, enforce reproducibility
- [ ] **Phase 2: Framework Skeleton** — Install DoML skills/workflows/agents; planning artifact templates; four core commands
- [x] **Phase 3: Kickoff Interview** — Guided business context interview with problem type detection and data validation (completed 2026-04-06)
- [ ] **Phase 4: Business Understanding Phase** — Notebook template + stakeholder HTML report
- [ ] **Phase 5: Data Understanding Phase** — EDA notebook with DuckDB, statistical tests, tidy validation + stakeholder HTML report

---

## Phase Details

### Phase 1: Infrastructure & Docker

**Goal**: Generate a fully reproducible Docker environment that any team member can start with `docker-compose up`, producing a JupyterLab instance at `localhost:8888` with Python, R, DuckDB, and all required analysis libraries pre-installed.

**Depends on**: Nothing (first phase)

**Requirements**: INFR-01, INFR-02, INFR-03, INFR-04, INFR-05, INFR-06, REPR-01, REPR-02, REPR-03, REPR-04

**Success Criteria** (what must be TRUE):
1. `docker-compose up` starts JupyterLab at `localhost:8888` with no manual setup
2. DuckDB is importable in both Python (`import duckdb`) and R (`library(duckdb)`) inside the container
3. `/data/raw/`, `/data/processed/`, `/data/external/`, `/notebooks/`, `/reports/`, `/models/` directories exist
4. `CLAUDE.md` is generated with DoML-specific instructions for Claude Code
5. `nbstripout` pre-commit hook is active — notebook outputs stripped before git commit
6. `requirements.txt` pins all package versions; no `latest` or unpinned dependencies

**Plans**: 3 plans

Plans:
- [x] 01-01: Docker environment (`docker-compose.yml`, `Dockerfile`, `requirements.txt` with pinned DuckDB + ML stack)
- [x] 01-02: Project directory scaffold and data immutability enforcement
- [ ] 01-03: Reproducibility setup (`nbstripout`, pre-commit, `CLAUDE.md` template)

---

### Phase 2: Framework Skeleton

**Goal**: Install the DoML skill/workflow/agent architecture into Claude Code, providing four working framework commands and planning artifact templates that DoML analysis projects use to track state across sessions.

**Depends on**: Phase 1

**Requirements**: PLAN-01, PLAN-02, PLAN-03, PLAN-04, CMD-01, CMD-02, CMD-03, CMD-04

**Success Criteria** (what must be TRUE):
1. `/doml-new-project` command is recognized and invokable in Claude Code
2. `/doml-plan-phase`, `/doml-execute-phase`, `/doml-progress` commands are recognized and invokable
3. `PROJECT.md`, `ROADMAP.md`, `STATE.md`, `config.json` templates exist and are generated at project init
4. Framework directory structure mirrors GSD pattern (`skills/`, `workflows/`, `agents/`, `templates/`, `references/`)
5. `STATE.md` persists current phase and key decisions across Claude Code sessions

**Plans**: 3 plans

Plans:
- [x] 02-01: Skills and command entry points (`/doml-new-project`, `/doml-plan-phase`, `/doml-execute-phase`, `/doml-progress`)
- [x] 02-02: Workflow orchestration files (new-project, plan-phase, execute-phase, progress workflows)
- [x] 02-03: Planning artifact templates (PROJECT.md, ROADMAP.md, STATE.md, config.json for analysis projects)

---

### Phase 3: Kickoff Interview

**Goal**: Implement the guided business context interview that extracts problem framing, validates the `/data/` folder, determines ML problem type, confirms whether time is a factor, and sets language preference — producing a written decision framing before any data is touched.

**Depends on**: Phase 2

**Requirements**: INTV-01, INTV-02, INTV-03, INTV-04, INTV-05

**Success Criteria** (what must be TRUE):
1. Interview asks about business question, dataset context, stakeholder, and expected outcome
2. Interview always explicitly asks whether time is a factor in the data
3. Interview validates `/data/` folder exists and detects file formats (CSV, Parquet, Excel) before proceeding
4. Interview produces a written decision framing saved to planning artifacts
5. Interview asks for language preference (Python default, R opt-in) and saves to `config.json`
6. Running `/doml-new-project` on an empty `/data/` folder produces a clear error, not a silent failure

**Plans**: 2 plans

Plans:
- [x] 03-01-PLAN.md — Interview workflow: AskUserQuestion sequence, ML type inference, domain research offer, atomic PROJECT.md + config.json write
- [x] 03-02-PLAN.md — Data scan module: doml/data_scan.py DuckDB introspection for CSV/Parquet/Excel, pytest infrastructure

---

### Phase 4: Business Understanding Phase

**Goal**: Implement the Business Understanding analysis phase — generating a Jupyter notebook documenting context, data inventory, problem type, and dataset provenance, plus a stakeholder HTML report — triggered by `/doml-execute-phase 1`.

**Depends on**: Phase 3

**Requirements**: BU-01, BU-02, BU-03, BU-04, BU-05, OUT-01, OUT-02, OUT-03

**Success Criteria** (what must be TRUE):
1. `notebooks/01_business_understanding.ipynb` is generated with narrative cells, data inventory, problem type, and provenance
2. Data inventory section uses DuckDB to query `/data/raw/` files (shape, dtypes, sample rows, null counts)
3. Notebook documents ML problem type determined in interview
4. `reports/business_summary.html` is generated with code cells hidden (`nbconvert --no-input`)
5. HTML report includes a Claude-generated executive narrative interpreting the business context
6. HTML report includes a caveats section (assumptions, limitations, correlation ≠ causation disclaimer)

**Plans**: 3 plans

Plans:
- [ ] 04-01: Business Understanding notebook template (narrative structure, markdown cells, DuckDB inventory section)
- [ ] 04-02: Notebook execution workflow (papermill parameterization, output to `/notebooks/`)
- [ ] 04-03: HTML report generation (nbconvert pipeline + Jinja2 executive summary + caveats section)

---

### Phase 5: Data Understanding Phase

**Goal**: Implement the Data Understanding analysis phase — generating a comprehensive EDA Jupyter notebook using DuckDB for large-file profiling, distribution/correlation/missing value analysis, tidy data validation, and optional time series stationarity tests, plus a stakeholder HTML report with Claude-generated narrative.

**Depends on**: Phase 4

**Requirements**: EDA-01, EDA-02, EDA-03, EDA-04, EDA-05, EDA-06, EDA-07, EDA-08, EDA-09, EDA-10, OUT-01, OUT-02, OUT-03

**Success Criteria** (what must be TRUE):
1. `notebooks/02_data_understanding.ipynb` is generated with all required EDA sections
2. DuckDB queries profile `/data/raw/` files without loading entire dataset into pandas (zero-copy scan)
3. Distribution analysis includes histograms, Q-Q plots, Shapiro-Wilk test, skewness, kurtosis for all numeric features
4. Correlation analysis uses appropriate method per feature type (Pearson / Cramér's V / point-biserial)
5. Missing value analysis includes heatmap, percentage by feature, and MCAR/MAR/MNAR assessment
6. Time series problems include ADF + KPSS stationarity tests and decomposition plot
7. Tidy data validation runs before feature engineering; violations are flagged (not silently fixed)
8. Cleaned dataset is written to `/data/processed/` at phase completion
9. `reports/eda_report.html` is generated with code hidden and Claude narrative interpreting key findings

**Plans**: 4 plans

Plans:
- [ ] 05-01: DuckDB-based data profiling section (schema, nulls, distributions, unique counts — SQL-first)
- [ ] 05-02: Statistical analysis sections (distributions, correlations, missing values — problem-type-aware)
- [ ] 05-03: Time series EDA additions (stationarity tests, decomposition — conditional on time-factor flag)
- [ ] 05-04: Tidy data validation, processed dataset output, and EDA HTML report generation

---

## ✅ Milestone 2 — Modelling (Complete)

**Milestone Goal:** Extend DoML with Data Modelling (all traditional ML problem types with leaderboard, SHAP, and hyperparameter tuning) — supervised (regression/classification) and unsupervised (clustering/dimensionality reduction).

### Phase 6: Data Preprocessing & Modelling — Regression & Classification

**Goal**: Implement a preprocessing notebook (imputation, encoding, scaling, feature engineering/selection) and modelling notebooks for supervised learning (regression and classification) with scikit-learn Pipelines, XGBoost/LightGBM, CV leaderboard, SHAP explainability, and Optuna tuning.

**Depends on**: Phase 5

**Requirements**: PREP-01, PREP-02, MOD-01, MOD-02, MOD-06, MOD-07, MOD-08, MOD-09, MOD-10

**Success Criteria** (what must be TRUE):
1. Preprocessing notebook template covers imputation, encoding, scaling, feature engineering/selection (PREP-01)
2. Preprocessed dataset written to `data/processed/preprocessed_{filename}` (PREP-02)
3. Modelling notebook generated for regression problems with DummyRegressor baseline always in leaderboard
4. Modelling notebook generated for classification problems with DummyClassifier baseline and stratified CV
5. Leaderboard (`models/leaderboard.csv`) shows only held-out CV metrics — never training scores (MOD-06)
6. SHAP values computed and visualized for every model in leaderboard (MOD-08)
7. Optuna tunes top-3 leaderboard models, 30 trials each (MOD-09)
8. Best model serialized to `/models/best_model.pkl` with `model_metadata.json` (MOD-10)

**Plans**: 5 plans

Plans:
- [ ] 06-01: Preprocessing notebook template (`preprocessing.ipynb` — imputation, encoding, scaling, feature engineering)
- [ ] 06-02: Regression modelling template (`modelling_regression.ipynb` — CV leaderboard, SHAP, Optuna)
- [ ] 06-03: Classification modelling template (`modelling_classification.ipynb` — stratified CV, AUC leaderboard, SHAP, Optuna)
- [ ] 06-04: execute-phase.md Phase 3 executor (preprocessing + problem-type routing + HTML model report)
- [ ] 06-05: `/doml-iterate-model` command stub (new skill + iterate-model.md workflow stub)

---

### Phase 7: Data Modelling — Clustering & Dimensionality Reduction

**Goal**: Implement modelling notebooks for unsupervised problems (clustering and dimensionality reduction) with appropriate internal evaluation metrics and UMAP/t-SNE visualization.

**Depends on**: Phase 5

**Requirements**: MOD-03, MOD-05

**Success Criteria** (what must be TRUE):
1. Clustering notebook generated with KMeans (elbow + silhouette), DBSCAN, hierarchical options
2. Dimensionality reduction notebook generated with PCA (variance curve), UMAP, t-SNE
3. Internal metrics (silhouette, Davies-Bouldin, Calinski-Harabasz) used — no accuracy metric for clustering
4. UMAP 2D visualization of clusters included

**Plans**: 4 plans

Plans:
- [ ] 07-01-PLAN.md — Clustering notebook template (KMeans, DBSCAN, hierarchical, ANOVA feature importance, UMAP 2D)
- [ ] 07-02-PLAN.md — Dimensionality reduction notebook template (PCA scree/biplot/loadings, UMAP 2D/3D/sensitivity, t-SNE perplexity sweep)
- [ ] 07-03-PLAN.md — execute-phase.md Phase 7 executor extension (Steps 3n-3t, routing table update)
- [ ] 07-04-PLAN.md — /doml-iterate-unsupervised command (SKILL.md + full 10-step iterate-unsupervised.md workflow)

---

---

## 📋 Milestone 3 — Refinement (In Progress)

**Milestone Goal:** Replace the generic `doml-execute-phase N` pattern with dedicated CRISP-DM-named commands, add data acquisition and anomaly detection capabilities, unify the iterate workflow, and add time series forecasting.

### Phase 8: Phase-Named Commands

**Goal**: Replace `doml-execute-phase` with dedicated CRISP-DM-named skills — `doml-business-understanding`, `doml-data-understanding`, and `doml-modelling` — each self-contained with its own workflow, notebook, and HTML report. Retire `doml-execute-phase` and `doml-plan-phase` as user-facing commands.

**Depends on**: Phase 7

**Requirements**: CMD-10, CMD-11, CMD-12

**Success Criteria** (what must be TRUE):
1. `doml-business-understanding` skill exists and runs the full BU phase (notebook + HTML report) without requiring a phase number
2. `doml-data-understanding` skill exists and runs the full EDA phase (notebook + HTML report) without requiring a phase number
3. `doml-modelling` skill exists and routes to the correct modelling notebook based on `config.json` `problem_type` (regression, classification, clustering, dim_reduction), including preprocessing
4. `doml-execute-phase` and `doml-plan-phase` removed from user-facing skills (or clearly marked internal)
5. `CLAUDE.md` and `doml-progress` updated to reference new command names

**Plans**: TBD

---

### Phase 9: `doml-get-data`

**Goal**: Implement a data acquisition skill that downloads datasets from Kaggle or direct URLs into `data/raw/`, and integrates with `doml-new-project` as a fallback when no data is found.

**Depends on**: Phase 8

**Requirements**: CMD-14, DATA-01, DATA-02, DATA-03, DATA-04

**Success Criteria** (what must be TRUE):
1. `doml-get-data kaggle owner/dataset-name` downloads dataset files to `data/raw/` using the Kaggle API
2. `doml-get-data url https://...` downloads a CSV/Parquet/Excel file to `data/raw/`
3. `doml-new-project` detects empty `data/raw/` and automatically invokes `doml-get-data` before continuing the interview
4. Each download appends a log entry to `data/raw/README.md` with source and timestamp

**Plans**: 2 plans

Plans:
- [x] 09-01-PLAN.md — SKILL.md entry point, get-data.md acquisition workflow (Steps 1–8), docker-compose.yml template update, requirements.in, .gitignore
- [x] 09-02-PLAN.md — new-project.md Step 3 modification: inline AskUserQuestion choice when data/raw/ is empty

---

### Phase 10: `doml-anomaly-detection`

**Goal**: Implement an optional anomaly detection phase that runs after `doml-data-understanding`, producing a dedicated notebook and HTML report covering Isolation Forest, LOF, and DBSCAN-based flagging.

**Depends on**: Phase 8

**Requirements**: CMD-13, ANOM-01, ANOM-02, ANOM-03, ANOM-04

**Success Criteria** (what must be TRUE):
1. `doml-anomaly-detection` skill exists and generates `notebooks/anomaly_detection.ipynb`
2. Notebook covers Isolation Forest, Local Outlier Factor, and DBSCAN-based anomaly detection
3. Notebook follows REPR-01, REPR-02, and tidy validation before analysis
4. `reports/anomaly_report.html` generated with code hidden and Claude narrative
5. Anomaly flags written to `data/processed/anomaly_flags_{filename}.csv`

**Plans**: 2 plans

Plans:
- [x] 10-01-PLAN.md — SKILL.md entry point + anomaly-detection.md workflow (Steps 1–11, --file / --guidance, Docker execution, HTML report, flag CSV verification)
- [x] 10-02-PLAN.md — Static nbformat v4 notebook template (anomaly_detection.ipynb — Setup → Data Load → Tidy Validation → Isolation Forest → LOF → DBSCAN → Consensus → Save Flags → Caveats)

---

### Phase 11: Unified `doml-iterate`

**Goal**: Merge `doml-iterate-model` and `doml-iterate-unsupervised` into a single `doml-iterate` command that auto-detects problem type, always produces new versioned notebooks and reports, and implements the full supervised iteration path (currently a stub).

**Depends on**: Phase 8

**Requirements**: CMD-15, ITER-01, ITER-02, ITER-03, ITER-04, ITER-05

**Success Criteria** (what must be TRUE):
1. `doml-iterate` reads `config.json` `problem_type` and routes correctly for all problem types
2. Every iteration produces a new versioned notebook — never overwrites a prior version
3. Every iteration produces a new versioned HTML report — never overwrites a prior version
4. Leaderboard appended (not replaced) with new iteration results
5. Supervised iteration path is fully implemented (10-step workflow matching unsupervised)
6. `doml-iterate-model` and `doml-iterate-unsupervised` skills removed

**Plans**: 2 plans

Plans:
- [x] 11-01-PLAN.md — SKILL.md entry point + unified iterate.md workflow (full 10-step supervised implementation, unsupervised path integrated, all four problem types routed, versioned HTML reports)
- [x] 11-02-PLAN.md — Retire old commands: delete doml-iterate-model + doml-iterate-unsupervised skill dirs and workflow files; update progress.md + CLAUDE.md

---

### Phase 12: `doml-forecasting`

**Goal**: Implement time series modelling and forecasting as a dedicated skill — ARIMA, Prophet, temporal CV, and prediction intervals — only activated when `time_factor=true` in `config.json`.

**Depends on**: Phase 8

**Requirements**: CMD-16, MOD-04, FORE-01, FORE-02, FORE-03, FORE-04 (deferred to Milestone 4)

**Note:** FORE-04 (forecast actuals tracking — compare predictions to actuals as new data arrives)
is deferred to Milestone 4. It requires multi-session state (saving forecast CSVs and a --compare
command to diff against actuals). The forecasting notebook includes a placeholder section documenting
the manual comparison procedure for analysts who need it before Milestone 4.

**Success Criteria** (what must be TRUE):
1. `doml-forecasting` skill exists and generates `notebooks/forecasting.ipynb`
2. Notebook uses only `TimeSeriesSplit` — no random splits
3. ARIMA and Prophet compared in leaderboard with temporal CV metrics
4. Forecast output includes point prediction + 80% and 95% prediction intervals
5. Skill exits early with a clear message if `time_factor=false` in `config.json`

**Plans**: 2 plans

Plans:
- [x] 12-01-PLAN.md — SKILL.md + forecasting.md workflow + pmdarima dependency
- [x] 12-02-PLAN.md — Static forecasting.ipynb notebook template (6-model leaderboard + prediction intervals)

---

## 🚧 Milestone 4 — Deployment (In Progress)

**Milestone Goal:** Add `doml-deploy-model` and `doml-iterate-deployment` to package the best leaderboard model into three production-ready artifact types — a portable CLI binary, a containerised FastAPI web service, and a browser-side ONNX/WASM page — each accompanied by a performance benchmarking report.

---

### Phase 13: Deployment Workflow Skeleton

**Goal**: Implement the `doml-deploy-model` SKILL.md entry point and `deploy-model.md` workflow orchestration: model resolution (leaderboard #1 or override), target selection, versioned `src/<modelname>/v1/` directory creation, `deployment_metadata.json`, and `model_name` extension to `model_metadata.json`.

**Depends on**: Phase 12

**Requirements**: DEPLOY-01, DEPLOY-02, DEPLOY-03, DEPLOY-04, DEPLOY-05

**Success Criteria**:
1. `doml-deploy-model` skill is recognised and invokable in Claude Code
2. Running `doml-deploy-model` without arguments selects the #1 leaderboard model and prompts for target
3. Running `doml-deploy-model --model <file>` uses the specified model instead
4. `src/<modelname>/v1/` directory is created with `deployment_metadata.json` containing model file, target, build date, and feature schema
5. `model_metadata.json` contains a `model_name` field after the workflow runs (derived from estimator class name if absent)

**Plans**: 2 plans

Plans:
- [x] 13-01-PLAN.md — SKILL.md entry point + deploy-model.md workflow (11 steps: model resolution, target selection, versioned directory creation, deployment_metadata.json)
- [x] 13-02-PLAN.md — Update progress.md to surface /doml-deploy-model as next action after modelling

---

### Phase 14: CLI Binary Target

**Goal**: Implement the CLI deployment target — generating `predict.py` with argparse, a PyInstaller spec file, and running the PyInstaller build inside the existing Docker container to produce a self-contained `dist/predict` Linux binary.

**Depends on**: Phase 13

**Requirements**: CLI-01, CLI-02, CLI-03, CLI-04, CLI-05, CLI-06

**Success Criteria**:
1. `src/<modelname>/v1/predict.py` is generated with JSON string input, JSON/CSV file input, and `--output` flag support
2. `src/<modelname>/v1/predict.spec` PyInstaller spec includes `--collect-all sklearn`, `--collect-all joblib`, and `--onedir`
3. PyInstaller build runs inside Docker and produces `src/<modelname>/v1/dist/predict`
4. Binary runs on a Linux machine with no Python installed and returns correct predictions
5. `--help` output lists all feature names, types, and example values
6. Binary exits 0 on success, 1 on input error, 2 on model error
7. `deployment_metadata.json` records `"platform": "linux-x86_64"`

**Plans**: TBD

---

### Phase 15: Web Service Target

**Goal**: Implement the FastAPI web service deployment target — generating `app.py` (with dynamic Pydantic model, `/predict`, `/health`, `/schema` endpoints), a Jinja2 prediction form template, `Dockerfile.serve`, and `docker-compose.serve.yml`.

**Depends on**: Phase 13

**Requirements**: WEB-01, WEB-02, WEB-03, WEB-04, WEB-05, WEB-06, WEB-07

**Success Criteria**:
1. `docker compose -f src/<modelname>/v1/docker-compose.serve.yml up` starts the service with no manual setup
2. `POST /predict` with a valid JSON body returns a correctly typed prediction response
3. `GET /health` returns `{"status": "ok", "model": "<name>", "version": "v1"}`
4. `GET /schema` returns feature names, types, and example values
5. `GET /docs` shows FastAPI auto-generated OpenAPI documentation
6. `GET /` renders an HTML form with one input per feature; numeric features use `type="number"`, categoricals use `<select>` populated from the processed dataset
7. Submitting the form returns the prediction result inline via `fetch()` without a page reload

**Plans**: TBD

---

### Phase 16: ONNX/WASM Target

**Goal**: Implement the ONNX/WebAssembly deployment target — converting the full sklearn Pipeline to ONNX via skl2onnx, enforcing the 20 MB size gate, and generating a self-contained `index.html` with the model embedded as base64 and inference running via onnxruntime-web.

**Depends on**: Phase 13

**Requirements**: WASM-01, WASM-02, WASM-03, WASM-04, WASM-05

**Success Criteria**:
1. Full sklearn Pipeline (ColumnTransformer + estimator) is exported as a single ONNX graph (not just the estimator)
2. `index.html` loads and runs inference in a browser with no server — zero network requests after initial page load
3. Prediction form is auto-generated from the feature schema embedded in the HTML
4. Submitting the form runs ONNX inference and displays the result inline
5. Workflow blocks WASM target for `forecasting` problem type and DBSCAN clustering with a clear message
6. Workflow blocks and warns if `model.onnx` exceeds 20 MB, suggesting the web service target

**Plans**: TBD

---

### Phase 17: Performance Report

**Goal**: Implement the `deployment_report.ipynb` notebook template and nbconvert pipeline — covering single/batch latency benchmarks, memory footprint, throughput projection, and a parity test that asserts the deployed endpoint matches in-memory model output.

**Depends on**: Phase 13 (requires deployment target files to exist)

**Requirements**: PERF-01, PERF-02, PERF-03, PERF-04, PERF-05, PERF-06, PERF-07

**Success Criteria**:
1. `notebooks/deployment_report.ipynb` is generated and executed after every `doml-deploy-model` run
2. Report shows single-prediction latency (mean ± std, 1000 runs) for the deployed target
3. Report shows batch latency at 10, 100, 1 000, and 10 000 rows
4. Parity test passes: test set predictions from deployed endpoint match in-memory model within tolerance (regression atol=1e-4; classification exact labels; clustering exact cluster IDs)
5. Report shows model load memory delta and per-prediction memory cost
6. Report shows projected throughput (requests/sec)
7. `reports/deployment_report.html` is generated with code hidden and a Claude narrative summarising results

**Plans**: TBD

---

### Phase 18: `doml-iterate-deployment`

**Goal**: Implement the `doml-iterate-deployment` skill and `iterate-deployment.md` workflow — detecting the current deployment version, routing to same-model version bump or new-model folder, re-running the deployment step and performance report, and supporting `--guidance` for direction without requiring a new model.

**Depends on**: Phases 13–17

**Requirements**: ITER-01, ITER-02, ITER-03, ITER-04, ITER-05

**Success Criteria**:
1. `doml-iterate-deployment` is recognised and invokable in Claude Code
2. Same model → new `src/<modelname>/v<N+1>/` with version scanned from existing directories (not assumed)
3. Different model → new `src/<newmodelname>/v1/` created
4. `--guidance` parameter is accepted and shapes the iteration direction
5. Running without a new model (inference tuning or target change) completes successfully
6. A fresh `deployment_report.ipynb` and `deployment_report.html` are generated for the new version

**Plans**: TBD

---

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Infrastructure & Docker | M1 | 4/4 | Complete | 2026-04-05 |
| 2. Framework Skeleton | M1 | 3/3 | Complete | 2026-04-06 |
| 3. Kickoff Interview | M1 | 2/2 | Complete | 2026-04-06 |
| 4. Business Understanding Phase | M2 | 3/3 | Complete | 2026-04-08 |
| 5. Data Understanding Phase | M2 | 4/4 | Complete | 2026-04-08 |
| 6. Preprocessing & Modelling — Regression & Classification | M2 | 5/5 | Complete | 2026-04-08 |
| 7. Modelling — Clustering & Dim. Reduction | M2 | 4/4 | Complete | 2026-04-07 |
| 8. Phase-Named Commands | M3 | TBD | Not started | — |
| 9. `doml-get-data` | M3 | 2/2 | Complete | 2026-04-11 |
| 10. `doml-anomaly-detection` | M3 | 2/2 | Complete | 2026-04-11 |
| 11. Unified `doml-iterate` | M3 | 2/2 | Complete | 2026-04-12 |
| 12. `doml-forecasting` | M3 | 2/2 | Complete | 2026-04-13 |
| 13. Deployment Workflow Skeleton | M4 | 2/2 | Complete   | 2026-04-14 |
| 14. CLI Binary Target | M4 | — | Not started | — |
| 15. Web Service Target | M4 | — | Not started | — |
| 16. ONNX/WASM Target | M4 | — | Not started | — |
| 17. Performance Report | M4 | — | Not started | — |
| 18. `doml-iterate-deployment` | M4 | — | Not started | — |
