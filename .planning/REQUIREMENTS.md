# Requirements: DoML — Do Machine Learning

**Defined:** 2026-04-04
**Core Value:** A data scientist can drop a dataset into `/data`, answer a few questions, and get a fully reproducible, peer-reviewable ML analysis with stakeholder-ready summaries — without re-inventing the process each time.

## v1 Requirements (Milestone 1)

Milestone 1 delivers the framework foundation plus Business Understanding and Data Understanding phases.

### Framework Infrastructure

- [ ] **INFR-01**: Framework installs into any Claude Code project via skills/workflows/agents directory structure
- [x] **INFR-02**: `docker-compose.yml` and `requirements.txt` generated at project creation using `jupyter/datascience-notebook` as base image
- [x] **INFR-03**: DuckDB installed and available in the Docker environment for both Python (`duckdb` package) and R (`duckdb` R package) — always present regardless of whether EDA uses it directly
- [x] **INFR-04**: Project directory structure scaffolded: `/data/raw/`, `/data/processed/`, `/data/external/`, `/notebooks/`, `/reports/`, `/models/`
- [x] **INFR-05**: Raw data in `/data/raw/` is treated as immutable — framework enforces no in-place modification of raw files
- [ ] **INFR-06**: `CLAUDE.md` generated at project creation with DoML-specific instructions for Claude Code
- [ ] **INFR-07**: Smoke test notebooks execute end-to-end inside the container and produce viewable output cells confirming the Python ML stack, R/tidyverse stack, and DuckDB are operational

### Planning Artifacts

- [ ] **PLAN-01**: `PROJECT.md` template generated for DoML analysis projects (captures business question, problem type, dataset context)
- [ ] **PLAN-02**: `ROADMAP.md` generated for each DoML analysis project (maps phases to analysis pipeline)
- [ ] **PLAN-03**: `STATE.md` maintained across sessions (current phase, decisions, blockers, session continuity)
- [ ] **PLAN-04**: `config.json` captures project preferences (language default, workflow agents enabled/disabled)

### Framework Commands

- [ ] **CMD-01**: `/doml-new-project` — guided project kickoff: interview → Docker generation → scaffold → planning artifacts
- [ ] **CMD-02**: `/doml-plan-phase` — create detailed phase plan with optional research agent and plan checker
- [ ] **CMD-03**: `/doml-execute-phase` — execute a planned phase and produce analysis artifacts
- [ ] **CMD-04**: `/doml-progress` — display current project status, completed phases, and next recommended action

### Project Kickoff Interview

- [x] **INTV-01**: Guided interview extracts: dataset description, business question, stakeholder context, and expected outcome
- [x] **INTV-02**: Interview always asks whether time is a factor in the dataset (determines if forecasting phase applies)
- [ ] **INTV-03**: Interview validates that `/data/` folder is populated and detects file formats (CSV, Parquet, Excel) before proceeding
- [x] **INTV-04**: Interview produces a written decision framing: "We are trying to [decision] using [metric] as a proxy"
- [x] **INTV-05**: Python is the default analysis language; interview allows user to opt into R for the project

### Business Understanding Phase

- [ ] **BU-01**: Business Understanding generates `notebooks/01_business_understanding.ipynb` — narrative cells documenting context, question, and assumptions
- [ ] **BU-02**: Notebook includes a data inventory section: file list, shapes, dtypes, sample rows (using DuckDB queries)
- [ ] **BU-03**: Notebook documents the ML problem type (to be determined — regression, classification, clustering, time series, or dimensionality reduction)
- [ ] **BU-04**: Notebook documents dataset provenance: how data was generated, known biases, collection period
- [ ] **BU-05**: Business Understanding generates `reports/business_summary.html` — stakeholder-facing HTML with executive context (code cells hidden)

### Data Understanding Phase

- [ ] **EDA-01**: Data Understanding generates `notebooks/02_data_understanding.ipynb` — full EDA notebook
- [ ] **EDA-02**: Notebook uses DuckDB for initial data profiling queries on raw files (shape, nulls, distributions, unique counts) — zero-copy, no pandas load required for initial scan
- [ ] **EDA-03**: Notebook includes distribution analysis: histograms, Q-Q plots, Shapiro-Wilk normality test, skewness, kurtosis for all numeric features
- [ ] **EDA-04**: Notebook includes correlation analysis: Pearson for continuous, Cramér's V for categorical, point-biserial for mixed
- [ ] **EDA-05**: Notebook includes missing value analysis: missingness heatmap, percentage by feature, MCAR/MAR/MNAR assessment
- [ ] **EDA-06**: For time series problems (flagged in BU phase): notebook includes stationarity tests (ADF, KPSS) and time series decomposition
- [ ] **EDA-07**: Notebook includes tidy data validation: confirms data conforms to tidy principles before feature engineering
- [ ] **EDA-08**: Cleaned/processed dataset written to `/data/processed/` at end of EDA phase
- [ ] **EDA-09**: Data Understanding generates `reports/eda_report.html` — stakeholder-facing HTML with key findings (code cells hidden)
- [ ] **EDA-10**: HTML EDA report includes a Claude-generated executive summary narrative interpreting findings in business terms

### Reproducibility

- [ ] **REPR-01**: All notebooks set random seeds at the top (`np.random.seed(42)` for Python, `set.seed(42)` for R)
- [x] **REPR-02**: All file paths resolved from project root via environment variable — no hardcoded absolute paths
- [ ] **REPR-03**: `nbstripout` configured via pre-commit hook to strip outputs before git commit
- [x] **REPR-04**: `requirements.txt` pins all Python package versions; `renv.lock` pins R packages if R notebooks used

### Outputs

- [ ] **OUT-01**: Technical Jupyter notebooks produced per phase — runnable, peer-reviewable, all analysis traceable to code cells
- [ ] **OUT-02**: Stakeholder HTML report produced per phase — code cells hidden (`nbconvert --no-input`), narrative-focused
- [ ] **OUT-03**: HTML reports include a caveats section: assumptions, limitations, and explicit statement that correlations are not causation

## v2 Requirements (Milestone 2)

### Data Preprocessing

- **PREP-01**: Preprocessing notebook template covers all four areas: imputation (numeric median/mean/KNN comparison + categorical most_frequent), encoding (OneHotEncoder for ≤10 unique values, OrdinalEncoder for >10), scaling (StandardScaler + RobustScaler comparison with tree-model note), feature engineering & selection (interaction candidates, importance ranking, |r|>0.95 redundancy flagging, VIF for regression)
- **PREP-02**: Preprocessed dataset written to `data/processed/preprocessed_{original_filename}` — used as input to the modelling notebook; never overwrites raw data

### Data Modelling

- **MOD-01**: Modelling notebook generated for regression problems (Linear, Ridge, Lasso, RandomForest, XGBoost)
- **MOD-02**: Modelling notebook generated for classification problems (Logistic, RF, XGBoost — binary and multi-class)
- **MOD-03**: Modelling notebook generated for clustering problems (KMeans, DBSCAN, hierarchical)
- **MOD-04**: Modelling notebook generated for time series problems (ARIMA, Prophet, ETS)
- **MOD-05**: Modelling notebook generated for dimensionality reduction (PCA, UMAP, t-SNE)
- **MOD-06**: Model leaderboard generated (`models/leaderboard.csv`) — shows only held-out validation metrics
- **MOD-07**: Baseline model always included in leaderboard (DummyClassifier/DummyRegressor or mean prediction)
- **MOD-08**: SHAP explainability output included for every model in leaderboard
- **MOD-09**: Optuna hyperparameter tuning for top-performing leaderboard models
- **MOD-10**: Best model serialized to `/models/best_model.pkl` with metadata JSON

### Forecasting

- **FORE-01**: Forecasting notebook generated (time series problems only)
- **FORE-02**: Forecasts include point prediction + 80% and 95% prediction intervals
- **FORE-03**: Temporal cross-validation enforced (`TimeSeriesSplit` — no random splits)
- **FORE-04**: Forecast tracking support: compare predictions to actuals as new data arrives

## v3 Requirements (Milestone 3 — Refinement)

### Phase-Named Commands

- **CMD-10**: `doml-business-understanding` — dedicated skill that runs the Business Understanding phase end-to-end (notebook + HTML report); replaces `doml-execute-phase 1`
- **CMD-11**: `doml-data-understanding` — dedicated skill that runs the EDA phase end-to-end (notebook + HTML report); replaces `doml-execute-phase 2`
- **CMD-12**: `doml-modelling` — dedicated skill that runs preprocessing + modelling for all supervised problem types (regression, classification, clustering, dimensionality reduction) in a single command; replaces `doml-execute-phase 3`
- **CMD-13**: `doml-anomaly-detection` — optional dedicated skill that deep-dives into anomalies; runs after `doml-data-understanding`; produces anomaly notebook + HTML report
- **CMD-14**: `doml-get-data` — dedicated skill that fetches datasets from Kaggle or direct URLs into `data/raw/`; runnable standalone or invoked automatically by `doml-new-project` when `/data/raw/` is empty
- **CMD-15**: `doml-iterate` — unified skill that runs a new modelling iteration for any problem type; always produces new versioned notebooks and reports (never overwrites originals)
- **CMD-16**: `doml-forecasting` — dedicated skill for time series modelling and forecasting (ARIMA, Prophet, temporal CV, prediction intervals); only runs when time-factor confirmed in Business Understanding

### Data Acquisition (`doml-get-data`)

- **DATA-01**: Accepts a Kaggle dataset slug (`owner/dataset-name`) and downloads files to `data/raw/` using the Kaggle API
- **DATA-02**: Accepts a direct URL (CSV, Parquet, Excel) and downloads to `data/raw/`
- **DATA-03**: Invoked automatically by `doml-new-project` when `/data/raw/` is empty or contains no supported files — prompts user for source before continuing interview
- **DATA-04**: Logs each download to `data/raw/README.md` with source URL/slug and download timestamp

### Anomaly Detection (`doml-anomaly-detection`)

- **ANOM-01**: Generates `notebooks/anomaly_detection.ipynb` — covers Isolation Forest, Local Outlier Factor, and DBSCAN-based anomaly flagging
- **ANOM-02**: Notebook follows all reproducibility rules (REPR-01, REPR-02) and tidy data validation before analysis
- **ANOM-03**: Generates `reports/anomaly_report.html` — code hidden, Claude-generated narrative interpreting anomaly findings
- **ANOM-04**: Anomaly flags written to `data/processed/anomaly_flags_{filename}.csv` for optional use in downstream modelling

### Unified Iteration (`doml-iterate`)

- **ITER-01**: Reads `config.json` `problem_type` and routes to the correct iteration pipeline (supervised or unsupervised)
- **ITER-02**: Always produces a new versioned notebook (e.g., `modelling_regression_v2.ipynb`, `modelling_clustering_v3.ipynb`) — never overwrites the previous version
- **ITER-03**: Always produces a new versioned HTML report (e.g., `model_report_v2.html`) — never overwrites the previous version
- **ITER-04**: Appends new results to the leaderboard (`models/leaderboard.csv` or `models/unsupervised_leaderboard.csv`) rather than replacing prior rows
- **ITER-05**: Accepts optional analyst-supplied direction via `--direction` flag to guide the iteration strategy

## Out of Scope

| Feature | Reason |
|---------|--------|
| Deep learning (PyTorch/TensorFlow) | Milestone 3 — different infrastructure needs, large Docker image |
| NLP / text data analysis | Future milestone — requires specialized tokenization, embeddings stack |
| Real-time / streaming data | Batch analysis only — streaming adds server complexity out of scope |
| SQL database connectors | DuckDB covers analytical SQL needs; connecting to Postgres/MySQL deferred |
| Fully automated AutoML | Anti-feature — black-box output removes the documented decision trail DoML is designed to create |
| Model deployment | Out of scope for analysis framework — produce artifacts, deployment is user's responsibility |
| Interactive dashboards (Streamlit/Dash) | nbconvert HTML reports are the delivery format; interactive dashboards add server dependency |
| Custom Docker base images | `jupyter/datascience-notebook` is the standard; custom images are user's responsibility |
| Great Expectations data quality gates | Deferred to v1.x — adds complexity; basic validation sufficient for Milestone 1 |
| Forecast actuals tracking | Deferred to Milestone 2 with full forecasting phase |

## Traceability

Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFR-01 | Phase 1 | Pending |
| INFR-02 | Phase 1 | Complete |
| INFR-03 | Phase 1 | Complete |
| INFR-04 | Phase 1 | Complete |
| INFR-05 | Phase 1 | Complete |
| INFR-06 | Phase 1 | Pending |
| INFR-07 | Phase 1 | Pending |
| PLAN-01 | Phase 2 | Pending |
| PLAN-02 | Phase 2 | Pending |
| PLAN-03 | Phase 2 | Pending |
| PLAN-04 | Phase 2 | Pending |
| CMD-01 | Phase 2 | Pending |
| CMD-02 | Phase 2 | Pending |
| CMD-03 | Phase 2 | Pending |
| CMD-04 | Phase 2 | Pending |
| INTV-01 | Phase 3 | Complete |
| INTV-02 | Phase 3 | Complete |
| INTV-03 | Phase 3 | Pending |
| INTV-04 | Phase 3 | Complete |
| INTV-05 | Phase 3 | Complete |
| PREP-01 | Phase 6 | Pending |
| PREP-02 | Phase 6 | Pending |
| BU-01 | Phase 4 | Pending |
| BU-02 | Phase 4 | Pending |
| BU-03 | Phase 4 | Pending |
| BU-04 | Phase 4 | Pending |
| BU-05 | Phase 4 | Pending |
| EDA-01 | Phase 5 | Pending |
| EDA-02 | Phase 5 | Pending |
| EDA-03 | Phase 5 | Pending |
| EDA-04 | Phase 5 | Pending |
| EDA-05 | Phase 5 | Pending |
| EDA-06 | Phase 5 | Pending |
| EDA-07 | Phase 5 | Pending |
| EDA-08 | Phase 5 | Pending |
| EDA-09 | Phase 5 | Pending |
| EDA-10 | Phase 5 | Pending |
| REPR-01 | Phase 1 | Pending |
| REPR-02 | Phase 1 | Complete |
| REPR-03 | Phase 1 | Pending |
| REPR-04 | Phase 1 | Complete |
| OUT-01 | Phase 4–5 | Pending |
| OUT-02 | Phase 4–5 | Pending |
| OUT-03 | Phase 4–5 | Pending |

| MOD-01 | Phase 6 | Pending |
| MOD-02 | Phase 6 | Pending |
| MOD-03 | Phase 7 | Pending |
| MOD-04 | Phase 8 | Pending |
| MOD-05 | Phase 7 | Pending |
| MOD-06 | Phase 6 | Pending |
| MOD-07 | Phase 6 | Pending |
| MOD-08 | Phase 6 | Pending |
| MOD-09 | Phase 6 | Pending |
| MOD-10 | Phase 6 | Pending |
| FORE-01 | Phase 8 | Pending |
| FORE-02 | Phase 8 | Pending |
| FORE-03 | Phase 8 | Pending |
| FORE-04 | Phase 8 | Pending |

**Coverage:**
- v1 requirements: 39 total
- v2 requirements: 16 total (PREP-01–02, MOD-01–10, FORE-01–04)
- Mapped to phases: 55
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-04*
*Last updated: 2026-04-04 after initial definition*
