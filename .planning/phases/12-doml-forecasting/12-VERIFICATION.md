---
phase: 12-doml-forecasting
verified: 2026-04-13T10:00:00Z
status: human_needed
score: 5/5 roadmap success criteria verified
re_verification: false
deferred:
  - truth: "FORE-04 forecast tracking: compare predictions to actuals as new data arrives"
    addressed_in: "Milestone 4"
    evidence: "ROADMAP.md Phase 12 Note: 'FORE-04 (forecast actuals tracking) is deferred to Milestone 4. It requires multi-session state (saving forecast CSVs and a --compare command to diff against actuals).'"
human_verification:
  - test: "Run /doml-forecasting --horizon 12 --target sales on a project where time_factor=true"
    expected: "Notebook executes inside Docker, reports/forecasting_report.html is produced with hidden code, models/forecast_leaderboard.csv contains 6 model rows, HTML shows executive summary and prediction interval fan chart"
    why_human: "Requires Docker running with pmdarima installed (docker compose build after pip-compile) and a real time series dataset in data/processed/"
  - test: "Run /doml-forecasting on a project where time_factor=false in config.json"
    expected: "Skill exits immediately with message: 'This dataset was not identified as time series. Set time_factor=true in .planning/config.json to enable forecasting.'"
    why_human: "Requires a live Claude Code session to exercise the skill entry point — can't verify argument parsing behavior from static files alone"
  - test: "Run /doml-forecasting with --horizon flag omitted"
    expected: "Skill exits with message: 'Forecast horizon required. Run: /doml-forecasting --horizon N --target COLUMN_NAME'"
    why_human: "Requires a live Claude Code session to exercise argument validation"
  - test: "Review reports/forecasting_report.html after a run"
    expected: "Code cells hidden (--no-input), executive summary present, caveats section includes 'correlation is not causation', prediction interval fan chart visible"
    why_human: "Visual HTML report quality, OUT-03 disclaimer readability, and chart rendering require human eyes"
---

# Phase 12: doml-forecasting Verification Report

**Phase Goal:** Implement time series modelling and forecasting as a dedicated skill — ARIMA, Prophet, temporal CV, and prediction intervals — only activated when `time_factor=true` in `config.json`.
**Verified:** 2026-04-13T10:00:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `doml-forecasting` skill exists and generates `notebooks/forecasting.ipynb` | VERIFIED | `.claude/skills/doml-forecasting/SKILL.md` exists (commit 65bfcaa); template `.claude/doml/templates/notebooks/forecasting.ipynb` is valid nbformat v4 with 24 cells; workflow Step 6 copies template to `notebooks/forecasting.ipynb` |
| 2 | Notebook uses only `TimeSeriesSplit` — no random splits | VERIFIED | `TimeSeriesSplit` present in notebook; `KFold`, `StratifiedKFold`, `train_test_split` appear only in Section 4 markdown cell as documentation of what is NOT used (comment: "FORE-03: TimeSeriesSplit ONLY — no random splits ever") |
| 3 | ARIMA and Prophet compared in leaderboard with temporal CV metrics | VERIFIED | `auto_arima` (pmdarima) and `Prophet` both present in notebook cells; `add_regressor()` used for regressors; leaderboard CSV appends rows via `pd.concat` with existing file; `models/forecast_leaderboard.csv` path confirmed |
| 4 | Forecast output includes point prediction + 80% and 95% prediction intervals | VERIFIED | Notebook contains "80%", "95%", "Prediction Interval", "quantile" (LightGBM quantile objective), `QuantileRegressor` (LinearRegression), XGBoost empirical residual std; all 6 models produce interval columns |
| 5 | Skill exits early with a clear message if `time_factor=false` in `config.json` | VERIFIED | forecasting.md Step 2 contains: `TIME_FACTOR=$(python3 -c "import json; c=json.load(open('.planning/config.json')); print(c.get('time_factor', False))")` and stops with clear message if not `True` |

**Score:** 5/5 roadmap truths verified

### Deferred Items

Items not yet met but explicitly addressed in later milestone phases.

| # | Item | Addressed In | Evidence |
|---|------|-------------|----------|
| 1 | FORE-04: Forecast tracking — compare predictions to actuals as new data arrives | Milestone 4 | ROADMAP.md Phase 12 Note documents deferral. Notebook Section 10 includes manual actuals comparison procedure for analysts who need it before Milestone 4 |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.claude/skills/doml-forecasting/SKILL.md` | Skill entry point with correct frontmatter | VERIFIED | name=doml-forecasting, argument-hint includes --horizon/--target, execution_context -> forecasting.md, AskUserQuestion in allowed-tools |
| `.claude/doml/workflows/forecasting.md` | 11-step workflow with all required steps | VERIFIED | 362 lines; Steps 1-11 all present; time_factor guard, --horizon/--target required validation, 900s timeout, narrative insertion, HTML report checks, leaderboard verification |
| `.claude/doml/templates/notebooks/forecasting.ipynb` | Valid nbformat v4 notebook template | VERIFIED | 24 cells, nbformat=4; all 6 models, TimeSeriesSplit, prediction intervals, leaderboard write, ACF/PACF, caveats, FORE-04 placeholder |
| `requirements.in` | pmdarima added once, prophet not duplicated | VERIFIED | `grep -c "^pmdarima$" requirements.in` = 1; `grep -c "^prophet$" requirements.in` = 1 |
| `.planning/ROADMAP.md` (Phase 12 section) | FORE-04 deferral documented | VERIFIED | Phase 12 section has Note block with FORE-04 deferral rationale, both plan files listed, Milestone 4 referenced |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `.claude/skills/doml-forecasting/SKILL.md` | `.claude/doml/workflows/forecasting.md` | `execution_context` block `@.claude/doml/workflows/forecasting.md` | WIRED | Lines 25-27 of SKILL.md; also referenced in `<process>` block line 34 |
| `forecasting.md` Step 2 | `.planning/config.json` | `time_factor` check python3 inline | WIRED | Step 2 reads config.json and checks `time_factor` via python3 subprocess |
| `forecasting.ipynb` params cell | All model cells | `HORIZON = None` sentinel variable | WIRED | Params cell at notebook index 2 contains `HORIZON = None`; injector script detects this pattern; all downstream cells reference `HORIZON`, `TARGET_COL`, `REGRESSORS`, `SEASONALITY`, `INPUT_FILE_OVERRIDE` |
| `TimeSeriesSplit` loop | leaderboard rows | MAE/RMSE/MAPE per fold accumulation | WIRED | `TimeSeriesSplit` present; leaderboard `to_csv` at `models_dir / 'forecast_leaderboard.csv'` |
| `forecast_leaderboard.csv` write cell | `models/forecast_leaderboard.csv` | `pd.DataFrame.to_csv` with append-mode logic | WIRED | `leaderboard_all.to_csv(lb_path, index=False)` after `pd.concat([existing_lb, leaderboard])` if file exists |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|-------------------|--------|
| `forecasting.ipynb` | `df` (time series data) | `pd.read_csv(input_path)` / `.parquet` / `.xlsx` from `INPUT_FILE_OVERRIDE` or `data/processed/` scan | Yes — reads real processed dataset | FLOWING |
| `forecasting.ipynb` | `leaderboard` | TimeSeriesSplit cross-validation metrics (MAE, RMSE, MAPE per fold per model) | Yes — computed from real model training | FLOWING |
| `forecasting.ipynb` | `forecast_leaderboard.csv` | `leaderboard_all.to_csv(lb_path)` | Yes — appends real run results | FLOWING |

### Behavioral Spot-Checks

Step 7b: SKIPPED for live execution checks (require Docker + real dataset). Static structural checks performed above instead.

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| SKILL.md recognizable by Claude Code | `ls .claude/skills/doml-forecasting/SKILL.md` | File exists, 36 lines | PASS |
| Workflow file substantive | `wc -l .claude/doml/workflows/forecasting.md` | 362 lines | PASS |
| pmdarima added once | `grep -c "^pmdarima$" requirements.in` | 1 | PASS |
| prophet not duplicated | `grep -c "^prophet$" requirements.in` | 1 | PASS |
| Notebook valid nbformat v4 | `python3 -c "import json; nb=json.load(open(...)); assert nb['nbformat']==4"` | nbformat=4, 24 cells | PASS |
| Commits documented in summaries exist | `git log 65bfcaa a7ebba6 525f2a2` | All 3 hashes resolve to real commits | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| CMD-16 | 12-01 | `doml-forecasting` — dedicated skill for time series modelling and forecasting; only runs when time-factor confirmed | SATISFIED | SKILL.md exists with name=doml-forecasting; forecasting.md Step 2 implements time_factor=true gate |
| MOD-04 | 12-02 | Modelling notebook generated for time series problems (ARIMA, Prophet, ETS) | SATISFIED | forecasting.ipynb contains ARIMA/SARIMA (via pmdarima), Prophet, plus LightGBM/XGBoost/LinearRegression/SeasonalNaive; 6-model leaderboard |
| FORE-01 | 12-02 | Forecasting notebook generated (time series problems only) | SATISFIED | forecasting.ipynb template created; workflow copies it to notebooks/forecasting.ipynb; Step 11 verifies models/forecast_leaderboard.csv exists |
| FORE-02 | 12-02 | Forecasts include point prediction + 80% and 95% prediction intervals | SATISFIED | Notebook contains "80%", "95%", "Prediction Interval", quantile objective for LightGBM, QuantileRegressor for LinearRegression, residual std for XGBoost |
| FORE-03 | 12-02 | Temporal cross-validation enforced (TimeSeriesSplit — no random splits) | SATISFIED | TimeSeriesSplit present in notebook; KFold/StratifiedKFold/train_test_split appear only in FORE-03 markdown documentation as explicitly excluded |
| FORE-04 | 12-01 | Forecast tracking support: compare predictions to actuals as new data arrives | DEFERRED | Explicitly deferred to Milestone 4 in ROADMAP.md. Notebook Section 10 contains documented manual procedure placeholder. Not a gap — intentional and documented. |

**Orphaned requirements check:** REQUIREMENTS.md traceability table maps FORE-01, FORE-02, FORE-03, FORE-04 to Phase 8 (historical planning artifact — these were later moved to Phase 12 during milestone restructuring). No requirements are orphaned from Phase 12's scope; all are accounted for.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `forecasting.ipynb` cell 2 (data load cell) | `except Exception: pass` | bare pass in except clause | Info | Legitimate error-handling pattern in datetime column detection loop — not a stub. Falls through to `if dt_col is None: raise ValueError(...)` check below it. No user-visible output suppressed. |

No blockers or stub anti-patterns found. The `except Exception: pass` is a standard Python pattern for probing column parseability; the actual error case is handled immediately after by `raise ValueError`.

### Human Verification Required

#### 1. End-to-End Run with Real Dataset

**Test:** On a project with `time_factor=true` in `config.json` and a processed CSV in `data/processed/`, run `/doml-forecasting --horizon 12 --target <column_name>`
**Expected:** Docker executes the notebook (≤900s), `notebooks/forecasting.ipynb` is populated with cell outputs, `reports/forecasting_report.html` is generated with code hidden, `models/forecast_leaderboard.csv` contains 6 model rows, completion message displays all three output paths
**Why human:** Requires Docker running with `pmdarima` installed after `pip-compile` + `docker compose build`; a real processed time series dataset must exist; HTML fan chart rendering requires visual inspection

#### 2. time_factor=false Early Exit

**Test:** On a project where `time_factor=false` (or absent) in `config.json`, invoke `/doml-forecasting --horizon 5 --target sales`
**Expected:** Skill stops immediately with message "This dataset was not identified as time series. Set time_factor=true in .planning/config.json to enable forecasting."
**Why human:** Requires a live Claude Code session to exercise skill invocation and argument resolution through the SKILL.md / workflow chain

#### 3. Missing Required Flag Validation

**Test:** Invoke `/doml-forecasting --target sales` (omitting --horizon), then invoke `/doml-forecasting --horizon 12` (omitting --target)
**Expected:** Each invocation stops with the appropriate error message naming the missing flag and showing the correct invocation format
**Why human:** Requires a live Claude Code session to verify Claude parses `$ARGUMENTS` correctly and stops before touching any files

#### 4. HTML Report Quality

**Test:** After a successful run, open `reports/forecasting_report.html` in a browser
**Expected:** Code cells are hidden (no input boxes), executive summary narrative is present as the first section, prediction interval fan chart is visible, caveats section contains "correlation is not causation" disclaimer, report is legible to a non-technical stakeholder
**Why human:** Visual report quality, stakeholder-readability, and chart rendering require human review; `--no-input` flag behavior can only be confirmed by viewing the output HTML

### Gaps Summary

No gaps. All 5 roadmap success criteria are verified against the actual codebase. All 6 required artifacts exist and are substantive and wired. FORE-04 is explicitly deferred to Milestone 4 with documentation in both ROADMAP.md and the notebook template.

Automated checks are complete. The 4 human verification items above are needed to confirm end-to-end execution behavior in a live Docker + Claude Code environment — they cannot be verified from static file inspection alone.

---

_Verified: 2026-04-13T10:00:00Z_
_Verifier: Claude (gsd-verifier)_
