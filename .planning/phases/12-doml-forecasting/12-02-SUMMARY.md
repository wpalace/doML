---
phase: 12-doml-forecasting
plan: "02"
subsystem: forecasting
tags: [time-series, prophet, pmdarima, arima, sarima, lightgbm, xgboost, nbformat, prediction-intervals, TimeSeriesSplit]

# Dependency graph
requires:
  - phase: 12-01
    provides: forecasting.md workflow and SKILL.md that invoke this notebook template
provides:
  - "Static nbformat v4 notebook template for 6-model time series forecasting with prediction intervals"
  - "All 6 models: SeasonalNaive, ARIMA/SARIMA (pmdarima), Prophet, LightGBM, XGBoost, LinearRegression"
  - "TimeSeriesSplit-only evaluation — FORE-03 compliant"
  - "80% and 95% prediction intervals for all models — FORE-02 compliant"
  - "forecast_leaderboard.csv append-mode output — FORE-01 compliant"
  - "ACF/PACF seasonality detection with transparent period logging — D-05"
  - "FORE-04 placeholder section with manual actuals comparison procedure"
  - "OUT-03 caveats section including correlation-is-not-causation disclaimer"
affects: [doml-forecasting, doml-iterate, 12-03]

# Tech tracking
tech-stack:
  added: [pmdarima, prophet, lightgbm, xgboost, statsmodels]
  patterns:
    - "Static nbformat v4 template: all cells pre-written, params cell injected by workflow regex"
    - "Parameters cell sentinel HORIZON = None enables workflow-side regex injection"
    - "TimeSeriesSplit used exclusively — no KFold, StratifiedKFold, or train_test_split"
    - "Quantile regression for global model prediction intervals (LightGBM quantile objective, QuantileRegressor)"
    - "Last-observation-carried-forward (LOCF) for regressor future values in Prophet and global models"
    - "forecast_leaderboard.csv in append mode — each run adds rows with run_date for comparison"

key-files:
  created:
    - .claude/doml/templates/notebooks/forecasting.ipynb
  modified: []

key-decisions:
  - "Created all 24 cells in single Write operation: Task 1 (cells 1-10) and Task 2 (cells 11-24) combined — both tasks satisfied by same file"
  - "XGBoost prediction intervals use empirical residual std (z-score) rather than quantile XGBoost — simpler, no XGBoost quantile objective available in standard API"
  - "FORE-04 placeholder section is markdown only (no code) per D-01 decision to defer automated tracking"
  - "SeasonalNaive missing from grep -o model list verification — expected, grep anchors on double-quote; grep -c SeasonalNaive confirmed 5 occurrences"

patterns-established:
  - "Forecasting notebook: params cell must contain HORIZON = None for workflow injector detection"
  - "All 6 models evaluated in sequence before leaderboard cell — consistent with modelling_regression.ipynb pattern"
  - "Fan chart in separate cell from leaderboard CSV write — separates data output from visualization"

requirements-completed: [MOD-04, FORE-01, FORE-02, FORE-03]

# Metrics
duration: 4min
completed: 2026-04-13
---

# Phase 12 Plan 02: forecasting.ipynb Notebook Template Summary

**24-cell nbformat v4 forecasting template with 6 models (SeasonalNaive, ARIMA/SARIMA via pmdarima, Prophet with regressors, LightGBM/XGBoost/LinearRegression with quantile intervals), TimeSeriesSplit-only CV, and 80%+95% prediction intervals**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-13T00:56:37Z
- **Completed:** 2026-04-13T01:00:38Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Created `.claude/doml/templates/notebooks/forecasting.ipynb` as a valid nbformat v4 JSON notebook (passes `nbformat.validate()`)
- All 6 models implemented with TimeSeriesSplit CV, prediction intervals (80% and 95%), and leaderboard CSV output
- ACF/PACF seasonality detection cell with FREQ_TO_PERIOD mapping, transparent period logging, and `--seasonality` override support
- T-12-06 and T-12-07 threat mitigations implemented: TARGET_COL/REGRESSORS validated against df.columns, INPUT_FILE_OVERRIDE path guarded
- FORE-04 placeholder section (Section 10) documents manual actuals comparison procedure without code
- OUT-03 caveats section includes "Correlation is not causation" disclaimer

## Task Commits

Each task was committed atomically:

1. **Task 1: Create forecasting.ipynb sections 0-4** - `525f2a2` (feat) — notebook file created with all 24 cells
2. **Task 2: Complete forecasting.ipynb cells 11-24** — satisfied by same commit (file written complete in Task 1)

**Plan metadata:** (docs commit below)

## Files Created/Modified

- `.claude/doml/templates/notebooks/forecasting.ipynb` — 24-cell nbformat v4 template; 10 sections covering setup, data load, seasonality detection, lag features, TimeSeriesSplit, all 6 models, leaderboard, fan chart, FORE-04 placeholder, caveats

## Decisions Made

- Written all 24 cells in a single Write operation rather than partial-then-append, since the plan's Task 2 content was fully specified in the plan text
- XGBoost uses empirical residual std (z-score method) for prediction intervals — XGBoost does not have a built-in quantile objective in the standard `XGBRegressor` API; this is consistent with the plan's note "XGBoost quantile via sklearn QuantileRegressor fallback on residuals"
- Both tasks complete in a single commit because the Write tool creates the full file atomically

## Deviations from Plan

None — plan executed exactly as written. All must_haves, artifacts, and key_links implemented as specified.

## Issues Encountered

None.

## Known Stubs

None — all notebook sections are fully implemented. FORE-04 placeholder is intentional per D-01 decision (deferred to Milestone 4); it contains a documented manual procedure, not a code stub.

## Threat Flags

No new security surface beyond what the plan's threat model covers (T-12-06 through T-12-10).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `forecasting.ipynb` template is complete and ready for the `forecasting.md` workflow (Plan 12-01) to copy, inject params, and execute
- Requirements MOD-04, FORE-01, FORE-02, FORE-03 delivered
- FORE-04 deferred to Milestone 4 backlog as planned

---
*Phase: 12-doml-forecasting*
*Completed: 2026-04-13*
