# Phase 6 Context: Data Modelling — Regression & Classification

**Phase:** 06 — Data Modelling — Regression & Classification
**Goal:** Implement modelling notebooks for supervised learning problems (regression and classification) with scikit-learn Pipelines, XGBoost/LightGBM, leaderboard, SHAP explainability, and Optuna tuning.
**Requirements:** MOD-01, MOD-02, MOD-06, MOD-07, MOD-08, MOD-09, MOD-10

---

## Prior Phase Outputs (Carrying Forward)

From Phase 5:
- `data/processed/[filename]` — structurally cleaned dataset (duplicates removed, date columns parsed) — starting point for preprocessing
- `.planning/config.json` — `problem_type`, `time_factor`, `analysis_language`, `dataset.path`, `dataset.format`
- `.planning/PROJECT.md` — business question, stakeholder context, known data quality issues
- EDA notebook outputs: flagged data quality issues, missingness patterns, correlation insights, tidy violations

Phase 5 CONTEXT.md Decision 4 confirmed: imputation was explicitly deferred from EDA and belongs in the preprocessing Pipeline here.

Packages available (requirements.txt — pinned):
- `scikit-learn`, `xgboost`, `lightgbm`, `shap`, `optuna`
- `pandas`, `numpy`, `matplotlib`, `seaborn`
- `nbformat==5.10.4`, `nbconvert==7.16.4`, `papermill==2.6.0`
- `duckdb==1.5.1`

---

<decisions>

## Decision 1: Phase 6 Splits into Two Sub-Phases (Roadmap Change Required)

**Resolved:** Phase 6 is split into:
- **Phase 6a — Data Preprocessing**: dedicated notebook for imputation, encoding, scaling, feature engineering, and feature selection
- **Phase 6b — Data Modelling**: regression and classification modelling notebook(s) that consume the preprocessed dataset

**Why:** Preprocessing is comprehensive enough to warrant its own notebook and potentially multiple iteration notebooks. Conflating it with modelling would produce an unreadably long notebook and obscure the preprocessing decisions made.

**Roadmap impact:** ROADMAP.md needs updating to insert Phase 6a (Preprocessing) before Phase 6b (Modelling). Downstream phases (Clustering, Time Series, Reports) renumber accordingly. This update should happen before planning begins.

**How to apply:** Plan 06-01 covers the preprocessing notebook template. Plan 06-02 and beyond cover modelling templates. execute-phase.md routing for Phase 6 runs preprocessing first, then modelling.

---

## Decision 2: Separate Notebook Templates Per Problem Type (Iterative Starting Points)

**Resolved:** Two modelling templates:
- `.claude/doml/templates/notebooks/modelling_regression.ipynb`
- `.claude/doml/templates/notebooks/modelling_classification.ipynb`

**Templates are starting points, not final artifacts.** The framework explicitly encourages and supports generating multiple iteration notebooks as the analyst explores findings and refines models. A second run of `/doml-execute-phase` should generate `notebooks/04_modelling_v2.ipynb`, not overwrite `v1`.

**execute-phase routing:** Reads `config.json` `problem_type` and copies the appropriate template. Notebook filename follows pattern: `notebooks/0{N}_modelling_{problem_type}_v{iteration}.ipynb` — never overwrites a prior version.

**How to apply:** execute-phase.md Phase 3 executor: check `problem_type`, select template, resolve next version number, copy to notebooks/, execute via nbconvert.

---

## Decision 3: Comprehensive Preprocessing Notebook

**Resolved:** The Phase 6a preprocessing notebook covers all four areas:

### 3a. Imputation
- Numeric: compare SimpleImputer(median), SimpleImputer(mean), KNNImputer(n_neighbors=5)
- Categorical: SimpleImputer(most_frequent) — standard, no comparison needed
- Present imputation impact: show before/after distributions for columns with significant missingness
- Analyst selects strategy per column; decision documented in a Markdown cell

### 3b. Encoding (Categorical)
- Low cardinality (≤ 10 unique values): OneHotEncoder (default)
- High cardinality (> 10 unique values): OrdinalEncoder with note explaining risk, or TargetEncoder if problem is supervised
- Present cardinality summary for all categorical columns
- Analyst selects per column

### 3c. Scaling / Normalization
- StandardScaler (default for linear models and SVMs)
- RobustScaler (recommended when outliers detected in EDA)
- Note: tree-based models (RF, XGBoost, LightGBM) do NOT require scaling — document this in a Markdown cell
- ColumnTransformer assembles the preprocessing pipeline with separate numeric and categorical paths

### 3d. Feature Engineering & Selection
- Interaction terms: present top 5 correlated feature pairs (from EDA) as candidate interactions
- Polynomial features: offered as option for linear regression problems
- Feature importance: RandomForest or mutual_info_regression/classif to rank features
- Correlation-based redundancy removal: flag pairs with |r| > 0.95, analyst decides which to drop
- VIF (variance inflation factor): computed for numeric features in regression problems, flags > 10

**Output:** Preprocessed dataset written to `data/processed/preprocessed_{original_filename}` — used as input to the modelling notebook.

**How to apply:** Plan 06-01 implements this notebook template. The preprocessing notebook is always the first artifact in Phase 6a.

---

## Decision 4: CV & Leaderboard Strategy — Holdout + 5-Fold CV

**Resolved:**
- **Holdout split:** 80% train / 20% test, stratified for classification (`stratify=y`). Split performed once at the top of the notebook; test set is sealed.
- **CV on training set:** 5-fold stratified CV for classification, 5-fold KFold for regression. Default 5 folds; notebook recommends 10 folds if `row_count < 2000`.
- **Leaderboard shows CV metrics only** (mean ± std across folds) — test set not used until final model selection. This enforces the "one peek" rule (MOD-06 requirement: held-out validation metrics only).
- **Test set reveal:** After Optuna tuning is complete and the best model is confirmed, test set score is computed and shown as the final row of the leaderboard with a distinct visual indicator.

**Primary metrics:**
- Regression: RMSE (primary), MAE, R² (secondary)
- Classification binary: ROC-AUC (primary), F1, precision, recall (secondary)
- Classification multi-class: macro F1 (primary), weighted F1 (secondary)

**Baseline always included (MOD-07):**
- Regression: DummyRegressor(strategy='mean')
- Classification: DummyClassifier(strategy='most_frequent')

**How to apply:** Leaderboard is a pandas DataFrame sorted by primary metric. Written to `models/leaderboard.csv` at each iteration (appended, not overwritten — all iteration results visible).

---

## Decision 5: Optuna Tuning — Top-3 Models, 30 Trials Each

**Resolved:** Optuna tunes the top 3 models from the leaderboard. Each model receives 30 trials.

**Implementation:**
- After baseline leaderboard is built, rank by primary metric, select top-3 (excluding DummyRegressor/Classifier)
- Run `optuna.create_study(direction='minimize'/'maximize')` per model with `n_trials=30`
- Tuned results are appended to the leaderboard with a `(tuned)` suffix in the model name
- Best tuned model is saved as `models/best_model.pkl` with `models/model_metadata.json`

**model_metadata.json contents (MOD-10):**
```json
{
  "model_name": "XGBRegressor (tuned)",
  "problem_type": "regression",
  "cv_metric": "rmse",
  "cv_score_mean": 12.34,
  "cv_score_std": 0.45,
  "test_score": 11.89,
  "feature_names": [...],
  "hyperparameters": {...},
  "training_date": "2026-04-07",
  "notebook_version": "v1"
}
```

**How to apply:** Optuna section follows the initial leaderboard section. Both the initial (untuned) and tuned results appear in the leaderboard — never replace, always append.

---

## Decision 6: SHAP Explainability — Every Model in Leaderboard

**Resolved (standard choices — no user input needed):**

| Model type | SHAP explainer | Visualizations |
|------------|---------------|----------------|
| Tree-based (RF, XGBoost, LGBM) | TreeExplainer | summary_plot (bar + beeswarm), top-10 features |
| Linear (Ridge, Lasso, Logistic) | LinearExplainer | summary_plot (bar), coefficients comparison |
| Other | KernelExplainer (background: 100 samples) | summary_plot (bar) |

SHAP computed on the validation fold of the first CV split (not the full training set — faster and representative).

**How to apply:** SHAP section follows each model's CV results in the leaderboard loop. One summary plot per model, saved as `reports/shap_{model_name}.png` for use in the Phase 9 report.

---

## Decision 7: Python-Only for Modelling Phases

**Resolved:** Phase 6 (preprocessing and modelling) is Python-only. No R templates.

**Rationale:** scikit-learn, XGBoost, SHAP, and Optuna are Python-native with no R equivalents of comparable quality. R projects that used the R EDA notebook (Phase 5) switch to Python for modelling.

**User experience:** The preprocessing and modelling notebooks include a top-of-notebook note: "This notebook uses Python regardless of the `analysis_language` config setting. scikit-learn, SHAP, and Optuna do not have comparable R equivalents."

**Deferred:** R modelling via tidymodels is noted as a Milestone 3 item.

**How to apply:** execute-phase.md for Phase 6: no `analysis_language` check needed — always use Python templates.

---

## Decision 8: Claude Interprets Results + `/doml-iterate-model` Command

**Resolved:** After each modelling notebook is executed, Claude:
1. Reads the leaderboard CSV and SHAP outputs from the executed notebook
2. Writes an **Interpretation & Recommendations** Markdown cell at the end of the notebook
3. Includes: top model finding, any anomalies (e.g., low baseline gap), suggested next steps (e.g., "XGBoost is dominating — try deeper tuning", "High variance in CV suggests overfitting")
4. Does NOT autonomously create a new iteration notebook — waits for analyst instruction

**`/doml-iterate-model` command (new framework command):**
- Takes an optional direction argument: `/doml-iterate-model "focus on XGBoost with custom feature engineering"`
- Reads the most recent modelling notebook and its interpretation cell
- Generates a new iteration notebook (next version number) incorporating the specified direction
- Runs the same CV + leaderboard + SHAP + Optuna pipeline on the iteration
- Appends results to the shared `models/leaderboard.csv` for cross-iteration comparison

**How to apply:** Plan 06-0x includes a stub for the `/doml-iterate-model` skill and workflow. Full implementation deferred to Phase 6b planning.

</decisions>

---

<canonical_refs>
- `.planning/config.json` — `problem_type`, `time_factor`, `analysis_language`, `dataset.path`
- `.planning/PROJECT.md` — business context, target variable, known data quality issues
- `.planning/phases/05-data-understanding/05-CONTEXT.md` — Decision 4 (imputation deferred), Decision 5 (DuckDB/pandas split), Decision 7 (tidy validation)
- `data/processed/` — cleaned dataset from EDA phase; input to preprocessing notebook
- `.claude/doml/templates/notebooks/` — existing BU and EDA templates (reference for cell structure patterns)
- `.claude/doml/workflows/execute-phase.md` — Phase 1 and 2 executors (patterns to follow for Phase 3 executor)
- `CLAUDE.md` — REPR-01 (seeds), REPR-02 (PROJECT_ROOT), INFR-05 (data/raw read-only), OUT-03 (caveats)
- `REQUIREMENTS.md` — MOD-01 through MOD-10 definitions
</canonical_refs>

---

<deferred>
## Roadmap Change Required Before Planning

- **ROADMAP.md update:** Insert Phase 6a (Data Preprocessing) before the current Phase 6 (Data Modelling). Renumber Phase 7 → 8, Phase 8 → 9, Phase 9 → 10. The current Phase 6 (Regression & Classification) becomes Phase 6b or Phase 7.
- **REQUIREMENTS.md:** Add a new MOD-00 or PREP-01 requirement for the preprocessing notebook (covers Decision 3 above).

## Deferred to Later Phases

- R modelling (tidymodels/caret) — Milestone 3
- Multi-class calibration curves — Phase 9 (Modelling Reports)
- Clustering and dimensionality reduction preprocessing — Phase 7 (Clustering & Dim. Reduction)
- Time series preprocessing (differencing, de-trending) — Phase 8 (Time Series Modelling)
- `/doml-iterate-model` full workflow implementation — Phase 6b planning

## Deferred to Milestone 2 (or 3)

- Neural network support (PyTorch/TensorFlow) — deep learning milestone
- Automated feature engineering (featuretools) — increases scope significantly
- Model drift monitoring — deployment concern, out of scope for analysis framework
</deferred>
