---
name: doml-forecasting
description: "Run time series forecasting for projects where time_factor=true in config.json. Generates notebooks/forecasting.ipynb with a 6-model leaderboard (SeasonalNaive, ARIMA/SARIMA, Prophet, LightGBM, XGBoost, Linear Regression), 80%+95% prediction intervals, temporal CV (TimeSeriesSplit only), and reports/forecasting_report.html. Requires Docker to be running."
argument-hint: "--horizon N --target COLUMN [--regressors COL1,COL2] [--seasonality daily|weekly|monthly|yearly|none] [--guidance \"analyst direction\"]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>
Run the DoML Forecasting phase end-to-end:
1. Validate project state, read config.json, and check time_factor=true
2. Parse required --horizon N and --target COLUMN flags (error if absent)
3. Resolve input file from data/processed/ using config.json dataset.path basename
4. Copy notebooks/forecasting.ipynb template and execute inside Docker
5. Write a forecasting executive narrative (model comparison + actionable next steps)
6. Generate reports/forecasting_report.html with code hidden (OUT-02)
7. Verify models/forecast_leaderboard.csv was written
</objective>

<execution_context>
@.claude/doml/workflows/forecasting.md
</execution_context>

<context>
Arguments: $ARGUMENTS
</context>

<process>
Execute the forecasting workflow from @.claude/doml/workflows/forecasting.md end-to-end.
</process>
