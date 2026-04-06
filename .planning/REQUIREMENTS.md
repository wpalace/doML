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

**Coverage:**
- v1 requirements: 39 total
- Mapped to phases: 39
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-04*
*Last updated: 2026-04-04 after initial definition*
