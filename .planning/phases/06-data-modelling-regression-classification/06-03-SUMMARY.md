---
phase: 06-data-modelling-regression-classification
plan: 03
status: complete
completed: 2026-04-07
---

# Plan 06-03 Summary: Classification Modelling Notebook Template

## Artifact Produced

`.claude/doml/templates/notebooks/modelling_classification.ipynb` — valid nbformat v4, 23 cells.

## Implementation

Full classification modelling template — mirrors regression template structure with classification-specific adaptations:

**Holdout + CV (Decision 4):**
- 80/20 train/test split with `stratify=y` (maintains class balance)
- 5-fold StratifiedKFold CV on training set
- Leaderboard shows CV metrics only; test set sealed until final selection

**Baseline (Decision 4 / MOD-07):**
- DummyClassifier(strategy='most_frequent') always first in leaderboard

**Models:**
- DummyClassifier, LogisticRegression, RandomForestClassifier, XGBClassifier, LGBMClassifier

**Primary metrics:**
- Binary: ROC-AUC (primary), F1, precision, recall (secondary)
- Multi-class: macro F1 (primary), weighted F1 (secondary)
- Metric selection guarded by `n_classes` detection

**SHAP (Decision 6):**
- TreeExplainer for tree-based; LinearExplainer for LogisticRegression
- summary_plot saved to `reports/shap_{model_name}.png`

**Optuna (Decision 5):**
- Top-3 models, 30 trials each
- Tuned results appended to leaderboard
- Best model → `models/best_model.pkl` + `models/model_metadata.json`

## Verification Passed

- nbformat.validate() → OK
- SEED=42, random.seed, np.random.seed, PROJECT_ROOT, correlation caveat: all OK
- DummyClassifier, leaderboard.csv, SHAP, Optuna, StratifiedKFold, best_model.pkl, model_metadata.json: all OK
