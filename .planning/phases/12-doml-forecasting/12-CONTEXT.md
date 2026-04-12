# Phase 12: `doml-forecasting` — Context

**Gathered:** 2026-04-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement a dedicated time series forecasting skill that activates only when `time_factor=true` in `config.json`. When invoked, it generates `notebooks/forecasting.ipynb` with a full leaderboard (SeasonalNaive + ARIMA/SARIMA + Prophet + global models), prediction intervals, temporal CV, and a stakeholder HTML report. This phase does NOT implement forecast tracking against actuals (FORE-04 deferred to backlog).

Input: `data/processed/` dataset (not raw). The analyst must specify a target column and optionally regressor columns. Prophet uses regressors; ARIMA/SARIMA runs univariate on the target.

</domain>

<decisions>
## Implementation Decisions

### D-01: FORE-04 (forecast tracking) — deferred to backlog
- Phase 12 implements CMD-16, FORE-01, FORE-02, FORE-03 only
- FORE-04 ("compare predictions to actuals as new data arrives") is too complex for this phase — requires multi-session state
- The notebook includes a placeholder section documenting how to do manual comparison when actuals arrive
- FORE-04 added to roadmap backlog for Milestone 4

### D-02: Forecast horizon — required `--horizon N` argument
- No default horizon — the analyst must specify explicitly (e.g. `/doml-forecasting --horizon 30 --target sales`)
- Forces the analyst to think about the business time horizon before forecasting
- Error if `--horizon` is omitted: "Forecast horizon required. Run: /doml-forecasting --horizon N --target COLUMN_NAME"
- Horizon N = number of periods ahead (period length inferred from time index frequency)

### D-03: Input source — `data/processed/` only
- Always reads from `data/processed/` — not `data/raw/`
- The EDA / preprocessing step is responsible for ensuring time-series-ready formatting (date parsing, frequency regularization, sorted index) before `doml-forecasting` is run
- If no file is found in `data/processed/`, stop with a clear message: "Run /doml-data-understanding and preprocessing first"
- File selection: uses `config.json` `dataset.path` basename to locate the processed file (same pattern as other doml skills)

### D-04: Univariate ARIMA/SARIMA + multivariate Prophet with regressors
- ARIMA/SARIMA: univariate on `--target` column only
- Prophet: uses `--regressors` columns via `add_regressor()` if provided; univariate otherwise
- LightGBM, XGBoost, Linear Regression: use lag features derived from `--target` column; optionally include `--regressors` as additional features
- Column specification flags:
  - `--target COLUMN_NAME` — required; the column to forecast
  - `--regressors COL1,COL2` — optional; comma-separated list of regressor columns for Prophet and global models

### D-05: Seasonality — auto-detect + `--seasonality` override
- Auto-detect dominant seasonal period using ACF/PACF analysis (statsmodels) and time index frequency inference
- Log the detected period in the notebook so it's transparent (not silent)
- Prophet: uses built-in seasonality inference (yearly/weekly/daily) — auto
- ARIMA/SARIMA: if seasonal period detected, use SARIMA with `m=period`; if not detected, use plain ARIMA
- Analyst override: `--seasonality daily|weekly|monthly|yearly|none` overrides auto-detection for all models
- SeasonalNaive baseline: uses auto-detected or overridden seasonal period

### D-06: Model scope — 6 models in leaderboard
1. **SeasonalNaive** — baseline; repeats last season's values
2. **ARIMA/SARIMA** — via `pmdarima.auto_arima()` for automatic order selection; seasonal variant if period detected
3. **Prophet** — with optional regressors; uncertainty intervals natively
4. **LightGBM** — lag features + rolling stats; TimeSeriesSplit CV
5. **XGBoost** — same feature engineering as LightGBM; TimeSeriesSplit CV
6. **Linear Regression** — same features; interpretable global baseline

All models evaluated on `TimeSeriesSplit` (FORE-03) — no random splits ever.
Metrics: MAE, RMSE, MAPE (where defined — avoids division by zero on zero targets).

### D-07: Prediction intervals (FORE-02)
- Point prediction + 80% and 95% prediction intervals for all models
- Prophet: native uncertainty intervals
- ARIMA/SARIMA: `get_forecast()` confidence intervals
- LightGBM/XGBoost/Linear: quantile regression approach (quantile 0.1, 0.5, 0.9 for 80% interval; 0.025, 0.5, 0.975 for 95%)
- SeasonalNaive: empirical intervals from residual standard deviation

### D-08: Skill invocation pattern — follows established doml conventions
- Command: `/doml-forecasting --horizon N --target COLUMN [--regressors COL1,COL2] [--seasonality PERIOD] [--guidance "..."]`
- `--guidance "..."` pattern: same as modelling.md and anomaly-detection.md — shapes Claude's narrative interpretation
- Early exit if `time_factor=false`: "This dataset was not identified as time series. Set time_factor=true in .planning/config.json to enable forecasting."

### Claude's Discretion
- Exact lag feature engineering (lag-1, lag-7, lag-30 vs others) — inferred from detected seasonal period
- Visualization choices (ACF/PACF plots, forecast fan charts, error distribution plots)
- HTML report CSS/styling — follows existing report patterns
- Exact pmdarima auto_arima hyperparameter ranges (stepwise search or full grid)
- Whether to add `pmdarima` to requirements.in (it's not currently installed) — researcher should verify

</decisions>

<specifics>
## Specific Ideas

- "When time is selected as important, the EDA step needs to ensure the data is adequately formatted for time series" — this is a deferred improvement to doml-data-understanding (not Phase 12 scope), but Phase 12 docs should clearly state the expected input format
- Leaderboard includes both classical (ARIMA/SARIMA, Prophet) and ML-based global models (LightGBM, XGBoost, Linear) — gives analyst a comparison across paradigms
- SARIMA variant auto-selected (vs plain ARIMA) based on seasonal period detection — no manual model type selection needed
- FORE-04 deferred: add to backlog as "forecast actuals tracking" — save forecast CSV + comparison command pattern when actuals arrive

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase requirements
- `.planning/REQUIREMENTS.md` §"Forecasting" — FORE-01 through FORE-04 (note FORE-04 deferred)
- `.planning/REQUIREMENTS.md` §"Commands" — CMD-16 definition
- `.planning/REQUIREMENTS.md` §"Modelling" — MOD-04 (ARIMA, Prophet, ETS spec)

### Established workflow patterns (reference implementations)
- `.claude/doml/workflows/anomaly-detection.md` — standalone skill pattern: config read → input file → notebook copy → Docker exec → HTML report → verification. `--guidance` flag handling.
- `.claude/doml/workflows/modelling.md` — reference for leaderboard structure, HTML report generation via nbconvert, `TimeSeriesSplit` pattern already used in supervised workflows
- `.claude/doml/workflows/iterate.md` — reference for versioned notebook patterns

### Existing skill structure
- `.claude/skills/doml-anomaly-detection/SKILL.md` — reference SKILL.md frontmatter (name, argument-hint, execution_context)
- `.claude/skills/doml-modelling/SKILL.md` — reference for multi-flag argument-hint format

### Notebook templates (for structure reference)
- `.claude/doml/templates/notebooks/modelling_regression.ipynb` — leaderboard pattern, CV structure, HTML report cell
- `.claude/doml/templates/notebooks/anomaly_detection.ipynb` — standalone notebook pattern, tidy validation, REPR-01/02

### Reproducibility rules (non-negotiable)
- `CLAUDE.md` §"Reproducibility Rules" — REPR-01 (seeds), REPR-02 (PROJECT_ROOT), REPR-03 (nbstripout), REPR-04 (pinned deps)

### Config schema
- `.planning/config.json` — `time_factor`, `dataset.path`, `dataset.format` fields used for routing and input file detection

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `doml/data_scan.py` — `scan_data_folder()` / `format_scan_report()` for locating input file from `config.json`
- `requirements.in` — scikit-learn (LightGBM/XGBoost for quantile regression, Linear Regression, TimeSeriesSplit) already installed; `prophet` and `pmdarima` need to be verified/added
- Existing notebooks use `TimeSeriesSplit` indirectly (data-understanding.md stationarity tests)

### Established Patterns
- Standalone workflow per skill: `anomaly-detection.md` Steps 1–11 — Phase 12 follows same pattern with `forecasting.md`
- Static nbformat v4 template: no Jinja2, dynamic content via Python code cells
- `--guidance "..."` flag: in `modelling.md` and `anomaly-detection.md` — same pattern
- nbconvert execute → nbconvert --no-input → HTML verify: standard across all Phase 8+ skills

### Integration Points
- `config.json` `time_factor` → early-exit gate (false = stop with message)
- `config.json` `dataset.path` → locate processed file in `data/processed/`
- `data/processed/` → input data landing zone
- `notebooks/` → output: `forecasting.ipynb`
- `reports/` → output: `forecasting_report.html`
- `models/` → output: `forecast_leaderboard.csv` (separate from regression/classification leaderboard)

</code_context>

<deferred>
## Deferred Ideas

- **FORE-04 (forecast actuals tracking)** — "compare predictions to actuals as new data arrives": save forecast CSV + `--compare` mode. Backlog for Milestone 4.
- **ETS model** — MOD-04 spec mentions ETS but user confirmed ARIMA/SARIMA + Prophet + global models is sufficient. ETS can be added in a future `/doml-iterate` iteration.
- **EDA time series formatting** — user noted that when `time_factor=true`, the EDA step should ensure time-series-ready output. This is a future enhancement to `doml-data-understanding`.
- **Multivariate forecasting (VAR models)** — full multivariate (multiple targets) deferred to Milestone 4. Phase 12 supports regressors in Prophet/global models only.
- **NeuralProphet** — considered but deferred; adds dependency and complexity.

</deferred>

---

*Phase: 12-doml-forecasting*
*Context gathered: 2026-04-12*
