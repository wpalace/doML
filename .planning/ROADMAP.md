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
- [ ] **Phase 3: Kickoff Interview** — Guided business context interview with problem type detection and data validation
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
- [ ] 03-01-PLAN.md — Interview workflow: AskUserQuestion sequence, ML type inference, domain research offer, atomic PROJECT.md + config.json write
- [ ] 03-02-PLAN.md — Data scan module: doml/data_scan.py DuckDB introspection for CSV/Parquet/Excel, pytest infrastructure

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

## 📋 Milestone 2 — Modelling + Forecasting (Planned)

**Milestone Goal:** Extend DoML with Data Modelling (all 5 traditional ML problem types with leaderboard, SHAP, and hyperparameter tuning) and optional Forecasting phase with prediction intervals.

### Phase 6: Data Modelling — Regression & Classification

**Goal**: Implement modelling notebooks for supervised learning problems (regression and classification) with scikit-learn Pipelines, XGBoost/LightGBM, leaderboard, SHAP explainability, and Optuna tuning.

**Depends on**: Phase 5

**Requirements**: MOD-01, MOD-02, MOD-06, MOD-07, MOD-08, MOD-09, MOD-10

**Success Criteria** (what must be TRUE):
1. Modelling notebook generated for regression problems with DummyRegressor baseline always in leaderboard
2. Modelling notebook generated for classification problems with DummyClassifier baseline and stratified CV
3. Leaderboard (`models/leaderboard.csv`) shows only held-out validation metrics — never training scores
4. SHAP values computed and visualized for every model in leaderboard
5. Optuna tunes hyperparameters for top leaderboard model
6. Best model serialized to `/models/best_model.pkl` with `model_metadata.json`

**Plans**: TBD

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

**Plans**: TBD

---

### Phase 8: Time Series Modelling & Forecasting

**Goal**: Implement the time series modelling and optional Forecasting phase with ARIMA, Prophet, temporal cross-validation, and prediction intervals — only activated when time-factor confirmed in Business Understanding.

**Depends on**: Phase 5 (requires stationarity analysis from EDA)

**Requirements**: MOD-04, FORE-01, FORE-02, FORE-03, FORE-04

**Success Criteria** (what must be TRUE):
1. Time series modelling notebook uses only `TimeSeriesSplit` — no random splits
2. ARIMA and Prophet models compared in leaderboard with temporal CV metrics
3. Forecasting notebook generates point forecast + 80% and 95% prediction intervals
4. Forecasting phase only activates when time-factor was confirmed in Business Understanding

**Plans**: TBD

---

### Phase 9: Modelling Reports & Leaderboard UI

**Goal**: Extend HTML report generation to cover modelling and forecasting phases — leaderboard display, SHAP visualizations, forecast charts with prediction intervals, and executive summaries.

**Depends on**: Phases 6–8

**Requirements**: MOD-06, OUT-01, OUT-02, OUT-03

**Success Criteria** (what must be TRUE):
1. `reports/model_report.html` generated with leaderboard, SHAP plots, code hidden
2. `reports/forecast_report.html` generated with forecast chart + prediction intervals
3. HTML reports include caveats: model limitations, out-of-sample risks, correlation ≠ causation

**Plans**: TBD

---

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Infrastructure & Docker | M1 | 3/3 | Complete | 2026-04-05 |
| 2. Framework Skeleton | M1 | 0/3 | Not started | — |
| 3. Kickoff Interview | M1 | 0/2 | Not started | — |
| 4. Business Understanding Phase | M1 | 0/3 | Not started | — |
| 5. Data Understanding Phase | M1 | 0/4 | Not started | — |
| 6. Modelling — Regression & Classification | M2 | TBD | Not started | — |
| 7. Modelling — Clustering & Dim. Reduction | M2 | TBD | Not started | — |
| 8. Time Series Modelling & Forecasting | M2 | TBD | Not started | — |
| 9. Modelling Reports & Leaderboard UI | M2 | TBD | Not started | — |
