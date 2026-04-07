---
phase: 06-data-modelling-regression-classification
plan: 01
status: complete
completed: 2026-04-07
---

# Plan 06-01 Summary: Preprocessing Notebook Template

## Artifact Produced

`.claude/doml/templates/notebooks/preprocessing.ipynb` — valid nbformat v4, 23 cells.

## Implementation

Full preprocessing notebook template covering all four areas from Decision 3:

**Section 1 — Imputation:**
- Detects numeric columns with missing values; compares SimpleImputer(median), SimpleImputer(mean), KNNImputer(n_neighbors=5)
- Shows before/after distributions for columns with >5% missing
- Categorical columns: SimpleImputer(most_frequent)
- Analyst Markdown cell for documenting chosen strategy per column

**Section 2 — Encoding:**
- Cardinality summary for all categorical columns
- OneHotEncoder for ≤10 unique values; OrdinalEncoder for >10 with risk note
- Analyst Markdown cell for encoding decisions

**Section 3 — Scaling:**
- Compares StandardScaler vs RobustScaler
- Markdown note: tree-based models (RF, XGBoost, LightGBM) do NOT require scaling
- ColumnTransformer assembles numeric path (imputer + scaler) and categorical path

**Section 4 — Feature Engineering & Selection:**
- Top 5 correlated pairs as candidate interaction features
- RandomForest / mutual_info importance ranking (guarded by problem_type)
- Flags column pairs with |r| > 0.95 for analyst review
- VIF computed for regression problems only

**Output:** Writes `data/processed/preprocessed_{original_filename}` (PREP-02)

## Reproducibility Compliance

- SEED = 42 set at cell 1 with random.seed(SEED) and np.random.seed(SEED) (REPR-01)
- PROJECT_ROOT resolved from os.environ.get('PROJECT_ROOT', '/home/jovyan/work') (REPR-02)
- No hardcoded absolute paths
- Final Markdown cell includes "Correlation is not causation" (OUT-03)
- nbformat.validate() passes

## Verification Passed

- `python3 -c "import nbformat; nb = nbformat.read('.claude/doml/templates/notebooks/preprocessing.ipynb', as_version=4); nbformat.validate(nb)"` → exits 0
- All 12 content checks: OK (config.json, data/processed, imputers, encoders, scalers, ColumnTransformer, VIF, mutual_info, preprocessed_ output)
