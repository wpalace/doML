# Phase 11: Unified `doml-iterate` — Context

**Gathered:** 2026-04-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Merge `doml-iterate-model` and `doml-iterate-unsupervised` into a single `doml-iterate` command that:
- Auto-detects problem type from `config.json`
- Routes to the correct iteration pipeline (supervised or unsupervised)
- Always produces new versioned notebooks (never overwrites)
- Always produces new versioned HTML reports (never overwrites) — for all problem types
- Appends leaderboard results (never replaces)
- Fully implements the supervised iteration path (currently a stub)
- Retires `doml-iterate-model` and `doml-iterate-unsupervised` skills

This is a command unification + stub implementation phase. The unsupervised 10-step workflow is already fully implemented and is the reference pattern. Supervised iteration is currently a 7-step stub that must be fully implemented.

</domain>

<decisions>
## Implementation Decisions

### D-01: Direction argument format — positional (not `--direction` flag)
- Invocation: `/doml-iterate "direction string"` — bare positional argument
- Matches established pattern: `doml-iterate-unsupervised`, `doml-anomaly-detection --guidance`
- No `--direction` flag despite ITER-05 spec wording — positional is the DoML convention
- Empty invocation (`/doml-iterate` with no args) defaults to re-running the same pipeline

### D-02: HTML reports for all problem types (ITER-03 fully satisfied)
- Every iteration produces a versioned HTML report regardless of problem type:
  - Supervised: `reports/model_report_v{N}.html`
  - Clustering: `reports/clustering_report_v{N}.html`
  - Dimensionality reduction: `reports/dimreduction_report_v{N}.html`
- Report content: code hidden (`nbconvert --no-input`), Claude narrative comparing this iteration vs prior, metric delta table
- Version number matches the notebook version (model_report_v2.html ↔ modelling_regression_v2.ipynb)
- Phase 7 deferred this for initial runs — Phase 11 adds it for iteration runs

### D-03: Supervised direction parsing — regex-first, Claude fallback
- Try structured regex pattern matching first for known patterns:
  - Model focus: `"XGBoost"`, `"Lasso"`, `"Ridge"` → narrow `models` dict to named models only
  - Optuna trials: `"trials=N"` → change `n_trials` in Optuna cells
  - Hyperparameter overrides: `"max_depth=N"`, `"n_estimators=N"` → inject into search space
  - Feature directives: `"drop {feature}"`, `"add polynomial"` → insert feature engineering cells
- If direction doesn't match any regex pattern → Claude interprets the natural language and writes new notebook cells directly using nbformat API
- Always add a Markdown annotation cell at the top of the algorithm section documenting the direction, regardless of which parsing path was used
- This matches the depth of unsupervised direction parsing (same structured-first approach)

### D-04: Unified command routes all four problem types
- `regression` → supervised pipeline (to be fully implemented)
- `classification` → supervised pipeline (to be fully implemented)
- `clustering` → unsupervised pipeline (already implemented in iterate-unsupervised.md)
- `dimensionality_reduction` → unsupervised pipeline (already implemented in iterate-unsupervised.md)
- Any other `problem_type` → clear error message with list of supported types

### D-05: Old commands removed
- `doml-iterate-model` skill directory deleted
- `doml-iterate-unsupervised` skill directory deleted
- `iterate-model.md` workflow deleted (superseded)
- `iterate-unsupervised.md` workflow absorbed into unified `iterate.md`
- `doml-progress` updated to reference `doml-iterate`

### Claude's Discretion
- Exact CSS/styling of new unsupervised HTML reports (follow established reports pattern)
- Whether to DRY-refactor shared steps between supervised/unsupervised into helper functions or keep them inline in the workflow
- Exact regex patterns for supervised direction parsing (model name matching, hyperparameter extraction)
- How to structure the unified `iterate.md` workflow file (single file with problem-type branches, or sub-workflows)

</decisions>

<specifics>
## Specific Ideas

- "By default the model should first evaluate if regex matching will achieve the user's guidance target. If it will not, the model may use full natural language" — this is the hybrid parsing approach for supervised direction strings
- The unsupervised workflow (`iterate-unsupervised.md`) is the reference implementation — supervised must match its 10-step structure
- HTML report version number must align with notebook version number for traceability

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing iteration workflows (primary reference)
- `.claude/doml/workflows/iterate-unsupervised.md` — Full 10-step unsupervised implementation; supervised must match this structure. Steps 1–10: config read, notebook discovery, prior interpretation, version resolution, template copy, cell modification, Docker exec, leaderboard append, interpretation cell, analyst report
- `.claude/doml/workflows/iterate-model.md` — Supervised stub (7 planned steps); shows intended structure but not implemented

### Skills to retire
- `.claude/skills/doml-iterate-model/SKILL.md` — Delete this directory
- `.claude/skills/doml-iterate-unsupervised/SKILL.md` — Delete this directory

### Established workflow patterns
- `.claude/doml/workflows/anomaly-detection.md` — Reference for `--guidance` argument handling (Phase 10 pattern)
- `.claude/doml/workflows/modelling.md` — Reference for supervised model execution, leaderboard write, HTML report generation via nbconvert

### Notebook templates (for supervised iteration)
- `.claude/doml/templates/notebooks/modelling_regression.ipynb` — Template to copy for regression v{N+1}
- `.claude/doml/templates/notebooks/modelling_classification.ipynb` — Template to copy for classification v{N+1}
- `.claude/doml/templates/notebooks/modelling_clustering.ipynb` — Template to copy for clustering v{N+1}
- `.claude/doml/templates/notebooks/modelling_dimreduction.ipynb` — Template to copy for dim_reduction v{N+1}

### Requirements
- `.planning/REQUIREMENTS.md` §"Unified Iteration" — ITER-01 through ITER-05
- `.planning/REQUIREMENTS.md` §"Commands" — CMD-15 definition

### Reproducibility rules
- `CLAUDE.md` §"Reproducibility Rules" — REPR-01 (seeds), REPR-02 (PROJECT_ROOT), REPR-03 (nbstripout), REPR-04 (pinned deps)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `doml/data_scan.py` — `scan_data_folder()` for locating input file from `config.json`
- `iterate-unsupervised.md` Steps 6–9 — nbformat cell modification, Docker exec, leaderboard append, interpretation cell — copy directly for supervised Steps 6–9
- `.planning/config.json` — `problem_type` field drives all routing

### Established Patterns
- Versioned notebooks: `notebooks/0{N}_modelling_{problem_type}_v{M}.ipynb` — glob + max version increment
- Leaderboard: append-only via `pd.concat` — never overwrite (ITER-04 confirmed in both existing workflows)
- nbformat cell injection: Python API only — never pass direction to shell (XSS-equivalent injection risk)
- HTML reports: `nbconvert --execute --to html --no-input` → verify file exists

### Integration Points
- `config.json` `problem_type` → routes to correct pipeline branch
- `models/leaderboard.csv` → supervised leaderboard (append)
- `models/unsupervised_leaderboard.csv` → unsupervised leaderboard (append)
- `reports/` → versioned HTML report output
- `notebooks/` → versioned notebook output

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 11-unified-doml-iterate*
*Context gathered: 2026-04-11*
