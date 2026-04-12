---
name: doml-iterate
description: "Generate a new modelling iteration for any problem type (regression, classification, clustering, dimensionality_reduction). Reads problem_type from config.json, always produces a new versioned notebook and HTML report, appends leaderboard results."
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

<objective>
Run a new modelling iteration for the current project's problem type (auto-detected from `.planning/config.json`).

This unified command covers all four problem types:
- `regression` — supervised pipeline: CV, RMSE, SHAP, Optuna, leaderboard append
- `classification` — supervised pipeline: CV, ROC-AUC, SHAP, Optuna, leaderboard append
- `clustering` — unsupervised pipeline: KMeans, DBSCAN, hierarchical, internal metrics, leaderboard append
- `dimensionality_reduction` — unsupervised pipeline: PCA, UMAP, t-SNE, variance explained, leaderboard append

Every iteration produces:
1. A new versioned notebook (e.g., `notebooks/04_modelling_regression_v2.ipynb`) — never overwrites prior versions
2. A versioned HTML report (e.g., `reports/model_report_v2.html`) with code hidden and a narrative comparing this iteration to the prior one
3. An appended row in the relevant leaderboard CSV — never replaces existing results
</objective>

<arguments>
- **direction** (optional): A quoted positional string describing the iteration focus.
  - If omitted: defaults to re-running the same pipeline with the same settings
  - Direction is parsed regex-first (structured patterns recognised automatically); unrecognised directions fall back to Claude natural-language interpretation
  - Examples:
    - `/doml-iterate` — re-run baseline pipeline with same settings
    - `/doml-iterate "focus on XGBoost with deeper hyperparameter search"`
    - `/doml-iterate "try Lasso with polynomial features"`
    - `/doml-iterate "try DBSCAN with finer eps grid around 0.3"`
    - `/doml-iterate "apply UMAP with n_neighbors=5"`
</arguments>

<execution_context>
@.claude/doml/workflows/iterate.md
</execution_context>

<context>
Direction (optional): {{args}}
</context>

<process>
Execute the iterate workflow from @.claude/doml/workflows/iterate.md.
</process>
