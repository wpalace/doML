# Analysis Roadmap: PROJECT_NAME

**Dataset:** DATASET_FILE
**Problem type:** unknown (set during kickoff interview)
**Created:** YYYY-MM-DD

---

## Milestone 1 — Foundation + EDA

**Goal:** Establish business context, inventory the dataset, and produce a full exploratory data analysis with stakeholder reports.

### Phase 1: Business Understanding

**Goal:** Document business question, data inventory, ML problem type, and dataset provenance. Produce a stakeholder HTML report framing the problem.

**Requirements:** BU-01, BU-02, BU-03, BU-04, BU-05, OUT-01, OUT-02, OUT-03

**Success Criteria:**
1. `notebooks/01_business_understanding.ipynb` generated with narrative, data inventory, problem type, provenance
2. `reports/business_summary.html` generated with code hidden and executive narrative
3. HTML report includes caveats section (correlation ≠ causation)

**Output:**
- `notebooks/01_business_understanding.ipynb`
- `reports/business_summary.html`

---

### Phase 2: Data Understanding

**Goal:** Full EDA using DuckDB for large-file profiling, statistical tests, missing value analysis, tidy validation, and (if time_factor=true) stationarity tests. Produce stakeholder HTML report.

**Requirements:** EDA-01 through EDA-10, OUT-01, OUT-02, OUT-03

**Success Criteria:**
1. `notebooks/02_data_understanding.ipynb` generated with all EDA sections
2. DuckDB used for initial profiling — no full pandas load for large files
3. Distribution, correlation, and missing value analyses included
4. Time series stationarity tests included if time_factor=true
5. Tidy data violations flagged before feature engineering
6. Cleaned dataset written to `data/processed/`
7. `reports/eda_report.html` generated with code hidden and Claude narrative

**Output:**
- `notebooks/02_data_understanding.ipynb`
- `data/processed/[dataset]_cleaned.[ext]`
- `reports/eda_report.html`

---

## Milestone 2 — Modelling + Forecasting *(planned)*

### Phase 3: Data Preparation *(Milestone 2)*

**Goal:** Feature engineering, encoding, scaling, and train/test split — producing a modelling-ready dataset.

**Output:**
- `notebooks/03_data_preparation.ipynb`
- `data/processed/[dataset]_features.[ext]`

---

### Phase 4: Modelling *(Milestone 2)*

**Goal:** Algorithm selection, training, leaderboard, SHAP explainability, and Optuna tuning.

**Output:**
- `notebooks/04_modelling.ipynb`
- `models/best_model.pkl`
- `models/leaderboard.csv`
- `reports/model_report.html`

---

### Phase 5: Evaluation *(Milestone 2)*

**Goal:** Final model evaluation, forecast generation (if time_factor=true), stakeholder-facing report with business interpretation.

**Output:**
- `notebooks/05_evaluation.ipynb`
- `reports/final_report.html`

---

## Progress

| Phase | Milestone | Status | Completed |
|-------|-----------|--------|-----------|
| 1. Business Understanding | M1 | Not started | — |
| 2. Data Understanding | M1 | Not started | — |
| 3. Data Preparation | M2 | Not started | — |
| 4. Modelling | M2 | Not started | — |
| 5. Evaluation | M2 | Not started | — |
