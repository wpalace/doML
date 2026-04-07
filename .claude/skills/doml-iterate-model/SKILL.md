---
name: doml-iterate-model
description: "Generate a new modelling iteration notebook with analyst-supplied direction, run the full CV + leaderboard + SHAP + Optuna pipeline, and append results to models/leaderboard.csv for cross-iteration comparison"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

<objective>
Generate a new modelling iteration notebook incorporating analyst-supplied direction.

Reads the most recent modelling notebook and its Claude interpretation cell, generates a new version notebook (v{N+1}) with the specified focus, runs the full CV + leaderboard + SHAP + Optuna pipeline, and appends all results to `models/leaderboard.csv` for cross-iteration comparison.
</objective>

> ⚠️ **This command is a stub.** Full implementation is scheduled for Phase 6b planning. The command is registered and invocable, but will display the planned workflow and manual workaround. It does not yet generate notebooks autonomously.

<arguments>
- **direction** (optional): A quoted string describing the modelling focus for this iteration.
  - If omitted: defaults to re-running the same pipeline on the same problem type
  - Examples:
    - `/doml-iterate-model` — re-run baseline pipeline with same settings
    - `/doml-iterate-model "focus on XGBoost with deeper hyperparameter tuning"`
    - `/doml-iterate-model "try Lasso and Ridge with polynomial features for linear baseline"`
    - `/doml-iterate-model "drop correlated features flagged in preprocessing, retrain all models"`
</arguments>

<execution_context>
@.claude/doml/workflows/iterate-model.md
</execution_context>

<context>
Direction (optional): {{args}}
</context>

<process>
Execute the iterate-model workflow from @.claude/doml/workflows/iterate-model.md.
</process>
