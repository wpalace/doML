---
phase: 06-data-modelling-regression-classification
plan: 02
status: complete
completed: 2026-04-07
---

# Plan 06-02 Summary: Regression Modelling Notebook Template

## Artifact Produced

`.claude/doml/templates/notebooks/modelling_regression.ipynb` — valid nbformat v4, 23 cells.

## Implementation

Full regression modelling template implementing Decisions 2, 4, 5, 6, 7, 8:

**Holdout + CV (Decision 4):**
- 80/20 train/test split at top of notebook; test set sealed
- 5-fold KFold CV on training set (recommends 10 if row_count < 2000)
- Leaderboard shows CV metrics only (mean ± std) — test set not revealed until after Optuna

**Baseline (Decision 4 / MOD-07):**
- DummyRegressor(strategy='mean') always first in leaderboard

**Models:**
- DummyRegressor, Ridge, Lasso, RandomForestRegressor, XGBRegressor, LGBMRegressor

**Primary metrics:** RMSE (primary), MAE, R² (secondary)

**SHAP (Decision 6):**
- TreeExplainer for tree-based; LinearExplainer for Ridge/Lasso
- summary_plot (bar + beeswarm), top-10 features
- Computed on first CV split validation fold
- Saved to `reports/shap_{model_name}.png`

**Optuna (Decision 5):**
- Top-3 leaderboard models tuned, 30 trials each
- Results appended to leaderboard with `(tuned)` suffix
- Best model serialized to `models/best_model.pkl` + `models/model_metadata.json`

**Python-only (Decision 7):** Top-of-notebook note about scikit-learn/SHAP/Optuna being Python-native

## Verification Passed

- nbformat.validate() → OK
- SEED=42, random.seed, np.random.seed, PROJECT_ROOT, correlation caveat: all OK
- DummyRegressor, leaderboard.csv, SHAP, Optuna, cross_val, best_model.pkl, model_metadata.json: all OK
