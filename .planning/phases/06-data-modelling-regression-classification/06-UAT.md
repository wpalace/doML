---
phase: 06-data-modelling-regression-classification
session_started: 2026-04-08
session_completed: 2026-04-09
status: passed
tests_total: 8
tests_passed: 8
tests_failed: 0
tests_pending: 0
---

# Phase 6 UAT — Data Modelling (Regression & Classification)

## What Phase 6 Built

- `preprocessing.ipynb` template — imputation, encoding, scaling, feature selection, writes `preprocessed_*` output
- `modelling_regression.ipynb` template — DummyRegressor baseline, 5-fold CV, RMSE leaderboard, SHAP, Optuna top-3
- `modelling_classification.ipynb` template — DummyClassifier baseline, StratifiedKFold, ROC-AUC leaderboard, SHAP, Optuna top-3
- `execute-phase.md` Phase 3 executor — Steps 3g–3m (routing, copy, execute, interpret) + Steps 5i–5l (model_report.html)
- `/doml-iterate-model` stub — SKILL.md + iterate-model.md workflow

## Test Results

| # | Test | Result | Notes |
|---|------|--------|-------|
| T1 | preprocessing.ipynb is valid nbformat and has required sections | PASS | |
| T2 | preprocessing.ipynb: REPR-01/02 compliance + preprocessed_ output path | PASS | |
| T3 | modelling_regression.ipynb: baseline, CV, leaderboard, SHAP, Optuna present | PASS | |
| T4 | modelling_classification.ipynb: StratifiedKFold, ROC-AUC, DummyClassifier | PASS | |
| T5 | execute-phase.md: Step 3g problem_type routing present | PASS | |
| T6 | execute-phase.md: preprocessing → modelling → interpret flow (3h–3m) | PASS | |
| T7 | execute-phase.md: model_report.html generation (5i–5l) | PASS | |
| T8 | /doml-iterate-model: SKILL.md discoverable + iterate-model.md workflow stub present | PASS | |

## Issues Found and Fixed During UAT

1. **`mean_squared_error(squared=False)` removed in sklearn 1.8.0** — replaced with `root_mean_squared_error()` in `modelling_regression.ipynb`
2. **SHAP cell `plt.show()` after `plt.savefig()`** — replaced with `plt.close()` in both modelling templates
3. **ROC curves added to classification notebook** — new cell after leaderboard, binary + macro OvR, saves to `reports/images/roc_curves.png`
4. **Image path moved to `reports/images/`** — all SHAP and ROC plots now saved to `reports/images/` subdirectory
5. **Requirement tags (MOD-06, MOD-07, MOD-08) in markdown cells** — converted to HTML comments; invisible in report, preserved in source
6. **Interpretation & Recommendations placeholder duplicated in report** — executor now replaces placeholder cell instead of appending
7. **HTML report not generating automatically** — added explicit Step 3m → Steps 5i–5l routing; Step 5i rewritten as self-contained script
8. **Images not appearing in HTML report** — added `display(IPyImage(...))` after each `plt.close()` to embed images as cell outputs
